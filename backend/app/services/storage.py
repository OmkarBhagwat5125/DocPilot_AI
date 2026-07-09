import logging
from supabase import create_client, Client
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        # Use service role key to have full storage administrative access
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
        self.bucket_name = "documents"
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            # Check if bucket exists, if not create it
            buckets = self.supabase.storage.list_buckets()
            exists = any(b.name == self.bucket_name for b in buckets)
            if not exists:
                logger.info(f"Creating storage bucket '{self.bucket_name}'...")
                self.supabase.storage.create_bucket(self.bucket_name, options={"public": False})
        except Exception as e:
            logger.warning(f"Could not verify/create bucket '{self.bucket_name}': {str(e)}")

    def upload_file(self, user_id: str, filename: str, file_content: bytes) -> str:
        file_path = f"{user_id}/{filename}"
        try:
            logger.info(f"Uploading file {filename} to Supabase storage path: {file_path}")
            # Upload using upsert to overwrite files with the same name
            self.supabase.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=file_content,
                file_options={"upsert": "true", "contentType": "application/octet-stream"}
            )
            return file_path
        except Exception as e:
            logger.error(f"Failed to upload file {filename} to storage: {str(e)}")
            raise e

    def download_file(self, user_id: str, filename: str) -> bytes:
        file_path = f"{user_id}/{filename}"
        try:
            logger.info(f"Downloading file {filename} from Supabase storage path: {file_path}")
            content = self.supabase.storage.from_(self.bucket_name).download(file_path)
            return content
        except Exception as e:
            logger.error(f"Failed to download file {filename} from storage: {str(e)}")
            raise e

    def list_files(self, user_id: str) -> list[dict]:
        try:
            logger.info(f"Listing storage files for user: {user_id}")
            # List files inside the user's subfolder
            res = self.supabase.storage.from_(self.bucket_name).list(path=user_id)
            files = []
            for item in res:
                # Filter out folder structures if any, and map to clean dict
                if item.get("name") and item["name"] != ".emptyFolderPlaceholder":
                    files.append({
                        "name": item["name"],
                        "id": item.get("id"),
                        "size": item.get("metadata", {}).get("size", 0),
                        "created_at": item.get("created_at")
                    })
            return files
        except Exception as e:
            logger.error(f"Failed to list files for user {user_id}: {str(e)}")
            return []

    def delete_file(self, user_id: str, filename: str) -> bool:
        file_path = f"{user_id}/{filename}"
        try:
            logger.info(f"Deleting file {filename} from Supabase storage path: {file_path}")
            self.supabase.storage.from_(self.bucket_name).remove([file_path])
            return True
        except Exception as e:
            logger.error(f"Failed to delete file {filename} from storage: {str(e)}")
            return False
object_storage = StorageService()
