# パス設定 - main_production.pyの最初に追加
import streamlit as st
import sys
import os
import time
from pathlib import Path
from typing import Dict, Any

# プロジェクトルートをパスに追加
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

# プロジェクトルートをPythonパスに追加
# Define current_dir for compatibility (in case of deployment issues)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# 設定とユーティリティのインポート
from src.config.settings import settings, load_env_config
from src.config.mobile_config import apply_mobile_styles, configure_mobile_layout
from src.utils.logger import setup_logging, get_logger, log_user_action, log_calculation_result
from src.utils.performance import performance_monitor, cache_manager
from src.utils.error_handler import global_error_handler, streamlit_error_boundary
from src.utils.security import security_manager, require_valid_session, rate_limited

# アプリケーションコンポーネントのインポート
from src.ui.input_handler import InputHandler
from src.ui.output_renderer import OutputRenderer
from src.core.packing_optimizer import SimplePacking
from src.core.shipping_calculator import ShippingCalculator
from src.vision.image_processor import ImageInputHandler
from src.visualization.packing_3d import Packing3DVisualizer, PackingStepsGenerator
from src.advanced.multi_carrier import MultiCarrierManager


class ProductionApp:
    """本番環境対応アプリケーション"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.setup_application()
        self.initialize_components()
    
    def setup_application(self):
        """アプリケーション初期設定"""
        try:
            # 環境設定の読み込み
            load_env_config()
            
            # ログ設定
            setup_logging(
                environment=settings.environment,
                log_level=settings.logging.level
            )
            
            # Streamlit設定
            streamlit_config = settings.get_streamlit_config()
            
            st.set_page_config(
                page_title="ミノルキューブ最適配送システム [Production]",
                page_icon="📦",
                layout="wide",
                initial_sidebar_state="collapsed"  # モバイル対応
            )
            
            # モバイル対応設定
            apply_mobile_styles()
            
            # セッション初期化
            if 'session_id' not in st.session_state:
                st.session_state.session_id = security_manager.create_session()
            
            self.logger.info("Application setup completed")
            
        except Exception as e:
            st.error("⚠️ システム初期化エラーが発生しました。")
            global_error_handler.handle_error(e)
            st.stop()
    
    @performance_monitor.time_function("component_initialization")
    def initialize_components(self):
        """コンポーネント初期化"""
        try:
            self.input_handler = InputHandler()
            self.image_handler = ImageInputHandler()
            self.output_renderer = OutputRenderer()
            self.packing_engine = SimplePacking()
            self.shipping_calculator = ShippingCalculator()
            self.visualizer_3d = Packing3DVisualizer()
            self.steps_generator = PackingStepsGenerator()
            self.multi_carrier = MultiCarrierManager()
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Component initialization failed: {str(e)}")
            raise
    
    @require_valid_session
    def render_header(self):
        """ヘッダー表示"""
        # カスタムCSS - モダンスタイリング
        st.markdown("""
        <style>
        /* メインヘッダー */
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
            color: white;
        }
        
        .main-title {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .main-subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 0;
        }
        
        /* カードスタイル */
        .modern-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border: 1px solid #e6e9ef;
            margin-bottom: 1rem;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .modern-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        /* タブスタイル */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px;
            border: 2px solid transparent;
            background: linear-gradient(45deg, #f8f9fa, #e9ecef);
            color: #495057;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(45deg, #4f46e5, #7c3aed);
            color: white;
            box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);
        }
        
        /* メトリクススタイル */
        .metric-container {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.2rem;
        }
        
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        /* ボタンスタイル */
        .stButton > button {
            background: linear-gradient(45deg, #4f46e5, #7c3aed);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.7rem 2rem;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(79, 70, 229, 0.4);
        }
        
        /* プライマリボタン（計算ボタン）を赤色に */
        .stButton > button[data-testid="baseButton-primary"], 
        .stButton > button[kind="primary"] {
            background: linear-gradient(45deg, #e74c3c, #c0392b) !important;
            color: white !important;
            box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3) !important;
        }
        
        .stButton > button[data-testid="baseButton-primary"]:hover,
        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(45deg, #c0392b, #a93226) !important;
            color: white !important;
            box-shadow: 0 8px 25px rgba(231, 76, 60, 0.4) !important;
            transform: translateY(-2px);
        }
        
        /* 入力フィールド */
        .stNumberInput > div > div > input {
            border-radius: 8px;
            border: 2px solid #e6e9ef;
            transition: border-color 0.3s ease;
        }
        
        .stNumberInput > div > div > input:focus {
            border-color: #4f46e5;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        }
        
        /* ラジオボタン */
        .stRadio > div {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            border: 2px solid #e6e9ef;
        }
        
        /* サイドバー */
        .css-1d391kg {
            background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        }
        
        /* アニメーション */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .fade-in {
            animation: fadeInUp 0.6s ease-out;
        }
        
        /* スピナー */
        .stSpinner > div {
            border-color: #4f46e5 !important;
        }
        
        /* データテーブル */
        .dataframe {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # モダンヘッダー
        st.markdown("""
        <div class="main-header fade-in">
            <div class="main-title">📦 ミノルキューブ最適配送システム</div>
            <div class="main-subtitle">✨ エンタープライズ版 - 高性能・高セキュリティ対応 ✨</div>
        </div>
        """, unsafe_allow_html=True)
        
    
    def render_sidebar(self):
        """サイドバー表示"""
        with st.sidebar:
            with st.expander("ℹ️ システム情報", expanded=False):
                # バージョン情報
                st.markdown("#### 🔧 バージョン")
                st.code("3.0.0 (Production)")
                
                # 機能情報
                st.markdown("#### ⚡ 主要機能")
                st.markdown("""
                - 🔥 **AI画像認識入力**
                - 🔥 **3D可視化表示**
                - 🔥 **詳細配送比較**
                - 🔥 **梱包手順ガイド**
                - 🛡️ **エンタープライズセキュリティ**
                - ⚡ **高性能キャッシング**
                - 📊 **詳細ログ分析**
                """)
                
                # 技術スタック情報
                st.markdown("#### 🔧 技術スタック")
                st.markdown("""
                - Streamlit (UI Framework)
                - OpenCV (画像処理)
                - Plotly (3D可視化)
                - Redis (キャッシュ)
                """)
                
                # セキュリティ情報
                st.markdown("#### 🛡️ セキュリティ")
                st.markdown("""
                - ファイル検証
                - レート制限
                - セッション管理
                - ログ監視
                """)
                
                # パフォーマンス情報
                st.markdown("#### ⚡ パフォーマンス")
                st.markdown("""
                - インメモリキャッシュ
                - 並列処理
                - 最適化アルゴリズム
                - CDN対応
                """)
            
            # システム状態 - モダンボタン
            st.markdown("""
            <div style="text-align: center; margin: 1rem 0;">
            """, unsafe_allow_html=True)
            if st.button("🔍 システム状態確認", use_container_width=True):
                self.show_system_status()
            st.markdown("</div>", unsafe_allow_html=True)
            
            # 使い方ガイド
            with st.expander("📖 使い方ガイド", expanded=False):
                st.markdown("""
                ### 🚀 高効率な使い方
                
                1. **画像入力推奨**: AI認識で効率化
                2. **結果の活用**: 3D表示で確認
                3. **コスト最適化**: 詳細比較で最安値選択
                
                ### 🛡️ セキュリティ機能
                - ファイルアップロード検証
                - レート制限による保護
                - セッション管理
                """)
    
    def show_system_status(self):
        """システム状態表示"""
        with st.expander("🔧 システム詳細状態", expanded=True):
            st.markdown("""
            <div class="modern-card">
                <h3 style="color: #4f46e5; text-align: center; margin-bottom: 1rem;">システム状態</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="modern-card">
                    <h4 style="color: #4f46e5; text-align: center;">⚡ パフォーマンス</h4>
                </div>
                """, unsafe_allow_html=True)
                
                perf_report = performance_monitor.get_performance_report()
                if perf_report:
                    for func_name, metrics in list(perf_report.items())[:3]:
                        st.markdown(f"""
                        <div class="metric-container" style="margin-bottom: 1rem;">
                            <div class="metric-label">{func_name.split('.')[-1]}</div>
                            <div class="metric-value">{metrics['avg_time']:.3f}s</div>
                            <div style="font-size: 0.8rem; opacity: 0.8;">{metrics['total_calls']} calls</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="modern-card" style="background: #e3f2fd; color: #1976d2; text-align: center;">
                        <p>パフォーマンスデータがありません</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="modern-card">
                    <h4 style="color: #4f46e5; text-align: center;">💾 キャッシュ状態</h4>
                </div>
                """, unsafe_allow_html=True)
                
                cache_stats = cache_manager.get_cache_stats()
                
                st.markdown(f"""
                <div class="metric-container" style="margin-bottom: 1rem;">
                    <div class="metric-label">キャッシュエントリ</div>
                    <div class="metric-value">{cache_stats['valid_entries']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-label">メモリ使用量</div>
                    <div class="metric-value">{cache_stats['memory_usage_mb']:.1f}MB</div>
                </div>
                """, unsafe_allow_html=True)
    
    @streamlit_error_boundary
    @rate_limited("main_calculation")
    @performance_monitor.time_function("main_calculation")
    def handle_calculation(self, quantities: Dict[str, int]):
        """メイン計算処理"""
        # ユーザーアクション記録
        log_user_action("calculation_started", {
            'total_items': sum(quantities.values()),
            'item_types': len([q for q in quantities.values() if q > 0])
        })
        
        # 入力内容の確認表示
        self.input_handler.display_product_summary(quantities)
        
        # 計算実行 - モダンスピナー
        st.markdown("""
        <div class="modern-card" style="text-align: center; background: linear-gradient(45deg, #74b9ff, #0984e3); color: white;">
            <h4>🔍 最適な配送方法を計算中...</h4>
        </div>
        """, unsafe_allow_html=True)
        
        with st.spinner(""):
            packing_results = self.packing_engine.calculate_packing(quantities)
            
            if packing_results:
                # 基本送料計算
                shipping_options = self.shipping_calculator.calculate_shipping_options(packing_results)
                
                # 拡張配送オプション計算
                try:
                    enhanced_options = self.multi_carrier.get_enhanced_shipping_options(packing_results)
                    self.logger.info(f"Enhanced options generated: {len(enhanced_options) if enhanced_options else 0}")
                except Exception as e:
                    self.logger.error(f"Enhanced options generation failed: {str(e)}")
                    enhanced_options = []
                
                # 結果ログ記録
                best_result = packing_results[0] if packing_results else None
                log_calculation_result(
                    "packing_optimization",
                    f"Items: {sum(quantities.values())}",
                    f"Box: {best_result.box.number if best_result else 'None'}"
                )
                
                # タブで結果を整理
                self.render_results_tabs(packing_results, shipping_options, enhanced_options)
                
            else:
                st.markdown("""
                <div class="modern-card" style="background: linear-gradient(45deg, #ff7675, #fd79a8); color: white; text-align: center;">
                    <h4>❌ 適切な輸送箱が見つかりませんでした</h4>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div class="modern-card" style="background: linear-gradient(45deg, #74b9ff, #0984e3); color: white; text-align: center;">
                    <h4>💡 提案</h4>
                    <p>商品数を調整するか、サポートチームにお問い合わせください</p>
                </div>
                """, unsafe_allow_html=True)
    
    def render_results_tabs(self, packing_results, shipping_options, enhanced_options):
        """結果タブ表示"""
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎯 基本結果", 
            "📦 3D可視化", 
            "🚚 詳細配送比較", 
            "📋 詳細梱包手順",
            "📊 分析データ"
        ])
        
        with tab1:
            st.header("🎯 基本最適化結果")
            self.output_renderer.render_results(packing_results, shipping_options)
            
            recommended = self.packing_engine.get_packing_recommendation(packing_results)
            if recommended:
                self.output_renderer.render_packing_visualization(recommended)
        
        with tab2:
            self.render_3d_visualization(packing_results)
        
        with tab3:
            st.header("🚚 詳細配送オプション比較")
            if enhanced_options:
                self.multi_carrier.render_enhanced_options(enhanced_options)
            else:
                st.warning("⚠️ 詳細配送オプションの生成に失敗しました。")
                st.info("💡 **代替手段**: 基本結果タブの送料情報をご確認ください。")
                
                # 基本送料情報を表示
                if shipping_options:
                    st.subheader("📦 基本送料情報")
                    for i, option in enumerate(shipping_options[:3]):
                        st.markdown(f"**オプション {i+1}:** {option.rate}円 ({option.carrier})")
                
                # デバッグ情報（本番環境では非表示）
                if not settings.is_production:
                    st.markdown("**🔧 デバッグ情報:**")
                    st.write(f"- Packing results: {len(packing_results)}")
                    st.write(f"- Shipping options: {len(shipping_options)}")
                    st.write(f"- Enhanced options: {len(enhanced_options) if enhanced_options else 0}")
        
        with tab4:
            self.render_packing_steps(packing_results)
        
        with tab5:
            self.render_analysis_data(packing_results, enhanced_options)
    
    @streamlit_error_boundary
    def render_3d_visualization(self, packing_results):
        """3D可視化表示"""
        st.header("📦 3D梱包可視化")
        
        if packing_results:
            recommended = self.packing_engine.get_packing_recommendation(packing_results)
            if recommended:
                try:
                    fig_3d = self.visualizer_3d.create_3d_visualization(recommended)
                    st.plotly_chart(fig_3d, use_container_width=True)
                    
                    st.info("""
                    💡 **3D表示の操作方法:**
                    - **マウスドラッグ**: 視点回転
                    - **スクロール**: ズームイン/アウト
                    - **ダブルクリック**: リセット
                    """)
                    
                except Exception as e:
                    st.error("3D可視化でエラーが発生しました。")
                    self.logger.error(f"3D visualization error: {str(e)}")
    
    def render_packing_steps(self, packing_results):
        """梱包手順表示"""
        st.header("📋 詳細梱包手順")
        
        recommended = self.packing_engine.get_packing_recommendation(packing_results)
        if recommended:
            steps = self.steps_generator.generate_packing_steps(recommended)
            self.steps_generator.render_packing_steps(steps)
    
    def render_analysis_data(self, packing_results, enhanced_options):
        """分析データ表示"""
        st.header("📊 詳細分析データ")
        
        if packing_results:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📦 パッキング効率")
                for i, result in enumerate(packing_results[:3]):
                    st.metric(
                        f"オプション {i+1}",
                        f"{result.utilization_rate:.1f}%",
                        f"{result.box.number}"
                    )
            
            with col2:
                st.subheader("💰 コスト分析")
                if enhanced_options:
                    costs = [opt.total_cost for opt in enhanced_options[:3]]
                    min_cost = min(costs)
                    for i, cost in enumerate(costs):
                        savings = cost - min_cost
                        st.metric(
                            f"オプション {i+1}",
                            f"¥{cost:,}",
                            f"+¥{savings:,}" if savings > 0 else "最安値"
                        )
    
    @streamlit_error_boundary
    def run(self):
        """メインアプリケーション実行"""
        # ヘッダー表示
        self.render_header()
        
        # サイドバー表示
        self.render_sidebar()
        
        # メインコンテンツをタブで分割
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🚀 最適化計算", "📦 箱ラインナップ"])
        st.markdown('</div>', unsafe_allow_html=True)
        
        with tab1:
            # メイン入力エリア
            st.markdown("""
            <div class="modern-card fade-in">
                <h2 style="color: #4f46e5; margin-bottom: 1rem;">📥 商品情報入力</h2>
            </div>
            """, unsafe_allow_html=True)
            
            # 手動入力のみ
            quantities = self.input_handler.render_manual_input()
            
            # 計算実行
            if quantities:
                st.markdown("""
                <div class="modern-card fade-in">
                    <h3 style="color: #4f46e5; text-align: center; margin-bottom: 1rem;">🚀 計算開始</h3>
                </div>
                """, unsafe_allow_html=True)
                self.handle_calculation(quantities)
        
        with tab2:
            self.render_detailed_box_lineup()
        
        # フッター
        self.render_footer()
    
    def render_detailed_box_lineup(self):
        """詳細な箱ラインナップページ"""
        st.markdown("""
        <div class="modern-card fade-in">
            <h2 style="color: #4f46e5; margin-bottom: 1rem;">📦 ダンボール箱ラインナップ</h2>
            <p style="color: #6c757d;">利用可能なダンボール箱の詳細仕様をご確認いただけます。</p>
        </div>
        """, unsafe_allow_html=True)
        
        from src.data.boxes import BoxMaster
        from src.data.products import ProductMaster
        
        box_master = BoxMaster()
        product_master = ProductMaster()
        boxes = box_master.get_all_boxes()
        
        # 概要テーブル
        st.markdown("""
        <div class="modern-card">
            <h3 style="color: #4f46e5; margin-bottom: 1rem;">📋 箱サイズ一覧表</h3>
        </div>
        """, unsafe_allow_html=True)
        
        table_data = []
        for box_name, box in boxes.items():
            inner_dims = box.inner_dimensions
            table_data.append({
                "箱番号": box_name,
                "外寸 (W×D×H)": f"{box.width}×{box.depth}×{box.height} cm",
                "内寸 (W×D×H)": f"{inner_dims[0]:.0f}×{inner_dims[1]:.0f}×{inner_dims[2]:.0f} cm",
                "体積": f"{box.volume:,.0f} cm³",
                "最大重量": f"{box.max_weight} kg"
            })
        
        import pandas as pd
        df = pd.DataFrame(table_data)
        
        # スタイル付きデータフレーム
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.dataframe(
            df, 
            use_container_width=True,
            hide_index=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 詳細情報
        st.markdown("""
        <div class="modern-card">
            <h3 style="color: #4f46e5; margin-bottom: 1rem;">📐 詳細仕様</h3>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(len(boxes))
        
        for i, (box_name, box) in enumerate(boxes.items()):
            with cols[i]:
                st.markdown(f"""
                <div class="modern-card" style="margin-bottom: 1rem;">
                    <h3 style="color: #4f46e5; text-align: center; margin-bottom: 1rem;">{box_name}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # 基本情報カード - より美しいスタイル
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 1.5rem;
                    border-radius: 15px;
                    margin-bottom: 1rem;
                    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
                    transition: transform 0.3s ease;
                ">
                    <h4 style="margin-bottom: 1rem; text-align: center;">📏 寸法</h4>
                    <div style="background: rgba(255,255,255,0.1); padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem;">
                        <strong>外寸:</strong> {box.width} × {box.depth} × {box.height} cm
                    </div>
                    <div style="background: rgba(255,255,255,0.1); padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem;">
                        <strong>内寸:</strong> {box.inner_dimensions[0]:.0f} × {box.inner_dimensions[1]:.0f} × {box.inner_dimensions[2]:.0f} cm
                    </div>
                    <div style="background: rgba(255,255,255,0.1); padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem;">
                        <strong>体積:</strong> {box.volume:,.0f} cm³
                    </div>
                    <div style="background: rgba(255,255,255,0.1); padding: 0.8rem; border-radius: 8px;">
                        <strong>最大重量:</strong> {box.max_weight} kg
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 容量目安 - モダンスタイル
                st.markdown("""
                <div class="modern-card" style="background: linear-gradient(45deg, #84fab0, #8fd3f4);">
                    <h4 style="color: white; text-align: center; margin-bottom: 1rem;">📦 容量目安</h4>
                </div>
                """, unsafe_allow_html=True)
                
                capacity_info = []
                for product_name in ['S', 'Sロング', 'L', 'Lロング', 'LL']:
                    product = product_master.get_product(product_name)
                    if product:
                        # 最適配置での個数計算
                        max_fit = self._calculate_max_fit_production(box, product)
                        capacity_info.append((product_name, max_fit))
                
                # 容量情報を美しく表示
                capacity_html = ""
                for product_name, max_fit in capacity_info:
                    capacity_html += f"""
                    <div style="
                        background: white;
                        margin: 0.3rem 0;
                        padding: 0.8rem;
                        border-radius: 8px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    ">
                        <span style="font-weight: 600; color: #4f46e5;">{product_name}サイズ</span>
                        <span style="
                            background: linear-gradient(45deg, #4f46e5, #7c3aed);
                            color: white;
                            padding: 0.3rem 0.8rem;
                            border-radius: 15px;
                            font-weight: bold;
                        ">{max_fit}個</span>
                    </div>
                    """
                
                st.markdown(f"""
                <div class="modern-card">
                    {capacity_html}
                </div>
                """, unsafe_allow_html=True)
    
    def _calculate_max_fit_production(self, box, product):
        """箱に入る最大個数を計算（Production版）"""
        inner_dims = box.inner_dimensions
        
        # 6つの向きをテスト
        orientations = [
            (product.width, product.depth, product.height),
            (product.depth, product.width, product.height),
            (product.width, product.height, product.depth),
            (product.depth, product.height, product.width),
            (product.height, product.width, product.depth),
            (product.height, product.depth, product.width)
        ]
        
        max_count = 0
        for w, d, h in orientations:
            x_count = int(inner_dims[0] // w)
            y_count = int(inner_dims[1] // d)
            z_count = int(inner_dims[2] // h)
            count = x_count * y_count * z_count
            max_count = max(max_count, count)
        
        return max_count
    
    def render_footer(self):
        """フッター表示"""
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 2rem;
            border-radius: 15px;
            margin-top: 3rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        ">
            <h3 style="margin-bottom: 0.5rem;">📦 ミノルキューブ最適配送システム</h3>
            <p style="opacity: 0.9; margin-bottom: 0;">送料最適化と梱包効率向上のためのツール</p>
        </div>
        """, unsafe_allow_html=True)


def main():
    """メイン関数"""
    try:
        app = ProductionApp()
        app.run()
    except Exception as e:
        st.error("🚨 システムエラーが発生しました。管理者にお問い合わせください。")
        global_error_handler.handle_error(e)


if __name__ == "__main__":
    main()