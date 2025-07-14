import streamlit as st
import sys
import os

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.input_handler import InputHandler
from src.ui.output_renderer import OutputRenderer
from src.core.packing_optimizer import SimplePacking
from src.core.shipping_calculator import ShippingCalculator


def main():
    st.set_page_config(
        page_title="ミノルキューブ最適配送システム",
        page_icon="📦",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📦 ミノルキューブ最適配送システム")
    st.markdown("### サイズの異なるミノルキューブ商品を最適な輸送箱で配送するためのツールです")
    st.markdown("---")
    
    # 初期化
    input_handler = InputHandler()
    output_renderer = OutputRenderer()
    packing_engine = SimplePacking()
    shipping_calculator = ShippingCalculator()
    
    # サイドバー
    with st.sidebar:
        st.header("📋 システム情報")
        
        # バージョン情報
        st.markdown("#### 🔧 バージョン")
        st.code("1.0.0 (MVP)")
        
        # 機能情報
        st.markdown("#### ⚡ 主な機能")
        st.markdown("""
        - ✅ 手動での商品数量入力
        - ✅ 最適輸送箱の自動選択  
        - ✅ 送料比較・最安値提案
        - ✅ 3D配置シミュレーション
        - 🚧 画像入力機能（開発中）
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
        
        st.markdown("---")
        
        # 使い方ガイド
        with st.expander("📖 使い方ガイド", expanded=False):
            st.markdown("""
            1. **商品数量を入力**
               各サイズの個数を入力
            
            2. **計算実行**
               「最適な輸送箱を計算」ボタンを押す
            
            3. **結果確認**
               推奨される輸送箱と送料を確認
            
            4. **詳細チェック**
               配置詳細情報で実現可能性を確認
            """)
    
    # メインコンテンツ
    quantities = input_handler.render_manual_input()
    
    if quantities:
        # 入力内容の確認表示
        input_handler.display_product_summary(quantities)
        
        # パッキング計算
        with st.spinner("🔍 最適な輸送箱を計算中..."):
            packing_results = packing_engine.calculate_packing(quantities)
            
            if packing_results:
                # 送料計算
                shipping_options = shipping_calculator.calculate_shipping_options(packing_results)
                
                # 結果表示
                output_renderer.render_results(packing_results, shipping_options)
                
                # 推奨結果の詳細表示
                recommended = packing_engine.get_packing_recommendation(packing_results)
                if recommended:
                    output_renderer.render_packing_visualization(recommended)
            else:
                st.error("❌ 適切な輸送箱が見つかりませんでした。商品数量を見直してください。")
                st.info("💡 **ヒント**: 商品数を減らすか、より大きなサイズの箱が必要かもしれません。")


if __name__ == "__main__":
    main()