"""
Streamlit Community Cloud Entry Point
ミノルキューブ最適配送システム v3.0.0 (Cloud Edition)
"""

import sys
import os
import streamlit as st
import traceback

# Add src to path - using absolute path construction
current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

# Set environment for Streamlit Community Cloud
os.environ['ENVIRONMENT'] = 'production'
os.environ['STREAMLIT_CLOUD'] = 'true'

# Import and run the production application
try:
    from src.main_production import main
    
    # Run the application
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    st.error(f"❌ Production版の読み込みに失敗しました: {str(e)}")
    st.info("🔧 Cloud版にフォールバック中...")
    
    # Fallback to cloud version
    try:
        from src.main_cloud import main as cloud_main
        cloud_main()
    except ImportError as fallback_error:
        st.error(f"❌ フォールバックも失敗しました: {str(fallback_error)}")
        
        # Final fallback: Show basic info
        st.markdown("### 📦 ミノルキューブ最適配送システム v3.0.0")
        st.markdown("**システムの準備中です。しばらくお待ちください。**")
        
        # Debug traceback
        st.markdown("### 🔧 詳細エラー情報")
        st.code(traceback.format_exc())
    
except Exception as e:
    st.error(f"❌ システムエラー: {str(e)}")
    st.info("💡 サポートにお問い合わせください。")
    
    # Debug information
    st.markdown("### 🔧 デバッグ情報")
    st.code(f"Python version: {sys.version}")
    st.code(f"Working directory: {os.getcwd()}")
    st.code(f"Python path: {sys.path}")
    st.code(f"Traceback:\n{traceback.format_exc()}")