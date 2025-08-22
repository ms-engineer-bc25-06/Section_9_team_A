"""
音声処理機能のモジュール
"""
import io
import wave
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, BinaryIO
import librosa
import soundfile as sf
from pydub import AudioSegment
from app.utils.constants import AUDIO_QUALITY_SETTINGS, SupportedAudioFormats


class AudioProcessor:
    """音声処理クラス"""
    
    def __init__(self):
        self.supported_formats = [fmt.value for fmt in SupportedAudioFormats]
    
    async def process_audio(self, audio_data: Union[bytes, BinaryIO], 
                           input_format: str, output_format: str = "wav",
                           quality: str = "medium") -> bytes:
        """音声データを処理"""
        try:
            # 入力形式をチェック
            if input_format.lower() not in self.supported_formats:
                raise ValueError(f"サポートされていない入力形式: {input_format}")
            
            # 音声データを読み込み
            if isinstance(audio_data, bytes):
                audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format=input_format)
            else:
                audio_segment = AudioSegment.from_file(audio_data, format=input_format)
            
            # 品質設定を適用
            audio_segment = self._apply_quality_settings(audio_segment, quality)
            
            # 出力形式に変換
            output_buffer = io.BytesIO()
            audio_segment.export(output_buffer, format=output_format)
            
            return output_buffer.getvalue()
            
        except Exception as e:
            raise ValueError(f"音声処理に失敗しました: {str(e)}")
    
    def _apply_quality_settings(self, audio_segment: AudioSegment, quality: str) -> AudioSegment:
        """品質設定を適用"""
        if quality not in AUDIO_QUALITY_SETTINGS:
            quality = "medium"
        
        settings = AUDIO_QUALITY_SETTINGS[quality]
        
        # サンプリングレートを変更
        if audio_segment.frame_rate != settings["sample_rate"]:
            audio_segment = audio_segment.set_frame_rate(settings["sample_rate"])
        
        # チャンネル数を変更
        if audio_segment.channels != settings["channels"]:
            if settings["channels"] == 1:
                audio_segment = audio_segment.set_channels(1)
            else:
                audio_segment = audio_segment.set_channels(2)
        
        return audio_segment
    
    async def analyze_audio(self, audio_data: bytes, format: str = "wav") -> Dict[str, Union[float, int, str]]:
        """音声データを分析"""
        try:
            # 音声データを読み込み
            y, sr = librosa.load(io.BytesIO(audio_data), sr=None)
            
            # 基本情報
            duration = librosa.get_duration(y=y, sr=sr)
            sample_rate = sr
            channels = 1 if len(y.shape) == 1 else 2
            
            # 音量分析
            rms = np.sqrt(np.mean(y**2))
            db = 20 * np.log10(rms + 1e-10)
            
            # スペクトラム分析
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            
            # メルスペクトログラム
            mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr)
            mel_spectrogram_db = librosa.power_to_db(mel_spectrogram, ref=np.max)
            
            # ピッチ分析
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_values = pitches[magnitudes > 0.1]
            
            return {
                "duration": float(duration),
                "sample_rate": int(sample_rate),
                "channels": int(channels),
                "rms": float(rms),
                "db": float(db),
                "spectral_centroid_mean": float(np.mean(spectral_centroids)),
                "spectral_rolloff_mean": float(np.mean(spectral_rolloff)),
                "mel_spectrogram_shape": mel_spectrogram_db.shape,
                "pitch_mean": float(np.mean(pitch_values)) if len(pitch_values) > 0 else 0.0,
                "pitch_std": float(np.std(pitch_values)) if len(pitch_values) > 0 else 0.0
            }
            
        except Exception as e:
            raise ValueError(f"音声分析に失敗しました: {str(e)}")
    
    async def enhance_audio(self, audio_data: bytes, enhancement_type: str = "noise_reduction") -> bytes:
        """音声をエンハンス"""
        try:
            # 音声データを読み込み
            y, sr = librosa.load(io.BytesIO(audio_data), sr=None)
            
            if enhancement_type == "noise_reduction":
                # ノイズ除去
                y_enhanced = self._reduce_noise(y, sr)
            elif enhancement_type == "normalize":
                # 音量正規化
                y_enhanced = self._normalize_audio(y)
            elif enhancement_type == "filter":
                # フィルタリング
                y_enhanced = self._apply_filters(y, sr)
            else:
                y_enhanced = y
            
            # 音声データを出力
            output_buffer = io.BytesIO()
            sf.write(output_buffer, y_enhanced, sr, format='WAV')
            
            return output_buffer.getvalue()
            
        except Exception as e:
            raise ValueError(f"音声エンハンスに失敗しました: {str(e)}")
    
    def _reduce_noise(self, y: np.ndarray, sr: int) -> np.ndarray:
        """ノイズ除去"""
        # スペクトラムサブトラクション法
        stft = librosa.stft(y)
        magnitude = np.abs(stft)
        phase = np.angle(stft)
        
        # ノイズフロアを推定（最初の1秒間）
        noise_samples = int(sr * 1.0)
        noise_magnitude = np.mean(magnitude[:, :noise_samples], axis=1, keepdims=True)
        
        # スペクトラムサブトラクション
        alpha = 2.0  # 減算係数
        enhanced_magnitude = magnitude - alpha * noise_magnitude
        enhanced_magnitude = np.maximum(enhanced_magnitude, 0.1 * magnitude)
        
        # 逆STFT
        enhanced_stft = enhanced_magnitude * np.exp(1j * phase)
        y_enhanced = librosa.istft(enhanced_stft)
        
        return y_enhanced
    
    def _normalize_audio(self, y: np.ndarray) -> np.ndarray:
        """音量正規化"""
        # RMS正規化
        target_rms = 0.1
        current_rms = np.sqrt(np.mean(y**2))
        
        if current_rms > 0:
            gain = target_rms / current_rms
            y_normalized = y * gain
        else:
            y_normalized = y
        
        # クリッピング防止
        max_val = 0.95
        y_normalized = np.clip(y_normalized, -max_val, max_val)
        
        return y_normalized
    
    def _apply_filters(self, y: np.ndarray, sr: int) -> np.ndarray:
        """フィルタを適用"""
        # ハイパスフィルタ（低周波ノイズ除去）
        y_filtered = librosa.effects.preemphasis(y, coef=0.97)
        
        # ローパスフィルタ（高周波ノイズ除去）
        cutoff_freq = 8000  # 8kHz
        nyquist = sr / 2
        normalized_cutoff = cutoff_freq / nyquist
        
        # バターワースフィルタ
        from scipy import signal
        b, a = signal.butter(4, normalized_cutoff, btype='low')
        y_filtered = signal.filtfilt(b, a, y_filtered)
        
        return y_filtered
    
    async def split_audio(self, audio_data: bytes, segment_duration: float = 30.0) -> List[bytes]:
        """音声をセグメントに分割"""
        try:
            # 音声データを読み込み
            y, sr = librosa.load(io.BytesIO(audio_data), sr=None)
            
            # セグメント長をサンプル数に変換
            segment_samples = int(segment_duration * sr)
            
            segments = []
            for i in range(0, len(y), segment_samples):
                segment = y[i:i + segment_samples]
                
                # セグメントを出力
                output_buffer = io.BytesIO()
                sf.write(output_buffer, segment, sr, format='WAV')
                segments.append(output_buffer.getvalue())
            
            return segments
            
        except Exception as e:
            raise ValueError(f"音声分割に失敗しました: {str(e)}")
    
    async def merge_audio(self, audio_segments: List[bytes]) -> bytes:
        """音声セグメントを結合"""
        try:
            if not audio_segments:
                raise ValueError("音声セグメントが指定されていません")
            
            # 最初のセグメントからサンプリングレートを取得
            y_first, sr = librosa.load(io.BytesIO(audio_segments[0]), sr=None)
            merged_audio = y_first
            
            # 残りのセグメントを結合
            for segment_data in audio_segments[1:]:
                y_segment, _ = librosa.load(io.BytesIO(segment_data), sr=sr)
                merged_audio = np.concatenate([merged_audio, y_segment])
            
            # 結合された音声を出力
            output_buffer = io.BytesIO()
            sf.write(output_buffer, merged_audio, sr, format='WAV')
            
            return output_buffer.getvalue()
            
        except Exception as e:
            raise ValueError(f"音声結合に失敗しました: {str(e)}")
    
    async def get_audio_info(self, audio_data: bytes, format: str = "wav") -> Dict[str, Union[str, int, float]]:
        """音声ファイルの基本情報を取得"""
        try:
            # 音声データを読み込み
            y, sr = librosa.load(io.BytesIO(audio_data), sr=None)
            
            # 基本情報
            duration = librosa.get_duration(y=y, sr=sr)
            channels = 1 if len(y.shape) == 1 else 2
            samples = len(y)
            
            # ファイルサイズ（概算）
            file_size = len(audio_data)
            
            return {
                "format": format,
                "duration_seconds": float(duration),
                "duration_formatted": self._format_duration(duration),
                "sample_rate": int(sr),
                "channels": int(channels),
                "samples": int(samples),
                "file_size_bytes": file_size,
                "file_size_formatted": self._format_file_size(file_size)
            }
            
        except Exception as e:
            raise ValueError(f"音声情報の取得に失敗しました: {str(e)}")
    
    def _format_duration(self, seconds: float) -> str:
        """時間をフォーマット"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def _format_file_size(self, size_bytes: int) -> str:
        """ファイルサイズをフォーマット"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}TB"


# シングルトンインスタンス
audio_processor = AudioProcessor()


async def process_audio_file(audio_data: bytes, input_format: str, 
                           output_format: str = "wav", quality: str = "medium") -> bytes:
    """音声ファイルを処理（簡易関数）"""
    return await audio_processor.process_audio(audio_data, input_format, output_format, quality)


async def analyze_audio_file(audio_data: bytes, format: str = "wav") -> Dict[str, Union[float, int, str]]:
    """音声ファイルを分析（簡易関数）"""
    return await audio_processor.analyze_audio(audio_data, format)


async def enhance_audio_file(audio_data: bytes, enhancement_type: str = "noise_reduction") -> bytes:
    """音声ファイルをエンハンス（簡易関数）"""
    return await audio_processor.enhance_audio(audio_data, enhancement_type)
