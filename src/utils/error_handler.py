import logging
import traceback
import streamlit as st
from typing import Any, Callable, Dict, Optional, Type
from functools import wraps
import sys
from datetime import datetime


class ErrorSeverity:
    """エラー重要度定義"""
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class ApplicationError(Exception):
    """アプリケーション固有エラー基底クラス"""
    
    def __init__(self, message: str, error_code: str = None, severity: str = ErrorSeverity.ERROR):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "APP_ERROR"
        self.severity = severity
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'message': self.message,
            'error_code': self.error_code,
            'severity': self.severity,
            'timestamp': self.timestamp.isoformat(),
            'type': self.__class__.__name__
        }


class PackingError(ApplicationError):
    """パッキング処理エラー"""
    
    def __init__(self, message: str, quantities: Dict = None):
        super().__init__(message, "PACKING_ERROR", ErrorSeverity.ERROR)
        self.quantities = quantities


class ImageProcessingError(ApplicationError):
    """画像処理エラー"""
    
    def __init__(self, message: str, image_info: Dict = None):
        super().__init__(message, "IMAGE_ERROR", ErrorSeverity.WARNING)
        self.image_info = image_info


class DataValidationError(ApplicationError):
    """データ検証エラー"""
    
    def __init__(self, message: str, invalid_data: Any = None):
        super().__init__(message, "VALIDATION_ERROR", ErrorSeverity.WARNING)
        self.invalid_data = invalid_data


class ErrorHandler:
    """統合エラーハンドリングクラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_count = {}
        self.last_errors = []
        self.max_error_history = 100
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """エラーを統一的に処理"""
        error_info = self._extract_error_info(error, context)
        self._log_error(error_info)
        self._update_error_statistics(error_info)
        self._show_user_message(error_info)
        
        return error_info
    
    def _extract_error_info(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """エラー情報を抽出"""
        if isinstance(error, ApplicationError):
            error_info = error.to_dict()
        else:
            error_info = {
                'message': str(error),
                'error_code': 'SYSTEM_ERROR',
                'severity': ErrorSeverity.ERROR,
                'timestamp': datetime.now().isoformat(),
                'type': error.__class__.__name__
            }
        
        # コンテキスト情報を追加
        if context:
            error_info['context'] = context
        
        # スタックトレース追加
        error_info['traceback'] = traceback.format_exc()
        
        # エラー発生場所を追加
        tb = sys.exc_info()[2]
        if tb:
            frame = tb.tb_frame
            error_info['location'] = {
                'file': frame.f_code.co_filename,
                'function': frame.f_code.co_name,
                'line': tb.tb_lineno
            }
        
        return error_info
    
    def _log_error(self, error_info: Dict[str, Any]):
        """エラーをログ出力"""
        severity = error_info.get('severity', ErrorSeverity.ERROR)
        message = f"[{error_info['error_code']}] {error_info['message']}"
        
        # ログレコードの予約語を除外したextraデータを作成
        reserved_keys = {
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
            'filename', 'module', 'lineno', 'funcName', 'created', 
            'msecs', 'relativeCreated', 'thread', 'threadName',
            'processName', 'process', 'exc_info', 'exc_text', 'stack_info',
            'message'  # messageも予約語として除外
        }
        
        extra_data = {k: v for k, v in error_info.items() if k not in reserved_keys}
        
        if severity == ErrorSeverity.CRITICAL:
            self.logger.critical(message, extra=extra_data)
        elif severity == ErrorSeverity.ERROR:
            self.logger.error(message, extra=extra_data)
        elif severity == ErrorSeverity.WARNING:
            self.logger.warning(message, extra=extra_data)
        else:
            self.logger.info(message, extra=extra_data)
    
    def _update_error_statistics(self, error_info: Dict[str, Any]):
        """エラー統計を更新"""
        error_code = error_info['error_code']
        self.error_count[error_code] = self.error_count.get(error_code, 0) + 1
        
        # エラー履歴を保持
        self.last_errors.append(error_info)
        if len(self.last_errors) > self.max_error_history:
            self.last_errors.pop(0)
    
    def _show_user_message(self, error_info: Dict[str, Any]):
        """ユーザーにエラーメッセージを表示"""
        severity = error_info.get('severity', ErrorSeverity.ERROR)
        message = error_info['message']
        error_code = error_info['error_code']
        
        if severity == ErrorSeverity.CRITICAL:
            st.error(f"🚨 **重大なエラーが発生しました**\n\n{message}\n\n問題が解決しない場合は、システム管理者にお問い合わせください。\n\nエラーコード: {error_code}")
        elif severity == ErrorSeverity.ERROR:
            st.error(f"❌ **エラー**: {message}\n\nエラーコード: {error_code}")
        elif severity == ErrorSeverity.WARNING:
            st.warning(f"⚠️ **警告**: {message}")
        else:
            st.info(f"ℹ️ {message}")
    
    def safe_execute(self, func: Callable, *args, **kwargs) -> Any:
        """安全な関数実行"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.handle_error(e, {'function': func.__name__, 'args': str(args)})
            return None
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """エラー統計を取得"""
        total_errors = sum(self.error_count.values())
        recent_errors = [err for err in self.last_errors[-10:]]  # 最新10件
        
        return {
            'total_errors': total_errors,
            'error_by_type': self.error_count.copy(),
            'recent_errors': recent_errors,
            'most_common_error': max(self.error_count.items(), key=lambda x: x[1]) if self.error_count else None
        }


def error_boundary(error_handler: ErrorHandler = None, 
                  fallback_value: Any = None,
                  show_error: bool = True):
    """エラーバウンダリデコレータ"""
    handler = error_handler or ErrorHandler()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if show_error:
                    handler.handle_error(e, {
                        'function': func.__name__,
                        'args': str(args)[:100],  # 長すぎる引数は切り捨て
                        'kwargs': str(kwargs)[:100]
                    })
                return fallback_value
        return wrapper
    return decorator


def validate_input(validation_rules: Dict[str, Callable]):
    """入力検証デコレータ"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 引数名を取得
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # 検証実行
            for param_name, validator in validation_rules.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not validator(value):
                        raise DataValidationError(
                            f"Invalid value for parameter '{param_name}': {value}",
                            {'parameter': param_name, 'value': value}
                        )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# グローバルエラーハンドラ
global_error_handler = ErrorHandler()


# よく使用される検証関数
def is_positive_number(value: Any) -> bool:
    """正の数値かチェック"""
    try:
        return float(value) > 0
    except (ValueError, TypeError):
        return False


def is_non_negative_integer(value: Any) -> bool:
    """非負の整数かチェック"""
    try:
        num = int(value)
        return num >= 0
    except (ValueError, TypeError):
        return False


def is_valid_size(value: str) -> bool:
    """有効なサイズ名かチェック"""
    valid_sizes = ['S', 'Sロング', 'L', 'Lロング', 'LL']
    return value in valid_sizes


def is_valid_quantities(quantities: Dict[str, int]) -> bool:
    """有効な数量辞書かチェック"""
    if not isinstance(quantities, dict):
        return False
    
    for size, qty in quantities.items():
        if not is_valid_size(size) or not is_non_negative_integer(qty):
            return False
    
    return sum(quantities.values()) > 0


# カスタムStreamlitエラーハンドラ
def streamlit_error_boundary(func: Callable) -> Callable:
    """Streamlit専用エラーバウンダリ"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Streamlitセッション情報を含めてエラー処理
            context = {
                'function': func.__name__,
                'session_id': getattr(st.session_state, 'session_id', 'unknown'),
                'page': getattr(st.session_state, 'current_page', 'unknown')
            }
            global_error_handler.handle_error(e, context)
            
            # ユーザーには簡潔なメッセージを表示
            st.error("処理中にエラーが発生しました。しばらく待ってから再度お試しください。")
            return None
    return wrapper