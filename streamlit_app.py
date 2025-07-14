"""
Streamlit Community Cloud Entry Point
ミノルキューブ最適配送システム v3.0.0 (Cloud Edition)
"""

import sys
import os
import streamlit as st

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set environment for Streamlit Community Cloud
os.environ['ENVIRONMENT'] = 'production'
os.environ['STREAMLIT_CLOUD'] = 'true'

# Import and run the cloud-optimized application
try:
    from src.main_cloud import main
    
    # Run the application
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    st.error(f"❌ インポートエラー: {str(e)}")
    st.info("🔧 システムの初期化中です。しばらくお待ちください...")
    
    # Fallback: Show basic info
    st.markdown("### 📦 ミノルキューブ最適配送システム v3.0.0")
    st.markdown("**システムの準備中です。しばらくお待ちください。**")
    
except Exception as e:
    st.error(f"❌ システムエラー: {str(e)}")
    st.info("💡 サポートにお問い合わせください。")
    
    # Debug information
    st.markdown("### 🔧 デバッグ情報")
    st.code(f"Python version: {sys.version}")
    st.code(f"Working directory: {os.getcwd()}")
    st.code(f"Python path: {sys.path}")