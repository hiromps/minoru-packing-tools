"""
輸送箱マスタデータ
配送用ダンボール箱の寸法・重量制限情報
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

@dataclass
class TransportBox:
    """輸送箱データクラス"""
    number: str         # 箱番号
    width: float        # 幅 (cm)
    depth: float        # 奥行 (cm)
    height: float       # 高さ (cm)
    max_weight: float   # 最大重量 (kg)
    
    @property
    def volume(self) -> float:
        """体積を計算 (cm³)"""
        return self.width * self.depth * self.height
    
    @property
    def inner_dimensions(self) -> Tuple[float, float, float]:
        """内寸を計算 (壁厚1cm想定)"""
        return (
            max(0, self.width - 2),
            max(0, self.depth - 2),
            max(0, self.height - 2)
        )
    
    @property
    def inner_volume(self) -> float:
        """内容積を計算"""
        inner = self.inner_dimensions
        return inner[0] * inner[1] * inner[2]
    
    def can_fit_weight(self, weight: float) -> bool:
        """重量制限チェック"""
        return weight <= self.max_weight
    
    def can_fit_volume(self, volume: float) -> bool:
        """体積制限チェック"""
        return volume <= self.inner_volume

class BoxMaster:
    """輸送箱マスタ管理クラス"""
    
    def __init__(self):
        self.boxes = {
            'No.1': TransportBox('No.1', 37.5, 37.0, 24.0, 10.0),  # 100サイズ相当
            'No.2': TransportBox('No.2', 50.2, 40.2, 31.0, 15.0),  # 120サイズ相当
            'No.5': TransportBox('No.5', 53.2, 40.2, 33.8, 20.0),  # 130サイズ相当
            'No.6（100箱）': TransportBox('No.6（100箱）', 50.2, 40.2, 50.8, 25.0),  # 140サイズ相当
            'No.15': TransportBox('No.15', 57.5, 40.2, 34.0, 25.0)  # 140サイズ相当
        }
    
    def get_box(self, number: str) -> Optional[TransportBox]:
        """箱情報を取得"""
        return self.boxes.get(number)
    
    def get_all_boxes(self) -> Dict[str, TransportBox]:
        """全箱情報を取得"""
        return self.boxes.copy()
    
    def get_box_list(self) -> List[TransportBox]:
        """箱リストを取得"""
        return list(self.boxes.values())
    
    def find_suitable_boxes(self, required_volume: float, required_weight: float) -> List[TransportBox]:
        """適合する箱を検索"""
        suitable_boxes = []
        
        for box in self.boxes.values():
            if box.can_fit_volume(required_volume) and box.can_fit_weight(required_weight):
                suitable_boxes.append(box)
        
        # 体積順にソート（小さいものから）
        suitable_boxes.sort(key=lambda x: x.volume)
        return suitable_boxes
    
    def get_optimal_box(self, required_volume: float, required_weight: float) -> Optional[TransportBox]:
        """最適な箱を取得"""
        suitable_boxes = self.find_suitable_boxes(required_volume, required_weight)
        return suitable_boxes[0] if suitable_boxes else None
    
    def add_box(self, box: TransportBox):
        """箱を追加"""
        self.boxes[box.number] = box
