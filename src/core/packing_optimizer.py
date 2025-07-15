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
        
        # 実際の3D配置シミュレーション（離散的パッキング）
        packed_positions = self._discrete_3d_packing(items, box_w, box_d, box_h)
        
        if not packed_positions:
            return None
        
        # 実際の使用体積を計算
        actual_volume = sum(item.width * item.depth * item.height for item in packed_positions)
        
        # 利用率計算（内寸基準）
        usable_volume = box_w * box_d * box_h
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
    
    def _discrete_3d_packing(self, items: List[Dict], box_w: float, box_d: float, box_h: float) -> List[PackedItem]:
        """離散的3Dパッキング（実際の配置数を計算）"""
        packed_items = []
        
        # 商品タイプ別にグループ化
        product_groups = {}
        for item in items:
            size = item['size']
            if size not in product_groups:
                product_groups[size] = {'product': item['product'], 'count': 0}
            product_groups[size]['count'] += 1
        
        # 各商品タイプに対して最適配置を計算
        current_z = 0
        
        for size, group_data in product_groups.items():
            product = group_data['product']
            count = group_data['count']
            
            # 最適な向きを決定（複数パターンをテスト）
            orientations = [
                (product.width, product.depth, product.height),
                (product.depth, product.width, product.height),
                (product.width, product.height, product.depth),
                (product.depth, product.height, product.width),
                (product.height, product.width, product.depth),
                (product.height, product.depth, product.width)
            ]
            
            best_layout = None
            max_fit = 0
            
            for w, d, h in orientations:
                # この向きで何個配置できるかを計算
                fit_count = self._calculate_discrete_fit(count, w, d, h, box_w, box_d, box_h - current_z)
                if fit_count > max_fit:
                    max_fit = fit_count
                    best_layout = (w, d, h, fit_count)
            
            if best_layout and max_fit > 0:
                w, d, h, fit_count = best_layout
                
                # 実際に配置できる数が要求数より少ない場合は失敗とする
                if fit_count < count:
                    return []  # 全部入らない場合は失敗
                
                # 実際の配置を生成
                placed_items = self._generate_discrete_positions(
                    product, fit_count, w, d, h, box_w, box_d, current_z
                )
                packed_items.extend(placed_items)
                
                # 使用した高さ分を更新
                if placed_items:
                    used_height = max(item.z + item.height for item in placed_items) - current_z
                    current_z += used_height
        
        return packed_items
    
    def _calculate_discrete_fit(self, desired_count: int, item_w: float, item_d: float, item_h: float, 
                               box_w: float, box_d: float, available_h: float) -> int:
        """離散的配置で何個入るかを計算"""
        # 各軸に何個入るかを計算
        x_count = int(box_w // item_w)
        y_count = int(box_d // item_d)
        z_count = int(available_h // item_h)
        
        # 1層あたりの配置数
        per_layer = x_count * y_count
        
        # 総配置可能数
        total_possible = per_layer * z_count
        
        # 実際に配置する数（要求数との小さい方）
        return min(desired_count, total_possible)
    
    def _generate_discrete_positions(self, product, count: int, item_w: float, item_d: float, item_h: float,
                                    box_w: float, box_d: float, start_z: float) -> List[PackedItem]:
        """離散的配置の座標を生成"""
        positions = []
        
        # 各軸の配置数を計算
        x_count = int(box_w // item_w)
        y_count = int(box_d // item_d)
        
        placed = 0
        z = start_z
        
        while placed < count:
            for y_idx in range(y_count):
                if placed >= count:
                    break
                for x_idx in range(x_count):
                    if placed >= count:
                        break
                    
                    x = x_idx * item_w
                    y = y_idx * item_d
                    
                    # 回転判定
                    rotated = (item_w != product.width or item_d != product.depth)
                    
                    positions.append(PackedItem(
                        product=product,
                        x=x, y=y, z=z,
                        width=item_w, depth=item_d, height=item_h,
                        rotated=rotated
                    ))
                    placed += 1
            
            # 次の層へ
            z += item_h
        
        return positions
    
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