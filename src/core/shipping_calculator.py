from typing import Dict, List, Optional
from dataclasses import dataclass
from src.data.rates import RateMaster, ShippingRate
from src.data.boxes import TransportBox
from src.core.packing_optimizer import PackingResult


@dataclass
class ShippingOption:
    """配送オプション情報"""
    packing_result: PackingResult
    shipping_rate: ShippingRate
    savings: Optional[int] = None
    
    def __str__(self) -> str:
        return f"{self.shipping_rate.carrier} - {self.packing_result.box.number}: ¥{self.shipping_rate.rate:,}"


class ShippingCalculator:
    """送料計算エンジン"""
    
    def __init__(self):
        self.rate_master = RateMaster()
    
    def calculate_shipping_options(self, packing_results: List[PackingResult]) -> List[ShippingOption]:
        """パッキング結果から配送オプションを計算"""
        options = []
        
        for result in packing_results:
            # 各運送業者の料金を取得
            rates = self.rate_master.get_all_rates_for_box(result.box.number)
            
            for rate in rates:
                option = ShippingOption(
                    packing_result=result,
                    shipping_rate=rate
                )
                options.append(option)
        
        # 最安値との差額を計算
        if options:
            min_rate = min(opt.shipping_rate.rate for opt in options)
            for option in options:
                option.savings = option.shipping_rate.rate - min_rate
        
        # 料金順にソート
        options.sort(key=lambda x: x.shipping_rate.rate)
        
        return options
    
    def get_cheapest_option(self, packing_results: List[PackingResult]) -> Optional[ShippingOption]:
        """最も安い配送オプションを取得"""
        cheapest = None
        
        for result in packing_results:
            rate = self.rate_master.get_cheapest_rate(result.box.number)
            if rate:
                option = ShippingOption(
                    packing_result=result,
                    shipping_rate=rate
                )
                if cheapest is None or option.shipping_rate.rate < cheapest.shipping_rate.rate:
                    cheapest = option
        
        return cheapest
    
    def compare_carriers(self, box_number: str) -> Dict[str, ShippingRate]:
        """指定箱での運送業者別料金比較"""
        comparison = {}
        
        for carrier in self.rate_master.get_carriers():
            rate = self.rate_master.get_rate(carrier, box_number)
            if rate:
                comparison[carrier] = rate
        
        return comparison