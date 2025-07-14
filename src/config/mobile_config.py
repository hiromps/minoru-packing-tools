"""
モバイル専用設定とCSS
"""
import streamlit as st

def apply_mobile_styles():
    """モバイル向けのカスタムCSS"""
    st.markdown("""
    <style>
    /* モバイル最適化のためのCSS */
    
    /* 基本設定 */
    .main .block-container {
        max-width: 100% !important;
        padding: 1rem !important;
    }
    
    /* ヘッダー調整 */
    .main h1, .main h2, .main h3 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* ボタン調整 */
    .stButton > button {
        width: 100% !important;
        margin-bottom: 0.5rem !important;
        font-size: 16px !important;
        padding: 0.5rem 1rem !important;
    }
    
    /* 入力フィールド調整 */
    .stNumberInput > div > div > input {
        font-size: 16px !important;
        padding: 0.5rem !important;
    }
    
    /* メトリクス調整 */
    .metric-container {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    
    /* テーブル調整 */
    .stDataFrame {
        font-size: 14px !important;
    }
    
    /* サイドバー調整 */
    .css-1d391kg {
        width: 100% !important;
    }
    
    /* コンテナ間のスペース */
    .element-container {
        margin-bottom: 0.5rem !important;
    }
    
    /* タブ調整 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 1rem;
        font-size: 14px;
    }
    
    /* エキスパンダー調整 */
    .streamlit-expanderHeader {
        font-size: 16px !important;
        padding: 0.5rem !important;
    }
    
    /* カード風レイアウト */
    .mobile-card {
        background-color: #ffffff;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* クイックアクションボタン */
    .quick-action-button {
        font-size: 14px !important;
        padding: 0.25rem 0.5rem !important;
        margin: 0.1rem !important;
    }
    
    /* レスポンシブ対応 */
    @media screen and (max-width: 768px) {
        .main .block-container {
            padding: 0.5rem !important;
        }
        
        .stColumns {
            gap: 0.5rem !important;
        }
        
        .stColumn {
            min-width: 0 !important;
        }
        
        /* テキストサイズ調整 */
        .stMarkdown p {
            font-size: 14px !important;
        }
        
        /* フォーム要素のサイズ */
        .stSelectbox, .stTextInput, .stNumberInput {
            margin-bottom: 0.5rem !important;
        }
    }
    
    /* 超小型画面対応 */
    @media screen and (max-width: 480px) {
        .main .block-container {
            padding: 0.25rem !important;
        }
        
        .stButton > button {
            font-size: 14px !important;
            padding: 0.4rem 0.8rem !important;
        }
        
        .stNumberInput > div > div > input {
            font-size: 14px !important;
        }
        
        /* タブを縦並びに */
        .stTabs [data-baseweb="tab-list"] {
            flex-direction: column !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            width: 100% !important;
            text-align: center !important;
        }
    }
    
    /* ダークモード対応 */
    @media (prefers-color-scheme: dark) {
        .mobile-card {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        
        .metric-container {
            background-color: #2d2d2d;
        }
    }
    
    /* タッチ操作最適化 */
    .stButton > button, .stSelectbox, .stNumberInput {
        touch-action: manipulation;
        -webkit-tap-highlight-color: transparent;
    }
    
    /* スクロール最適化 */
    .main {
        scroll-behavior: smooth;
    }
    
    /* アニメーション軽量化 */
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
    </style>
    """, unsafe_allow_html=True)

def configure_mobile_layout():
    """モバイル向けStreamlit設定"""
    st.set_page_config(
        page_title="📦 ミノルキューブ配送システム",
        page_icon="📦",
        layout="wide",
        initial_sidebar_state="collapsed",  # モバイルではサイドバーを初期非表示
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': None
        }
    )

def add_mobile_navigation():
    """モバイル向けナビゲーション"""
    st.markdown("""
    <div style="position: fixed; bottom: 0; left: 0; right: 0; 
                background: white; padding: 0.5rem; border-top: 1px solid #ddd; 
                z-index: 999; display: flex; justify-content: space-around;">
        <button onclick="window.scrollTo(0, 0)" style="border: none; background: none; 
                color: #666; font-size: 12px; cursor: pointer;">
            ⬆️ トップ
        </button>
        <button onclick="window.scrollTo(0, document.body.scrollHeight)" 
                style="border: none; background: none; color: #666; 
                font-size: 12px; cursor: pointer;">
            ⬇️ 下部
        </button>
    </div>
    """, unsafe_allow_html=True)

def mobile_friendly_dataframe(df, height=None):
    """モバイル対応のデータフレーム表示"""
    return st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=height or min(400, len(df) * 35 + 100)
    )

def mobile_metric_card(title, value, delta=None, help_text=None):
    """モバイル向けメトリクスカード"""
    with st.container():
        st.markdown(f"""
        <div class="mobile-card">
            <h4 style="margin-bottom: 0.5rem; color: #666;">{title}</h4>
            <h2 style="margin: 0; color: #333;">{value}</h2>
            {f'<p style="margin: 0.25rem 0; color: #666; font-size: 14px;">{delta}</p>' if delta else ''}
            {f'<p style="margin: 0.25rem 0; color: #888; font-size: 12px;">{help_text}</p>' if help_text else ''}
        </div>
        """, unsafe_allow_html=True)

def mobile_progress_bar(progress, text=""):
    """モバイル向けプログレスバー"""
    st.progress(progress)
    if text:
        st.caption(text)

def mobile_info_card(title, content):
    """モバイル向け情報カード"""
    with st.expander(title, expanded=False):
        st.markdown(content)

def mobile_quick_actions(actions):
    """モバイル向けクイックアクションボタン"""
    cols = st.columns(len(actions))
    for i, (label, callback) in enumerate(actions.items()):
        with cols[i]:
            if st.button(label, key=f"quick_{i}", use_container_width=True):
                callback()

def detect_mobile():
    """モバイル端末検出（JavaScript経由）"""
    st.markdown("""
    <script>
    function detectMobile() {
        return window.innerWidth <= 768;
    }
    
    if (detectMobile()) {
        document.body.classList.add('mobile-device');
    }
    </script>
    """, unsafe_allow_html=True)

def mobile_alert(message, alert_type="info"):
    """モバイル向けアラート"""
    icon_map = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌"
    }
    
    color_map = {
        "info": "#d1ecf1",
        "success": "#d4edda",
        "warning": "#fff3cd",
        "error": "#f8d7da"
    }
    
    st.markdown(f"""
    <div style="background-color: {color_map[alert_type]}; 
                padding: 1rem; border-radius: 0.5rem; 
                margin: 0.5rem 0; border-left: 4px solid #666;">
        {icon_map[alert_type]} {message}
    </div>
    """, unsafe_allow_html=True)