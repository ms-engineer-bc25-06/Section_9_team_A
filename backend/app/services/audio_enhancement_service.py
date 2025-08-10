import numpy as np
import librosa
from typing import Optional, Tuple, Dict, Any
import structlog
from datetime import datetime
import asyncio
from dataclasses import dataclass
from enum import Enum

logger = structlog.get_logger()


class EnhancementType(str, Enum):
    """音声品質向上の種類"""
    NOISE_REDUCTION = "noise_reduction"
    ECHO_CANCELLATION = "echo_cancellation"
    GAIN_CONTROL = "gain_control"
    SPECTRAL_ENHANCEMENT = "spectral_enhancement"


@dataclass
class EnhancementResult:
    """音声品質向上の結果"""
    enhanced_audio: bytes
    enhancement_type: EnhancementType
    quality_metrics: Dict[str, float]
    processing_time_ms: float
    timestamp: datetime


class AudioEnhancementService:
    """音声品質向上サービス"""
    
    def __init__(self):
        self.noise_profile: Optional[np.ndarray] = None
        self.echo_profile: Optional[np.ndarray] = None
        self.enhancement_history: Dict[str, EnhancementResult] = {}
        
        # 音声処理パラメータ
        self.noise_reduction_strength = 2.0
        self.echo_cancellation_strength = 0.8
        self.gain_boost_factor = 1.2
        
        # ノイズプロファイルの更新頻度
        self.noise_profile_update_interval = 10  # 秒
        self.last_noise_profile_update = datetime.now()
        
        logger.info("音声品質向上サービスを初期化しました")
    
    async def enhance_audio(
        self, 
        audio_data: bytes, 
        sample_rate: int = 16000,
        enhancement_types: list[EnhancementType] = None
    ) -> EnhancementResult:
        """音声品質向上のメイン処理"""
        start_time = datetime.now()
        
        if enhancement_types is None:
            enhancement_types = [EnhancementType.NOISE_REDUCTION, EnhancementType.ECHO_CANCELLATION]
        
        try:
            # バイトデータをnumpy配列に変換
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            audio_float = audio_array.astype(np.float32) / 32768.0
            
            enhanced_audio = audio_float.copy()
            quality_metrics = {}
            
            # 各品質向上処理を適用
            for enhancement_type in enhancement_types:
                if enhancement_type == EnhancementType.NOISE_REDUCTION:
                    enhanced_audio, noise_metrics = await self._remove_noise(enhanced_audio, sample_rate)
                    quality_metrics.update(noise_metrics)
                    
                elif enhancement_type == EnhancementType.ECHO_CANCELLATION:
                    enhanced_audio, echo_metrics = await self._cancel_echo(enhanced_audio, sample_rate)
                    quality_metrics.update(echo_metrics)
                    
                elif enhancement_type == EnhancementType.GAIN_CONTROL:
                    enhanced_audio, gain_metrics = await self._apply_gain_control(enhanced_audio)
                    quality_metrics.update(gain_metrics)
                    
                elif enhancement_type == EnhancementType.SPECTRAL_ENHANCEMENT:
                    enhanced_audio, spectral_metrics = await self._enhance_spectrum(enhanced_audio, sample_rate)
                    quality_metrics.update(spectral_metrics)
            
            # 音声レベルを正規化
            enhanced_audio = np.clip(enhanced_audio, -1.0, 1.0)
            
            # バイトデータに戻す
            enhanced_bytes = (enhanced_audio * 32768).astype(np.int16).tobytes()
            
            # 処理時間を計算
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # 結果を作成
            result = EnhancementResult(
                enhanced_audio=enhanced_bytes,
                enhancement_type=enhancement_types[0] if len(enhancement_types) == 1 else EnhancementType.NOISE_REDUCTION,
                quality_metrics=quality_metrics,
                processing_time_ms=processing_time,
                timestamp=datetime.now()
            )
            
            # 履歴に保存
            chunk_id = f"enhanced_{int(datetime.now().timestamp() * 1000)}"
            self.enhancement_history[chunk_id] = result
            
            logger.info(
                "音声品質向上完了",
                enhancement_types=[et.value for et in enhancement_types],
                processing_time_ms=processing_time,
                quality_metrics=quality_metrics
            )
            
            return result
            
        except Exception as e:
            logger.error(f"音声品質向上に失敗: {e}")
            # エラーの場合は元の音声データを返す
            return EnhancementResult(
                enhanced_audio=audio_data,
                enhancement_type=EnhancementType.NOISE_REDUCTION,
                quality_metrics={"error": 1.0},
                processing_time_ms=0.0,
                timestamp=datetime.now()
            )
    
    async def _remove_noise(self, audio: np.ndarray, sample_rate: int) -> Tuple[np.ndarray, Dict[str, float]]:
        """ノイズ除去処理"""
        try:
            # STFT（短時間フーリエ変換）
            stft = librosa.stft(audio, n_fft=1024, hop_length=256)
            
            # ノイズプロファイルの更新（定期的に）
            await self._update_noise_profile(audio, sample_rate)
            
            if self.noise_profile is not None:
                # スペクトルサブトラクションによるノイズ除去
                noise_subtracted = stft - self.noise_reduction_strength * self.noise_profile
                noise_subtracted = np.maximum(noise_subtracted, 0.1 * np.abs(stft))
                
                # ISTFT（逆短時間フーリエ変換）
                enhanced_audio = librosa.istft(noise_subtracted, hop_length=256)
                
                # 品質メトリクスを計算
                snr_before = self._calculate_snr(audio)
                snr_after = self._calculate_snr(enhanced_audio)
                noise_reduction_ratio = (snr_after - snr_before) / max(snr_before, 1e-10)
                
                metrics = {
                    "snr_before": snr_before,
                    "snr_after": snr_after,
                    "noise_reduction_ratio": noise_reduction_ratio,
                    "noise_profile_updated": self.noise_profile is not None
                }
                
                return enhanced_audio, metrics
            else:
                # ノイズプロファイルがない場合は元の音声を返す
                return audio, {"snr": self._calculate_snr(audio), "noise_reduction_applied": False}
                
        except Exception as e:
            logger.error(f"ノイズ除去に失敗: {e}")
            return audio, {"error": 1.0}
    
    async def _cancel_echo(self, audio: np.ndarray, sample_rate: int) -> Tuple[np.ndarray, Dict[str, float]]:
        """エコーキャンセル処理"""
        try:
            if self.echo_profile is not None:
                # エコー除去（簡易版）
                echo_cancelled = audio - self.echo_cancellation_strength * self.echo_profile[:len(audio)]
                echo_cancelled = np.clip(echo_cancelled, -1.0, 1.0)
                
                # 品質メトリクスを計算
                echo_reduction = np.mean(np.abs(audio - echo_cancelled))
                
                metrics = {
                    "echo_reduction": echo_reduction,
                    "echo_cancellation_applied": True
                }
                
                return echo_cancelled, metrics
            else:
                # エコープロファイルがない場合は元の音声を返す
                return audio, {"echo_cancellation_applied": False}
                
        except Exception as e:
            logger.error(f"エコーキャンセルに失敗: {e}")
            return audio, {"error": 1.0}
    
    async def _apply_gain_control(self, audio: np.ndarray) -> Tuple[np.ndarray, Dict[str, float]]:
        """ゲイン制御"""
        try:
            # 現在のRMSレベルを計算
            current_rms = np.sqrt(np.mean(audio**2))
            
            # 目標レベル（-12dB）
            target_rms = 0.25
            
            if current_rms > 0:
                # ゲイン調整係数を計算
                gain_factor = min(self.gain_boost_factor, target_rms / current_rms)
                
                # ゲインを適用
                enhanced_audio = audio * gain_factor
                
                metrics = {
                    "original_rms": current_rms,
                    "target_rms": target_rms,
                    "gain_factor": gain_factor,
                    "final_rms": np.sqrt(np.mean(enhanced_audio**2))
                }
                
                return enhanced_audio, metrics
            else:
                return audio, {"gain_control_applied": False}
                
        except Exception as e:
            logger.error(f"ゲイン制御に失敗: {e}")
            return audio, {"error": 1.0}
    
    async def _enhance_spectrum(self, audio: np.ndarray, sample_rate: int) -> Tuple[np.ndarray, Dict[str, float]]:
        """スペクトル強調"""
        try:
            # STFT
            stft = librosa.stft(audio, n_fft=1024, hop_length=256)
            
            # スペクトル強調（高周波成分を少し強調）
            frequencies = np.linspace(0, sample_rate/2, stft.shape[0])
            enhancement_filter = 1.0 + 0.3 * (frequencies / (sample_rate/2))
            enhancement_filter = np.clip(enhancement_filter, 0.5, 2.0)
            
            # フィルターを適用
            enhanced_stft = stft * enhancement_filter[:, np.newaxis]
            
            # ISTFT
            enhanced_audio = librosa.istft(enhanced_stft, hop_length=256)
            
            # 品質メトリクス
            high_freq_enhancement = np.mean(enhancement_filter)
            
            metrics = {
                "spectral_enhancement_factor": high_freq_enhancement,
                "spectral_enhancement_applied": True
            }
            
            return enhanced_audio, metrics
            
        except Exception as e:
            logger.error(f"スペクトル強調に失敗: {e}")
            return audio, {"error": 1.0}
    
    async def _update_noise_profile(self, audio: np.ndarray, sample_rate: int):
        """ノイズプロファイルを更新"""
        try:
            current_time = datetime.now()
            
            # 更新間隔をチェック
            if (current_time - self.last_noise_profile_update).total_seconds() < self.noise_profile_update_interval:
                return
            
            # 最初の1秒間をノイズとして扱う
            noise_samples = int(sample_rate)
            if len(audio) >= noise_samples:
                noise_segment = audio[:noise_samples]
                
                # STFT
                noise_stft = librosa.stft(noise_segment, n_fft=1024, hop_length=256)
                
                # ノイズプロファイルを更新
                if self.noise_profile is None:
                    self.noise_profile = np.mean(np.abs(noise_stft), axis=1, keepdims=True)
                else:
                    # 指数移動平均で更新
                    alpha = 0.1
                    self.noise_profile = alpha * np.mean(np.abs(noise_stft), axis=1, keepdims=True) + \
                                       (1 - alpha) * self.noise_profile
                
                self.last_noise_profile_update = current_time
                logger.debug("ノイズプロファイルを更新しました")
                
        except Exception as e:
            logger.error(f"ノイズプロファイル更新に失敗: {e}")
    
    def _calculate_snr(self, audio: np.ndarray) -> float:
        """SNR（Signal-to-Noise Ratio）を計算"""
        try:
            # 簡易的なSNR計算
            signal_power = np.mean(audio**2)
            noise_power = np.var(audio) * 0.1  # 簡易ノイズ推定
            
            if noise_power > 0:
                snr = 10 * np.log10(signal_power / noise_power)
                return max(snr, -20)  # -20dB以下は制限
            else:
                return 0.0
                
        except Exception:
            return 0.0
    
    def set_enhancement_parameters(self, **kwargs):
        """音声品質向上パラメータを設定"""
        if 'noise_reduction_strength' in kwargs:
            self.noise_reduction_strength = kwargs['noise_reduction_strength']
        if 'echo_cancellation_strength' in kwargs:
            self.echo_cancellation_strength = kwargs['echo_cancellation_strength']
        if 'gain_boost_factor' in kwargs:
            self.gain_boost_factor = kwargs['gain_boost_factor']
        
        logger.info(f"音声品質向上パラメータを更新: {kwargs}")
    
    def get_enhancement_stats(self) -> Dict[str, Any]:
        """音声品質向上の統計情報を取得"""
        if not self.enhancement_history:
            return {"total_processed": 0}
        
        total_processed = len(self.enhancement_history)
        avg_processing_time = np.mean([r.processing_time_ms for r in self.enhancement_history.values()])
        
        # 品質メトリクスの統計
        all_metrics = []
        for result in self.enhancement_history.values():
            if "error" not in result.quality_metrics:
                all_metrics.append(result.quality_metrics)
        
        if all_metrics:
            avg_snr_improvement = np.mean([m.get("noise_reduction_ratio", 0) for m in all_metrics])
            avg_echo_reduction = np.mean([m.get("echo_reduction", 0) for m in all_metrics])
        else:
            avg_snr_improvement = 0.0
            avg_echo_reduction = 0.0
        
        return {
            "total_processed": total_processed,
            "avg_processing_time_ms": avg_processing_time,
            "avg_snr_improvement": avg_snr_improvement,
            "avg_echo_reduction": avg_echo_reduction,
            "noise_profile_available": self.noise_profile is not None,
            "echo_profile_available": self.echo_profile is not None
        }
    
    def clear_history(self):
        """処理履歴をクリア"""
        self.enhancement_history.clear()
        logger.info("音声品質向上履歴をクリアしました")


# グローバルインスタンス
audio_enhancement_service = AudioEnhancementService()
