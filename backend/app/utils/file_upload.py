"""
ファイルアップロード機能のモジュール
"""
import os
import hashlib
import mimetypes
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import aiofiles
from fastapi import UploadFile, HTTPException
from app.utils.constants import FileType, MAX_FILE_SIZE, SupportedAudioFormats, SupportedVideoFormats, SupportedDocumentFormats


class FileUploadManager:
    """ファイルアップロード管理クラス"""
    
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
        
        # ファイルタイプ別のディレクトリを作成
        for file_type in FileType:
            (self.upload_dir / file_type.value).mkdir(exist_ok=True)
    
    async def save_file(self, file: UploadFile, file_type: FileType, 
                       user_id: str, session_id: Optional[str] = None) -> Dict[str, str]:
        """ファイルを保存"""
        try:
            # ファイルサイズをチェック
            await self._validate_file_size(file, file_type)
            
            # ファイル形式をチェック
            await self._validate_file_format(file, file_type)
            
            # ファイル名を生成
            filename = await self._generate_filename(file, user_id, session_id)
            
            # 保存パスを決定
            save_path = self._get_save_path(filename, file_type, user_id, session_id)
            
            # ファイルを保存
            await self._save_file_to_disk(file, save_path)
            
            # ファイル情報を返す
            return {
                "filename": filename,
                "original_name": file.filename,
                "file_path": str(save_path),
                "file_type": file_type.value,
                "size": save_path.stat().st_size,
                "mime_type": file.content_type or "application/octet-stream",
                "uploaded_at": str(save_path.stat().st_mtime)
            }
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"ファイルアップロードに失敗しました: {str(e)}")
    
    async def _validate_file_size(self, file: UploadFile, file_type: FileType) -> None:
        """ファイルサイズを検証"""
        # ファイルサイズを取得
        file.seek(0, 2)  # ファイルの末尾に移動
        file_size = file.tell()
        file.seek(0)  # ファイルの先頭に戻す
        
        max_size = MAX_FILE_SIZE.get(file_type, MAX_FILE_SIZE[FileType.OTHER])
        
        if file_size > max_size:
            raise ValueError(f"ファイルサイズが制限を超えています。最大: {self._format_size(max_size)}")
    
    async def _validate_file_format(self, file: UploadFile, file_type: FileType) -> None:
        """ファイル形式を検証"""
        if not file.filename:
            raise ValueError("ファイル名が指定されていません")
        
        file_ext = Path(file.filename).suffix.lower().lstrip('.')
        
        if file_type == FileType.AUDIO:
            if file_ext not in [fmt.value for fmt in SupportedAudioFormats]:
                raise ValueError(f"サポートされていない音声形式です: {file_ext}")
        elif file_type == FileType.VIDEO:
            if file_ext not in [fmt.value for fmt in SupportedVideoFormats]:
                raise ValueError(f"サポートされていない動画形式です: {file_ext}")
        elif file_type == FileType.DOCUMENT:
            if file_ext not in [fmt.value for fmt in SupportedDocumentFormats]:
                raise ValueError(f"サポートされていない文書形式です: {file_ext}")
    
    async def _generate_filename(self, file: UploadFile, user_id: str, 
                                session_id: Optional[str] = None) -> str:
        """ファイル名を生成"""
        # 元のファイル名から拡張子を取得
        original_name = file.filename or "unknown"
        file_ext = Path(original_name).suffix
        
        # ユニークなファイル名を生成
        timestamp = str(int(os.path.getmtime(file.file.name) if hasattr(file.file, 'name') else 0))
        hash_input = f"{user_id}_{session_id or 'no_session'}_{timestamp}_{original_name}"
        file_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        
        return f"{timestamp}_{file_hash}{file_ext}"
    
    def _get_save_path(self, filename: str, file_type: FileType, 
                       user_id: str, session_id: Optional[str] = None) -> Path:
        """保存パスを取得"""
        # ユーザー別ディレクトリ
        user_dir = self.upload_dir / file_type.value / user_id
        user_dir.mkdir(exist_ok=True)
        
        # セッション別ディレクトリ（指定されている場合）
        if session_id:
            session_dir = user_dir / session_id
            session_dir.mkdir(exist_ok=True)
            return session_dir / filename
        else:
            return user_dir / filename
    
    async def _save_file_to_disk(self, file: UploadFile, save_path: Path) -> None:
        """ファイルをディスクに保存"""
        async with aiofiles.open(save_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
    
    def _format_size(self, size_bytes: int) -> str:
        """ファイルサイズを人間が読みやすい形式に変換"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}TB"
    
    async def delete_file(self, file_path: str) -> bool:
        """ファイルを削除"""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception:
            return False
    
    async def get_file_info(self, file_path: str) -> Optional[Dict[str, str]]:
        """ファイル情報を取得"""
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            stat = path.stat()
            return {
                "filename": path.name,
                "file_path": str(path),
                "size": stat.st_size,
                "created_at": str(stat.st_ctime),
                "modified_at": str(stat.st_mtime),
                "mime_type": mimetypes.guess_type(str(path))[0] or "application/octet-stream"
            }
        except Exception:
            return None
    
    async def list_user_files(self, user_id: str, file_type: Optional[FileType] = None) -> List[Dict[str, str]]:
        """ユーザーのファイル一覧を取得"""
        files = []
        
        if file_type:
            user_dir = self.upload_dir / file_type.value / user_id
            if user_dir.exists():
                files.extend(await self._scan_directory(user_dir, user_id))
        else:
            for ft in FileType:
                user_dir = self.upload_dir / ft.value / user_id
                if user_dir.exists():
                    files.extend(await self._scan_directory(user_dir, user_id))
        
        return files
    
    async def _scan_directory(self, directory: Path, user_id: str) -> List[Dict[str, str]]:
        """ディレクトリをスキャンしてファイル情報を取得"""
        files = []
        
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "filename": file_path.name,
                    "file_path": str(file_path),
                    "relative_path": str(file_path.relative_to(self.upload_dir)),
                    "size": stat.st_size,
                    "created_at": str(stat.st_ctime),
                    "modified_at": str(stat.st_mtime),
                    "mime_type": mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
                })
        
        return files
    
    def get_upload_directory(self) -> str:
        """アップロードディレクトリのパスを取得"""
        return str(self.upload_dir.absolute())
    
    async def cleanup_old_files(self, max_age_days: int = 30) -> int:
        """古いファイルをクリーンアップ"""
        import time
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 3600
        deleted_count = 0
        
        for file_path in self.upload_dir.rglob('*'):
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                    except Exception:
                        continue
        
        return deleted_count


# シングルトンインスタンス
file_upload_manager = FileUploadManager()


async def upload_file(file: UploadFile, file_type: FileType, 
                     user_id: str, session_id: Optional[str] = None) -> Dict[str, str]:
    """ファイルをアップロード（簡易関数）"""
    return await file_upload_manager.save_file(file, file_type, user_id, session_id)


async def delete_uploaded_file(file_path: str) -> bool:
    """アップロードされたファイルを削除（簡易関数）"""
    return await file_upload_manager.delete_file(file_path)


async def get_uploaded_file_info(file_path: str) -> Optional[Dict[str, str]]:
    """アップロードされたファイルの情報を取得（簡易関数）"""
    return await file_upload_manager.get_file_info(file_path)
