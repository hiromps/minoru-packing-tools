from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import streamlit as st
import pandas as pd
import datetime
from src.data.rates import RatesMaster, ShippingRate
from src.core.packing_optimizer import PackingResult


@dataclass
class CarrierService:
    """運送業者サービス情報"""
    carrier: str
    service_name: str
    delivery_time: str
    tracking: bool
    insurance: bool
    special_features: List[str]


@dataclass
class EnhancedShippingOption:
    """拡張配送オプション"""
    packing_result: PackingResult
    shipping_rate: ShippingRate
    service: CarrierService
    estimated_delivery: str
    total_cost: int  # 送料 + オプション料金
    savings: int = 0
    recommendation_score: float = 0.0


class MultiCarrierManager:
    """複数運送業者管理システム"""
    
    def __init__(self):
        self.rate_master = RatesMaster()
        self.services = self._initialize_services()
        self.special_rates = self._initialize_special_rates()
    
    def _initialize_services(self) -> Dict[str, List[CarrierService]]:
        """運送業者サービスを初期化"""
        return {
            'ヤマト運輸': [
                CarrierService(
                    carrier='ヤマト運輸',
                    service_name='宅急便',
                    delivery_time='翌日-翌々日',
                    tracking=True,
                    insurance=True,
                    special_features=['時間指定', '再配達無料', 'コンビニ受取']
                ),
                CarrierService(
                    carrier='ヤマト運輸',
                    service_name='ネコポス',
                    delivery_time='翌日-翌々日',
                    tracking=True,
                    insurance=False,
                    special_features=['ポスト投函', '薄型専用']
                ),
                CarrierService(
                    carrier='ヤマト運輸',
                    service_name='宅急便コンパクト',
                    delivery_time='翌日-翌々日',
                    tracking=True,
                    insurance=True,
                    special_features=['専用BOX', 'コンパクト']
                )
            ],
            '佐川急便': [
                CarrierService(
                    carrier='佐川急便',
                    service_name='飛脚宅配便',
                    delivery_time='翌日-翌々日',
                    tracking=True,
                    insurance=True,
                    special_features=['時間指定', '営業所留め']
                ),
                CarrierService(
                    carrier='佐川急便',
                    service_name='飛脚メール便',
                    delivery_time='2-4日',
                    tracking=True,
                    insurance=False,
                    special_features=['ポスト投函', '安価']
                )
            ],
            '日本郵便': [
                CarrierService(
                    carrier='日本郵便',
                    service_name='ゆうパック',
                    delivery_time='翌日-翌々日',
                    tracking=True,
                    insurance=True,
                    special_features=['郵便局受取', 'コンビニ受取', '着払い可']
                ),
                CarrierService(
                    carrier='日本郵便',
                    service_name='クリックポスト',
                    delivery_time='翌日-翌々日',
                    tracking=True,
                    insurance=False,
                    special_features=['全国一律料金', 'ポスト投函']
                ),
                CarrierService(
                    carrier='日本郵便',
                    service_name='レターパック',
                    delivery_time='翌日',
                    tracking=True,
                    insurance=False,
                    special_features=['対面配達', '全国一律料金']
                )
            ]
        }
    
    def _initialize_special_rates(self) -> Dict[str, Dict[str, int]]:
        """特別料金（オプション）を初期化"""
        return {
            'time_designation': {'ヤマト運輸': 0, '佐川急便': 0, '日本郵便': 0},  # 時間指定
            'cash_on_delivery': {'ヤマト運輸': 330, '佐川急便': 330, '日本郵便': 260},  # 代引き
            'insurance_extra': {'ヤマト運輸': 0, '佐川急便': 0, '日本郵便': 0},  # 追加保険
            'express_delivery': {'ヤマト運輸': 220, '佐川急便': 220, '日本郵便': 320}  # 速達
        }
    
    def get_enhanced_shipping_options(self, packing_results: List[PackingResult], 
                                    options: Dict[str, bool] = None) -> List[EnhancedShippingOption]:
        """拡張配送オプションを取得"""
        if options is None:
            options = {}
        
        enhanced_options = []
        
        try:
            for result in packing_results:
                # 各運送業者のサービスをチェック
                for carrier in self.services:
                    try:
                        rates_for_carrier = self.rate_master.get_rates_by_carrier(carrier)
                        rate = next((r for r in rates_for_carrier if r.box_size == result.box.number), None)
                        if not rate:
                            # レートが見つからない場合、デフォルト値を使用
                            rate = self._create_default_rate(carrier, result.box.number)
                        
                        for service in self.services[carrier]:
                            # サービスが箱サイズに適用可能かチェック
                            if self._is_service_applicable(service, result):
                                total_cost = rate.rate
                                
                                # オプション料金を追加
                                total_cost += self._calculate_option_costs(carrier, options)
                                
                                # 配達予定日を計算
                                estimated_delivery = self._calculate_delivery_date(service)
                                
                                enhanced_option = EnhancedShippingOption(
                                    packing_result=result,
                                    shipping_rate=rate,
                                    service=service,
                                    estimated_delivery=estimated_delivery,
                                    total_cost=total_cost
                                )
                                
                                enhanced_options.append(enhanced_option)
                    except Exception as e:
                        # 個別のサービス処理でエラーが発生した場合はスキップ
                        continue
        except Exception as e:
            # 全体的な処理でエラーが発生した場合
            return []
        
        # 推奨スコアを計算
        self._calculate_recommendation_scores(enhanced_options)
        
        # 最安値との差額を計算
        if enhanced_options:
            min_cost = min(opt.total_cost for opt in enhanced_options)
            for opt in enhanced_options:
                opt.savings = opt.total_cost - min_cost
        
        # 推奨スコア順にソート
        enhanced_options.sort(key=lambda x: (-x.recommendation_score, x.total_cost))
        
        return enhanced_options
    
    def _is_service_applicable(self, service: CarrierService, result: PackingResult) -> bool:
        """サービスが適用可能かチェック"""
        # ネコポスやクリックポストは薄型のみ
        if service.service_name in ['ネコポス', 'クリックポスト']:
            return result.box.height <= 3.0  # 3cm以下
        
        # 宅急便コンパクトは小型のみ
        if service.service_name == '宅急便コンパクト':
            return result.box.number in ['B-60', 'B-80']
        
        return True
    
    def _calculate_option_costs(self, carrier: str, options: Dict[str, bool]) -> int:
        """オプション料金を計算"""
        total_cost = 0
        
        for option_name, enabled in options.items():
            if enabled and option_name in self.special_rates:
                total_cost += self.special_rates[option_name].get(carrier, 0)
        
        return total_cost
    
    def _calculate_delivery_date(self, service: CarrierService) -> str:
        """配達予定日を計算"""
        import datetime
        today = datetime.date.today()
        
        if '翌日' in service.delivery_time:
            delivery_date = today + datetime.timedelta(days=1)
        elif '翌々日' in service.delivery_time:
            delivery_date = today + datetime.timedelta(days=2)
        elif '2-4日' in service.delivery_time:
            delivery_date = today + datetime.timedelta(days=3)
        else:
            delivery_date = today + datetime.timedelta(days=2)
        
        return delivery_date.strftime('%m/%d (%a)')
    
    def _calculate_recommendation_scores(self, options: List[EnhancedShippingOption]):
        """推奨スコアを計算"""
        if not options:
            return
        
        costs = [opt.total_cost for opt in options]
        min_cost = min(costs)
        max_cost = max(costs)
        cost_range = max_cost - min_cost if max_cost > min_cost else 1
        
        for opt in options:
            score = 0.0
            
            # コスト評価（40%）
            cost_score = 1.0 - ((opt.total_cost - min_cost) / cost_range)
            score += cost_score * 0.4
            
            # 配送速度評価（30%）
            if '翌日' in opt.service.delivery_time:
                speed_score = 1.0
            elif '翌々日' in opt.service.delivery_time:
                speed_score = 0.8
            else:
                speed_score = 0.6
            score += speed_score * 0.3
            
            # サービス品質評価（20%）
            quality_score = 0.0
            if opt.service.tracking:
                quality_score += 0.3
            if opt.service.insurance:
                quality_score += 0.3
            quality_score += len(opt.service.special_features) * 0.1
            score += min(quality_score, 1.0) * 0.2
            
            # 容積利用率評価（10%）
            utilization_score = min(opt.packing_result.utilization_rate / 100.0, 1.0)
            score += utilization_score * 0.1
            
            opt.recommendation_score = score
    
    def _create_default_rate(self, carrier: str, box_number: str) -> ShippingRate:
        """デフォルトレートを作成"""
        # 箱サイズに基づく概算送料
        default_rates = {
            'ヤマト運輸': 800,
            '佐川急便': 750,
            '日本郵便': 700
        }
        
        return ShippingRate(
            carrier=carrier,
            size=box_number,
            rate=default_rates.get(carrier, 800)
        )
    
    def render_enhanced_options(self, options: List[EnhancedShippingOption]):
        """拡張配送オプションを表示"""
        if not options:
            st.error("❌ 配送オプションが見つかりませんでした。")
            return
        
        st.header("🚚 詳細配送オプション比較")
        
        # 推奨オプション
        best_option = options[0]
        self._render_best_option(best_option)
        
        # 比較表
        self._render_comparison_table(options[:10])  # 上位10件
        
        # フィルター機能
        self._render_filter_options()
    
    def _render_best_option(self, option: EnhancedShippingOption):
        """最推奨オプションを表示"""
        st.subheader("🏆 最推奨配送方法")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🚚 運送業者",
                option.service.carrier,
                option.service.service_name
            )
        
        with col2:
            st.metric(
                "💰 総費用",
                f"¥{option.total_cost:,}",
                f"基本料金: ¥{option.shipping_rate.rate:,}"
            )
        
        with col3:
            st.metric(
                "📅 配達予定",
                option.estimated_delivery,
                option.service.delivery_time
            )
        
        with col4:
            st.metric(
                "⭐ 推奨度",
                f"{option.recommendation_score:.1%}",
                f"📦 {option.packing_result.box.number}"
            )
        
        # サービス特徴
        with st.expander("🔍 サービス詳細", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**✅ 利用可能サービス:**")
                features = option.service.special_features.copy()
                if option.service.tracking:
                    features.append("追跡サービス")
                if option.service.insurance:
                    features.append("損害保険")
                
                for feature in features:
                    st.markdown(f"- {feature}")
            
            with col2:
                st.markdown("**📊 評価詳細:**")
                st.markdown(f"- 推奨スコア: {option.recommendation_score:.1%}")
                st.markdown(f"- 容積利用率: {option.packing_result.utilization_rate:.1f}%")
                st.markdown(f"- 総重量: {option.packing_result.total_weight:.1f}kg")
    
    def _render_comparison_table(self, options: List[EnhancedShippingOption]):
        """比較表を表示"""
        st.subheader("📊 配送オプション比較表")
        
        # データフレーム作成
        data = []
        for i, opt in enumerate(options):
            data.append({
                "順位": i + 1,
                "運送業者": opt.service.carrier,
                "サービス": opt.service.service_name,
                "箱サイズ": opt.packing_result.box.number,
                "総費用": f"¥{opt.total_cost:,}",
                "配達予定": opt.estimated_delivery,
                "推奨度": f"{opt.recommendation_score:.1%}",
                "追跡": "✅" if opt.service.tracking else "❌",
                "保険": "✅" if opt.service.insurance else "❌",
                "差額": f"+¥{opt.savings:,}" if opt.savings > 0 else "最安"
            })
        
        df = pd.DataFrame(data)
        
        # スタイル付きで表示
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
    
    def _render_filter_options(self):
        """フィルターオプションを表示"""
        with st.expander("🔧 詳細フィルター", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**配送オプション:**")
                time_designation = st.checkbox("時間指定")
                cash_on_delivery = st.checkbox("代金引換")
                
            with col2:
                st.markdown("**サービス要件:**")
                require_tracking = st.checkbox("追跡必須")
                require_insurance = st.checkbox("保険必須")
                
            with col3:
                st.markdown("**配送速度:**")
                max_delivery_days = st.selectbox(
                    "最大配送日数",
                    [1, 2, 3, 4, 5],
                    index=2
                )
            
            # フィルター適用ボタン
            if st.button("🔍 フィルターを適用", use_container_width=True):
                st.info("フィルター機能は次回アップデートで実装予定です。")