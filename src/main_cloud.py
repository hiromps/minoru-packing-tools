"""
Streamlit Community Cloud Optimized Version
ミノルキューブ最適配送システム v3.0.0 (Cloud Edition)
"""

import streamlit as st
import sys
import os
import time
from typing import Dict, Any
import traceback

# 環境設定
os.environ['ENVIRONMENT'] = 'production'
os.environ['STREAMLIT_CLOUD'] = 'true'

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 基本ライブラリのインポート
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# 軽量化されたコンポーネントのインポート
try:
    from src.data.products import ProductMaster, Product
    from src.data.boxes import BoxMaster, TransportBox
    from src.core.packing_optimizer import SimplePacking, PackingResult
    from src.core.shipping_calculator import ShippingCalculator
except ImportError as e:
    st.error(f"❌ コンポーネントのインポートエラー: {str(e)}")
    st.stop()

class CloudApp:
    """Streamlit Community Cloud最適化版アプリケーション"""
    
    def __init__(self):
        self.setup_page()
        self.init_components()
    
    def setup_page(self):
        """ページ設定"""
        st.set_page_config(
            page_title="ミノルキューブ最適配送システム v3.0.0",
            page_icon="📦",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # カスタムCSS
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        .metric-card {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #FF6B6B;
        }
        .success-box {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 5px;
            padding: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def init_components(self):
        """コンポーネント初期化"""
        try:
            self.product_master = ProductMaster()
            self.box_master = BoxMaster()
            self.packing_engine = SimplePacking()
            self.shipping_calculator = ShippingCalculator()
        except Exception as e:
            st.error(f"❌ システム初期化エラー: {str(e)}")
            st.stop()
    
    def render_header(self):
        """ヘッダー表示"""
        st.markdown("""
        <div class="main-header">
            <h1 style="color: white; margin: 0;">📦 ミノルキューブ最適配送システム</h1>
            <p style="color: white; margin: 0; opacity: 0.9;">v3.0.0 - Cloud Edition | 送料最適化と3D配置パッキング</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """サイドバー表示"""
        with st.sidebar:
            st.markdown("### 📋 システム情報")
            st.info("""
            **バージョン**: 3.0.0 (Cloud)  
            **環境**: Streamlit Community Cloud  
            **機能**: 3D最適化パッキング
            """)
            
            st.markdown("### 🚀 主要機能")
            st.markdown("""
            - ✅ 3D重ね配置最適化
            - ✅ 送料計算・比較
            - ✅ 梱包手順ガイド
            - ✅ 3D可視化表示
            """)
            
            st.markdown("### 📦 利用可能な箱サイズ")
            self.render_box_lineup()
            
            st.markdown("### 💡 使い方")
            st.markdown("""
            1. 商品数量を入力
            2. 「計算実行」をクリック
            3. 最適な箱と配置を確認
            4. 梱包手順に従って作業
            """)
    
    def render_box_lineup(self):
        """箱のラインナップ情報を表示"""
        boxes = self.box_master.get_all_boxes()
        
        for box_name, box in boxes.items():
            with st.expander(f"📦 {box_name}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    **外寸**  
                    {box.width} × {box.depth} × {box.height} cm
                    
                    **内寸**  
                    {box.inner_dimensions[0]:.0f} × {box.inner_dimensions[1]:.0f} × {box.inner_dimensions[2]:.0f} cm
                    """)
                
                with col2:
                    st.markdown(f"""
                    **体積**  
                    {box.volume:,.0f} cm³
                    
                    **最大重量**  
                    {box.max_weight} kg
                    """)
                
                # 容量の目安を表示
                st.markdown("**容量の目安:**")
                s_product = self.product_master.get_product('S')
                if s_product:
                    # Sサイズが何個入るかの概算
                    s_per_layer = int(box.inner_dimensions[0] // s_product.width) * int(box.inner_dimensions[1] // s_product.depth)
                    s_layers = int(box.inner_dimensions[2] // s_product.height)
                    s_total = s_per_layer * s_layers
                    st.markdown(f"- Sサイズ: 約{s_total}個まで")
    
    def render_detailed_box_lineup(self):
        """詳細な箱ラインナップページ"""
        st.header("📦 ダンボール箱ラインナップ")
        st.markdown("利用可能なダンボール箱の詳細仕様をご確認いただけます。")
        
        boxes = self.box_master.get_all_boxes()
        
        # 概要テーブル
        st.subheader("📋 箱サイズ一覧表")
        
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
        st.dataframe(df, use_container_width=True)
        
        # 詳細情報
        st.subheader("📐 詳細仕様")
        
        cols = st.columns(len(boxes))
        
        for i, (box_name, box) in enumerate(boxes.items()):
            with cols[i]:
                st.markdown(f"### {box_name}")
                
                # 基本情報カード
                st.markdown(f"""
                <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                    <h4>📏 寸法</h4>
                    <p><strong>外寸:</strong> {box.width} × {box.depth} × {box.height} cm</p>
                    <p><strong>内寸:</strong> {box.inner_dimensions[0]:.0f} × {box.inner_dimensions[1]:.0f} × {box.inner_dimensions[2]:.0f} cm</p>
                    <p><strong>体積:</strong> {box.volume:,.0f} cm³</p>
                    <p><strong>最大重量:</strong> {box.max_weight} kg</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 容量目安
                st.markdown("**📦 容量目安**")
                for product_name in ['S', 'Sロング', 'L', 'Lロング', 'LL']:
                    product = self.product_master.get_product(product_name)
                    if product:
                        # 最適配置での個数計算
                        max_fit = self._calculate_max_fit(box, product)
                        st.markdown(f"- {product_name}サイズ: {max_fit}個")
                
    def _calculate_max_fit(self, box, product):
        """箱に入る最大個数を計算"""
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
    
    def render_input_section(self):
        """入力セクション表示"""
        st.markdown("### 📥 商品情報入力")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 小サイズ商品")
            s_qty = st.number_input("Sサイズ", min_value=0, max_value=100, value=0, key="s_size")
            s_long_qty = st.number_input("Sロングサイズ", min_value=0, max_value=100, value=0, key="s_long_size")
        
        with col2:
            st.markdown("#### 大サイズ商品")
            l_qty = st.number_input("Lサイズ", min_value=0, max_value=100, value=0, key="l_size")
            l_long_qty = st.number_input("Lロングサイズ", min_value=0, max_value=100, value=0, key="l_long_size")
            ll_qty = st.number_input("LLサイズ", min_value=0, max_value=100, value=0, key="ll_size")
        
        quantities = {
            'S': s_qty,
            'Sロング': s_long_qty,
            'L': l_qty,
            'Lロング': l_long_qty,
            'LL': ll_qty
        }
        
        return quantities
    
    def calculate_packing(self, quantities):
        """パッキング計算"""
        try:
            # 商品数量チェック
            total_items = sum(quantities.values())
            if total_items == 0:
                st.warning("⚠️ 商品を入力してください。")
                return None
            
            with st.spinner("🔍 最適な配送方法を計算中..."):
                # パッキング計算
                packing_results = self.packing_engine.calculate_packing(quantities)
                
                if packing_results:
                    # 送料計算
                    shipping_options = self.shipping_calculator.calculate_shipping_options(packing_results)
                    return packing_results, shipping_options
                else:
                    st.error("❌ 適切な配送箱が見つかりませんでした。")
                    return None
                    
        except Exception as e:
            st.error(f"❌ 計算エラー: {str(e)}")
            return None
    
    def render_results(self, packing_results, shipping_options):
        """結果表示"""
        if not packing_results:
            return
        
        # 推奨結果
        recommended = self.packing_engine.get_packing_recommendation(packing_results)
        
        st.markdown("### 🎯 最適化結果")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h4>📦 推奨箱</h4>
                <p><strong>{}</strong></p>
                <p>{}cm × {}cm × {}cm</p>
            </div>
            """.format(
                recommended.box.number,
                recommended.box.width,
                recommended.box.depth,
                recommended.box.height
            ), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h4>📊 利用効率</h4>
                <p><strong>{:.1f}%</strong></p>
                <p>重量: {:.1f}kg</p>
            </div>
            """.format(
                recommended.utilization_rate,
                recommended.total_weight
            ), unsafe_allow_html=True)
        
        with col3:
            if shipping_options:
                best_shipping = shipping_options[0]
                st.markdown("""
                <div class="metric-card">
                    <h4>💰 推奨送料</h4>
                    <p><strong>{:.0f}円</strong></p>
                    <p>{}</p>
                </div>
                """.format(
                    best_shipping.shipping_rate.rate,
                    best_shipping.shipping_rate.carrier
                ), unsafe_allow_html=True)
        
        # 詳細結果
        st.markdown("### 📋 詳細結果")
        
        tab1, tab2, tab3 = st.tabs(["📦 パッキング詳細", "🚚 送料比較", "📐 3D可視化"])
        
        with tab1:
            self.render_packing_details(recommended)
        
        with tab2:
            self.render_shipping_comparison(shipping_options)
        
        with tab3:
            self.render_3d_visualization(recommended)
    
    def render_packing_details(self, result):
        """パッキング詳細表示"""
        if not result:
            return
        
        st.markdown("#### 📦 箱情報")
        box_info = pd.DataFrame({
            '項目': ['型番', '外寸', '内寸', '最大重量', '利用率'],
            '値': [
                result.box.number,
                f"{result.box.width}×{result.box.depth}×{result.box.height}cm",
                f"{result.box.inner_dimensions[0]}×{result.box.inner_dimensions[1]}×{result.box.inner_dimensions[2]}cm",
                f"{result.box.max_weight}kg",
                f"{result.utilization_rate:.1f}%"
            ]
        })
        st.dataframe(box_info, use_container_width=True, hide_index=True)
        
        st.markdown("#### 📋 梱包手順")
        if hasattr(result, 'packed_items') and result.packed_items:
            steps = self.packing_engine.get_packing_steps(result)
            for i, step in enumerate(steps, 1):
                st.markdown(f"**Step {i}:** {step.get('description', 'N/A')}")
        else:
            st.info("💡 商品を順番に配置してください。")
    
    def render_shipping_comparison(self, shipping_options):
        """送料比較表示"""
        if not shipping_options:
            st.info("送料情報がありません。")
            return
        
        st.markdown("#### 🚚 配送オプション比較")
        
        shipping_data = []
        for option in shipping_options[:5]:  # 上位5つ
            shipping_data.append({
                '配送業者': option.shipping_rate.carrier,
                '送料': f"{option.shipping_rate.rate:.0f}円",
                '配送日数': option.shipping_rate.delivery_days,
                '箱サイズ': option.shipping_rate.box_size
            })
        
        df = pd.DataFrame(shipping_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # 送料比較グラフ
        fig = px.bar(
            df.head(3), 
            x='配送業者', 
            y=[float(x.replace('円', '')) for x in df.head(3)['送料']],
            title="送料比較",
            labels={'y': '送料 (円)'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def render_3d_visualization(self, result):
        """3D可視化表示"""
        if not result or not hasattr(result, 'packed_items'):
            st.info("3D可視化データがありません。")
            return
        
        st.markdown("#### 🎲 3D配置可視化")
        
        try:
            # 3D散布図でアイテム配置を表示
            fig = go.Figure()
            
            # 箱の枠線を追加
            box = result.box
            fig.add_trace(go.Scatter3d(
                x=[0, box.width, box.width, 0, 0, 0, box.width, box.width, 0, 0, box.width, box.width, 0, 0, box.width, box.width],
                y=[0, 0, box.depth, box.depth, 0, 0, 0, box.depth, box.depth, 0, 0, box.depth, box.depth, 0, 0, box.depth],
                z=[0, 0, 0, 0, 0, box.height, box.height, box.height, box.height, box.height, 0, 0, box.height, box.height, box.height, 0],
                mode='lines',
                line=dict(color='blue', width=2),
                name='配送箱'
            ))
            
            # パッキングされたアイテムを表示
            if hasattr(result, 'packed_items') and result.packed_items:
                for i, item in enumerate(result.packed_items):
                    fig.add_trace(go.Scatter3d(
                        x=[item.x + item.width/2],
                        y=[item.y + item.depth/2],
                        z=[item.z + item.height/2],
                        mode='markers',
                        marker=dict(
                            size=10,
                            color=f'rgb({50 + i*50}, {100 + i*30}, {150 + i*20})',
                            symbol='square'
                        ),
                        name=f'{item.product.size}',
                        text=f'Size: {item.product.size}<br>Position: ({item.x:.1f}, {item.y:.1f}, {item.z:.1f})'
                    ))
            
            fig.update_layout(
                title="3D配置図",
                scene=dict(
                    xaxis_title="幅 (cm)",
                    yaxis_title="奥行 (cm)",
                    zaxis_title="高さ (cm)",
                    aspectmode='cube'
                ),
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"3D可視化エラー: {str(e)}")
            st.info("💡 基本的な配置情報を表示します。")
    
    def run(self):
        """アプリケーション実行"""
        try:
            # ヘッダー表示
            self.render_header()
            
            # サイドバー表示
            self.render_sidebar()
            
            # メインコンテンツをタブで分割
            tab1, tab2 = st.tabs(["🚀 最適化計算", "📦 箱ラインナップ"])
            
            with tab1:
                # 入力セクション
                quantities = self.render_input_section()
                
                # 計算実行ボタン
                if st.button("🚀 計算実行", type="primary", use_container_width=True):
                    results = self.calculate_packing(quantities)
                    if results:
                        packing_results, shipping_options = results
                        self.render_results(packing_results, shipping_options)
            
            with tab2:
                self.render_detailed_box_lineup()
            
            # フッター
            st.markdown("---")
            st.markdown("**📦 ミノルキューブ最適配送システム v3.0.0** - Cloud Edition")
            st.markdown("🚀 Powered by Streamlit Community Cloud")
            
        except Exception as e:
            st.error(f"❌ システムエラー: {str(e)}")
            st.code(traceback.format_exc())

def main():
    """メイン関数"""
    try:
        app = CloudApp()
        app.run()
    except Exception as e:
        st.error(f"❌ アプリケーション起動エラー: {str(e)}")
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()