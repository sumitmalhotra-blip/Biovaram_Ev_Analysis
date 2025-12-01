"""
Samples Query Router
====================

Endpoints for querying sample data.

Endpoints:
- GET /samples           - List all samples with optional filters
- GET /samples/{id}      - Get specific sample details
- GET /samples/{id}/fcs  - Get FCS results for sample
- GET /samples/{id}/nta  - Get NTA results for sample
- DELETE /samples/{id}   - Delete sample and all related data

Author: CRMIT Backend Team
Date: November 21, 2025
"""

from typing import Optional, List  # noqa: F401
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore[import-not-found]
from sqlalchemy import select, func  # type: ignore[import-not-found]
from loguru import logger

from src.database.connection import get_session
from src.database.models import Sample, FCSResult, NTAResult, QCReport, ProcessingJob  # type: ignore[import-not-found]

router = APIRouter()


# ============================================================================
# List Samples Endpoint
# ============================================================================

@router.get("/", response_model=dict)
async def list_samples(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    treatment: Optional[str] = Query(None, description="Filter by treatment"),
    qc_status: Optional[str] = Query(None, description="Filter by QC status (pass/warn/fail)"),
    processing_status: Optional[str] = Query(None, description="Filter by processing status"),
    db: AsyncSession = Depends(get_session)
):
    """
    List all samples with optional filters.
    
    **Query Parameters:**
    - skip: Pagination offset (default: 0)
    - limit: Number of results (default: 100, max: 1000)
    - treatment: Filter by treatment (e.g., "CD81", "ISO")
    - qc_status: Filter by QC status ("pass", "warn", "fail")
    - processing_status: Filter by processing status ("pending", "completed", "failed")
    
    **Response:**
    ```json
    {
        "total": 150,
        "skip": 0,
        "limit": 100,
        "samples": [
            {
                "id": 1,
                "sample_id": "P5_F10_CD81",
                "treatment": "CD81",
                "qc_status": "pass",
                "processing_status": "completed",
                "upload_timestamp": "2025-11-21T12:00:00",
                "has_fcs": true,
                "has_nta": true,
                "has_tem": false
            },
            ...
        ]
    }
    ```
    """
    try:
        # Build query
        query = select(Sample)
        
        # Apply filters
        if treatment:
            query = query.where(Sample.treatment == treatment)
        if qc_status:
            query = query.where(Sample.qc_status == qc_status)
        if processing_status:
            query = query.where(Sample.processing_status == processing_status)
        
        # Get total count
        count_query = select(func.count()).select_from(Sample)
        if treatment:
            count_query = count_query.where(Sample.treatment == treatment)
        if qc_status:
            count_query = count_query.where(Sample.qc_status == qc_status)
        if processing_status:
            count_query = count_query.where(Sample.processing_status == processing_status)
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        samples = result.scalars().all()
        
        # Format response
        samples_data = []
        for sample in samples:
            upload_ts = getattr(sample, 'upload_timestamp', None)
            samples_data.append({
                "id": sample.id,
                "sample_id": sample.sample_id,
                "biological_sample_id": sample.biological_sample_id,
                "treatment": sample.treatment,
                "qc_status": sample.qc_status,
                "processing_status": sample.processing_status,
                "upload_timestamp": upload_ts.isoformat() if upload_ts else None,
                "has_fcs": sample.file_path_fcs is not None,
                "has_nta": sample.file_path_nta is not None,
                "has_tem": sample.file_path_tem is not None,
            })
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "samples": samples_data
        }
        
    except Exception as e:
        logger.exception(f"❌ Failed to list samples: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list samples: {str(e)}"
        )


# ============================================================================
# Get Sample Details Endpoint
# ============================================================================

@router.get("/{sample_id}", response_model=dict)
async def get_sample(
    sample_id: str,
    db: AsyncSession = Depends(get_session)
):
    """
    Get detailed information for a specific sample.
    
    **Path Parameters:**
    - sample_id: Sample identifier (e.g., "P5_F10_CD81")
    
    **Response:**
    ```json
    {
        "id": 1,
        "sample_id": "P5_F10_CD81",
        "biological_sample_id": "P5_F10",
        "treatment": "CD81",
        "concentration_ug": 1.0,
        "preparation_method": "SEC",
        "qc_status": "pass",
        "processing_status": "completed",
        "upload_timestamp": "2025-11-21T12:00:00",
        "files": {
            "fcs": "data/uploads/20251121_120000_file.fcs",
            "nta": "data/uploads/20251121_120100_file.txt",
            "tem": null
        },
        "results": {
            "fcs_count": 1,
            "nta_count": 1,
            "qc_reports_count": 2
        }
    }
    ```
    """
    try:
        # Query sample
        query = select(Sample).where(Sample.sample_id == sample_id)
        result = await db.execute(query)
        sample = result.scalar_one_or_none()
        
        if not sample:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sample not found: {sample_id}"
            )
        
        # Get related results counts
        fcs_query = select(func.count()).select_from(FCSResult).where(FCSResult.sample_id == sample.id)
        fcs_count = (await db.execute(fcs_query)).scalar()
        
        nta_query = select(func.count()).select_from(NTAResult).where(NTAResult.sample_id == sample.id)
        nta_count = (await db.execute(nta_query)).scalar()
        
        qc_query = select(func.count()).select_from(QCReport).where(QCReport.sample_id == sample.id)
        qc_count = (await db.execute(qc_query)).scalar()
        
        upload_ts = getattr(sample, 'upload_timestamp', None)
        exp_date = getattr(sample, 'experiment_date', None)
        
        return {
            "id": sample.id,
            "sample_id": sample.sample_id,
            "biological_sample_id": sample.biological_sample_id,
            "treatment": sample.treatment,
            "concentration_ug": sample.concentration_ug,
            "preparation_method": sample.preparation_method,
            "passage_number": sample.passage_number,
            "fraction_number": sample.fraction_number,
            "qc_status": sample.qc_status,
            "processing_status": sample.processing_status,
            "operator": sample.operator,
            "notes": sample.notes,
            "upload_timestamp": upload_ts.isoformat() if upload_ts else None,
            "experiment_date": exp_date.isoformat() if exp_date else None,
            "files": {
                "fcs": sample.file_path_fcs,
                "nta": sample.file_path_nta,
                "tem": sample.file_path_tem,
            },
            "results": {
                "fcs_count": fcs_count,
                "nta_count": nta_count,
                "qc_reports_count": qc_count,
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Failed to get sample {sample_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sample: {str(e)}"
        )


# ============================================================================
# Get FCS Results Endpoint
# ============================================================================

@router.get("/{sample_id}/fcs", response_model=dict)
async def get_fcs_results(
    sample_id: str,
    db: AsyncSession = Depends(get_session)
):
    """
    Get FCS analysis results for a sample.
    
    **Response:**
    ```json
    {
        "sample_id": "P5_F10_CD81",
        "results": [
            {
                "id": 1,
                "total_events": 50000,
                "fsc_median": 15000,
                "ssc_median": 8000,
                "particle_size_median_nm": 82.5,
                "cd81_positive_pct": 45.2,
                "debris_pct": 5.3,
                "processed_at": "2025-11-21T12:05:00"
            }
        ]
    }
    ```
    """
    try:
        # Get sample
        sample_query = select(Sample).where(Sample.sample_id == sample_id)
        sample_result = await db.execute(sample_query)
        sample = sample_result.scalar_one_or_none()
        
        if not sample:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sample not found: {sample_id}"
            )
        
        # Get FCS results
        fcs_query = select(FCSResult).where(FCSResult.sample_id == sample.id)
        fcs_result = await db.execute(fcs_query)
        fcs_results = fcs_result.scalars().all()
        
        results_data = []
        for fcs in fcs_results:
            processed = getattr(fcs, 'processed_at', None)
            results_data.append({
                "id": fcs.id,
                "total_events": fcs.total_events,
                "fsc_mean": fcs.fsc_mean,
                "fsc_median": fcs.fsc_median,
                "ssc_mean": fcs.ssc_mean,
                "ssc_median": fcs.ssc_median,
                "particle_size_mean_nm": fcs.particle_size_mean_nm,
                "particle_size_median_nm": fcs.particle_size_median_nm,
                "cd9_positive_pct": fcs.cd9_positive_pct,
                "cd81_positive_pct": fcs.cd81_positive_pct,
                "cd63_positive_pct": fcs.cd63_positive_pct,
                "debris_pct": fcs.debris_pct,
                "doublets_pct": fcs.doublets_pct,
                "processed_at": processed.isoformat() if processed else None,
                "parquet_file": fcs.parquet_file_path,
            })
        
        return {
            "sample_id": sample_id,
            "results": results_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Failed to get FCS results for {sample_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get FCS results: {str(e)}"
        )


# ============================================================================
# Get NTA Results Endpoint
# ============================================================================

@router.get("/{sample_id}/nta", response_model=dict)
async def get_nta_results(
    sample_id: str,
    db: AsyncSession = Depends(get_session)
):
    """
    Get NTA analysis results for a sample.
    
    **Response:**
    ```json
    {
        "sample_id": "P5_F10_CD81",
        "results": [
            {
                "id": 1,
                "mean_size_nm": 85.3,
                "median_size_nm": 82.1,
                "d10_nm": 65.2,
                "d90_nm": 105.3,
                "concentration_particles_ml": 1.5e11,
                "temperature_celsius": 22.5,
                "processed_at": "2025-11-21T12:10:00"
            }
        ]
    }
    ```
    """
    try:
        # Get sample
        sample_query = select(Sample).where(Sample.sample_id == sample_id)
        sample_result = await db.execute(sample_query)
        sample = sample_result.scalar_one_or_none()
        
        if not sample:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sample not found: {sample_id}"
            )
        
        # Get NTA results
        nta_query = select(NTAResult).where(NTAResult.sample_id == sample.id)
        nta_result = await db.execute(nta_query)
        nta_results = nta_result.scalars().all()
        
        results_data = []
        for nta in nta_results:
            processed = getattr(nta, 'processed_at', None)
            results_data.append({
                "id": nta.id,
                "mean_size_nm": nta.mean_size_nm,
                "median_size_nm": nta.median_size_nm,
                "d10_nm": nta.d10_nm,
                "d50_nm": nta.d50_nm,
                "d90_nm": nta.d90_nm,
                "concentration_particles_ml": nta.concentration_particles_ml,
                "temperature_celsius": nta.temperature_celsius,
                "ph": nta.ph,
                "bin_50_80nm_pct": nta.bin_50_80nm_pct,
                "bin_80_100nm_pct": nta.bin_80_100nm_pct,
                "bin_100_120nm_pct": nta.bin_100_120nm_pct,
                "processed_at": processed.isoformat() if processed else None,
                "parquet_file": nta.parquet_file_path,
            })
        
        return {
            "sample_id": sample_id,
            "results": results_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Failed to get NTA results for {sample_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get NTA results: {str(e)}"
        )


# ============================================================================
# Delete Sample Endpoint
# ============================================================================

@router.delete("/{sample_id}", response_model=dict)
async def delete_sample(
    sample_id: str,
    db: AsyncSession = Depends(get_session)
):
    """
    Delete a sample and all related data.
    
    **WARNING:** This will permanently delete:
    - Sample record
    - All FCS results
    - All NTA results
    - All QC reports
    - All processing jobs
    - Audit log will record deletion
    
    **Response:**
    ```json
    {
        "success": true,
        "message": "Sample P5_F10_CD81 deleted successfully",
        "deleted_records": {
            "fcs_results": 1,
            "nta_results": 1,
            "qc_reports": 2,
            "processing_jobs": 3
        }
    }
    ```
    """
    try:
        # Get sample
        query = select(Sample).where(Sample.sample_id == sample_id)
        result = await db.execute(query)
        sample = result.scalar_one_or_none()
        
        if not sample:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sample not found: {sample_id}"
            )
        
        # Count related records (for response)
        fcs_count = (await db.execute(
            select(func.count()).select_from(FCSResult).where(FCSResult.sample_id == sample.id)
        )).scalar()
        
        nta_count = (await db.execute(
            select(func.count()).select_from(NTAResult).where(NTAResult.sample_id == sample.id)
        )).scalar()
        
        qc_count = (await db.execute(
            select(func.count()).select_from(QCReport).where(QCReport.sample_id == sample.id)
        )).scalar()
        
        job_count = (await db.execute(
            select(func.count()).select_from(ProcessingJob).where(ProcessingJob.sample_id == sample.id)
        )).scalar()
        
        # Delete sample (cascade will delete related records)
        await db.delete(sample)
        await db.commit()
        
        logger.warning(f"🗑️  Deleted sample: {sample_id} (FCS: {fcs_count}, NTA: {nta_count}, QC: {qc_count}, Jobs: {job_count})")
        
        return {
            "success": True,
            "message": f"Sample {sample_id} deleted successfully",
            "deleted_records": {
                "fcs_results": fcs_count,
                "nta_results": nta_count,
                "qc_reports": qc_count,
                "processing_jobs": job_count,
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Failed to delete sample {sample_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete sample: {str(e)}"
        )
