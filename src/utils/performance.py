import time
import functools
import streamlit as st
from typing import Any, Callable, Dict, List
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio


class PerformanceMonitor:
    """パフォーマンス監視クラス"""
    
    def __init__(self):
        self.metrics = {}
        self.logger = logging.getLogger(__name__)
    
    def time_function(self, func_name: str = None):
        """関数実行時間を測定するデコレータ"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                name = func_name or f"{func.__module__}.{func.__name__}"
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    # メトリクス記録
                    if name not in self.metrics:
                        self.metrics[name] = []
                    self.metrics[name].append(execution_time)
                    
                    # ログ出力
                    self.logger.info(f"⏱️ {name}: {execution_time:.3f}s")
                    
                    # 遅い処理への警告（1秒以上）
                    if execution_time > 1.0:
                        self.logger.warning(f"🐌 Slow operation detected: {name} took {execution_time:.3f}s")
                    
                    return result
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    self.logger.error(f"❌ {name} failed after {execution_time:.3f}s: {str(e)}")
                    raise
                    
            return wrapper
        return decorator
    
    def get_performance_report(self) -> Dict[str, Dict[str, float]]:
        """パフォーマンスレポートを生成"""
        report = {}
        
        for func_name, times in self.metrics.items():
            if times:
                report[func_name] = {
                    'avg_time': sum(times) / len(times),
                    'min_time': min(times),
                    'max_time': max(times),
                    'total_calls': len(times),
                    'total_time': sum(times)
                }
        
        return report


class CacheManager:
    """キャッシュ管理クラス"""
    
    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
        self.logger = logging.getLogger(__name__)
    
    def get(self, key: str) -> Any:
        """キャッシュからデータを取得"""
        if key in self.cache:
            self.access_times[key] = time.time()
            self.logger.debug(f"🎯 Cache hit: {key}")
            return self.cache[key]
        
        self.logger.debug(f"💨 Cache miss: {key}")
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """キャッシュにデータを保存"""
        # キャッシュサイズ制限チェック
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        self.cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl,
            'created_at': time.time()
        }
        self.access_times[key] = time.time()
        self.logger.debug(f"💾 Cache set: {key} (TTL: {ttl}s)")
    
    def _evict_oldest(self):
        """最も古いキャッシュエントリを削除"""
        if not self.access_times:
            return
        
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        self.delete(oldest_key)
        self.logger.debug(f"🗑️ Cache evicted: {oldest_key}")
    
    def delete(self, key: str):
        """キャッシュエントリを削除"""
        self.cache.pop(key, None)
        self.access_times.pop(key, None)
    
    def clear_expired(self):
        """期限切れキャッシュを削除"""
        current_time = time.time()
        expired_keys = []
        
        for key, data in self.cache.items():
            if current_time > data['expires_at']:
                expired_keys.append(key)
        
        for key in expired_keys:
            self.delete(key)
            self.logger.debug(f"⏰ Expired cache removed: {key}")
        
        return len(expired_keys)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """キャッシュ統計を取得"""
        current_time = time.time()
        expired_count = sum(1 for data in self.cache.values() 
                          if current_time > data['expires_at'])
        
        return {
            'total_entries': len(self.cache),
            'expired_entries': expired_count,
            'valid_entries': len(self.cache) - expired_count,
            'cache_usage': f"{len(self.cache)}/{self.max_size}",
            'memory_usage_mb': self._estimate_memory_usage()
        }
    
    def _estimate_memory_usage(self) -> float:
        """メモリ使用量を推定（MB）"""
        import sys
        total_size = 0
        
        for key, data in self.cache.items():
            total_size += sys.getsizeof(key)
            total_size += sys.getsizeof(data)
            total_size += sys.getsizeof(data['value'])
        
        return total_size / (1024 * 1024)  # MB


class ParallelProcessor:
    """並列処理管理クラス"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)
    
    def process_parallel(self, func: Callable, items: List[Any], 
                        chunk_size: int = None) -> List[Any]:
        """並列処理でタスクを実行"""
        if not items:
            return []
        
        # 小さなリストは並列化しない
        if len(items) < 4:
            return [func(item) for item in items]
        
        # チャンクサイズ自動計算
        if chunk_size is None:
            chunk_size = max(1, len(items) // self.max_workers)
        
        results = []
        start_time = time.time()
        
        try:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # タスクを並列実行
                future_to_item = {
                    executor.submit(func, item): item 
                    for item in items
                }
                
                for future in as_completed(future_to_item):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        item = future_to_item[future]
                        self.logger.error(f"❌ Parallel task failed for {item}: {str(e)}")
                        results.append(None)
            
            execution_time = time.time() - start_time
            self.logger.info(f"⚡ Parallel processing completed: {len(items)} items in {execution_time:.3f}s")
            
        except Exception as e:
            self.logger.error(f"❌ Parallel processing failed: {str(e)}")
            # フォールバック：順次処理
            results = [func(item) for item in items]
        
        return results


# グローバルインスタンス
performance_monitor = PerformanceMonitor()
cache_manager = CacheManager()
parallel_processor = ParallelProcessor()


def cached_function(ttl: int = 3600, key_func: Callable = None):
    """キャッシュ付き関数デコレータ"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # キャッシュキー生成
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # キャッシュから取得試行
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result['value']
            
            # 関数実行
            result = func(*args, **kwargs)
            
            # キャッシュに保存
            cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


@st.cache_data(ttl=3600)
def streamlit_cached_calculation(func_name: str, *args, **kwargs):
    """Streamlitキャッシュを活用した計算"""
    # この関数は具体的な計算関数をラップして使用
    pass