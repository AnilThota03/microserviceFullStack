import base64
import os
import httpx
import asyncio
from datetime import datetime
from bson import ObjectId
from fastapi import UploadFile, HTTPException
from microBackend.dependencies.azure_blob_service import upload_to_blob_storage, delete_blob_from_url
from comparison_document_service.models.comparison_document import get_comparison_document_collection
from comparison_document_service.schemas.comparison_document import ComparisonDocumentUpdate, ComparisonDocumentOut

# --- M1 MODEL WORKFLOW ---
async def call_comparison_api_m1(document_id: str, original_file_url: str, modified_file_url: str, name: str):
    """
    Calls the external comparison API for model M1 and stores the comparison data.
    """
    print(f"[SERVICE] Starting M1 comparison for document_id: {document_id}")
    try:
        COMPARISON_API_URL = "http://20.55.73.107:6004/compare"
        payload = {"original_document": original_file_url, "modified_document": modified_file_url}
        
        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(COMPARISON_API_URL, json=payload)
            
            if response.status_code == 200:
                api_response = response.json()
                compared_url = api_response.get("output_file")
                
                # --- NEW: Extract the pages data from the response ---
                pages_data = api_response.get("pages") 
                
                if compared_url:
                    documents = get_comparison_document_collection()
                    
                    # --- NEW: Add comparisonData to the update payload ---
                    update_payload = {
                        "comparedDocument": compared_url,
                        "isCompared": True,
                        "comparisonData": pages_data, # Store the pages array
                        "updatedAt": datetime.utcnow()
                    }
                    
                    await documents.update_one(
                        {"_id": ObjectId(document_id)},
                        {"$set": update_payload}
                    )
                    print(f"🚀 [SERVICE] M1 Comparison successful. Updated document: {document_id}")
            else:
                print(f"[ERROR] M1 Comparison API failed for doc {document_id}: {response.text}")
    except Exception as e:
        print(f"[ERROR] An exception occurred during M1 comparison for doc {document_id}: {e}")

# --- M2 MODEL WORKFLOW ---

async def upload_m2_results_to_blob(name: str, pdf_data: dict) -> dict:
    """Helper to upload all three PDFs from the M2 API response concurrently."""
    safe_name = name.strip().replace(' ', '_')

    # Define blob paths for the new PDF files
    orig_blob_name = f"comparison/original/{safe_name}.pdf"
    mod_blob_name = f"comparison/modified/{safe_name}.pdf"
    comp_blob_name = f"comparison/compared/{safe_name}.pdf"

    # Create upload tasks to run in parallel
    upload_tasks = [
        upload_to_blob_storage("pdit", pdf_data["original_bytes"], orig_blob_name, "application/pdf"),
        upload_to_blob_storage("pdit", pdf_data["modified_bytes"], mod_blob_name, "application/pdf"),
        upload_to_blob_storage("pdit", pdf_data["compared_bytes"], comp_blob_name, "application/pdf")
    ]

    # Run tasks concurrently and gather results
    original_url, modified_url, compared_url = await asyncio.gather(*upload_tasks)

    return {
        "originalDocument": original_url,
        "modifiedDocument": modified_url,
        "comparedDocument": compared_url,
    }

async def call_and_process_m2_api(document_id: str, orig_content_bytes: bytes, orig_content_type: str, mod_content_bytes: bytes, mod_content_type: str, name: str):
    
    
    """Main background task for the M2 workflow."""
    print(f"[SERVICE] Starting M2 comparison for document_id: {document_id}")
    try:
        M2_API_URL = "http://localhost:5005/api/Compare/document"
        orig_b64 = base64.b64encode(orig_content_bytes).decode('utf-8')
        mod_b64 = base64.b64encode(mod_content_bytes).decode('utf-8')
        payload = [
            {"$content-type": orig_content_type, "$content": orig_b64},
            {"$content-type": mod_content_type, "$content": mod_b64}
        ]

        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(M2_API_URL, json=payload)

        if response.status_code == 200:
            api_response = response.json()
            
            # Decode all three PDFs from the API response
            pdf_data = {
                "original_bytes": base64.b64decode(api_response["data"][0]["$content"]),
                "modified_bytes": base64.b64decode(api_response["data"][1]["$content"]),
                "compared_bytes": base64.b64decode(api_response["data"][2]["$content"])
            }
            
            # Upload all PDFs to blob storage concurrently
            print(f"[SERVICE] Uploading 3 PDFs for M2 doc: {document_id}")
            doc_urls = await upload_m2_results_to_blob(name, pdf_data)
            
            # Update the placeholder document with all new URLs and data
            documents = get_comparison_document_collection()
            update_payload = {
                **doc_urls,
                "isCompared": True,
                "type": "pdf",  # Update type to pdf
                "updatedAt": datetime.utcnow()
            }
            await documents.update_one(
                {"_id": ObjectId(document_id)},
                {"$set": update_payload}
            )
            print(f"🚀 [SERVICE] M2 workflow complete. Updated document: {document_id}")
        else:
            print(f"[ERROR] M2 Comparison API failed for doc {document_id}: {response.text}")
    except Exception as e:
        print(f"[ERROR] An exception occurred during M2 workflow for doc {document_id}: {e}")

# --- MAIN DISPATCHER FUNCTION ---
async def create_comparison_document_with_files(
    name: str, original_file: UploadFile, modified_file: UploadFile,
    project_id: str, user_id: str, type: str, model: str = "m1"
):
    documents = get_comparison_document_collection()

    if model == "m2":
        # M2 Workflow: Create placeholder, respond, then process in background
        print("[SERVICE] M2 model selected. Creating placeholder document.")
        orig_content_bytes = await original_file.read()
        mod_content_bytes = await modified_file.read()

        # Insert a placeholder document with nulls for file URLs
        doc_dict = {
            "name": name, "originalDocument": None, "modifiedDocument": None, "comparedDocument": None,
            "isCompared": False, "model": model, "projectId": ObjectId(project_id),
            "type": type, "userId": ObjectId(user_id), "createdAt": datetime.utcnow(), "updatedAt": datetime.utcnow()
        }
        result = await documents.insert_one(doc_dict)
        
        # Trigger the full M2 workflow in the background
        asyncio.create_task(call_and_process_m2_api(
            document_id=str(result.inserted_id),
            orig_content_bytes=orig_content_bytes,
            orig_content_type=original_file.content_type,
            mod_content_bytes=mod_content_bytes,
            mod_content_type=modified_file.content_type,
            name=name
        ))
    else:
        # M1 Workflow: Upload first, create full record, then process comparison
        print("[SERVICE] M1 model selected. Uploading initial documents.")
        orig_content_bytes = await original_file.read()
        mod_content_bytes = await modified_file.read()

        orig_ext = os.path.splitext(original_file.filename)[-1].lower()
        orig_blob_name = f"comparison/original/{name.strip().replace(' ', '_')}{orig_ext}"
        orig_blob_url = await upload_to_blob_storage("pdit", orig_content_bytes, orig_blob_name, original_file.content_type)

        mod_ext = os.path.splitext(modified_file.filename)[-1].lower()
        mod_blob_name = f"comparison/modified/{name.strip().replace(' ', '_')}{mod_ext}"
        mod_blob_url = await upload_to_blob_storage("pdit", mod_content_bytes, mod_blob_name, modified_file.content_type)
        
        doc_dict = {
            "name": name, "originalDocument": orig_blob_url, "modifiedDocument": mod_blob_url, "comparedDocument": None,
            "isCompared": False, "model": model, "projectId": ObjectId(project_id),
            "type": type, "userId": ObjectId(user_id), "createdAt": datetime.utcnow(), "updatedAt": datetime.utcnow()
        }
        result = await documents.insert_one(doc_dict)

        # Trigger the M1 comparison in the background
        asyncio.create_task(call_comparison_api_m1(
            document_id=str(result.inserted_id),
            original_file_url=orig_blob_url,
            modified_file_url=mod_blob_url,
            name=name
        ))

    # For both models, prepare and send the immediate response
    doc_dict["_id"] = str(result.inserted_id)
    doc_dict["projectId"] = str(doc_dict["projectId"])
    doc_dict["userId"] = str(doc_dict["userId"])
    return ComparisonDocumentOut(**doc_dict)

# --- OTHER CRUD FUNCTIONS ---

async def get_comparison_document_by_id(document_id: str):
    documents = get_comparison_document_collection()
    doc = await documents.find_one({"_id": ObjectId(document_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="ComparisonDocument not found")
    doc["_id"] = str(doc["_id"])
    doc["projectId"] = str(doc["projectId"])
    doc["userId"] = str(doc["userId"])
    return ComparisonDocumentOut(**doc)

async def get_comparison_documents_by_project_id(project_id: str):
    documents = get_comparison_document_collection()
    result = []
    async for doc in documents.find({"projectId": ObjectId(project_id)}):
        doc["_id"] = str(doc["_id"])
        doc["projectId"] = str(doc["projectId"])
        doc["userId"] = str(doc["userId"])
        result.append(ComparisonDocumentOut(**doc))
    return result

async def update_comparison_document(document_id: str, data: ComparisonDocumentUpdate):
    documents = get_comparison_document_collection()
    update_data = {k: v for k, v in data.dict(exclude_unset=True).items()}
    update_data["updatedAt"] = datetime.utcnow()
    updated = await documents.find_one_and_update(
        {"_id": ObjectId(document_id)},
        {"$set": update_data},
        return_document=True
    )
    if not updated:
        raise HTTPException(status_code=404, detail="ComparisonDocument not found")
    updated["_id"] = str(updated["_id"])
    updated["projectId"] = str(updated["projectId"])
    updated["userId"] = str(updated["userId"])
    return ComparisonDocumentOut(**updated)

async def delete_comparison_document(document_id: str):
    documents = get_comparison_document_collection()
    doc = await documents.find_one({"_id": ObjectId(document_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="ComparisonDocument not found")
    
    # Optionally delete files from blob storage as well
    if doc.get("originalDocument"):
        await delete_blob_from_url(doc["originalDocument"])
    if doc.get("modifiedDocument"):
        await delete_blob_from_url(doc["modifiedDocument"])
    if doc.get("comparedDocument"):
        await delete_blob_from_url(doc["comparedDocument"])
        
    await documents.delete_one({"_id": ObjectId(document_id)})
    return {"message": "ComparisonDocument and associated files deleted successfully"}