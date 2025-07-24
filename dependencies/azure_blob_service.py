# app/services/azure_blob.py
import os
from datetime import datetime
from typing import Union, Optional
from urllib.parse import urlparse

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import ContentSettings
from azure.storage.blob.aio import BlobServiceClient
from decouple import config
from fastapi import UploadFile

AZURE_CONTAINER = os.getenv("AZURE_BLOB_CONTAINER", "pdit")
blob_service_client = BlobServiceClient.from_connection_string(config("AZURE_STORAGE_CONNECTION_STRING")) 


def generate_blob_name(folder: str, original_filename: str, custom_name: str = None) -> str:
    """
    Generates a blob name with optional custom name and folder path.
    If custom_name is not provided, uses timestamped version of original_filename.
    """
    ext = os.path.splitext(original_filename)[-1]
    safe_name = custom_name or f"{int(datetime.utcnow().timestamp())}-{original_filename}"
    return f"{folder.strip('/')}/{safe_name}{ext}".replace(" ", "_")


# --- MODIFIED FUNCTION ---
async def upload_to_blob_storage(
    container_name: str,
    file_data: Union[UploadFile, bytes], # Can now be UploadFile or bytes
    custom_name: str,
    content_type: Optional[str] = None   # Required when file_data is bytes
) -> str:
    """
    Uploads a file to Azure Blob Storage.
    Can handle a FastAPI UploadFile object or raw bytes.
    """
    container_client = blob_service_client.get_container_client(container_name)
    try:
        await container_client.create_container()
    except ResourceExistsError:
        pass

    # --- New logic to handle both UploadFile and bytes ---
    if isinstance(file_data, UploadFile):
        # Existing workflow: get data and type from UploadFile object
        upload_data = file_data.file
        mime_type = file_data.content_type or 'application/octet-stream'
    elif isinstance(file_data, bytes):
        # New M2 workflow: use the provided bytes and content_type
        if not content_type:
            raise ValueError("content_type must be provided when uploading bytes.")
        upload_data = file_data
        mime_type = content_type
    else:
        raise TypeError("file_data must be an instance of UploadFile or bytes.")
    # --- End of new logic ---

    blob_name = custom_name.replace(" ", "_")
    blob_client = container_client.get_blob_client(blob_name)
    
    # Use the determined mime_type
    content_settings = ContentSettings(
        content_type=mime_type,
        content_disposition='inline'
    )
    
    # Upload the determined data
    await blob_client.upload_blob(upload_data, overwrite=True, content_settings=content_settings)

    return f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob_name}"


async def delete_blob_from_url(blob_url: str):
    """
    Deletes a blob using its public URL.
    """
    parsed_url = urlparse(blob_url)
    path_parts = parsed_url.path.lstrip("/").split("/", 1)

    if len(path_parts) != 2 or path_parts[0] != AZURE_CONTAINER:
        raise ValueError("Invalid blob URL: container not found or incorrect path.")

    container_name = path_parts[0]
    blob_path = path_parts[1]

    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_path)

    try:
        await blob_client.delete_blob()
        print(f"[AZURE] Deleted blob: {blob_path}")
    except Exception as e:
        print(f"[AZURE] Failed to delete blob: {blob_path}, Error: {e}")
        raise e