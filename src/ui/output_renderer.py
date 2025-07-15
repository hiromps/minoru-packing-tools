import streamlit as st
from typing import List, Optional
from src.core.packing_optimizer import PackingResult
from src.core.shipping_calculator import ShippingOption, ShippingCalculator


class OutputRenderer:
    """結果表示を処理するクラス"""
    
    def __init__(self):
        self.shipping_calculator = ShippingCalculator()
    
    def render_results(self, packing_results: List[PackingResult], shipping_options: List[ShippingOption]):
        """パッキング結果と配送オプションを表示"""
        if not packing_results:
            st.error("適切な輸送箱が見つかりませんでした。商品数量を見直してください。")
            return
        
        # 表形式で結果を表示
        self._render_results_table(shipping_options)
    
    def _render_results_table(self, shipping_options: List[ShippingOption]):
        """結果を表形式で表示"""
        if not shipping_options:
            st.warning("配送オプションがありません。")
            return
        
        # 最適解を大きく強調表示
        best_option = shipping_options[0]
        self._render_best_solution(best_option)
        
        # その他の比較オプション
        if len(shipping_options) > 1:
            self._render_comparison_table(shipping_options)
    
    def _render_best_solution(self, option: ShippingOption):
        """最適解を大きく強調表示"""
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(231, 76, 60, 0.3);
            text-align: center;
        ">
            <h2 style="margin-bottom: 1rem; font-size: 2rem;">🏆 最適な配送方法</h2>
            <p style="font-size: 1.1rem; opacity: 0.9; margin-bottom: 0;">最も効率的で経済的な配送オプションです</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 3つの重要な情報を大きく表示
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 2rem;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
                margin-bottom: 1rem;
            ">
                <h3 style="margin-bottom: 1rem; font-size: 1.5rem;">📦</h3>
                <h2 style="margin-bottom: 0.5rem; font-size: 2.5rem;">{option.packing_result.box.number}</h2>
                <p style="font-size: 1.1rem; opacity: 0.9; margin: 0;">輸送箱</p>
                <p style="font-size: 0.9rem; opacity: 0.8; margin: 0;">{option.packing_result.box.width}×{option.packing_result.box.depth}×{option.packing_result.box.height} cm</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
                color: white;
                padding: 2rem;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 8px 25px rgba(46, 204, 113, 0.3);
                margin-bottom: 1rem;
            ">
                <h3 style="margin-bottom: 1rem; font-size: 1.5rem;">💰</h3>
                <h2 style="margin-bottom: 0.5rem; font-size: 2.5rem;">¥{option.shipping_rate.rate:,}</h2>
                <p style="font-size: 1.1rem; opacity: 0.9; margin: 0;">送料</p>
                <p style="font-size: 0.9rem; opacity: 0.8; margin: 0;">{option.shipping_rate.carrier}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            efficiency_bg = "linear-gradient(135deg, #f39c12 0%, #e67e22 100%)" if option.packing_result.utilization_rate < 70 else "linear-gradient(135deg, #27ae60 0%, #2ecc71 100%)"
            efficiency_text = "余裕あり" if option.packing_result.utilization_rate < 70 else "効率的"
            
            st.markdown(f"""
            <div style="
                background: {efficiency_bg};
                color: white;
                padding: 2rem;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 8px 25px rgba(46, 204, 113, 0.3);
                margin-bottom: 1rem;
            ">
                <h3 style="margin-bottom: 1rem; font-size: 1.5rem;">📊</h3>
                <h2 style="margin-bottom: 0.5rem; font-size: 2.5rem;">{option.packing_result.utilization_rate:.1f}%</h2>
                <p style="font-size: 1.1rem; opacity: 0.9; margin: 0;">容積利用率</p>
                <p style="font-size: 0.9rem; opacity: 0.8; margin: 0;">{efficiency_text}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 重要な詳細情報をコンパクトに表示
        st.markdown(f"""
        <div style="
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 12px;
            border-left: 5px solid #e74c3c;
            margin-bottom: 2rem;
        ">
            <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 1rem;">
                <div style="text-align: center;">
                    <h4 style="color: #4f46e5; margin-bottom: 0.5rem;">📋 商品数</h4>
                    <p style="font-size: 1.2rem; font-weight: bold; margin: 0;">{len(option.packing_result.items)}個</p>
                </div>
                <div style="text-align: center;">
                    <h4 style="color: #4f46e5; margin-bottom: 0.5rem;">⚖️ 総重量</h4>
                    <p style="font-size: 1.2rem; font-weight: bold; margin: 0;">{option.packing_result.total_weight:.1f}kg</p>
                </div>
                <div style="text-align: center;">
                    <h4 style="color: #4f46e5; margin-bottom: 0.5rem;">📦 内寸</h4>
                    <p style="font-size: 1.2rem; font-weight: bold; margin: 0;">{option.packing_result.box.inner_dimensions[0]:.0f}×{option.packing_result.box.inner_dimensions[1]:.0f}×{option.packing_result.box.inner_dimensions[2]:.0f} cm</p>
                </div>
                <div style="text-align: center;">
                    <h4 style="color: #4f46e5; margin-bottom: 0.5rem;">🚚 配送日数</h4>
                    <p style="font-size: 1.2rem; font-weight: bold; margin: 0;">{option.shipping_rate.delivery_days}日</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_comparison_table(self, shipping_options: List[ShippingOption]):
        """比較表を表示"""
        st.markdown("""
        <div style="
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border: 1px solid #e6e9ef;
            margin-bottom: 1rem;
        ">
            <h3 style="color: #4f46e5; margin-bottom: 1rem; text-align: center;">📊 その他のオプション比較</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # データを表形式で準備（2位以降のみ表示）
        import pandas as pd
        
        table_data = []
        for i, option in enumerate(shipping_options[1:5], 2):  # 2位から5位まで表示
            rank = "🥈" if i == 2 else "🥉" if i == 3 else f"{i}位"
            
            table_data.append({
                "順位": rank,
                "輸送箱": option.packing_result.box.number,
                "箱サイズ (W×D×H)": f"{option.packing_result.box.width}×{option.packing_result.box.depth}×{option.packing_result.box.height} cm",
                "運送業者": option.shipping_rate.carrier,
                "送料": f"¥{option.shipping_rate.rate:,}",
                "容積利用率": f"{option.packing_result.utilization_rate:.1f}%",
                "総重量": f"{option.packing_result.total_weight:.1f}kg"
            })
        
        if table_data:  # 2位以降がある場合のみ表示
            df = pd.DataFrame(table_data)
            
            # モダンスタイルで表を表示
            st.markdown("""
            <div style="
                background: white;
                border-radius: 12px;
                padding: 1rem;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                border: 1px solid #e6e9ef;
            ">
            """, unsafe_allow_html=True)
            
            st.dataframe(
                df, 
                use_container_width=True,
                hide_index=True
            )
            
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="
                background: #e3f2fd;
                color: #1976d2;
                padding: 1rem;
                border-radius: 10px;
                text-align: center;
            ">
                <p style="margin: 0;">他の配送オプションはありません。上記が最適な選択です。</p>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_best_option_details(self, option: ShippingOption):
        """最安値オプションの詳細情報を表示"""
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            margin-top: 1rem;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        ">
            <h4 style="margin-bottom: 1rem; text-align: center;">🏆 推奨オプション詳細</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # 詳細情報を3列で表示
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="
                background: white;
                padding: 1rem;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            ">
                <h4 style="color: #4f46e5; margin-bottom: 0.5rem;">📦 輸送箱</h4>
                <p style="font-size: 1.2rem; font-weight: bold; margin: 0;">{}</p>
                <p style="color: #6c757d; margin: 0;">{}cm</p>
            </div>
            """.format(
                option.packing_result.box.number,
                f"{option.packing_result.box.width}×{option.packing_result.box.depth}×{option.packing_result.box.height}"
            ), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="
                background: white;
                padding: 1rem;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            ">
                <h4 style="color: #4f46e5; margin-bottom: 0.5rem;">💰 送料</h4>
                <p style="font-size: 1.2rem; font-weight: bold; margin: 0;">¥{:,}</p>
                <p style="color: #6c757d; margin: 0;">{}</p>
            </div>
            """.format(
                option.shipping_rate.rate,
                option.shipping_rate.carrier
            ), unsafe_allow_html=True)
        
        with col3:
            efficiency_color = "#28a745" if option.packing_result.utilization_rate >= 70 else "#ffc107"
            efficiency_text = "効率的" if option.packing_result.utilization_rate >= 70 else "余裕あり"
            
            st.markdown("""
            <div style="
                background: white;
                padding: 1rem;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            ">
                <h4 style="color: #4f46e5; margin-bottom: 0.5rem;">📊 利用率</h4>
                <p style="font-size: 1.2rem; font-weight: bold; margin: 0;">{:.1f}%</p>
                <p style="color: {}; margin: 0;">{}</p>
            </div>
            """.format(
                option.packing_result.utilization_rate,
                efficiency_color,
                efficiency_text
            ), unsafe_allow_html=True)
    
    def _render_recommendation(self, option: ShippingOption):
        """推奨オプションを表示"""
        st.subheader("🎯 推奨配送方法")
        
        # モバイル完全対応：縦並びで表示
        st.metric(
            "📦 輸送箱",
            option.packing_result.box.number,
            f"{option.packing_result.box.width}×{option.packing_result.box.depth}×{option.packing_result.box.height}cm",
            help="推奨される輸送箱のサイズ"
        )
        
        st.metric(
            "🚚 運送業者",
            option.shipping_rate.carrier,
            f"¥{option.shipping_rate.rate:,}",
            help="最安値の運送業者と送料"
        )
        
        utilization = option.packing_result.utilization_rate
        st.metric(
            "📊 容積利用率",
            f"{utilization:.1f}%",
            "🟢 効率的" if utilization >= 70 else "🟡 余裕あり",
            help="箱の容積に対する商品の占有率"
        )
        
        # 詳細情報をカード形式で
        with st.expander("📋 詳細情報", expanded=False):
            # モバイル完全対応：縦並びで表示
            st.info(f"""
            **重量情報**
            - 総重量: {option.packing_result.total_weight:.1f}kg
            - 箱の最大重量: {option.packing_result.box.max_weight}kg
            - 重量利用率: {(option.packing_result.total_weight/option.packing_result.box.max_weight)*100:.1f}%
            """)
            
            st.info(f"""
            **容積情報**
            - 総体積: {option.packing_result.total_volume:.0f}cm³
            - 商品数: {len(option.packing_result.items)}個
            - 箱の内容積: {option.packing_result.box.inner_dimensions[0]*option.packing_result.box.inner_dimensions[1]*option.packing_result.box.inner_dimensions[2]:.0f}cm³
            """)
    
    def _render_alternatives(self, options: List[ShippingOption]):
        """代替オプションを表示"""
        st.subheader("🔄 その他の配送オプション")
        
        # 代替案をカード形式で表示
        alternatives = [opt for i, opt in enumerate(options[:5]) if i > 0]
        
        if not alternatives:
            st.info("他の配送オプションはありません。")
            return
        
        # モバイル完全対応：カード形式で縦並び表示
        for i, option in enumerate(alternatives):
            with st.container():
                st.markdown(f"**📦 {option.packing_result.box.number}**")
                st.caption(f"サイズ: {option.packing_result.box.width}×{option.packing_result.box.depth}×{option.packing_result.box.height}cm")
                
                st.markdown(f"**🚚 {option.shipping_rate.carrier}**")
                st.caption(f"利用率: {option.packing_result.utilization_rate:.1f}%")
                
                st.markdown(f"**💰 ¥{option.shipping_rate.rate:,}**")
                if option.savings and option.savings > 0:
                    st.caption(f"最安値より +¥{option.savings:,}")
                else:
                    st.caption("最安値")
                
                st.divider()
    
    def render_packing_visualization(self, result: PackingResult):
        """パッキング配置の簡易可視化"""
        st.subheader("📦 梱包イメージ")
        
        # モバイル完全対応：縦並びで表示
        st.markdown("#### 📐 箱の詳細")
        st.info(f"""
        **📦 箱サイズ**: {result.box.number}
        **📏 外寸**: {result.box.width}×{result.box.depth}×{result.box.height}cm
        **📏 内寸**: {result.box.inner_dimensions[0]:.1f}×{result.box.inner_dimensions[1]:.1f}×{result.box.inner_dimensions[2]:.1f}cm
        **⚖️ 最大重量**: {result.box.max_weight}kg
        """)
        
        st.markdown("#### 📋 内容物")
        # 商品リストを表示
        product_counts = {}
        for item in result.items:
            size = item['size']
            product_counts[size] = product_counts.get(size, 0) + 1
        
        # カード形式で内容物を表示
        for size, count in product_counts.items():
            st.markdown(f"- **{size}サイズ**: {count}個")
        
        # 配置可能性の詳細チェック
        self._show_feasibility_details(result)
    
    def _show_feasibility_details(self, result: PackingResult):
        """配置可能性の詳細情報を表示"""
        with st.expander("🔍 配置詳細情報", expanded=False):
            # モバイル完全対応：縦並びで表示
            
            # 重量チェック
            weight_ratio = (result.total_weight / result.box.max_weight) * 100
            st.metric(
                "⚖️ 重量使用率", 
                f"{weight_ratio:.1f}%",
                "✅ OK" if weight_ratio <= 100 else "❌ オーバー",
                help=f"商品重量 {result.total_weight:.1f}kg / 最大重量 {result.box.max_weight}kg"
            )
            
            # 容積チェック
            inner_volume = result.box.inner_dimensions[0] * result.box.inner_dimensions[1] * result.box.inner_dimensions[2]
            volume_ratio = (result.total_volume / inner_volume) * 100
            st.metric(
                "📐 容積使用率", 
                f"{volume_ratio:.1f}%",
                "✅ 効率的" if volume_ratio <= 80 else "⚠️ 要注意",
                help=f"商品体積 {result.total_volume:.0f}cm³ / 内容積 {inner_volume:.0f}cm³"
            )
            
            # 配置効率
            packing_efficiency = min(100, (result.total_volume / inner_volume) * 125)  # 効率係数考慮
            st.metric(
                "📦 配置効率", 
                f"{packing_efficiency:.1f}%",
                "🟢 良好" if packing_efficiency >= 70 else "🟡 余裕",
                help="実際の配置を考慮した効率性"
            )
            
            st.divider()
            
            # 寸法チェック
            st.markdown("#### 📏 寸法適合性チェック")
            box_w, box_d, box_h = result.box.inner_dimensions
            
            oversized_items = []
            for item in result.items:
                product = item['product']
                if (product.width > box_w or product.depth > box_d or product.height > box_h):
                    oversized_items.append(f"{item['size']}サイズ ({product.width}×{product.depth}×{product.height}cm)")
            
            if oversized_items:
                st.error("❌ **サイズオーバーの商品があります:**")
                for item in oversized_items:
                    st.markdown(f"- {item}")
                st.warning("⚠️ この配置は実現できません。より大きな箱を選択してください。")
            else:
                st.success("✅ **全ての商品が箱の内寸に収まります**")
                st.info(f"📏 箱の内寸: {box_w:.1f}×{box_d:.1f}×{box_h:.1f}cm")