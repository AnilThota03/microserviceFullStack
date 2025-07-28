import logging
from typing import List
from fastapi import APIRouter, File, Form, HTTPException, status, UploadFile
from comparison_document_service.schemas.comparison_document import ComparisonDocumentListOut, ComparisonDocumentOut, ComparisonDocumentUpdate
from comparison_document_service.services.comparison_document import (
    create_comparison_document_with_files,
    delete_comparison_document,
    get_comparison_document_by_id,
    get_comparison_documents_by_project_id,
    update_comparison_document
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/comparison-document/api/document",
    tags=["ComparisonDocument"]
)

@router.post("/", response_model=ComparisonDocumentOut, status_code=status.HTTP_201_CREATED)
async def create(
    name: str = Form(...),
    original_file: UploadFile = File(...),
    modified_file: UploadFile = File(...),
    project_id: str = Form(...),
    user_id: str = Form(...),
    type: str = Form(...),
    model: str = Form(None)
):
    logger.debug(f"[create] Called with name={name}, project_id={project_id}, user_id={user_id}, type={type}, model={model}")
    try:
        result = await create_comparison_document_with_files(
            name=name,
            original_file=original_file,
            modified_file=modified_file,
            project_id=project_id,
            user_id=user_id,
            type=type,
            model=model
        )
        logger.info(f"[create] Successfully created comparison document with ID: {getattr(result, 'id', 'N/A')}")
        return result
    except Exception as e:
        logger.error(f"[create] Failed to create comparison document '{name}': {e}")
        raise

@router.get("/{document_id}", response_model=ComparisonDocumentOut)
async def get_by_id(document_id: str):
    logger.debug(f"[get_by_id] Called with document_id={document_id}")
    try:
        result = await get_comparison_document_by_id(document_id)
        logger.info(f"[get_by_id] Fetched comparison document with ID: {document_id}")
        return result
    except Exception as e:
        logger.error(f"[get_by_id] Failed to fetch document_id={document_id}: {e}")
        raise

@router.get("/project/{project_id}", response_model=ComparisonDocumentListOut)
async def get_by_project(project_id: str):
    logger.debug(f"[get_by_project] Called with project_id={project_id}")
    try:
        documents = await get_comparison_documents_by_project_id(project_id)
        logger.info(f"[get_by_project] Found {len(documents)} documents for project ID: {project_id}")
        return {"message": "Documents fetched successfully", "data": documents}
    except Exception as e:
        logger.error(f"[get_by_project] Failed for project_id={project_id}: {e}")
        raise

@router.put("/{document_id}", response_model=ComparisonDocumentOut)
async def update(document_id: str, data: ComparisonDocumentUpdate):
    logger.debug(f"[update] Called with document_id={document_id}, data={data}")
    try:
        updated_document = await update_comparison_document(document_id, data)
        logger.info(f"[update] Successfully updated document with ID: {document_id}")
        return updated_document
    except Exception as e:
        logger.error(f"[update] Failed to update document_id={document_id}: {e}")
        raise

@router.delete("/{document_id}")
async def delete(document_id: str):
    logger.debug(f"[delete] Called with document_id={document_id}")
    try:
        logger.warning(f"[delete] Request to delete comparison document with ID: {document_id}")
        result = await delete_comparison_document(document_id)
        logger.info(f"[delete] Successfully deleted document with ID: {document_id}")
        return result
    except Exception as e:
        logger.error(f"[delete] Failed to delete document_id={document_id}: {e}")
        raise
