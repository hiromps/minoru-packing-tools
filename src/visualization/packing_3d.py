import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import streamlit as st
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from src.core.packing_optimizer import PackingResult
from src.data.products import Product


@dataclass
class Item3D:
    """3D配置用アイテム情報"""
    product: Product
    position: Tuple[float, float, float]  # x, y, z
    size: str
    color: str


class Packing3DVisualizer:
    """3Dパッキング可視化エンジン"""
    
    def __init__(self):
        self.colors = {
            'S': '#FF6B6B',      # 赤
            'Sロング': '#FF8E53',  # オレンジ
            'L': '#4ECDC4',      # ティール
            'Lロング': '#45B7D1',  # 青
            'LL': '#96CEB4'      # 緑
        }
    
    def create_3d_visualization(self, packing_result: PackingResult) -> go.Figure:
        """3Dパッキング可視化を作成"""
        fig = go.Figure()
        
        # 箱の描画
        self._add_box_to_figure(fig, packing_result.box)
        
        # 商品の配置計算と描画
        item_positions = self._calculate_item_positions(packing_result)
        self._add_items_to_figure(fig, item_positions)
        
        # レイアウト設定
        self._configure_layout(fig, packing_result.box)
        
        return fig
    
    def _add_box_to_figure(self, fig: go.Figure, box):
        """箱をfigureに追加"""
        # 箱の外枠
        x_box = [0, box.width, box.width, 0, 0, box.width, box.width, 0]
        y_box = [0, 0, box.depth, box.depth, 0, 0, box.depth, box.depth]
        z_box = [0, 0, 0, 0, box.height, box.height, box.height, box.height]
        
        # 底面
        fig.add_trace(go.Mesh3d(
            x=[0, box.width, box.width, 0],
            y=[0, 0, box.depth, box.depth],
            z=[0, 0, 0, 0],
            i=[0, 0], j=[1, 2], k=[2, 3],
            color='lightgray',
            opacity=0.3,
            name='箱の底面'
        ))
        
        # 箱の枠線
        edges = [
            # 底面の枠
            [0, 1], [1, 2], [2, 3], [3, 0],
            # 上面の枠
            [4, 5], [5, 6], [6, 7], [7, 4],
            # 縦の枠
            [0, 4], [1, 5], [2, 6], [3, 7]
        ]
        
        for edge in edges:
            fig.add_trace(go.Scatter3d(
                x=[x_box[edge[0]], x_box[edge[1]]],
                y=[y_box[edge[0]], y_box[edge[1]]],
                z=[z_box[edge[0]], z_box[edge[1]]],
                mode='lines',
                line=dict(color='black', width=3),
                showlegend=False
            ))
    
    def _calculate_item_positions(self, packing_result: PackingResult) -> List[Item3D]:
        """アイテムの3D配置を計算"""
        items_3d = []
        
        # 簡易的な層状配置アルゴリズム
        current_x, current_y, current_z = 1, 1, 0  # 梱包材分の余白
        max_height_in_layer = 0
        box_inner_w, box_inner_d, box_inner_h = packing_result.box.inner_dimensions
        
        # サイズ別にグループ化
        size_groups = {}
        for item in packing_result.items:
            size = item['size']
            if size not in size_groups:
                size_groups[size] = []
            size_groups[size].append(item)
        
        # 高さ順にソート（低いものから配置）
        sorted_sizes = sorted(size_groups.keys(), 
                            key=lambda s: size_groups[s][0]['product'].height)
        
        for size in sorted_sizes:
            items = size_groups[size]
            
            for item in items:
                product = item['product']
                
                # 現在の行に配置できるかチェック
                if current_x + product.width > box_inner_w:
                    # 次の行に移動
                    current_x = 1
                    current_y += max_height_in_layer + 0.5
                    max_height_in_layer = 0
                    
                    # 次の行が箱に収まらない場合は次の層に
                    if current_y + product.depth > box_inner_d:
                        current_y = 1
                        current_z += max_height_in_layer
                        max_height_in_layer = 0
                
                # アイテム配置
                items_3d.append(Item3D(
                    product=product,
                    position=(current_x, current_y, current_z),
                    size=size,
                    color=self.colors.get(size, '#999999')
                ))
                
                # 次の位置を更新
                current_x += product.width + 0.2  # 隙間
                max_height_in_layer = max(max_height_in_layer, product.height)
        
        return items_3d
    
    def _add_items_to_figure(self, fig: go.Figure, items_3d: List[Item3D]):
        """アイテムをfigureに追加"""
        for i, item in enumerate(items_3d):
            x, y, z = item.position
            w, d, h = item.product.width, item.product.depth, item.product.height
            
            # 立方体の8つの頂点
            vertices = [
                [x, y, z], [x+w, y, z], [x+w, y+d, z], [x, y+d, z],  # 底面
                [x, y, z+h], [x+w, y, z+h], [x+w, y+d, z+h], [x, y+d, z+h]  # 上面
            ]
            
            vertices = np.array(vertices)
            
            # 立方体の面を定義
            faces = [
                [0, 1, 2, 3], [4, 7, 6, 5],  # 底面, 上面
                [0, 4, 5, 1], [2, 6, 7, 3],  # 前面, 後面
                [0, 3, 7, 4], [1, 5, 6, 2]   # 左面, 右面
            ]
            
            # Mesh3dで立方体を描画
            fig.add_trace(go.Mesh3d(
                x=vertices[:, 0],
                y=vertices[:, 1], 
                z=vertices[:, 2],
                i=[0, 4, 0, 2, 0, 1],
                j=[1, 7, 3, 6, 4, 5],
                k=[2, 6, 7, 7, 5, 6],
                color=item.color,
                opacity=0.8,
                name=f'{item.size}_{i+1}',
                hovertemplate=f'<b>{item.size}サイズ</b><br>' +
                             f'位置: ({x:.1f}, {y:.1f}, {z:.1f})<br>' +
                             f'寸法: {w}×{d}×{h}cm<extra></extra>'
            ))
    
    def _configure_layout(self, fig: go.Figure, box):
        """図のレイアウトを設定"""
        fig.update_layout(
            title={
                'text': f'📦 3D梱包レイアウト - {box.number}',
                'x': 0.5,
                'font': {'size': 20}
            },
            scene=dict(
                xaxis_title='幅 (cm)',
                yaxis_title='奥行 (cm)',
                zaxis_title='高さ (cm)',
                xaxis=dict(range=[0, box.width + 2]),
                yaxis=dict(range=[0, box.depth + 2]),
                zaxis=dict(range=[0, box.height + 2]),
                aspectmode='manual',
                aspectratio=dict(
                    x=box.width/max(box.width, box.depth, box.height),
                    y=box.depth/max(box.width, box.depth, box.height),
                    z=box.height/max(box.width, box.depth, box.height)
                ),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            ),
            width=800,
            height=600,
            margin=dict(l=0, r=0, t=50, b=0)
        )


class PackingStepsGenerator:
    """梱包手順生成器"""
    
    def __init__(self):
        self.step_templates = {
            'prepare': "📦 {box_name}の箱を準備します",
            'layer_start': "🏗️ 第{layer}層目の配置を開始します",
            'place_item': "📍 {size}サイズを位置({x:.1f}, {y:.1f})に配置",
            'layer_complete': "✅ 第{layer}層目が完了しました",
            'packaging_complete': "🎉 梱包が完了しました！"
        }
    
    def generate_packing_steps(self, packing_result: PackingResult) -> List[Dict[str, str]]:
        """梱包手順を生成"""
        steps = []
        
        # 準備
        steps.append({
            'type': 'prepare',
            'title': f"箱の準備 - {packing_result.box.number}",
            'description': f"{packing_result.box.width}×{packing_result.box.depth}×{packing_result.box.height}cmの箱を準備します",
            'icon': '📦'
        })
        
        # アイテムを層別に整理
        layers = self._organize_items_by_layers(packing_result)
        
        for layer_num, layer_items in enumerate(layers, 1):
            # 層開始
            steps.append({
                'type': 'layer_start',
                'title': f"第{layer_num}層目の開始",
                'description': f"{len(layer_items)}個のアイテムを配置します",
                'icon': '🏗️'
            })
            
            # 各アイテムの配置
            for i, item in enumerate(layer_items, 1):
                steps.append({
                    'type': 'place_item',
                    'title': f"{item['size']}サイズの配置",
                    'description': f"第{layer_num}層目の{i}番目として配置",
                    'icon': '📍',
                    'details': {
                        'size': item['size'],
                        'dimensions': f"{item['product'].width}×{item['product'].depth}×{item['product'].height}cm",
                        'weight': f"{item['product'].weight}kg"
                    }
                })
            
            # 層完了
            steps.append({
                'type': 'layer_complete',
                'title': f"第{layer_num}層目完了",
                'description': "次の層の準備をします",
                'icon': '✅'
            })
        
        # 完了
        steps.append({
            'type': 'packaging_complete',
            'title': "梱包完了",
            'description': f"全{len(packing_result.items)}個のアイテムの梱包が完了しました",
            'icon': '🎉'
        })
        
        return steps
    
    def _organize_items_by_layers(self, packing_result: PackingResult) -> List[List[Dict]]:
        """アイテムを層別に整理"""
        # 簡易的な層分け（高さ別）
        height_groups = {}
        for item in packing_result.items:
            height = item['product'].height
            if height not in height_groups:
                height_groups[height] = []
            height_groups[height].append(item)
        
        # 高さ順にソートして層として返す
        sorted_heights = sorted(height_groups.keys())
        return [height_groups[height] for height in sorted_heights]
    
    def render_packing_steps(self, steps: List[Dict[str, str]]):
        """梱包手順をStreamlitで表示"""
        st.subheader("")
        
        for i, step in enumerate(steps, 1):
            with st.container():
                col1, col2 = st.columns([1, 10])
                
                with col1:
                    st.markdown(f"### {step['icon']}")
                
                with col2:
                    st.markdown(f"**ステップ {i}: {step['title']}**")
                    st.write(step['description'])
                    
                    if 'details' in step:
                        with st.expander(f"📝 詳細情報"):
                            for key, value in step['details'].items():
                                st.write(f"- **{key}**: {value}")
                
                if i < len(steps):
                    st.markdown("---")