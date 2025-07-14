import streamlit as st
from typing import Dict, Optional


class ImageInputHandler:
    """画像入力処理クラス（未実装）"""
    
    def __init__(self):
        pass
    
    def render_image_input(self) -> Optional[Dict[str, int]]:
        """画像入力フォームを表示（未実装機能）"""
        st.header("📷 画像入力機能")
        
        # 未実装メッセージ
        st.info("🚧 **この機能は現在開発中です**")
        
        st.markdown("""
        ### 📋 予定されている機能
        - 📸 商品画像のアップロード
        - 🔍 AI画像認識による自動サイズ判定
        - 📊 検出結果の表示・修正
        
        ### 💡 現在の推奨方法
        商品数量は「**手動入力**」をご利用ください。
        """)
        
        # 手動入力への誘導
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔙 手動入力に戻る", type="primary", use_container_width=True):
                st.rerun()
        
        return None