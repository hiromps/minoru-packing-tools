import streamlit as st
import sys
import os

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.input_handler import InputHandler
from src.ui.output_renderer import OutputRenderer
from src.core.packing_optimizer import SimplePacking
from src.core.shipping_calculator import ShippingCalculator

# Phase 2機能の条件付きインポート
try:
    from src.visualization.packing_3d import Packing3DVisualizer, PackingStepsGenerator
    from src.advanced.multi_carrier import MultiCarrierManager
    ADVANCED_FEATURES = True
except ImportError as e:
    ADVANCED_FEATURES = False
    IMPORT_ERROR = str(e)

try:
    from src.vision.image_processor import ImageInputHandler
    IMAGE_FEATURES = True
except ImportError as e:
    IMAGE_FEATURES = False
    IMAGE_ERROR = str(e)


def main():
    st.set_page_config(
        page_title="ミノルキューブ最適配送システム",
        page_icon="📦",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # ライブラリ依存状況の確認
    missing_libs = []
    if not ADVANCED_FEATURES:
        missing_libs.append("plotly (3D可視化用)")
    if not IMAGE_FEATURES:
        missing_libs.append("opencv-python (画像認識用)")
    
    # タイトル表示
    if missing_libs:
        st.title("📦 ミノルキューブ最適配送システム (Lite版)")
        st.warning(f"""
        **⚠️ 一部機能が無効です**
        
        以下のライブラリが不足しています:
        {', '.join(missing_libs)}
        
        **インストールコマンド:**
        ```bash
        pip install plotly opencv-python matplotlib
        ```
        """)
    else:
        st.title("📦 ミノルキューブ最適配送システム v2.0")
    
    st.markdown("### サイズの異なるミノルキューブ商品を最適な輸送箱で配送するためのツール")
    st.markdown("---")
    
    # 初期化
    input_handler = InputHandler()
    output_renderer = OutputRenderer()
    packing_engine = SimplePacking()
    shipping_calculator = ShippingCalculator()
    
    if ADVANCED_FEATURES:
        visualizer_3d = Packing3DVisualizer()
        steps_generator = PackingStepsGenerator()
        multi_carrier = MultiCarrierManager()
    
    if IMAGE_FEATURES:
        image_handler = ImageInputHandler()
    
    # サイドバー
    with st.sidebar:
        st.header("📋 システム情報")
        
        # 機能状況
        st.markdown("#### 🔧 利用可能機能")
        st.markdown("✅ **基本機能 (Phase 1)**")
        st.markdown("- 手動入力")
        st.markdown("- パッキング最適化")
        st.markdown("- 送料計算")
        
        if IMAGE_FEATURES:
            st.markdown("✅ **画像認識** (Phase 2)")
        else:
            st.markdown("❌ **画像認識** (要: opencv-python)")
        
        if ADVANCED_FEATURES:
            st.markdown("✅ **拡張機能** (Phase 2)")
            st.markdown("- 3D可視化")
            st.markdown("- 詳細配送比較")
            st.markdown("- 梱包手順ガイド")
        else:
            st.markdown("❌ **拡張機能** (要: plotly等)")
        
        # インストールガイド
        if missing_libs:
            with st.expander("📥 ライブラリインストール", expanded=True):
                st.code("""
                # 全機能を有効にする
                pip install plotly opencv-python matplotlib tensorflow ultralytics
                
                # または最小構成
                pip install plotly opencv-python
                """)
        
        # 対応サイズ
        st.markdown("#### 📦 対応サイズ")
        size_info = [
            ("Sサイズ", "6.5×6.5×6.5cm"),
            ("Sロング", "6.5×6.5×9.7cm"),
            ("Lサイズ", "9.7×9.7×9.7cm"),
            ("Lロング", "9.7×9.7×16.2cm"),
            ("LLサイズ", "13×13×13cm")
        ]
        
        for size, dimensions in size_info:
            st.markdown(f"- **{size}**: {dimensions}")
    
    # メイン入力エリア
    st.header("📥 商品情報入力")
    
    # 入力方法選択
    input_options = ["⌨️ 手動入力"]
    if IMAGE_FEATURES:
        input_options.insert(0, "📷 画像入力 (AI認識・Beta)")
    
    if len(input_options) > 1:
        input_method = st.radio(
            "入力方法を選択してください:",
            input_options,
            horizontal=True
        )
    else:
        input_method = input_options[0]
        st.info("💡 画像入力機能を使用するには `pip install opencv-python` を実行してください。")
    
    quantities = None
    
    if input_method.startswith("📷") and IMAGE_FEATURES:
        quantities = image_handler.render_image_input()
    else:
        quantities = input_handler.render_manual_input()
    
    if quantities:
        # 入力内容の確認表示
        input_handler.display_product_summary(quantities)
        
        # 計算実行
        with st.spinner("🔍 最適な配送方法を計算中..."):
            packing_results = packing_engine.calculate_packing(quantities)
            
            if packing_results:
                # 基本送料計算
                shipping_options = shipping_calculator.calculate_shipping_options(packing_results)
                
                # タブ構成の決定
                tabs = ["🎯 基本結果"]
                if ADVANCED_FEATURES:
                    tabs.extend(["📦 3D可視化", "🚚 詳細配送比較", "📋 詳細梱包手順"])
                
                if len(tabs) == 1:
                    # 基本機能のみ
                    st.header("🎯 最適化結果")
                    output_renderer.render_results(packing_results, shipping_options)
                    
                    recommended = packing_engine.get_packing_recommendation(packing_results)
                    if recommended:
                        output_renderer.render_packing_visualization(recommended)
                else:
                    # タブ表示
                    tab_objects = st.tabs(tabs)
                    
                    with tab_objects[0]:
                        st.header("🎯 基本最適化結果")
                        output_renderer.render_results(packing_results, shipping_options)
                        
                        recommended = packing_engine.get_packing_recommendation(packing_results)
                        if recommended:
                            output_renderer.render_packing_visualization(recommended)
                    
                    if ADVANCED_FEATURES and len(tab_objects) > 1:
                        # 拡張配送オプション計算
                        enhanced_options = multi_carrier.get_enhanced_shipping_options(packing_results)
                        
                        with tab_objects[1]:
                            st.header("📦 3D梱包可視化")
                            if packing_results:
                                recommended = packing_engine.get_packing_recommendation(packing_results)
                                if recommended:
                                    try:
                                        fig_3d = visualizer_3d.create_3d_visualization(recommended)
                                        st.plotly_chart(fig_3d, use_container_width=True)
                                        
                                        st.info("""
                                        💡 **3D表示の操作方法:**
                                        - **マウスドラッグ**: 視点回転
                                        - **スクロール**: ズームイン/アウト
                                        - **ダブルクリック**: リセット
                                        - **ホバー**: 商品詳細表示
                                        """)
                                        
                                    except Exception as e:
                                        st.error(f"3D可視化エラー: {str(e)}")
                        
                        with tab_objects[2]:
                            st.header("🚚 詳細配送オプション比較")
                            if enhanced_options:
                                multi_carrier.render_enhanced_options(enhanced_options)
                            else:
                                st.warning("詳細配送オプションが見つかりませんでした。")
                        
                        with tab_objects[3]:
                            st.header("📋 詳細梱包手順")
                            recommended = packing_engine.get_packing_recommendation(packing_results)
                            if recommended:
                                steps = steps_generator.generate_packing_steps(recommended)
                                steps_generator.render_packing_steps(steps)
                            else:
                                st.warning("梱包手順を生成できませんでした。")
                        
            else:
                st.error("❌ 適切な輸送箱が見つかりませんでした。商品数量を見直してください。")
                st.info("💡 **ヒント**: 商品数を減らすか、より大きなサイズの箱が必要かもしれません。")


if __name__ == "__main__":
    main()