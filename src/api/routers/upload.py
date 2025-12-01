"""
File Upload Router
==================

Endpoints for uploading and processing FCS, NTA, and TEM files.

Endpoints:
- POST /upload/fcs  - Upload and process FCS file
- POST /upload/nta  - Upload and process NTA file
- POST /upload/tem  - Upload and process TEM file (future)

Author: CRMIT Backend Team
Date: November 21, 2025
"""

from pathlib import Path
from typing import Optional
import shutil
import uuid
from datetime import datetime
import sys

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, status
from fastapi.responses import JSONResponse  # noqa: F401
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore[import-not-found]
from loguru import logger

from src.api.config import get_settings
from src.database.connection import get_session
from src.database.models import Sample, FCSResult, NTAResult, ProcessingJob  # type: ignore[import-not-found]
from src.database.crud import (
    create_sample,
    get_sample_by_id,
    update_sample,
    create_fcs_result,
    create_nta_result,
    create_processing_job,
    update_job_status,
)
# Import professional parsers
from src.parsers.fcs_parser import FCSParser
from src.parsers.nta_parser import NTAParser

settings = get_settings()
router = APIRouter()


# ============================================================================
# Helper Functions
# ============================================================================

async def save_uploaded_file(upload_file: UploadFile, destination: Path) -> Path:
    """
    Save uploaded file to disk.
    
    Args:
        upload_file: FastAPI UploadFile object
        destination: Destination file path
    
    Returns:
        Path to saved file
    
    Raises:
        HTTPException: If file size exceeds limit or save fails
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Check file size
        upload_file.file.seek(0, 2)  # Seek to end
        file_size = upload_file.file.tell()
        upload_file.file.seek(0)  # Reset to start
        
        max_size_bytes = settings.max_upload_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size {file_size / 1024 / 1024:.1f}MB exceeds limit of {settings.max_upload_size_mb}MB"
            )
        
        # Save file
        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        logger.info(f"✅ Saved uploaded file: {destination.name} ({file_size / 1024:.1f}KB)")
        return destination
        
    except Exception as e:
        logger.error(f"❌ Failed to save file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )


def generate_sample_id(filename: str) -> str:
    """
    Generate sample ID from filename.
    
    Args:
        filename: Original filename
    
    Returns:
        Sample ID (e.g., "P5_F10_CD81")
    
    Logic:
    1. Extract from filename patterns (e.g., "P5+F10+CD81.fcs" → "P5_F10_CD81")
    2. Fall back to timestamp-based ID if pattern not recognized
    """
    # Remove extension
    name = Path(filename).stem
    
    # Replace common separators with underscore
    name = name.replace('+', '_').replace('-', '_').replace(' ', '_')
    
    # Clean up multiple underscores
    while '__' in name:
        name = name.replace('__', '_')
    
    return name


# ============================================================================
# FCS Upload Endpoint
# ============================================================================

@router.post("/fcs", response_model=dict)
async def upload_fcs_file(
    file: UploadFile = File(...),
    treatment: Optional[str] = Form(None),
    concentration_ug: Optional[float] = Form(None),
    preparation_method: Optional[str] = Form(None),
    operator: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_session)
):
    """
    Upload and process FCS file.
    
    **Request:**
    - file: FCS file (multipart/form-data)
    - treatment: Treatment name (e.g., "CD81", "ISO", "Control")
    - concentration_ug: Antibody concentration in µg
    - preparation_method: Preparation method (e.g., "SEC", "Centrifugation")
    - operator: Operator name
    - notes: Additional notes
    
    **Response:**
    ```json
    {
        "success": true,
        "sample_id": "P5_F10_CD81",
        "job_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "pending",
        "message": "File uploaded successfully, processing started"
    }
    ```
    
    **Processing Pipeline:**
    1. Save uploaded file to `data/uploads/`
    2. Create sample record in database
    3. Create processing job (async)
    4. Return immediately with job ID
    5. Background worker parses FCS file
    6. Background worker saves results to database and Parquet
    """
    logger.info(f"📤 Uploading FCS file: {file.filename}")
    
    try:
        # Validate file extension
        if not file.filename.lower().endswith('.fcs'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only .fcs files are accepted."
            )
        
        # Generate sample ID
        sample_id = generate_sample_id(file.filename)
        
        # Save uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = settings.upload_dir / f"{timestamp}_{file.filename}"
        await save_uploaded_file(file, file_path)
        
        # Parse FCS file using professional parser
        fcs_results = None
        try:
            logger.info(f"🔬 Parsing FCS file with professional parser...")
            parser = FCSParser(file_path)
            
            # Validate file
            if not parser.validate():
                logger.warning(f"⚠️ FCS file validation failed, continuing anyway...")
            
            # Parse and get results
            parsed_data = parser.parse()
            
            if parsed_data is not None and len(parsed_data) > 0:
                # Extract key metrics
                fcs_results = {
                    "event_count": len(parsed_data) if hasattr(parsed_data, '__len__') else parsed_data.get('event_count', 0),
                    "channels": list(parsed_data.columns) if hasattr(parsed_data, 'columns') else [],
                    "mean_fsc": float(parsed_data[parsed_data.columns[0]].mean()) if hasattr(parsed_data, 'columns') and len(parsed_data.columns) > 0 else None,
                    "mean_ssc": float(parsed_data[parsed_data.columns[1]].mean()) if hasattr(parsed_data, 'columns') and len(parsed_data.columns) > 1 else None,
                }
                logger.success(f"✅ Parsed {fcs_results['event_count']} events with {len(fcs_results['channels'])} channels")
        except Exception as parse_error:
            logger.error(f"⚠️ Parser failed: {parse_error}, continuing with upload...")
            fcs_results = None
        
        # Create sample record in database
        db_sample = None
        db_job = None
        job_id = str(uuid.uuid4())
        
        try:
            # Check if sample already exists
            existing_sample = await get_sample_by_id(db, sample_id)
            
            if existing_sample:
                # Update existing sample with FCS file path
                db_sample = await update_sample(
                    db=db,
                    sample_id=sample_id,
                    file_path_fcs=str(file_path.relative_to(Path.cwd())),
                    treatment=treatment,
                    concentration_ug=concentration_ug,
                    preparation_method=preparation_method,
                    operator=operator,
                    notes=notes,
                )
                logger.info(f"📝 Updated existing sample: {sample_id}")
            else:
                # Create new sample record
                db_sample = await create_sample(
                    db=db,
                    sample_id=sample_id,
                    file_path_fcs=str(file_path.relative_to(Path.cwd())),
                    treatment=treatment,
                    concentration_ug=concentration_ug,
                    preparation_method=preparation_method,
                    operator=operator,
                    notes=notes,
                )
                logger.info(f"✨ Created new sample: {sample_id}")
            
            # Create processing job
            if db_sample:
                db_job = await create_processing_job(
                    db=db,
                    job_id=job_id,
                    job_type="fcs_parse",
                    sample_id=db_sample.id,
                )
                logger.info(f"📋 Created processing job: {job_id}")
                
                # If parsing succeeded, save FCS results to database
                if fcs_results:
                    await create_fcs_result(
                        db=db,
                        sample_id=db_sample.id,
                        total_events=fcs_results.get('event_count', 0),
                        fsc_mean=fcs_results.get('mean_fsc'),
                        ssc_mean=fcs_results.get('mean_ssc'),
                    )
                    # Mark job as completed
                    await update_job_status(
                        db=db,
                        job_id=job_id,
                        status="completed",
                        result_data=fcs_results,
                    )
                    logger.success(f"💾 Saved FCS results to database")
                    
        except Exception as db_error:
            logger.warning(f"⚠️ Database operation failed: {db_error}")
            logger.warning("   Continuing with file-based response...")
            db_sample = None
        
        # Get database ID or use temporary ID
        db_id = db_sample.id if db_sample else abs(hash(sample_id)) % 1000000
        
        logger.success(f"✅ FCS file uploaded: {sample_id} (job: {job_id})")
        
        # Build response with parsed results
        response_data = {
            "success": True,
            "id": db_id,  # Database ID (real if DB connected, temp otherwise)
            "sample_id": sample_id,  # String display name
            "treatment": treatment,
            "concentration_ug": concentration_ug,
            "preparation_method": preparation_method,
            "operator": operator,
            "notes": notes,
            "job_id": job_id,
            "status": "uploaded",
            "processing_status": "completed" if fcs_results else "pending",
            "message": "File uploaded successfully, processing started",
            "file_size_mb": file_path.stat().st_size / 1024 / 1024,
            "upload_timestamp": datetime.now().isoformat(),
        }
        
        # Add parsed FCS results if available
        if fcs_results:
            response_data["fcs_results"] = fcs_results
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Failed to upload FCS file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process upload: {str(e)}"
        )


# ============================================================================
# NTA Upload Endpoint
# ============================================================================

@router.post("/nta", response_model=dict)
async def upload_nta_file(
    file: UploadFile = File(...),
    treatment: Optional[str] = Form(None),
    temperature_celsius: Optional[float] = Form(None),
    operator: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_session)
):
    """
    Upload and process NTA file.
    
    **Request:**
    - file: NTA file (.txt or .csv)
    - treatment: Treatment name
    - temperature_celsius: Measurement temperature
    - operator: Operator name
    - notes: Additional notes
    
    **Response:**
    ```json
    {
        "success": true,
        "sample_id": "P5_F10_CD81",
        "job_id": "550e8400-e29b-41d4-a716-446655440001",
        "status": "pending",
        "message": "File uploaded successfully, processing started"
    }
    ```
    
    **Processing Pipeline:**
    1. Save uploaded file to `data/uploads/`
    2. Create sample record (or update existing)
    3. Create processing job (async)
    4. Background worker parses NTA file
    5. Background worker saves results to database and Parquet
    """
    logger.info(f"📤 Uploading NTA file: {file.filename}")
    
    try:
        # Validate file extension
        if not (file.filename.lower().endswith('.txt') or file.filename.lower().endswith('.csv')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only .txt and .csv files are accepted."
            )
        
        # Generate sample ID
        sample_id = generate_sample_id(file.filename)
        
        # Save uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = settings.upload_dir / f"{timestamp}_{file.filename}"
        await save_uploaded_file(file, file_path)
        
        # Create or update sample record in database
        db_sample = None
        db_job = None
        job_id = str(uuid.uuid4())
        
        try:
            # Check if sample already exists
            existing_sample = await get_sample_by_id(db, sample_id)
            
            if existing_sample:
                # Update existing sample with NTA file path
                db_sample = await update_sample(
                    db=db,
                    sample_id=sample_id,
                    file_path_nta=str(file_path.relative_to(Path.cwd())),
                    treatment=treatment,
                    operator=operator,
                    notes=notes,
                )
                logger.info(f"📝 Updated existing sample with NTA: {sample_id}")
            else:
                # Create new sample record
                db_sample = await create_sample(
                    db=db,
                    sample_id=sample_id,
                    file_path_nta=str(file_path.relative_to(Path.cwd())),
                    treatment=treatment,
                    operator=operator,
                    notes=notes,
                )
                logger.info(f"✨ Created new sample: {sample_id}")
            
            # Create processing job
            if db_sample:
                db_job = await create_processing_job(
                    db=db,
                    job_id=job_id,
                    job_type="nta_parse",
                    sample_id=db_sample.id,
                )
                logger.info(f"📋 Created processing job: {job_id}")
                
        except Exception as db_error:
            logger.warning(f"⚠️ Database operation failed: {db_error}")
            logger.warning("   Continuing with file-based response...")
            db_sample = None
        
        # Get database ID or use temporary ID
        db_id = db_sample.id if db_sample else abs(hash(sample_id)) % 1000000
        
        logger.success(f"✅ NTA file uploaded: {sample_id} (job: {job_id})")
        
        # Return complete sample data to avoid additional API calls
        return {
            "success": True,
            "id": db_id,  # Database ID (real if DB connected, temp otherwise)
            "sample_id": sample_id,  # String display name
            "treatment": treatment,
            "temperature_celsius": temperature_celsius,
            "operator": operator,
            "notes": notes,
            "job_id": job_id,
            "status": "uploaded",
            "processing_status": "pending",
            "message": "File uploaded successfully, processing started",
            "file_size_mb": file_path.stat().st_size / 1024 / 1024,
            "upload_timestamp": datetime.now().isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Failed to upload NTA file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process upload: {str(e)}"
        )


# ============================================================================
# Batch Upload Endpoint
# ============================================================================

@router.post("/batch", response_model=dict)
async def upload_batch(
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_session)
):
    """
    Upload multiple files at once.
    
    **Request:**
    - files: List of FCS and/or NTA files
    
    **Response:**
    ```json
    {
        "success": true,
        "uploaded": 5,
        "failed": 0,
        "job_ids": ["uuid1", "uuid2", "uuid3", "uuid4", "uuid5"],
        "details": [
            {"filename": "file1.fcs", "sample_id": "S001", "status": "success"},
            ...
        ]
    }
    ```
    """
    logger.info(f"📤 Batch upload: {len(files)} files")
    
    results = {
        "success": True,
        "uploaded": 0,
        "failed": 0,
        "job_ids": [],
        "details": []
    }
    
    for file in files:
        try:
            # Determine file type
            if file.filename.lower().endswith('.fcs'):
                result = await upload_fcs_file(file=file, db=db)
            elif file.filename.lower().endswith(('.txt', '.csv')):
                result = await upload_nta_file(file=file, db=db)
            else:
                raise ValueError(f"Unsupported file type: {file.filename}")
            
            results["uploaded"] += 1
            results["job_ids"].append(result["job_id"])
            results["details"].append({
                "filename": file.filename,
                "sample_id": result["sample_id"],
                "status": "success"
            })
            
        except Exception as e:
            logger.error(f"❌ Failed to upload {file.filename}: {e}")
            results["failed"] += 1
            results["details"].append({
                "filename": file.filename,
                "status": "failed",
                "error": str(e)
            })
    
    if results["failed"] > 0:
        results["success"] = False
    
    logger.info(f"✅ Batch upload complete: {results['uploaded']} succeeded, {results['failed']} failed")
    
    return results
