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
        
        st.header("最適配送提案")
        
        # 推奨オプションを取得
        recommended = self.shipping_calculator.get_cheapest_option(packing_results)
        
        if recommended:
            self._render_recommendation(recommended)
        
        # その他のオプション
        if len(shipping_options) > 1:
            self._render_alternatives(shipping_options)
    
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