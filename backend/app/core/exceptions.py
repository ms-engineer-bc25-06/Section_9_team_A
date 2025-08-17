from typing import Any, Dict, Optional


class BridgeLineException(Exception):
    """BridgeLineアプリケーションの基底例外クラス"""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(BridgeLineException):
    """バリデーション例外"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "VALIDATION_ERROR", details)


class NotFoundException(BridgeLineException):
    """リソースが見つからない例外"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "NOT_FOUND", details)


class PermissionException(BridgeLineException):
    """権限不足例外"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "PERMISSION_DENIED", details)


class AuthenticationException(BridgeLineException):
    """認証失敗例外"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTHENTICATION_FAILED", details)


class DatabaseException(BridgeLineException):
    """データベース例外"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "DATABASE_ERROR", details)


class ExternalServiceException(BridgeLineException):
    """外部サービス例外"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", details)


class RateLimitException(BridgeLineException):
    """レート制限例外"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "RATE_LIMIT_EXCEEDED", details)


class ConfigurationException(BridgeLineException):
    """設定例外"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONFIGURATION_ERROR", details)


class AnalysisError(BridgeLineException):
    """AI分析処理例外"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "ANALYSIS_ERROR", details)


class PrivacyError(BridgeLineException):
    """プライバシー制御例外"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "PRIVACY_ERROR", details)


class AccessDeniedError(BridgeLineException):
    """データアクセス拒否例外"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "ACCESS_DENIED", details)


class BusinessLogicException(BridgeLineException):
    """ビジネスロジック例外"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "BUSINESS_LOGIC_ERROR", details)
