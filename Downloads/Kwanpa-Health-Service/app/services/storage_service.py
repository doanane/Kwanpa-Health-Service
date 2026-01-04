import os
import shutil
import logging
from fastapi import UploadFile
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.use_azure = False
        self.container_name = settings.AZURE_STORAGE_CONTAINER
        self.blob_service_client = None

        if settings.AZURE_STORAGE_CONNECTION_STRING:
            try:
                from azure.storage.blob import BlobServiceClient
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    settings.AZURE_STORAGE_CONNECTION_STRING
                )
                self.use_azure = True
                logger.info("Azure Blob Storage initialized")
            except Exception as e:
                logger.warning(f"Failed to init Azure Storage: {e}. Using local storage.")

    async def upload_file(self, file: UploadFile, folder: str = "general") -> str:
        """
        Uploads file to Azure Blob or Local Storage.
        Returns the URL or relative path.
        """
        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1]
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_name = f"{folder}/{timestamp}_{file.filename}"

        if self.use_azure:
            try:
                blob_client = self.blob_service_client.get_blob_client(
                    container=self.container_name, blob=unique_name
                )
                file.file.seek(0)
                blob_client.upload_blob(file.file, overwrite=True)
                return blob_client.url
            except Exception as e:
                logger.error(f"Azure upload failed: {e}. Falling back to local.")
                # Fallthrough to local

        # Local Storage Fallback
        upload_dir = f"uploads/{folder}"
        os.makedirs(upload_dir, exist_ok=True)
        local_path = os.path.join(upload_dir, f"{timestamp}_{file.filename}")
        
        file.file.seek(0)
        with open(local_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Return URL path for frontend
        return f"/uploads/{folder}/{timestamp}_{file.filename}"

storage_service = StorageService()