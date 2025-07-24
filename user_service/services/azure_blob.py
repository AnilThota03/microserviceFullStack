async def upload_to_blob_storage(container, file, custom_name):
    # Stub for blob upload
    print(f"[BLOB] Uploading {file.filename} as {custom_name} to {container}")
    return f"https://dummy.blob.core.windows.net/{container}/{custom_name}"

async def delete_blob_from_url(url):
    # Stub for blob delete
    print(f"[BLOB] Deleting {url}")
    return True
