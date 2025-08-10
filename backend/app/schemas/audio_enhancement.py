from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class EnhancementType(str, Enum):
    """音声品質向上の種類"""
    NOISE_REDUCTION = "noise_reduction"
    ECHO_CANCELLATION = "echo_cancellation"
    GAIN_CONTROL = "gain_control"
    SPECTRAL_ENHANCEMENT = "spectral_enhancement"


class AudioEnhancementRequest(BaseModel):
    """音声品質向上リクエスト"""
    enhancement_types: Optional[List[EnhancementType]] = Field(
        default=[EnhancementType.NOISE_REDUCTION, EnhancementType.ECHO_CANCELLATION],
        description="適用する品質向上処理の種類"
    )
    sample_rate: int = Field(
        default=16000,
        ge=8000,
        le=48000,
        description="サンプリングレート（Hz）"
    )
    noise_reduction_strength: Optional[float] = Field(
        default=2.0,
        ge=0.1,
        le=5.0,
        description="ノイズ除去の強度"
    )
    echo_cancellation_strength: Optional[float] = Field(
        default=0.8,
        ge=0.1,
        le=1.0,
        description="エコーキャンセルの強度"
    )
    gain_boost_factor: Optional[float] = Field(
        default=1.2,
        ge=0.5,
        le=3.0,
        description="ゲインブースト係数"
    )


class AudioEnhancementResponse(BaseModel):
    """音声品質向上レスポンス"""
    message: str = Field(description="処理結果のメッセージ")
    enhancement_types: List[str] = Field(description="適用された品質向上処理の種類")
    quality_metrics: Dict[str, float] = Field(description="品質向上のメトリクス")
    processing_time_ms: float = Field(description="処理時間（ミリ秒）")
    original_file_size: int = Field(description="元ファイルサイズ（バイト）")
    enhanced_file_size: int = Field(description="処理後ファイルサイズ（バイト）")
    timestamp: datetime = Field(description="処理完了時刻")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EnhancementStatsResponse(BaseModel):
    """音声品質向上統計レスポンス"""
    total_processed: int = Field(description="総処理件数")
    avg_processing_time_ms: float = Field(description="平均処理時間（ミリ秒）")
    avg_snr_improvement: float = Field(description="平均SNR改善率")
    avg_echo_reduction: float = Field(description="平均エコー除去率")
    noise_profile_available: bool = Field(description="ノイズプロファイルの利用可能性")
    echo_profile_available: bool = Field(description="エコープロファイルの利用可能性")
    timestamp: datetime = Field(description="統計取得時刻")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EnhancementParameters(BaseModel):
    """音声品質向上パラメータ"""
    noise_reduction_strength: Optional[float] = Field(
        default=None,
        ge=0.1,
        le=5.0,
        description="ノイズ除去の強度"
    )
    echo_cancellation_strength: Optional[float] = Field(
        default=None,
        ge=0.1,
        le=1.0,
        description="エコーキャンセルの強度"
    )
    gain_boost_factor: Optional[float] = Field(
        default=None,
        ge=0.5,
        le=3.0,
        description="ゲインブースト係数"
    )


class QualityMetrics(BaseModel):
    """音声品質メトリクス"""
    snr_before: Optional[float] = Field(description="処理前SNR（dB）")
    snr_after: Optional[float] = Field(description="処理後SNR（dB）")
    noise_reduction_ratio: Optional[float] = Field(description="ノイズ除去率")
    echo_reduction: Optional[float] = Field(description="エコー除去率")
    original_rms: Optional[float] = Field(description="元音声のRMSレベル")
    target_rms: Optional[float] = Field(description="目標RMSレベル")
    gain_factor: Optional[float] = Field(description="適用されたゲイン係数")
    final_rms: Optional[float] = Field(description="最終RMSレベル")
    spectral_enhancement_factor: Optional[float] = Field(description="スペクトル強調係数")
    noise_profile_updated: Optional[bool] = Field(description="ノイズプロファイル更新状況")
    echo_cancellation_applied: Optional[bool] = Field(description="エコーキャンセル適用状況")
    gain_control_applied: Optional[bool] = Field(description="ゲイン制御適用状況")
    spectral_enhancement_applied: Optional[bool] = Field(description="スペクトル強調適用状況")
    error: Optional[float] = Field(description="エラーが発生した場合のフラグ")


class EnhancementHistoryItem(BaseModel):
    """音声品質向上履歴アイテム"""
    chunk_id: str = Field(description="音声チャンクID")
    enhancement_type: EnhancementType = Field(description="適用された品質向上処理の種類")
    quality_metrics: QualityMetrics = Field(description="品質向上のメトリクス")
    processing_time_ms: float = Field(description="処理時間（ミリ秒）")
    timestamp: datetime = Field(description="処理時刻")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EnhancementHistoryResponse(BaseModel):
    """音声品質向上履歴レスポンス"""
    items: List[EnhancementHistoryItem] = Field(description="履歴アイテムのリスト")
    total_count: int = Field(description="総履歴件数")
    timestamp: datetime = Field(description="履歴取得時刻")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
