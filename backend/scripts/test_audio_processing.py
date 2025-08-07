#!/usr/bin/env python3
"""
音声処理機能テストスクリプト
音声データ処理、レベル計算、録音機能をテストします
"""

import asyncio
import base64
import numpy as np
import wave
import io
from datetime import datetime
from typing import List

from app.services.audio_processing_service import AudioProcessingService, AudioChunk
from app.schemas.websocket import AudioDataMessage


def generate_test_audio(
    duration_ms: int = 100, frequency: float = 440.0, amplitude: float = 0.5
) -> bytes:
    """テスト用音声データを生成"""
    sample_rate = 16000
    samples = int(sample_rate * duration_ms / 1000)

    # サイン波を生成
    t = np.linspace(0, duration_ms / 1000, samples, False)
    audio_data = amplitude * np.sin(2 * np.pi * frequency * t)

    # 16-bit整数に変換
    audio_int16 = (audio_data * 32767).astype(np.int16)

    return audio_int16.tobytes()


def generate_silence(duration_ms: int = 100) -> bytes:
    """無音データを生成"""
    sample_rate = 16000
    samples = int(sample_rate * duration_ms / 1000)

    # 無音データ
    audio_data = np.zeros(samples, dtype=np.int16)

    return audio_data.tobytes()


async def test_audio_processing():
    """音声処理機能のテスト"""
    print("🎵 音声処理機能テストを開始します")
    print("=" * 50)

    # 音声処理サービスを初期化
    audio_processor = AudioProcessingService()

    # テスト用セッションID
    session_id = "test-audio-session"
    user_id = 1

    try:
        # 1. 音声データ生成テスト
        print("📊 1. 音声データ生成テスト")

        # 440Hzの音声データ
        audio_data_440 = generate_test_audio(100, 440.0, 0.5)
        print(f"   ✅ 440Hz音声データ生成: {len(audio_data_440)} bytes")

        # 無音データ
        silence_data = generate_silence(100)
        print(f"   ✅ 無音データ生成: {len(silence_data)} bytes")

        # 2. 音声データ処理テスト
        print("\n📊 2. 音声データ処理テスト")

        # 440Hz音声データを処理
        audio_message_440 = AudioDataMessage(
            session_id=session_id,
            user_id=user_id,
            data=base64.b64encode(audio_data_440).decode(),
            timestamp=datetime.now().isoformat(),
            chunk_id="test_chunk_440",
            sample_rate=16000,
            channels=1,
        )

        chunk_440 = await audio_processor.process_audio_data(audio_message_440)
        print(f"   ✅ 440Hz音声データ処理完了: {chunk_440.chunk_id}")

        # 無音データを処理
        audio_message_silence = AudioDataMessage(
            session_id=session_id,
            user_id=user_id,
            data=base64.b64encode(silence_data).decode(),
            timestamp=datetime.now().isoformat(),
            chunk_id="test_chunk_silence",
            sample_rate=16000,
            channels=1,
        )

        chunk_silence = await audio_processor.process_audio_data(audio_message_silence)
        print(f"   ✅ 無音データ処理完了: {chunk_silence.chunk_id}")

        # 3. 音声レベル計算テスト
        print("\n📊 3. 音声レベル計算テスト")

        # 440Hz音声のレベル計算
        level_440 = audio_processor._calculate_audio_level(chunk_440)
        print(f"   📈 440Hz音声レベル: {level_440.level:.4f}")
        print(f"   🎤 話者検出: {level_440.is_speaking}")
        print(f"   📊 RMS: {level_440.rms:.4f}")
        print(f"   📊 ピーク: {level_440.peak:.4f}")

        # 無音のレベル計算
        level_silence = audio_processor._calculate_audio_level(chunk_silence)
        print(f"   📈 無音レベル: {level_silence.level:.4f}")
        print(f"   🎤 話者検出: {level_silence.is_speaking}")
        print(f"   📊 RMS: {level_silence.rms:.4f}")
        print(f"   📊 ピーク: {level_silence.peak:.4f}")

        # 4. 録音機能テスト
        print("\n📊 4. 録音機能テスト")

        # 録音開始
        await audio_processor.start_recording(session_id)
        print("   ✅ 録音開始")

        # 録音中に音声データを処理
        for i in range(5):
            audio_data = generate_test_audio(100, 440.0 + i * 100, 0.3)
            audio_message = AudioDataMessage(
                session_id=session_id,
                user_id=user_id,
                data=base64.b64encode(audio_data).decode(),
                timestamp=datetime.now().isoformat(),
                chunk_id=f"recording_chunk_{i}",
                sample_rate=16000,
                channels=1,
            )

            chunk = await audio_processor.process_audio_data(audio_message)
            print(f"   📝 録音チャンク {i + 1}: {chunk.chunk_id}")

        # 録音停止
        await audio_processor.stop_recording(session_id)
        print("   ✅ 録音停止")

        # 5. 音声レベル履歴テスト
        print("\n📊 5. 音声レベル履歴テスト")

        levels = await audio_processor.get_session_audio_levels(session_id, user_id)
        print(f"   📈 音声レベル履歴: {len(levels)} 件")

        for i, level in enumerate(levels):
            print(
                f"      {i + 1}. レベル: {level.level:.4f}, 話者: {level.is_speaking}"
            )

        # 6. 参加者音声レベルテスト
        print("\n📊 6. 参加者音声レベルテスト")

        participant_levels = (
            await audio_processor.get_session_participants_audio_levels(session_id)
        )
        print(f"   👥 参加者数: {len(participant_levels)}")

        for user_id, level in participant_levels.items():
            print(
                f"      👤 ユーザー {user_id}: レベル {level.level:.4f}, 話者 {level.is_speaking}"
            )

        # 7. 音声フォーマット変換テスト
        print("\n📊 7. 音声フォーマット変換テスト")

        # RAW → WAV変換
        raw_data = generate_test_audio(100, 440.0, 0.5)
        wav_data = audio_processor.convert_audio_format(raw_data, "raw", "wav", 16000)
        print(f"   ✅ RAW → WAV変換: {len(raw_data)} → {len(wav_data)} bytes")

        # WAV → RAW変換
        raw_data_converted = audio_processor.convert_audio_format(
            wav_data, "wav", "raw"
        )
        print(f"   ✅ WAV → RAW変換: {len(wav_data)} → {len(raw_data_converted)} bytes")

        # 8. バッファクリアテスト
        print("\n📊 8. バッファクリアテスト")

        await audio_processor.clear_session_buffer(session_id)
        print("   ✅ 音声バッファをクリアしました")

        # クリア後の状態確認
        levels_after_clear = await audio_processor.get_session_audio_levels(
            session_id, user_id
        )
        print(f"   📊 クリア後のレベル数: {len(levels_after_clear)}")

        print("\n✅ 音声処理機能テスト完了")

    except Exception as e:
        print(f"\n❌ テストエラー: {e}")
        raise


async def test_multiple_users():
    """複数ユーザーの音声処理テスト"""
    print("\n👥 複数ユーザー音声処理テスト")
    print("=" * 50)

    audio_processor = AudioProcessingService()
    session_id = "test-multi-user-session"

    try:
        # 3人のユーザーが音声を送信
        for user_id in range(1, 4):
            # 各ユーザーが異なる周波数の音声を送信
            frequency = 440.0 + (user_id - 1) * 100
            audio_data = generate_test_audio(100, frequency, 0.3)

            audio_message = AudioDataMessage(
                session_id=session_id,
                user_id=user_id,
                data=base64.b64encode(audio_data).decode(),
                timestamp=datetime.now().isoformat(),
                chunk_id=f"multi_user_chunk_{user_id}",
                sample_rate=16000,
                channels=1,
            )

            chunk = await audio_processor.process_audio_data(audio_message)
            level = audio_processor._calculate_audio_level(chunk)

            print(
                f"👤 ユーザー {user_id}: 周波数 {frequency}Hz, レベル {level.level:.4f}"
            )

        # 全参加者の音声レベルを取得
        participant_levels = (
            await audio_processor.get_session_participants_audio_levels(session_id)
        )
        print(f"\n📊 参加者音声レベル:")

        for user_id, level in participant_levels.items():
            print(
                f"   👤 ユーザー {user_id}: レベル {level.level:.4f}, 話者 {level.is_speaking}"
            )

        print("✅ 複数ユーザーテスト完了")

    except Exception as e:
        print(f"❌ 複数ユーザーテストエラー: {e}")


if __name__ == "__main__":
    print("🚀 音声処理テストを開始します")

    # 単一ユーザーテスト
    asyncio.run(test_audio_processing())

    # 複数ユーザーテスト
    asyncio.run(test_multiple_users())

    print("\n🎉 全てのテストが完了しました")
