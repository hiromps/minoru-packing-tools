"""
運賃マスタデータ
配送業者別料金情報
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class ShippingRate:
    """配送料金データクラス"""
    carrier: str        # 配送業者名
    box_size: str       # 対応箱サイズ
    rate: float         # 料金 (円)
    delivery_days: int  # 配送日数
    
    def __str__(self) -> str:
        return f"{self.carrier} - {self.box_size}: {self.rate:.0f}円 ({self.delivery_days}日)"

class RatesMaster:
    """運賃マスタ管理クラス"""
    
    def __init__(self):
        self.rates = [
            # ヤマト運輸
            ShippingRate("ヤマト運輸", "No.1", 800, 1),
            ShippingRate("ヤマト運輸", "No.2", 1000, 1),
            ShippingRate("ヤマト運輸", "No.5", 1300, 1),
            ShippingRate("ヤマト運輸", "No.6（100箱）", 1600, 1),
            ShippingRate("ヤマト運輸", "No.15", 2000, 1),
            
            # 佐川急便
            ShippingRate("佐川急便", "No.1", 750, 1),
            ShippingRate("佐川急便", "No.2", 950, 1),
            ShippingRate("佐川急便", "No.5", 1250, 1),
            ShippingRate("佐川急便", "No.6（100箱）", 1550, 1),
            ShippingRate("佐川急便", "No.15", 1950, 1),
            
            # 日本郵便
            ShippingRate("日本郵便", "No.1", 850, 2),
            ShippingRate("日本郵便", "No.2", 1050, 2),
            ShippingRate("日本郵便", "No.5", 1350, 2),
            ShippingRate("日本郵便", "No.6（100箱）", 1650, 2),
            ShippingRate("日本郵便", "No.15", 2050, 2),
        ]
    
    def get_rates_for_box(self, box_size: str) -> List[ShippingRate]:
        """指定された箱サイズの料金を取得"""
        return [rate for rate in self.rates if rate.box_size == box_size]
    
    def get_rates_by_carrier(self, carrier: str) -> List[ShippingRate]:
        """指定された配送業者の料金を取得"""
        return [rate for rate in self.rates if rate.carrier == carrier]
    
    def get_cheapest_rate(self, box_size: str) -> Optional[ShippingRate]:
        """最安料金を取得"""
        rates = self.get_rates_for_box(box_size)
        return min(rates, key=lambda x: x.rate) if rates else None
    
    def get_fastest_rate(self, box_size: str) -> Optional[ShippingRate]:
        """最速配送を取得"""
        rates = self.get_rates_for_box(box_size)
        return min(rates, key=lambda x: x.delivery_days) if rates else None
    
    def get_all_rates(self) -> List[ShippingRate]:
        """全料金を取得"""
        return self.rates.copy()
    
    def add_rate(self, rate: ShippingRate):
        """料金を追加"""
        self.rates.append(rate)