import os
from typing import Dict, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DatabaseConfig:
    """データベース設定"""
    host: str = "localhost"
    port: int = 5432
    database: str = "minoru_packing"
    username: str = "admin"
    password: str = ""
    pool_size: int = 5


@dataclass
class CacheConfig:
    """キャッシュ設定"""
    max_size: int = 1000
    default_ttl: int = 3600  # 1時間
    redis_url: str = None


@dataclass
class LoggingConfig:
    """ログ設定"""
    level: str = "INFO"
    log_dir: str = "logs"
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5
    structured_logs: bool = True


@dataclass
class SecurityConfig:
    """セキュリティ設定"""
    secret_key: str = ""
    max_upload_size: int = 10485760  # 10MB
    allowed_image_extensions: list = None
    rate_limit_per_minute: int = 60
    session_timeout: int = 3600  # 1時間


@dataclass
class PerformanceConfig:
    """パフォーマンス設定"""
    max_workers: int = 4
    calculation_timeout: int = 30  # 30秒
    enable_parallel_processing: bool = True
    enable_caching: bool = True


class Settings:
    """アプリケーション設定管理"""
    
    def __init__(self, environment: str = None):
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self.debug = self.environment == "development"
        self.is_production = self.environment == "production"
        
        # 設定を環境別に初期化
        self._load_config()
    
    def _load_config(self):
        """環境別設定を読み込み"""
        if self.environment == "production":
            self._load_production_config()
        elif self.environment == "staging":
            self._load_staging_config()
        else:
            self._load_development_config()
    
    def _load_development_config(self):
        """開発環境設定"""
        self.database = DatabaseConfig(
            host="localhost",
            database="minoru_packing_dev",
            username="dev_user",
            password=os.getenv("DB_PASSWORD", "dev_password")
        )
        
        self.cache = CacheConfig(
            max_size=100,
            default_ttl=600  # 10分
        )
        
        self.logging = LoggingConfig(
            level="DEBUG",
            log_dir="logs/dev"
        )
        
        self.security = SecurityConfig(
            secret_key=os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"),
            allowed_image_extensions=['.jpg', '.jpeg', '.png', '.bmp'],
            rate_limit_per_minute=120  # 開発時は緩く
        )
        
        self.performance = PerformanceConfig(
            max_workers=2,
            calculation_timeout=60  # 開発時は長めに
        )
    
    def _load_staging_config(self):
        """ステージング環境設定"""
        self.database = DatabaseConfig(
            host=os.getenv("DB_HOST", "staging-db"),
            database=os.getenv("DB_NAME", "minoru_packing_staging"),
            username=os.getenv("DB_USER", "staging_user"),
            password=os.getenv("DB_PASSWORD", "")
        )
        
        self.cache = CacheConfig(
            max_size=500,
            default_ttl=1800,  # 30分
            redis_url=os.getenv("REDIS_URL")
        )
        
        self.logging = LoggingConfig(
            level="INFO",
            log_dir="logs/staging"
        )
        
        self.security = SecurityConfig(
            secret_key=os.getenv("SECRET_KEY", ""),
            allowed_image_extensions=['.jpg', '.jpeg', '.png'],
            rate_limit_per_minute=80
        )
        
        self.performance = PerformanceConfig(
            max_workers=3,
            calculation_timeout=45
        )
    
    def _load_production_config(self):
        """本番環境設定"""
        self.database = DatabaseConfig(
            host=os.getenv("DB_HOST", ""),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", ""),
            username=os.getenv("DB_USER", ""),
            password=os.getenv("DB_PASSWORD", "")
        )
        
        self.cache = CacheConfig(
            max_size=2000,
            default_ttl=3600,  # 1時間
            redis_url=os.getenv("REDIS_URL")
        )
        
        self.logging = LoggingConfig(
            level="WARNING",
            log_dir=os.getenv("LOG_DIR", "/var/log/minoru-packing"),
            max_file_size=52428800,  # 50MB
            backup_count=10
        )
        
        self.security = SecurityConfig(
            secret_key=os.getenv("SECRET_KEY", ""),
            max_upload_size=5242880,  # 5MB（本番では小さく）
            allowed_image_extensions=['.jpg', '.jpeg', '.png'],
            rate_limit_per_minute=30  # 本番では厳しく
        )
        
        self.performance = PerformanceConfig(
            max_workers=int(os.getenv("MAX_WORKERS", "4")),
            calculation_timeout=20,  # 本番では短く
            enable_parallel_processing=True,
            enable_caching=True
        )
    
    def get_streamlit_config(self) -> Dict[str, Any]:
        """Streamlit用設定を取得"""
        return {
            'server': {
                'maxUploadSize': self.security.max_upload_size // (1024 * 1024),  # MB
                'enableCORS': self.environment != "production",
                'enableXsrfProtection': self.environment == "production"
            },
            'browser': {
                'gatherUsageStats': False
            },
            'theme': {
                'primaryColor': '#FF6B6B',
                'backgroundColor': '#FFFFFF',
                'secondaryBackgroundColor': '#F0F2F6',
                'textColor': '#262730'
            }
        }
    
    def validate_config(self) -> Dict[str, str]:
        """設定の妥当性をチェック"""
        errors = []
        
        # 必須設定のチェック
        if self.environment == "production":
            if not self.security.secret_key:
                errors.append("SECRET_KEY is required in production")
            
            if not self.database.password:
                errors.append("Database password is required in production")
        
        # セキュリティチェック
        if len(self.security.secret_key) < 32:
            errors.append("SECRET_KEY should be at least 32 characters long")
        
        # パフォーマンスチェック
        if self.performance.max_workers > 8:
            errors.append("MAX_WORKERS should not exceed 8 for stability")
        
        return errors


# グローバル設定インスタンス
settings = Settings()


# 環境変数から設定を更新する関数
def load_env_config():
    """環境変数から設定を再読み込み"""
    global settings
    environment = os.getenv("ENVIRONMENT", "development")
    settings = Settings(environment)
    
    # 設定検証
    errors = settings.validate_config()
    if errors:
        raise ValueError(f"Configuration errors: {'; '.join(errors)}")


# 設定値を安全に取得する関数
def get_setting(key: str, default: Any = None) -> Any:
    """設定値を安全に取得"""
    try:
        keys = key.split('.')
        value = settings
        
        for k in keys:
            value = getattr(value, k)
        
        return value
    except AttributeError:
        return default


# よく使用される設定値のショートカット
def is_production() -> bool:
    """本番環境かどうか"""
    return settings.environment == "production"


def is_debug() -> bool:
    """デバッグモードかどうか"""
    return settings.debug


def get_log_level() -> str:
    """ログレベルを取得"""
    return settings.logging.level


def get_max_workers() -> int:
    """最大ワーカー数を取得"""
    return settings.performance.max_workers