from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ShippingRate:
    """送料情報を管理するクラス"""
    carrier: str
    size_code: str
    box_number: str
    rate: int
    
    def __str__(self) -> str:
        return f"{self.carrier} - {self.size_code}: ¥{self.rate:,}"


class RateMaster:
    """運賃マスタを管理するクラス"""
    
    def __init__(self):
        self._rates: List[ShippingRate] = [
            # ヤマト運輸 - 実際の箱番号に対応
            ShippingRate(carrier='ヤマト運輸', size_code='60', box_number='60サイズS 12入', rate=850),
            ShippingRate(carrier='ヤマト運輸', size_code='60', box_number='L4入り', rate=850),
            ShippingRate(carrier='ヤマト運輸', size_code='60', box_number='60サイズLL2入', rate=850),
            ShippingRate(carrier='ヤマト運輸', size_code='80', box_number='80サイズ', rate=1050),
            ShippingRate(carrier='ヤマト運輸', size_code='100', box_number='LL12入', rate=1300),
            ShippingRate(carrier='ヤマト運輸', size_code='100', box_number='No.1', rate=1300),
            ShippingRate(carrier='ヤマト運輸', size_code='120', box_number='No.14', rate=1500),
            ShippingRate(carrier='ヤマト運輸', size_code='120', box_number='No.10', rate=1500),
            ShippingRate(carrier='ヤマト運輸', size_code='120', box_number='No.16', rate=1500),
            ShippingRate(carrier='ヤマト運輸', size_code='130', box_number='No.2', rate=1700),
            ShippingRate(carrier='ヤマト運輸', size_code='130', box_number='No.5', rate=1700),
            ShippingRate(carrier='ヤマト運輸', size_code='130', box_number='No.15', rate=1700),
            ShippingRate(carrier='ヤマト運輸', size_code='140', box_number='12号', rate=1950),
            ShippingRate(carrier='ヤマト運輸', size_code='140', box_number='No.6', rate=1950),
            
            # 佐川急便
            ShippingRate(carrier='佐川急便', size_code='60', box_number='60サイズS 12入', rate=800),
            ShippingRate(carrier='佐川急便', size_code='60', box_number='L4入り', rate=800),
            ShippingRate(carrier='佐川急便', size_code='60', box_number='60サイズLL2入', rate=800),
            ShippingRate(carrier='佐川急便', size_code='80', box_number='80サイズ', rate=1000),
            ShippingRate(carrier='佐川急便', size_code='100', box_number='LL12入', rate=1250),
            ShippingRate(carrier='佐川急便', size_code='100', box_number='No.1', rate=1250),
            ShippingRate(carrier='佐川急便', size_code='120', box_number='No.14', rate=1450),
            ShippingRate(carrier='佐川急便', size_code='120', box_number='No.10', rate=1450),
            ShippingRate(carrier='佐川急便', size_code='120', box_number='No.16', rate=1450),
            ShippingRate(carrier='佐川急便', size_code='130', box_number='No.2', rate=1650),
            ShippingRate(carrier='佐川急便', size_code='130', box_number='No.5', rate=1650),
            ShippingRate(carrier='佐川急便', size_code='130', box_number='No.15', rate=1650),
            ShippingRate(carrier='佐川急便', size_code='140', box_number='12号', rate=1900),
            ShippingRate(carrier='佐川急便', size_code='140', box_number='No.6', rate=1900),
            
            # 日本郵便
            ShippingRate(carrier='日本郵便', size_code='60', box_number='60サイズS 12入', rate=810),
            ShippingRate(carrier='日本郵便', size_code='60', box_number='L4入り', rate=810),
            ShippingRate(carrier='日本郵便', size_code='60', box_number='60サイズLL2入', rate=810),
            ShippingRate(carrier='日本郵便', size_code='80', box_number='80サイズ', rate=1020),
            ShippingRate(carrier='日本郵便', size_code='100', box_number='LL12入', rate=1270),
            ShippingRate(carrier='日本郵便', size_code='100', box_number='No.1', rate=1270),
            ShippingRate(carrier='日本郵便', size_code='120', box_number='No.14', rate=1470),
            ShippingRate(carrier='日本郵便', size_code='120', box_number='No.10', rate=1470),
            ShippingRate(carrier='日本郵便', size_code='120', box_number='No.16', rate=1470),
            ShippingRate(carrier='日本郵便', size_code='130', box_number='No.2', rate=1670),
            ShippingRate(carrier='日本郵便', size_code='130', box_number='No.5', rate=1670),
            ShippingRate(carrier='日本郵便', size_code='130', box_number='No.15', rate=1670),
            ShippingRate(carrier='日本郵便', size_code='140', box_number='12号', rate=1920),
            ShippingRate(carrier='日本郵便', size_code='140', box_number='No.6', rate=1920),
        ]
        
        # 検索用インデックス
        self._rate_index: Dict[str, Dict[str, ShippingRate]] = {}
        for rate in self._rates:
            if rate.carrier not in self._rate_index:
                self._rate_index[rate.carrier] = {}
            self._rate_index[rate.carrier][rate.box_number] = rate
    
    def get_rate(self, carrier: str, box_number: str) -> Optional[ShippingRate]:
        """指定運送業者・箱サイズの送料を取得"""
        if carrier in self._rate_index and box_number in self._rate_index[carrier]:
            return self._rate_index[carrier][box_number]
        return None
    
    def get_cheapest_rate(self, box_number: str) -> Optional[ShippingRate]:
        """指定箱サイズで最も安い送料を取得"""
        cheapest = None
        for carrier in self._rate_index:
            rate = self.get_rate(carrier, box_number)
            if rate and (cheapest is None or rate.rate < cheapest.rate):
                cheapest = rate
        return cheapest
    
    def get_all_rates_for_box(self, box_number: str) -> List[ShippingRate]:
        """指定箱サイズの全運送業者の送料を取得"""
        rates = []
        for carrier in self._rate_index:
            rate = self.get_rate(carrier, box_number)
            if rate:
                rates.append(rate)
        return sorted(rates, key=lambda x: x.rate)
    
    def get_carriers(self) -> List[str]:
        """利用可能な運送業者一覧を取得"""
        return list(self._rate_index.keys())