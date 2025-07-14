from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from src.data.products import ProductMaster, Product
from src.data.boxes import BoxMaster, TransportBox


@dataclass
class PackedItem:
    """配置済み商品の情報"""
    product: Product
    x: float  # X座標
    y: float  # Y座標  
    z: float  # Z座標（高さ）
    width: float
    depth: float
    height: float
    rotated: bool = False  # 回転されているか


@dataclass
class PackingResult:
    """パッキング結果を保持するクラス"""
    box: TransportBox
    items: List[Dict[str, any]]
    packed_items: List[PackedItem]  # 3D配置情報
    total_weight: float
    total_volume: float
    utilization_rate: float
    is_feasible: bool
    packing_efficiency: float = 0.0  # パッキング効率
    
    def __str__(self) -> str:
        return f"Box: {self.box.number}, Items: {len(self.items)}, Utilization: {self.utilization_rate:.1%}, Efficiency: {self.packing_efficiency:.1%}"


class SimplePacking:
    """シンプルなパッキング計算エンジン"""
    
    def __init__(self):
        self.product_master = ProductMaster()
        self.box_master = BoxMaster()
    
    def calculate_packing(self, quantities: Dict[str, int]) -> List[PackingResult]:
        """商品リストから最適な箱を計算"""
        # 総重量と総体積を計算
        total_weight = 0.0
        total_volume = 0.0
        items = []
        
        for size, qty in quantities.items():
            if qty > 0:
                product = self.product_master.get_product(size)
                total_weight += product.weight * qty
                total_volume += product.volume * qty
                
                for _ in range(qty):
                    items.append({
                        'product': product,
                        'size': size
                    })
        
        # 体積順にソート（大きいものから）
        items.sort(key=lambda x: x['product'].volume, reverse=True)
        
        # 適合する箱を探す
        suitable_boxes = self.box_master.find_suitable_boxes(total_volume, total_weight)
        
        # デバッグ情報
        print(f"DEBUG: Total volume: {total_volume:.2f} cm³, Total weight: {total_weight:.2f} kg")
        print(f"DEBUG: Found {len(suitable_boxes)} suitable boxes: {[box.number for box in suitable_boxes]}")
        
        results = []
        for box in suitable_boxes:
            # 簡易的なパッキング判定
            result = self._try_pack_items(box, items, total_weight, total_volume)
            print(f"DEBUG: Box {box.number} packing result: {'Success' if result else 'Failed'}")
            if result:
                results.append(result)
        
        # 利用率でソート（高い順）
        results.sort(key=lambda x: x.utilization_rate, reverse=True)
        
        return results
    
    def _try_pack_items(self, box: TransportBox, items: List[Dict], 
                       total_weight: float, total_volume: float) -> Optional[PackingResult]:
        """アイテムを箱に詰めてみる（3D配置考慮版）"""
        # 重量チェック
        if not box.can_fit_weight(total_weight):
            return None
        
        # 内寸取得
        inner_dims = box.inner_dimensions
        box_w, box_d, box_h = inner_dims
        usable_volume = box_w * box_d * box_h
        
        # 体積チェック
        if total_volume > usable_volume:
            return None
        
        # 3D配置シミュレーション
        packed_positions = self._advanced_3d_packing(items, box_w, box_d, box_h)
        
        if not packed_positions:
            return None
        
        # 実際の使用体積を計算
        actual_volume = sum(item.width * item.depth * item.height for item in packed_positions)
        
        # 利用率計算（内寸基準）
        utilization = (actual_volume / usable_volume) * 100
        
        # パッキング効率計算（空間の無駄を最小化）
        max_height_used = max((item.z + item.height) for item in packed_positions) if packed_positions else 0
        efficiency = (actual_volume / (box_w * box_d * max_height_used)) * 100 if max_height_used > 0 else 0
        
        return PackingResult(
            box=box,
            items=items,
            packed_items=packed_positions,
            total_weight=total_weight,
            total_volume=actual_volume,
            utilization_rate=utilization,
            packing_efficiency=efficiency,
            is_feasible=True
        )
    
    def _advanced_3d_packing(self, items: List[Dict], box_w: float, box_d: float, box_h: float) -> List[PackedItem]:
        """高度な3Dパッキングアルゴリズム（Bottom-Left-Fill戦略）"""
        packed_items = []
        
        # アイテムを体積の大きい順にソート
        sorted_items = sorted(items, key=lambda x: x['product'].volume, reverse=True)
        
        # 3D空間を管理するための座標リスト
        free_positions = [(0, 0, 0)]  # (x, y, z)
        
        for item_data in sorted_items:
            product = item_data['product']
            
            # 複数の向きを試す（回転考慮）
            orientations = [
                (product.width, product.depth, product.height, False),  # 元の向き
                (product.depth, product.width, product.height, True),   # 90度回転
            ]
            
            placed = False
            for width, depth, height, rotated in orientations:
                if placed:
                    break
                    
                # 各可能位置で配置を試す
                for pos_idx, (x, y, z) in enumerate(free_positions):
                    # 箱の境界チェック
                    if (x + width <= box_w and 
                        y + depth <= box_d and 
                        z + height <= box_h):
                        
                        # 他のアイテムとの干渉チェック
                        if not self._check_collision(packed_items, x, y, z, width, depth, height):
                            # 重量安定性チェック
                            if self._check_stability(packed_items, x, y, z, width, depth, height, product.weight):
                                # 配置可能
                                packed_item = PackedItem(
                                    product=product,
                                    x=x, y=y, z=z,
                                    width=width, depth=depth, height=height,
                                    rotated=rotated
                                )
                                packed_items.append(packed_item)
                                
                                # 使用した位置を削除
                                free_positions.pop(pos_idx)
                                
                                # 新しい配置可能位置を追加
                                self._add_new_positions(free_positions, x, y, z, width, depth, height)
                                
                                placed = True
                                break
            
            # 配置できなかった場合は失敗
            if not placed:
                return []
        
        return packed_items
    
    def _check_collision(self, packed_items: List[PackedItem], x: float, y: float, z: float, 
                        width: float, depth: float, height: float) -> bool:
        """新しいアイテムが既存アイテムと干渉するかチェック"""
        for item in packed_items:
            # 3D空間での重複チェック
            if not (x >= item.x + item.width or x + width <= item.x or
                   y >= item.y + item.depth or y + depth <= item.y or
                   z >= item.z + item.height or z + height <= item.z):
                return True  # 衝突あり
        return False  # 衝突なし
    
    def _add_new_positions(self, positions: List[Tuple[float, float, float]], 
                          x: float, y: float, z: float, width: float, depth: float, height: float):
        """新しいアイテム配置後の候補位置を追加"""
        # 新しい配置可能位置を計算
        new_positions = [
            (x + width, y, z),      # 右側
            (x, y + depth, z),      # 奥側
            (x, y, z + height),     # 上側
        ]
        
        for pos in new_positions:
            if pos not in positions:
                positions.append(pos)
        
        # 位置をソート（左下奥優先）
        positions.sort(key=lambda p: (p[2], p[1], p[0]))
    
    def _check_stability(self, packed_items: List[PackedItem], x: float, y: float, z: float,
                        width: float, depth: float, height: float, weight: float) -> bool:
        """重量安定性をチェック"""
        # 底面（z=0）の場合は常に安定
        if z == 0:
            return True
        
        # 支持面積の計算
        support_area = 0.0
        required_area = width * depth
        
        # 下にある全てのアイテムをチェック
        for item in packed_items:
            # アイテムの上面がこのアイテムの底面と接触しているかチェック
            if abs(item.z + item.height - z) < 0.01:  # 浮動小数点の誤差を考慮
                # 重複する面積を計算
                overlap_x = max(0, min(x + width, item.x + item.width) - max(x, item.x))
                overlap_y = max(0, min(y + depth, item.y + item.depth) - max(y, item.y))
                overlap_area = overlap_x * overlap_y
                support_area += overlap_area
        
        # 重量制限チェック（下のアイテムが支えられるか）
        if not self._check_weight_distribution(packed_items, x, y, z, width, depth, weight):
            return False
        
        # 少なくとも50%の支持面積が必要
        stability_threshold = 0.5
        return (support_area / required_area) >= stability_threshold
    
    def _check_weight_distribution(self, packed_items: List[PackedItem], x: float, y: float, z: float,
                                  width: float, depth: float, new_weight: float) -> bool:
        """重量分散をチェック"""
        max_weight_per_item = 50.0  # kg（仮の制限値）
        
        # 新しいアイテムが乗る下のアイテムをチェック
        for item in packed_items:
            if abs(item.z + item.height - z) < 0.01:  # 直下のアイテム
                # 重複する面積を計算
                overlap_x = max(0, min(x + width, item.x + item.width) - max(x, item.x))
                overlap_y = max(0, min(y + depth, item.y + item.depth) - max(y, item.y))
                
                if overlap_x > 0 and overlap_y > 0:
                    # 重量が分散される割合を計算
                    overlap_ratio = (overlap_x * overlap_y) / (width * depth)
                    distributed_weight = new_weight * overlap_ratio
                    
                    # そのアイテムにかかる総重量を計算
                    total_weight_on_item = self._calculate_weight_on_item(packed_items, item)
                    total_weight_on_item += distributed_weight
                    
                    # 重量制限チェック
                    if total_weight_on_item > max_weight_per_item:
                        return False
        
        return True
    
    def _calculate_weight_on_item(self, packed_items: List[PackedItem], target_item: PackedItem) -> float:
        """特定のアイテムにかかっている総重量を計算"""
        total_weight = target_item.product.weight
        
        # その上にあるアイテムの重量を加算
        for item in packed_items:
            if item.z > target_item.z + target_item.height - 0.01:
                # 重複チェック
                overlap_x = max(0, min(target_item.x + target_item.width, item.x + item.width) - 
                              max(target_item.x, item.x))
                overlap_y = max(0, min(target_item.y + target_item.depth, item.y + item.depth) - 
                              max(target_item.y, item.y))
                
                if overlap_x > 0 and overlap_y > 0:
                    # 重量の一部がこのアイテムにかかる
                    overlap_ratio = (overlap_x * overlap_y) / (item.width * item.depth)
                    total_weight += item.product.weight * overlap_ratio
        
        return total_weight
    
    def _can_fit_in_layer(self, products: List[Product], layer_w: float, layer_d: float) -> bool:
        """1つの層内に商品が配置可能かチェック（旧互換性のため保持）"""
        # 簡易的な2D配置チェック
        total_area = sum(p.width * p.depth for p in products)
        available_area = layer_w * layer_d
        
        # 面積チェック（効率係数0.9を適用）
        if total_area > available_area * 0.9:
            return False
        
        # 最大寸法チェック
        max_width = max(p.width for p in products)
        max_depth = max(p.depth for p in products)
        
        if max_width > layer_w or max_depth > layer_d:
            return False
        
        return True
    
    def get_packing_recommendation(self, results: List[PackingResult]) -> Optional[PackingResult]:
        """最適な箱を推奨"""
        if not results:
            return None
        
        # パッキング効率を重視して選択
        for result in results:
            if result.packing_efficiency >= 60:  # 効率60%以上を優先
                return result
        
        # 効率が低い場合は利用率を重視
        for result in results:
            if result.utilization_rate >= 50:
                return result
        
        # どちらも満たさない場合は最も効率の高いものを選択
        return max(results, key=lambda x: x.packing_efficiency) if results else None
    
    def get_packing_steps(self, result: PackingResult) -> List[Dict[str, any]]:
        """パッキング手順を生成（簡潔版）"""
        if not result or not result.packed_items:
            return []
        
        # 商品をサイズ別にグループ化
        size_groups = {}
        for item in result.packed_items:
            size = item.product.size
            if size not in size_groups:
                size_groups[size] = []
            size_groups[size].append(item)
        
        # 簡潔なステップを生成
        steps = []
        step_num = 1
        
        # 高さ順にレイヤー分け
        layers = {}
        for item in result.packed_items:
            layer_height = int(item.z / 10) * 10  # 10cm単位でレイヤー分け
            if layer_height not in layers:
                layers[layer_height] = []
            layers[layer_height].append(item)
        
        # レイヤー毎にまとめてステップ化
        for layer_height in sorted(layers.keys()):
            layer_items = layers[layer_height]
            
            # 同じレイヤーの商品をサイズ別にグループ化
            layer_groups = {}
            for item in layer_items:
                size = item.product.size
                if size not in layer_groups:
                    layer_groups[size] = 0
                layer_groups[size] += 1
            
            # レイヤー説明を生成
            if layer_height == 0:
                layer_desc = "底面に配置"
            else:
                layer_desc = f"高さ{layer_height}cm付近に配置"
            
            # グループ化された商品説明
            items_desc = []
            for size, count in layer_groups.items():
                if count == 1:
                    items_desc.append(f"{size}")
                else:
                    items_desc.append(f"{size} × {count}個")
            
            step = {
                'step': step_num,
                'description': f"{layer_desc}: {', '.join(items_desc)}",
                'items_count': len(layer_items)
            }
            steps.append(step)
            step_num += 1
        
        return steps
    
    def _get_placement_description(self, item: PackedItem) -> str:
        """配置説明を生成"""
        desc = f"{item.product.size}を"
        
        if item.z == 0:
            desc += "箱の底面に"
        else:
            desc += f"高さ{item.z:.1f}cmの位置に"
        
        if item.rotated:
            desc += "（90度回転して）"
        
        desc += "配置"
        
        return desc
    
    def get_packing_summary(self, result: PackingResult) -> Dict[str, any]:
        """パッキング結果のサマリーを生成"""
        if not result:
            return {}
        
        # 高さの使用状況
        max_height_used = max((item.z + item.height) for item in result.packed_items) if result.packed_items else 0
        height_efficiency = (max_height_used / result.box.inner_dimensions[2]) * 100
        
        # 重量分布
        weight_per_layer = {}
        for item in result.packed_items:
            layer = int(item.z)
            weight_per_layer[layer] = weight_per_layer.get(layer, 0) + item.product.weight
        
        return {
            'box_info': {
                'model': result.box.number,
                'dimensions': f"{result.box.width} × {result.box.depth} × {result.box.height} cm",
                'inner_dimensions': f"{result.box.inner_dimensions[0]} × {result.box.inner_dimensions[1]} × {result.box.inner_dimensions[2]} cm",
                'max_weight': f"{result.box.max_weight} kg"
            },
            'packing_stats': {
                'total_items': len(result.packed_items),
                'total_weight': f"{result.total_weight:.1f} kg",
                'volume_utilization': f"{result.utilization_rate:.1f}%",
                'packing_efficiency': f"{result.packing_efficiency:.1f}%",
                'height_used': f"{max_height_used:.1f} cm",
                'height_efficiency': f"{height_efficiency:.1f}%"
            },
            'weight_distribution': weight_per_layer,
            'item_count_by_size': self._count_items_by_size(result.packed_items)
        }
    
    def _count_items_by_size(self, packed_items: List[PackedItem]) -> Dict[str, int]:
        """サイズ別アイテム数をカウント"""
        counts = {}
        for item in packed_items:
            size = item.product.size
            counts[size] = counts.get(size, 0) + 1
        return counts