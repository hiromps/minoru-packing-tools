import hashlib
import hmac
import secrets
import time
from typing import Dict, List, Optional, Any
import streamlit as st
from PIL import Image
import io
import logging
from src.config.settings import settings


class SecurityManager:
    """セキュリティ管理クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rate_limit_store = {}
        self.session_store = {}
    
    def validate_file_upload(self, uploaded_file) -> Dict[str, Any]:
        """ファイルアップロードの安全性検証"""
        result = {
            'is_valid': False,
            'error': None,
            'file_info': {}
        }
        
        try:
            # ファイルサイズチェック
            if uploaded_file.size > settings.security.max_upload_size:
                result['error'] = f"ファイルサイズが上限({settings.security.max_upload_size // (1024*1024)}MB)を超えています"
                return result
            
            # ファイル拡張子チェック
            file_extension = f".{uploaded_file.name.split('.')[-1].lower()}"
            if file_extension not in settings.security.allowed_image_extensions:
                result['error'] = f"対応していないファイル形式です。対応形式: {', '.join(settings.security.allowed_image_extensions)}"
                return result
            
            # ファイル内容の検証（画像として正常に読み込めるか）
            try:
                image = Image.open(uploaded_file)
                image.verify()  # 画像の整合性チェック
                
                # ファイルポインタをリセット
                uploaded_file.seek(0)
                
                # 画像情報を取得
                image = Image.open(uploaded_file)
                result['file_info'] = {
                    'format': image.format,
                    'size': image.size,
                    'mode': image.mode,
                    'filename': uploaded_file.name,
                    'file_size': uploaded_file.size
                }
                
                # 異常に大きな画像のチェック
                max_dimension = 4096
                if image.size[0] > max_dimension or image.size[1] > max_dimension:
                    result['error'] = f"画像サイズが大きすぎます（最大{max_dimension}×{max_dimension}ピクセル）"
                    return result
                
                # ファイルポインタをリセット
                uploaded_file.seek(0)
                
                result['is_valid'] = True
                self.logger.info(f"File upload validated: {uploaded_file.name}")
                
            except Exception as e:
                result['error'] = "有効な画像ファイルではありません"
                self.logger.warning(f"Invalid image file uploaded: {str(e)}")
                return result
            
        except Exception as e:
            result['error'] = "ファイル検証中にエラーが発生しました"
            self.logger.error(f"File validation error: {str(e)}")
        
        return result
    
    def check_rate_limit(self, identifier: str, action: str = "default") -> bool:
        """レート制限チェック"""
        current_time = time.time()
        key = f"{identifier}:{action}"
        
        # 古いエントリをクリーンアップ
        self._cleanup_rate_limit_store(current_time)
        
        if key not in self.rate_limit_store:
            self.rate_limit_store[key] = []
        
        # 過去1分間のリクエスト数をカウント
        recent_requests = [
            req_time for req_time in self.rate_limit_store[key]
            if current_time - req_time < 60
        ]
        
        # レート制限チェック
        if len(recent_requests) >= settings.security.rate_limit_per_minute:
            self.logger.warning(f"Rate limit exceeded for {identifier}")
            return False
        
        # 現在のリクエストを記録
        self.rate_limit_store[key] = recent_requests + [current_time]
        return True
    
    def _cleanup_rate_limit_store(self, current_time: float):
        """レート制限ストアの古いエントリを削除"""
        keys_to_remove = []
        
        for key, timestamps in self.rate_limit_store.items():
            # 1時間以上古いエントリは削除
            recent_timestamps = [
                ts for ts in timestamps
                if current_time - ts < 3600
            ]
            
            if recent_timestamps:
                self.rate_limit_store[key] = recent_timestamps
            else:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.rate_limit_store[key]
    
    def sanitize_input(self, data: Any) -> Any:
        """入力データのサニタイズ"""
        if isinstance(data, str):
            # HTMLタグの無効化
            data = data.replace('<', '&lt;').replace('>', '&gt;')
            # SQLインジェクション対策の基本的なフィルタリング
            dangerous_patterns = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_']
            for pattern in dangerous_patterns:
                data = data.replace(pattern, '')
            return data.strip()
        
        elif isinstance(data, dict):
            return {key: self.sanitize_input(value) for key, value in data.items()}
        
        elif isinstance(data, list):
            return [self.sanitize_input(item) for item in data]
        
        return data
    
    def generate_session_token(self) -> str:
        """セッショントークンを生成"""
        return secrets.token_urlsafe(32)
    
    def validate_session(self, token: str) -> bool:
        """セッショントークンの検証"""
        if not token or token not in self.session_store:
            return False
        
        session_data = self.session_store[token]
        current_time = time.time()
        
        # セッションタイムアウトチェック
        if current_time - session_data['created_at'] > settings.security.session_timeout:
            del self.session_store[token]
            return False
        
        # 最終アクセス時刻を更新
        session_data['last_access'] = current_time
        return True
    
    def create_session(self, user_data: Dict[str, Any] = None) -> str:
        """新しいセッションを作成"""
        token = self.generate_session_token()
        current_time = time.time()
        
        self.session_store[token] = {
            'created_at': current_time,
            'last_access': current_time,
            'user_data': user_data or {}
        }
        
        # 古いセッションをクリーンアップ
        self._cleanup_sessions(current_time)
        
        return token
    
    def _cleanup_sessions(self, current_time: float):
        """期限切れセッションの削除"""
        expired_tokens = []
        
        for token, session_data in self.session_store.items():
            if current_time - session_data['created_at'] > settings.security.session_timeout:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            del self.session_store[token]
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """セキュリティイベントのログ記録"""
        log_data = {
            'event_type': 'security_event',
            'security_event': event_type,
            'timestamp': time.time(),
            'session_id': getattr(st.session_state, 'session_id', 'unknown'),
            'details': details
        }
        
        self.logger.warning(f"Security event: {event_type}", extra=log_data)


class InputValidator:
    """入力検証クラス"""
    
    @staticmethod
    def validate_quantities(quantities: Dict[str, int]) -> Dict[str, Any]:
        """商品数量の検証"""
        result = {'is_valid': True, 'errors': []}
        
        if not isinstance(quantities, dict):
            result['is_valid'] = False
            result['errors'].append("数量データの形式が正しくありません")
            return result
        
        valid_sizes = ['S', 'Sロング', 'L', 'Lロング', 'LL']
        total_items = 0
        
        for size, qty in quantities.items():
            # サイズ名の検証
            if size not in valid_sizes:
                result['errors'].append(f"無効なサイズです: {size}")
                result['is_valid'] = False
            
            # 数量の検証
            if not isinstance(qty, int) or qty < 0:
                result['errors'].append(f"無効な数量です: {size} = {qty}")
                result['is_valid'] = False
            
            # 最大数量チェック
            if qty > 1000:
                result['errors'].append(f"数量が多すぎます: {size} = {qty}")
                result['is_valid'] = False
            
            total_items += qty
        
        # 総数量チェック
        if total_items == 0:
            result['errors'].append("少なくとも1つ以上の商品を入力してください")
            result['is_valid'] = False
        
        if total_items > 5000:
            result['errors'].append("商品の総数が多すぎます")
            result['is_valid'] = False
        
        return result
    
    @staticmethod
    def validate_calculation_input(data: Any) -> bool:
        """計算入力の検証"""
        # 基本的な型チェック
        if not isinstance(data, (dict, list, int, float, str)):
            return False
        
        # 再帰的な検証（辞書や配列の場合）
        if isinstance(data, dict):
            return all(InputValidator.validate_calculation_input(v) for v in data.values())
        elif isinstance(data, list):
            return all(InputValidator.validate_calculation_input(item) for item in data)
        
        return True


# CSRFトークン管理
class CSRFProtection:
    """CSRF攻撃対策"""
    
    def __init__(self):
        self.tokens = {}
    
    def generate_token(self, session_id: str) -> str:
        """CSRFトークンを生成"""
        token = secrets.token_urlsafe(32)
        self.tokens[session_id] = {
            'token': token,
            'created_at': time.time()
        }
        return token
    
    def validate_token(self, session_id: str, token: str) -> bool:
        """CSRFトークンを検証"""
        if session_id not in self.tokens:
            return False
        
        stored_data = self.tokens[session_id]
        
        # トークンの有効期限チェック（1時間）
        if time.time() - stored_data['created_at'] > 3600:
            del self.tokens[session_id]
            return False
        
        return hmac.compare_digest(stored_data['token'], token)


# グローバルインスタンス
security_manager = SecurityManager()
input_validator = InputValidator()
csrf_protection = CSRFProtection()


# Streamlit用セキュリティデコレータ
def require_valid_session(func):
    """有効なセッションを要求するデコレータ"""
    def wrapper(*args, **kwargs):
        # セッションIDの取得または生成
        if 'session_id' not in st.session_state:
            st.session_state.session_id = security_manager.create_session()
        
        # セッションの検証
        if not security_manager.validate_session(st.session_state.session_id):
            st.session_state.session_id = security_manager.create_session()
        
        return func(*args, **kwargs)
    
    return wrapper


def rate_limited(action: str = "default"):
    """レート制限デコレータ"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # クライアント識別子（簡易版）
            identifier = getattr(st.session_state, 'session_id', 'anonymous')
            
            if not security_manager.check_rate_limit(identifier, action):
                st.error("🚫 リクエストが多すぎます。しばらく待ってから再度お試しください。")
                st.stop()
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator