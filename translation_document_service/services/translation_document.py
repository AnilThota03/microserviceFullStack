import os
from datetime import datetime
from typing import Optional
import httpx
from translation_document_service.models.translation_document import get_document_collection
from translation_document_service.schemas.translation_document import DocumentOut, DocumentUpdate
from microBackend.dependencies.azure_blob_service import delete_blob_from_url, upload_to_blob_storage
from bson import ObjectId
from fastapi import HTTPException, UploadFile


async def create_document(
    name: str,
    type: str,
    is_translated: bool,
    project_id: str,
    file: UploadFile,
    user_id: str
):
    """
    Creates a document record and uploads the associated file to blob storage.
    """
    print("[SERVICE] create_document called")

    # 1. Construct the blob name (path in the container)
    ext = os.path.splitext(file.filename)[-1]
    custom_filename = f"original-documents/{name.strip().replace(' ', '_')}{ext}"

    # 2. Upload to Azure Blob Storage
    try:
        blob_url = await upload_to_blob_storage(
            container_name="pdit",
            file_data=file,  # Pass the entire UploadFile object
            custom_name=custom_filename,
            content_type=file.content_type # Pass content_type explicitly
        )
    except Exception as e:
        print(f"❌ Blob upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {e}")

    # 3. Insert metadata into MongoDB
    documents = get_document_collection()
    doc_dict = {
        "name": name,
        "type": type,
        "isTranslated": is_translated,
        "originalDocument": blob_url,
        "translatedDocument": None,
        "projectId": ObjectId(project_id),
        "userId": ObjectId(user_id),
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }

    result = await documents.insert_one(doc_dict)
    
    # 4. Prepare and return the response
    doc_dict["_id"] = str(result.inserted_id)
    doc_dict["projectId"] = str(doc_dict["projectId"])
    doc_dict["userId"] = str(doc_dict["userId"])

    return DocumentOut(**doc_dict)


async def get_documents_by_project_id(project_id: str):
    """
    Retrieves all documents associated with a specific project ID.
    """
    print(f"[SERVICE] get_documents_by_project_id called with project_id={project_id}")
    documents = get_document_collection()
    result = []

    cursor = documents.find({"projectId": ObjectId(project_id)})
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc["projectId"] = str(doc["projectId"])
        doc["userId"] = str(doc["userId"])
        result.append(DocumentOut(**doc))

    return result


async def get_document_by_id(document_id: str):
    """
    Retrieves a single document by its ID.
    """
    print(f"[SERVICE] get_document_by_id called with document_id={document_id}")
    documents = get_document_collection()
    doc = await documents.find_one({"_id": ObjectId(document_id)})

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Convert ObjectIds to strings for the response model
    doc["_id"] = str(doc["_id"])
    if "projectId" in doc and isinstance(doc["projectId"], ObjectId):
        doc["projectId"] = str(doc["projectId"])
    if "userId" in doc and isinstance(doc["userId"], ObjectId):
        doc["userId"] = str(doc["userId"])

    return DocumentOut.model_validate(doc)


async def update_document(document_id: str, document_update: DocumentUpdate):
    """
    Updates a document's metadata in the database.
    """
    print(f"[SERVICE] update_document called with document_id={document_id}")
    documents = get_document_collection()
    
    # Create update payload, excluding unset fields
    update_data = document_update.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided.")

    update_data["updatedAt"] = datetime.utcnow()

    updated_doc = await documents.find_one_and_update(
        {"_id": ObjectId(document_id)},
        {"$set": update_data},
        return_document=True
    )

    if not updated_doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Convert ObjectIds for the response
    updated_doc["_id"] = str(updated_doc["_id"])
    updated_doc["projectId"] = str(updated_doc["projectId"])
    updated_doc["userId"] = str(updated_doc["userId"])

    return DocumentOut(**updated_doc)


async def delete_document(document_id: str):
    """
    Deletes a document record and its associated file from blob storage.
    """
    print(f"[SERVICE] delete_document called with document_id={document_id}")
    documents = get_document_collection()
    doc_to_delete = await documents.find_one({"_id": ObjectId(document_id)})

    if not doc_to_delete:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete files from Azure Blob Storage if they exist
    if doc_to_delete.get("originalDocument"):
        await delete_blob_from_url(doc_to_delete["originalDocument"])
    if doc_to_delete.get("translatedDocument"):
        await delete_blob_from_url(doc_to_delete["translatedDocument"])

    # Delete the document from MongoDB
    await documents.delete_one({"_id": ObjectId(document_id)})
    return {"message": "Document and associated files deleted successfully"}


async def create_document_with_file(
    name: str,
    project_id: str,
    file: UploadFile,
    user_id: str,
    
    target_language: str
):
    """
    Handles the entire process of uploading a document for translation.
    It uploads the original file, creates a DB record, and triggers a
    background task for the translation API call.
    """
    print(f"[SERVICE] create_document_with_file called for user {user_id}")

    # 1. Construct a unique, clean filename for the blob
    ext = os.path.splitext(file.filename)[-1]
    base_name = name.strip().replace(' ', '_')
    blob_name = f"original-documents/{base_name}{ext}"

    file_bytes = await file.read()

    # 2. Upload the original file to Azure Blob Storage
    try:
        blob_url = await upload_to_blob_storage(
            container_name="pdit",
            file_data=file_bytes, 
            custom_name=blob_name,
            content_type=file.content_type
        )
    except Exception as e:
        print(f"❌ Blob upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {e}")

    # 3. Save document metadata to the database
    documents = get_document_collection()
    doc_dict = {
        "name": name,
        "type": file.content_type, # Type is derived from the file
        "isTranslated": False, # isTranslated is always False on creation
        "originalDocument": blob_url,
        "translatedDocument": None,
        "projectId": ObjectId(project_id),
        "userId": ObjectId(user_id),
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
        "sourceLanguage": None,
        "targetLanguage": target_language
    }

    result = await documents.insert_one(doc_dict)
    document_id = str(result.inserted_id)

    # 4. Trigger the translation API call as a background task
    import asyncio
    asyncio.create_task(call_translation_api(
        document_id=document_id,
        input_file_url=blob_url,
        
        target_language=target_language,
        original_filename_base=base_name,
        original_extension=ext
    ))

    # 5. Immediately return the created document info to the user
    doc_dict["_id"] = document_id
    doc_dict["projectId"] = str(doc_dict["projectId"])
    doc_dict["userId"] = str(doc_dict["userId"])
    
    return DocumentOut(**doc_dict)


async def call_translation_api(
    document_id: str,
    input_file_url: str,
   
    target_language: str,
    original_filename_base: str,
    original_extension: str
):
    """
    (Background Task) Calls the external translation service,
    and upon success, updates the document record with the translated file URL.
    """
    print(f"[BACKGROUND] Starting translation for document_id: {document_id}")
    
    translated_filename = f"{original_filename_base}{original_extension}"
    output_file_url = f"https://pradfassignment.blob.core.windows.net/pdit/translated-documents/{translated_filename}"
    translation_payload = {
        "input_file": input_file_url,
        "tgt_lang": target_language,
       
        "output_file": output_file_url
    }
    
    print(f"[BACKGROUND] Calling translation API with payload: {translation_payload}")
    
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                "http://20.55.73.107:6003/translate",
                json=translation_payload,
                headers={"Content-Type": "application/json"}
            )
        
        response.raise_for_status()

        translation_response = response.json()
        print(f"[BACKGROUND] Translation API response: {translation_response}")
        
        translated_file_url = translation_response.get("output_file")
        source_language = translation_response.get("src_lang")
        
        if translated_file_url:
            # --- MODIFIED: Pass the detected source language to the update function ---
            await update_document_with_translation(document_id, translated_file_url, source_language)
            print(f"[SUCCESS] Document {document_id} updated with translation: {translated_file_url}")
        else:
            print(f"[ERROR] 'output_file' not found in translation response for doc {document_id}: {translation_response}")


    except httpx.TimeoutException:
        print(f"[ERROR] Translation API call timed out for document {document_id}")
    except httpx.HTTPStatusError as e:
        print(f"[ERROR] Translation API failed with status {e.response.status_code} for doc {document_id}: {e.response.text}")
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred during translation for doc {document_id}: {e}")


async def update_document_with_translation(document_id: str, translated_file_url: str, source_language: str):
    """
    Updates a document record with the URL of the translated file and the detected source language.
    """
    documents = get_document_collection()
    
    # --- MODIFIED: Prepare update payload including the source language ---
    update_fields = {
        "translatedDocument": translated_file_url,
        "isTranslated": True,
        "updatedAt": datetime.utcnow()
    }
    if source_language:
        update_fields["sourceLanguage"] = source_language

    update_result = await documents.update_one(
        {"_id": ObjectId(document_id)},
        {"$set": update_fields}
    )
    
    if update_result.modified_count == 1:
        print(f"[SERVICE] Successfully updated document {document_id} in DB.")
    else:
        # This could happen if the document was deleted while translation was in progress
        print(f"[ERROR] Failed to find and update document {document_id} in DB.")



async def update_document_with_file(document_id: str, file: UploadFile, name: str = None):
    """
    Replaces a document's original file and optionally updates its name.
    """
    print(f"[SERVICE] update_document_with_file called for doc_id={document_id}")
    documents = get_document_collection()

    doc = await documents.find_one({"_id": ObjectId(document_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.get("originalDocument"):
        await delete_blob_from_url(doc["originalDocument"])

    ext = os.path.splitext(file.filename)[-1]
    safe_name = (name or doc.get("name", "untitled")).strip().replace(" ", "_")
    blob_path = f"original-documents/{safe_name}{ext}"
    
    blob_url = await upload_to_blob_storage(
        container_name="pdit",
        file_data=file,
        custom_name=blob_path,
        content_type=file.content_type
    )

    update_data = {
        "originalDocument": blob_url,
        "updatedAt": datetime.utcnow()
    }
    if name:
        update_data["name"] = name

    updated_doc = await documents.find_one_and_update(
        {"_id": ObjectId(document_id)},
        {"$set": update_data},
        return_document=True
    )

    updated_doc["_id"] = str(updated_doc["_id"])
    updated_doc["projectId"] = str(updated_doc["projectId"])
    updated_doc["userId"] = str(updated_doc["userId"])
    
    return DocumentOut.model_validate(updated_doc)