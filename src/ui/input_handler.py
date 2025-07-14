from typing import Dict, Optional
import streamlit as st
from src.data.products import ProductMaster


class InputHandler:
    """商品入力を処理するクラス"""
    
    def __init__(self):
        self.product_master = ProductMaster()
    
    def render_manual_input(self) -> Optional[Dict[str, int]]:
        """手動入力フォームを表示し、入力値を返す"""
        st.header("📦 商品数量入力")
        
        # 商品サイズ一覧を取得
        sizes = self.product_master.get_all_sizes()
        
        # クイックアクション処理（widget作成前に実行）
        if st.session_state.get('reset_all', False):
            for size in sizes:
                if f"qty_{size}" in st.session_state:
                    del st.session_state[f"qty_{size}"]
            st.session_state.reset_all = False
            st.success("入力値をリセットしました！")
        
        if st.session_state.get('increment_all', False):
            for size in sizes:
                current = st.session_state.get(f"qty_{size}", 0)
                st.session_state[f"qty_{size}"] = current + 1
            st.session_state.increment_all = False
            st.success("全て+1しました！")
        
        if st.session_state.get('decrement_all', False):
            for size in sizes:
                current = st.session_state.get(f"qty_{size}", 0)
                st.session_state[f"qty_{size}"] = max(0, current - 1)
            st.session_state.decrement_all = False
            st.success("全て-1しました！")
        
        # 個別クイック設定処理（widget作成前に実行）
        for size in sizes:
            if st.session_state.get(f"quick_set_{size}"):
                st.session_state[f"qty_{size}"] = st.session_state[f"quick_set_{size}"]
                del st.session_state[f"quick_set_{size}"]
        
        # コンパクトなクイックアクション行
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("🔄 リセット", use_container_width=True):
                st.session_state.reset_all = True
                st.rerun()
        
        with col2:
            if st.button("➕ 全て+1", use_container_width=True):
                st.session_state.increment_all = True
                st.rerun()
        
        with col3:
            if st.button("➖ 全て-1", use_container_width=True):
                st.session_state.decrement_all = True
                st.rerun()
        
        # モバイル対応：画面サイズに応じてカラム数を調整
        quantities = {}
        
        # サイズ別クイック設定値を定義
        quick_values = {
            'S': [10, 50, 100, 200],
            'Sロング': [5, 20, 50, 100],
            'L': [3, 10, 30, 50],
            'Lロング': [2, 5, 15, 30],
            'LL': [1, 3, 10, 20]
        }
        
        # モバイル最適化されたコンパクトな入力欄
        for size in sizes:
            product = self.product_master.get_product(size)
            values = quick_values.get(size, [1, 5, 10, 20])
            
            # コンパクトなコンテナ
            with st.container():
                # サイズ名と基本情報を1行で表示
                st.markdown(f"**{size}** 📏{product.width}×{product.depth}×{product.height}cm ⚖️{product.weight:.1f}kg")
                
                # 入力欄とクイック設定を1行で配置
                input_col, quick_col = st.columns([1, 2])
                
                with input_col:
                    quantities[size] = st.number_input(
                        "数量",
                        min_value=0,
                        value=st.session_state.get(f"qty_{size}", 0),
                        step=1,
                        key=f"qty_{size}",
                        label_visibility="collapsed"
                    )
                
                with quick_col:
                    # クイック設定ボタン（サイズ別）
                    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
                    
                    with q_col1:
                        if st.button(str(values[0]), key=f"quick_{values[0]}_{size}", use_container_width=True):
                            st.session_state[f"quick_set_{size}"] = values[0]
                            st.rerun()
                    
                    with q_col2:
                        if st.button(str(values[1]), key=f"quick_{values[1]}_{size}", use_container_width=True):
                            st.session_state[f"quick_set_{size}"] = values[1]
                            st.rerun()
                    
                    with q_col3:
                        if st.button(str(values[2]), key=f"quick_{values[2]}_{size}", use_container_width=True):
                            st.session_state[f"quick_set_{size}"] = values[2]
                            st.rerun()
                    
                    with q_col4:
                        if st.button(str(values[3]), key=f"quick_{values[3]}_{size}", use_container_width=True):
                            st.session_state[f"quick_set_{size}"] = values[3]
                            st.rerun()
        
        # コンパクトなリアルタイムサマリー
        total_items = sum(quantities.values())
        if total_items > 0:
            # 総重量と総体積を計算
            total_weight = sum(self.product_master.get_product(size).weight * qty 
                             for size, qty in quantities.items() if qty > 0)
            total_volume = sum(self.product_master.get_product(size).volume * qty 
                             for size, qty in quantities.items() if qty > 0)
            
            # 1行でコンパクトにサマリー表示
            st.markdown(f"**📊 合計:** {total_items}個 | {total_weight:.1f}kg | {total_volume:.0f}cm³")
            
            # 入力内訳を1行で表示
            breakdown = []
            for size, qty in quantities.items():
                if qty > 0:
                    breakdown.append(f"{size}×{qty}")
            if breakdown:
                st.caption(f"📋 {' | '.join(breakdown)}")
        
        # 計算ボタンをフル幅で表示（モバイル対応）
        button_disabled = total_items == 0
        if st.button("🔍 最適な輸送箱を計算", type="primary", use_container_width=True, disabled=button_disabled):
            if total_items > 0:
                return quantities
            else:
                st.error("少なくとも1つ以上の商品を入力してください。")
                return None
        
        return None
    
    def display_product_summary(self, quantities: Dict[str, int]):
        """入力された商品の概要を表示"""
        st.subheader("📋 入力内容確認")
        
        total_items = 0
        total_weight = 0.0
        total_volume = 0.0
        
        summary_data = []
        for size, qty in quantities.items():
            if qty > 0:
                product = self.product_master.get_product(size)
                item_weight = product.weight * qty
                item_volume = product.volume * qty
                
                summary_data.append({
                    "サイズ": size,
                    "数量": f"{qty}個",
                    "単体重量": f"{product.weight:.1f}kg",
                    "合計重量": f"{item_weight:.1f}kg",
                    "合計体積": f"{item_volume:.0f}cm³"
                })
                
                total_items += qty
                total_weight += item_weight
                total_volume += item_volume
        
        if summary_data:
            # レスポンシブテーブル表示
            st.dataframe(
                summary_data, 
                use_container_width=True,
                hide_index=True
            )
            
            # サマリー情報をカード形式で表示
            st.markdown("### 📊 集計結果")
            
            # モバイル完全対応：縦並びで表示
            st.metric(
                "📦 総個数", 
                f"{total_items}個",
                help="入力された全商品の合計個数"
            )
            st.metric(
                "⚖️ 総重量", 
                f"{total_weight:.1f}kg",
                help="全商品の合計重量"
            )
            st.metric(
                "📐 総体積", 
                f"{total_volume:.0f}cm³",
                help="全商品の合計体積"
            )