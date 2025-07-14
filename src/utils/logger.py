import logging
import logging.handlers
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
import streamlit as st
from pathlib import Path


class StructuredFormatter(logging.Formatter):
    """構造化ログフォーマッター"""
    
    def format(self, record: logging.LogRecord) -> str:
        # 基本ログ情報
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # 例外情報があれば追加
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # カスタム属性があれば追加
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'exc_info', 'exc_text', 'stack_info']:
                log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False, default=str)


class ApplicationLogger:
    """アプリケーション専用ログクラス"""
    
    def __init__(self, 
                 name: str = "minoru_packing",
                 log_level: str = "INFO",
                 log_dir: str = "logs",
                 max_file_size: int = 10485760,  # 10MB
                 backup_count: int = 5):
        
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # ロガー設定
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # 既存のハンドラーをクリア
        self.logger.handlers.clear()
        
        # ファイルハンドラー（回転ログ）
        log_file = self.log_dir / f"{name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, 
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(file_handler)
        
        # エラーログ専用ファイル
        error_log_file = self.log_dir / f"{name}_error.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(error_handler)
        
        # 開発環境ではコンソール出力も追加
        if os.getenv('ENVIRONMENT', 'development') == 'development':
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
    
    def get_logger(self) -> logging.Logger:
        """ロガーインスタンスを取得"""
        return self.logger
    
    def log_user_action(self, action: str, details: Dict[str, Any] = None):
        """ユーザーアクションをログ記録"""
        log_data = {
            'event_type': 'user_action',
            'action': action,
            'session_id': getattr(st.session_state, 'session_id', 'unknown'),
            'user_ip': self._get_client_ip(),
            'timestamp': datetime.now().isoformat()
        }
        
        if details:
            log_data.update(details)
        
        self.logger.info(f"User action: {action}", extra=log_data)
    
    def log_performance(self, operation: str, duration: float, details: Dict[str, Any] = None):
        """パフォーマンス情報をログ記録"""
        log_data = {
            'event_type': 'performance',
            'operation': operation,
            'duration_ms': duration * 1000,
            'timestamp': datetime.now().isoformat()
        }
        
        if details:
            log_data.update(details)
        
        if duration > 1.0:  # 1秒以上の処理は警告
            self.logger.warning(f"Slow operation: {operation} took {duration:.3f}s", extra=log_data)
        else:
            self.logger.info(f"Performance: {operation} completed in {duration:.3f}s", extra=log_data)
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """エラー情報をログ記録"""
        log_data = {
            'event_type': 'error',
            'error_type': error.__class__.__name__,
            'error_message': str(error),
            'session_id': getattr(st.session_state, 'session_id', 'unknown'),
            'timestamp': datetime.now().isoformat()
        }
        
        if context:
            log_data.update(context)
        
        self.logger.error(f"Error occurred: {str(error)}", extra=log_data, exc_info=True)
    
    def log_business_event(self, event: str, data: Dict[str, Any]):
        """ビジネスイベントをログ記録"""
        log_data = {
            'event_type': 'business_event',
            'event': event,
            'timestamp': datetime.now().isoformat()
        }
        log_data.update(data)
        
        self.logger.info(f"Business event: {event}", extra=log_data)
    
    def _get_client_ip(self) -> str:
        """クライアントIPアドレスを取得"""
        try:
            # StreamlitでのクライアントIP取得は制限があるため、
            # 可能な範囲で取得を試行
            return "unknown"
        except:
            return "unknown"
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """ログ統計を取得"""
        stats = {
            'log_files': [],
            'total_size_mb': 0
        }
        
        try:
            for log_file in self.log_dir.glob(f"{self.name}*.log*"):
                file_stats = log_file.stat()
                stats['log_files'].append({
                    'name': log_file.name,
                    'size_mb': file_stats.st_size / (1024 * 1024),
                    'modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat()
                })
                stats['total_size_mb'] += file_stats.st_size / (1024 * 1024)
        except Exception as e:
            self.logger.error(f"Failed to get log statistics: {str(e)}")
        
        return stats


class StreamlitLogHandler(logging.Handler):
    """Streamlit用ログハンドラー（開発時のデバッグ用）"""
    
    def __init__(self):
        super().__init__()
        self.logs = []
        self.max_logs = 100
    
    def emit(self, record: logging.LogRecord):
        """ログレコードを処理"""
        try:
            log_entry = {
                'timestamp': datetime.fromtimestamp(record.created),
                'level': record.levelname,
                'message': record.getMessage(),
                'logger': record.name
            }
            
            self.logs.append(log_entry)
            
            # 最大ログ数を超えたら古いものを削除
            if len(self.logs) > self.max_logs:
                self.logs.pop(0)
                
        except Exception:
            self.handleError(record)
    
    def get_logs(self, level: str = None, limit: int = 50):
        """ログを取得"""
        logs = self.logs.copy()
        
        if level:
            logs = [log for log in logs if log['level'] == level.upper()]
        
        return logs[-limit:]


# グローバルロガーインスタンス
app_logger = ApplicationLogger()
logger = app_logger.get_logger()

# Streamlit用ログハンドラー（開発時）
streamlit_handler = StreamlitLogHandler()


def setup_logging(environment: str = "development", log_level: str = "INFO"):
    """ログ設定を初期化"""
    global app_logger, logger
    
    app_logger = ApplicationLogger(
        log_level=log_level,
        log_dir="logs" if environment == "production" else "logs/dev"
    )
    logger = app_logger.get_logger()
    
    # 開発環境ではStreamlitハンドラーも追加
    if environment == "development":
        logger.addHandler(streamlit_handler)
    
    logger.info(f"Logging initialized for {environment} environment")


def get_logger(name: str = None) -> logging.Logger:
    """ロガーを取得"""
    if name:
        return logging.getLogger(name)
    return logger


# 便利な関数
def log_function_call(func_name: str, args: Dict[str, Any] = None):
    """関数呼び出しをログ記録"""
    details = {'function': func_name}
    if args:
        details['arguments'] = str(args)[:200]  # 長すぎる引数は切り捨て
    
    app_logger.log_user_action('function_call', details)


def log_user_input(input_type: str, data: Dict[str, Any]):
    """ユーザー入力をログ記録"""
    app_logger.log_user_action('user_input', {
        'input_type': input_type,
        'data_summary': str(data)[:100]  # 個人情報を避けるため概要のみ
    })


def log_calculation_result(calculation_type: str, input_summary: str, result_summary: str):
    """計算結果をログ記録"""
    app_logger.log_business_event('calculation_completed', {
        'calculation_type': calculation_type,
        'input_summary': input_summary,
        'result_summary': result_summary
    })


def log_user_action(action: str, details: Dict[str, Any] = None):
    """ユーザーアクションをログ記録（モジュールレベル関数）"""
    app_logger.log_user_action(action, details)


def log_calc(calculation_type: str, input_data: Dict[str, Any], result_data: Dict[str, Any]):
    """計算処理をログ記録（モジュールレベル関数）"""
    app_logger.log_business_event('calculation', {
        'type': calculation_type,
        'input': str(input_data)[:200],
        'result': str(result_data)[:200]
    })