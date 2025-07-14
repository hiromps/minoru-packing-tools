# パス設定 - main_production.pyの最初に追加
from pathlib import Path

# プロジェクトルートをパスに追加
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))
import streamlit as st
import sys
import os
import time
from typing import Dict, Any

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
        st.title("📦 ミノルキューブ最適配送システム")
        st.markdown("### エンタープライズ版 - 高性能・高セキュリティ対応")
        
        # 環境表示（本番では非表示にする場合）
        if not settings.is_production:
            st.info(f"🔧 動作環境: {settings.environment.upper()}")
        
        st.markdown("---")
    
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
            
            # システム状態
            if st.button("🔍 システム状態確認"):
                self.show_system_status()
            
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
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**⚡ パフォーマンス**")
                perf_report = performance_monitor.get_performance_report()
                if perf_report:
                    for func_name, metrics in list(perf_report.items())[:3]:
                        st.metric(
                            func_name.split('.')[-1],
                            f"{metrics['avg_time']:.3f}s",
                            f"{metrics['total_calls']} calls"
                        )
                else:
                    st.info("パフォーマンスデータがありません")
            
            with col2:
                st.markdown("**💾 キャッシュ状態**")
                cache_stats = cache_manager.get_cache_stats()
                st.metric("キャッシュエントリ", cache_stats['valid_entries'])
                st.metric("メモリ使用量", f"{cache_stats['memory_usage_mb']:.1f}MB")
    
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
        
        # 計算実行
        with st.spinner("🔍 最適な配送方法を計算中..."):
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
                st.error("❌ 適切な輸送箱が見つかりませんでした。")
                st.info("💡 **提案**: 商品数を調整するか、サポートチームにお問い合わせください。")
    
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
        
        # メイン入力エリア
        st.header("📥 商品情報入力")
        
        # 入力方法選択
        input_method = st.radio(
            "入力方法を選択してください:",
            ["⌨️ 手動入力", "📷 AI画像認識入力"],
            horizontal=True
        )
        
        quantities = None
        
        if input_method == "⌨️ 手動入力":
            quantities = self.input_handler.render_manual_input()
        else:
            quantities = self.image_handler.render_image_input()
        
        # 計算実行
        if quantities:
            self.handle_calculation(quantities)
        
        # フッター
        self.render_footer()
    
    def render_footer(self):
        """フッター表示"""
        st.markdown("---")
        st.markdown("**📦 ミノルキューブ最適配送システム** - 送料最適化と梱包効率向上のためのツール")


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