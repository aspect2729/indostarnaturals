"""
Temporary Admin Endpoint for Running Migrations
WARNING: This should be removed after initial deployment!
"""
import logging
import subprocess
from fastapi import APIRouter, HTTPException, Header
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/run-migrations")
async def run_migrations(x_admin_secret: str = Header(None)):
    """
    Temporary endpoint to run database migrations
    
    SECURITY: Requires X-Admin-Secret header matching JWT_SECRET_KEY
    
    Usage:
    curl -X POST https://your-app.onrender.com/admin/run-migrations \
         -H "X-Admin-Secret: your-jwt-secret-key"
    
    WARNING: Remove this endpoint after successful deployment!
    """
    # Verify admin secret
    if not x_admin_secret or x_admin_secret != settings.JWT_SECRET_KEY:
        logger.warning("Unauthorized migration attempt")
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    try:
        logger.info("Starting database migrations...")
        
        # Run alembic upgrade
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True,
            timeout=300  # 5 minute timeout
        )
        
        logger.info("Migrations completed successfully")
        
        return {
            "status": "success",
            "message": "Database migrations completed successfully",
            "output": result.stdout,
            "warning": "IMPORTANT: Remove this endpoint after deployment!"
        }
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Migration failed: {e.stderr}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Migration failed",
                "stderr": e.stderr,
                "stdout": e.stdout
            }
        )
    except subprocess.TimeoutExpired:
        logger.error("Migration timeout")
        raise HTTPException(status_code=500, detail="Migration timeout after 5 minutes")
    except Exception as e:
        logger.error(f"Unexpected error during migration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/migration-status")
async def migration_status(x_admin_secret: str = Header(None)):
    """
    Check current migration status
    
    SECURITY: Requires X-Admin-Secret header
    """
    if not x_admin_secret or x_admin_secret != settings.JWT_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    try:
        # Check current alembic version
        result = subprocess.run(
            ["alembic", "current"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        
        # Check if there are pending migrations
        history = subprocess.run(
            ["alembic", "history"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        
        return {
            "current_version": result.stdout.strip(),
            "history": history.stdout,
            "status": "ok"
        }
        
    except Exception as e:
        logger.error(f"Failed to check migration status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
