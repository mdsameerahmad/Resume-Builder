from typing import BinaryIO, Optional
from supabase import create_client, Client
from app.core.config import settings
from .storage_service import StorageService
from loguru import logger

class SupabaseStorage(StorageService):
    def __init__(self, bucket_name: str = "resume-upload"):
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.bucket_name = bucket_name
        # Try to create bucket if it doesn't exist (only works with Service Role key)
        try:
            self.supabase.storage.create_bucket(self.bucket_name, options={"public": True})
            logger.info(f"Created Supabase bucket: {self.bucket_name}")
        except Exception as e:
            # If bucket already exists or key doesn't have permissions, this might fail silently
            logger.debug(f"Bucket check/creation status: {e}")

    async def upload_file(self, file: BinaryIO, file_name: str, folder: Optional[str] = None) -> str:
        path = f"{folder}/{file_name}" if folder else file_name
        
        try:
            # Ensure file pointer is at the start
            file.seek(0)
            content = file.read()
            
            # The Supabase SDK upload returns a response object or dict
            response = self.supabase.storage.from_(self.bucket_name).upload(
                path=path,
                file=content,
                file_options={"content-type": "application/pdf" if path.endswith(".pdf") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
            )
            
            # Check for error in dict response (common in some versions)
            if isinstance(response, dict) and "error" in response:
                logger.error(f"Supabase upload error: {response}")
                raise Exception(f"Upload failed: {response['error']}")
                
            return await self.get_public_url(path)
        except Exception as e:
            logger.error(f"Error uploading to Supabase: {e}")
            raise

    async def delete_file(self, file_path: str) -> bool:
        try:
            self.supabase.storage.from_(self.bucket_name).remove([file_path])
            return True
        except Exception as e:
            logger.error(f"Error deleting from Supabase: {e}")
            return False

    async def get_public_url(self, file_path: str) -> str:
        try:
            res = self.supabase.storage.from_(self.bucket_name).get_public_url(file_path)
            # Handle both string and object responses
            if hasattr(res, 'public_url'):
                return res.public_url
            return str(res)
        except Exception as e:
            logger.error(f"Error getting public URL: {e}")
            raise

    async def file_exists(self, file_path: str) -> bool:
        try:
            # list files in the directory of file_path
            folder = "/".join(file_path.split("/")[:-1])
            name = file_path.split("/")[-1]
            files = self.supabase.storage.from_(self.bucket_name).list(folder)
            return any(f['name'] == name for f in files)
        except Exception:
            return False
