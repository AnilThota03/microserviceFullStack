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
    logger.info(f"Request to create comparison document '{name}' for project '{project_id}' by user '{user_id}'.")
    result = await create_comparison_document_with_files(
        name=name,
        original_file=original_file,
        modified_file=modified_file,
        project_id=project_id,
        user_id=user_id,
        type=type,
        model=model
    )
    logger.info(f"Successfully created comparison document with ID: {result.id}")
    return result

@router.get("/{document_id}", response_model=ComparisonDocumentOut)
async def get_by_id(document_id: str):
    logger.info(f"Fetching comparison document with ID: {document_id}")
    return await get_comparison_document_by_id(document_id)

@router.get("/project/{project_id}", response_model=ComparisonDocumentListOut)
async def get_by_project(project_id: str):
    logger.info(f"Fetching all comparison documents for project ID: {project_id}")
    documents = await get_comparison_documents_by_project_id(project_id)
    logger.info(f"Found {len(documents)} documents for project ID: {project_id}")
    return {"message": "Documents fetched successfully", "data": documents}

@router.put("/{document_id}", response_model=ComparisonDocumentOut)
async def update(document_id: str, data: ComparisonDocumentUpdate):
    logger.info(f"Updating comparison document with ID: {document_id}")
    updated_document = await update_comparison_document(document_id, data)
    logger.info(f"Successfully updated document with ID: {document_id}")
    return updated_document

@router.delete("/{document_id}")
async def delete(document_id: str):
    logger.warning(f"Request to delete comparison document with ID: {document_id}")
    result = await delete_comparison_document(document_id)
    logger.info(f"Successfully deleted document with ID: {document_id}")
    return result
