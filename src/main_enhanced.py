import streamlit as st
import sys
import os

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.input_handler import InputHandler
from src.ui.output_renderer import OutputRenderer
from src.core.packing_optimizer import SimplePacking
from src.core.shipping_calculator import ShippingCalculator
from src.vision.image_processor import ImageInputHandler
from src.visualization.packing_3d import Packing3DVisualizer, PackingStepsGenerator
from src.advanced.multi_carrier import MultiCarrierManager


def main():
    st.set_page_config(
        page_title="ミノルキューブ最適配送システム v2.0",
        page_icon="📦",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📦 ミノルキューブ最適配送システム v2.0")
    st.markdown("### AI画像認識・3D可視化・詳細配送比較に対応した次世代梱包最適化ツール")
    st.markdown("---")
    
    # 初期化
    input_handler = InputHandler()
    image_handler = ImageInputHandler()
    output_renderer = OutputRenderer()
    packing_engine = SimplePacking()
    shipping_calculator = ShippingCalculator()
    visualizer_3d = Packing3DVisualizer()
    steps_generator = PackingStepsGenerator()
    multi_carrier = MultiCarrierManager()
    
    # サイドバー
    with st.sidebar:
        st.header("📋 システム情報 v2.0")
        
        # バージョン情報
        st.markdown("#### 🔧 バージョン")
        st.code("2.0.0 (Phase 2)")
        
        # 新機能
        st.markdown("#### 🆕 Phase 2 新機能")
        st.markdown("""
        - 🔥 **AI画像認識入力** (Beta)
        - 🔥 **3D可視化表示**
        - 🔥 **詳細配送比較**
        - 🔥 **梱包手順ガイド**
        """)
        
        # 従来機能
        st.markdown("#### ⚡ Phase 1 機能")
        st.markdown("""
        - ✅ 手動での商品数量入力
        - ✅ 最適輸送箱の自動選択  
        - ✅ 送料比較・最安値提案
        - ✅ 3D配置シミュレーション
        """)
        
        # 対応サイズ
        st.markdown("#### 📦 対応サイズ")
        size_info = [
            ("Sサイズ", "6.5×6.5×6.5cm", "0.073kg"),
            ("Sロング", "6.5×6.5×9.7cm", "0.099kg"),
            ("Lサイズ", "9.7×9.7×9.7cm", "0.169kg"),
            ("Lロング", "9.7×9.7×16.2cm", "0.246kg"),
            ("LLサイズ", "13×13×13cm", "0.308kg")
        ]
        
        for size, dimensions, weight in size_info:
            st.markdown(f"- **{size}**: {dimensions} ({weight})")
        
        st.markdown("---")
        
        # 使い方ガイド
        with st.expander("📖 v2.0 使い方ガイド", expanded=False):
            st.markdown("""
            ### 🚀 入力方法を選択
            
            #### 📱 画像入力 (推奨・Beta)
            1. 商品を明るい場所で撮影
            2. 画像をアップロード
            3. AI認識結果を確認・修正
            4. 計算実行
            
            #### ⌨️ 手動入力 (従来)
            1. 各サイズの個数を入力
            2. 計算実行
            
            ### 🎯 結果の確認
            - **基本結果**: 推奨箱と送料
            - **3D表示**: 立体的な梱包イメージ
            - **詳細比較**: 全運送業者比較
            - **手順ガイド**: ステップ詳細
            """)
    
    # メイン入力エリア
    st.header("📥 商品情報入力")
    
    # 入力方法選択
    input_method = st.radio(
        "入力方法を選択してください:",
        ["📷 画像入力 (AI認識・Beta)", "⌨️ 手動入力 (従来)"],
        horizontal=True
    )
    
    quantities = None
    
    if input_method == "📷 画像入力 (AI認識・Beta)":
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
                
                # 拡張配送オプション計算
                enhanced_options = multi_carrier.get_enhanced_shipping_options(packing_results)
                
                # タブで結果を整理
                tab1, tab2, tab3, tab4 = st.tabs([
                    "🎯 基本結果", 
                    "📦 3D可視化", 
                    "🚚 詳細配送比較", 
                    "📋 詳細梱包手順"
                ])
                
                with tab1:
                    st.header("🎯 基本最適化結果")
                    # 従来の結果表示
                    output_renderer.render_results(packing_results, shipping_options)
                    
                    # 推奨結果の詳細表示
                    recommended = packing_engine.get_packing_recommendation(packing_results)
                    if recommended:
                        output_renderer.render_packing_visualization(recommended)
                
                with tab2:
                    st.header("📦 3D梱包可視化")
                    if packing_results:
                        recommended = packing_engine.get_packing_recommendation(packing_results)
                        if recommended:
                            try:
                                # 3D可視化
                                fig_3d = visualizer_3d.create_3d_visualization(recommended)
                                st.plotly_chart(fig_3d, use_container_width=True)
                                
                                # 3D表示の説明
                                st.info("""
                                💡 **3D表示の操作方法:**
                                - **マウスドラッグ**: 視点回転
                                - **スクロール**: ズームイン/アウト
                                - **ダブルクリック**: リセット
                                - **ホバー**: 商品詳細表示
                                """)
                                
                            except Exception as e:
                                st.error(f"3D可視化エラー: {str(e)}")
                                st.info("3D表示には対応ライブラリが必要です。requirements.txtをご確認ください。")
                        else:
                            st.warning("3D表示用のデータがありません。")
                    else:
                        st.warning("表示するパッキング結果がありません。")
                
                with tab3:
                    st.header("🚚 詳細配送オプション比較")
                    if enhanced_options:
                        multi_carrier.render_enhanced_options(enhanced_options)
                    else:
                        st.warning("詳細配送オプションが見つかりませんでした。")
                
                with tab4:
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
    
    # フッター
    st.markdown("---")
    with st.expander("ℹ️ システム情報", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🔧 技術スタック:**
            - Streamlit (UI)
            - OpenCV (画像処理)
            - Plotly (3D可視化)
            - NumPy/SciPy (数値計算)
            """)
        
        with col2:
            st.markdown("""
            **📊 対応機能:**
            - AI画像認識 (Beta)
            - 3D配置シミュレーション
            - 多数運送業者対応
            - レスポンシブ対応
            """)


if __name__ == "__main__":
    main()