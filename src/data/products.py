"""
製品マスタデータ
ミノルキューブ商品の寸法・重量情報
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class Product:
    """製品データクラス"""
    size: str           # サイズ名
    width: float        # 幅 (cm)
    depth: float        # 奥行 (cm)
    height: float       # 高さ (cm)
    weight: float       # 重量 (kg)
    
    @property
    def volume(self) -> float:
        """体積を計算 (cm³)"""
        return self.width * self.depth * self.height
    
    @property
    def dimensions(self) -> tuple:
        """寸法を取得"""
        return (self.width, self.depth, self.height)

class ProductMaster:
    """製品マスタ管理クラス"""
    
    def __init__(self):
        self.products = {
            'S': Product('S', 6.5, 6.5, 6.5, 0.073),
            'Sロング': Product('Sロング', 6.5, 6.5, 9.7, 0.099),
            'L': Product('L', 9.7, 9.7, 9.7, 0.169),
            'Lロング': Product('Lロング', 9.7, 9.7, 16.2, 0.246),
            'LL': Product('LL', 13.0, 13.0, 13.0, 0.308)
        }
    
    def get_product(self, size: str) -> Optional[Product]:
        """製品情報を取得"""
        return self.products.get(size)
    
    def get_all_products(self) -> Dict[str, Product]:
        """全製品情報を取得"""
        return self.products.copy()
    
    def get_product_list(self) -> List[Product]:
        """製品リストを取得"""
        return list(self.products.values())
    
    def add_product(self, product: Product):
        """製品を追加"""
        self.products[product.size] = product
    
    def get_total_volume(self, quantities: Dict[str, int]) -> float:
        """総体積を計算"""
        total = 0.0
        for size, qty in quantities.items():
            product = self.get_product(size)
            if product:
                total += product.volume * qty
        return total
    
    def get_total_weight(self, quantities: Dict[str, int]) -> float:
        """総重量を計算"""
        total = 0.0
        for size, qty in quantities.items():
            product = self.get_product(size)
            if product:
                total += product.weight * qty
        return total
