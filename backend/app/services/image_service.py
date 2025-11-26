"""Image Upload Service

Handles image upload to S3-compatible storage with validation.
"""
import uuid
import io
from typing import Optional, BinaryIO
from fastapi import UploadFile, HTTPException
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings


class ImageService:
    """Service for image upload and management"""
    
    # Allowed image types
    ALLOWED_CONTENT_TYPES = {
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/webp': '.webp'
    }
    
    # Maximum file size: 5MB
    MAX_FILE_SIZE = 5 * 1024 * 1024
    
    def __init__(self):
        """Initialize S3 client"""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
            endpoint_url=settings.S3_ENDPOINT_URL
        )
        self.bucket_name = settings.S3_BUCKET_NAME
        self.cdn_base_url = settings.CDN_BASE_URL
    
    def validate_image(self, file: UploadFile) -> None:
        """
        Validate image file type and size.
        
        Args:
            file: Uploaded file
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate content type
        if file.content_type not in self.ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(self.ALLOWED_CONTENT_TYPES.keys())}"
            )
        
        # Read file to check size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {self.MAX_FILE_SIZE / (1024 * 1024)}MB"
            )
    
    def generate_unique_filename(self, original_filename: str, content_type: str) -> str:
        """
        Generate unique filename for S3 storage.
        
        Args:
            original_filename: Original filename
            content_type: File content type
            
        Returns:
            Unique filename with extension
        """
        # Get file extension from content type
        extension = self.ALLOWED_CONTENT_TYPES.get(content_type, '.jpg')
        
        # Generate unique filename using UUID
        unique_id = uuid.uuid4().hex
        filename = f"products/{unique_id}{extension}"
        
        return filename
    
    async def upload_image(
        self,
        file: UploadFile,
        folder: str = "products"
    ) -> str:
        """
        Upload image to S3 and return CDN URL.
        
        Args:
            file: Uploaded file
            folder: S3 folder/prefix
            
        Returns:
            CDN URL of uploaded image
            
        Raises:
            HTTPException: If upload fails
        """
        # Validate image
        self.validate_image(file)
        
        # Generate unique filename
        filename = f"{folder}/{uuid.uuid4().hex}{self.ALLOWED_CONTENT_TYPES[file.content_type]}"
        
        try:
            # Read file content
            file_content = await file.read()
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=file_content,
                ContentType=file.content_type,
                ACL='public-read'  # Make publicly accessible
            )
            
            # Generate CDN URL
            if self.cdn_base_url:
                url = f"{self.cdn_base_url}/{filename}"
            else:
                # Fallback to S3 URL
                url = f"https://{self.bucket_name}.s3.{settings.S3_REGION}.amazonaws.com/{filename}"
            
            return url
            
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload image: {str(e)}"
            )
        finally:
            # Reset file pointer
            await file.seek(0)
    
    def delete_image(self, image_url: str) -> bool:
        """
        Delete image from S3 storage.
        
        Args:
            image_url: Full URL of the image
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            # Extract filename from URL
            if self.cdn_base_url and image_url.startswith(self.cdn_base_url):
                filename = image_url.replace(f"{self.cdn_base_url}/", "")
            else:
                # Extract from S3 URL
                parts = image_url.split(f"{self.bucket_name}.s3.")
                if len(parts) > 1:
                    filename = parts[1].split('/', 1)[1] if '/' in parts[1] else parts[1]
                else:
                    return False
            
            # Delete from S3
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=filename
            )
            
            return True
            
        except ClientError as e:
            print(f"Failed to delete image: {str(e)}")
            return False
    
    def get_image_url(self, filename: str) -> str:
        """
        Get full CDN URL for a filename.
        
        Args:
            filename: S3 filename/key
            
        Returns:
            Full CDN URL
        """
        if self.cdn_base_url:
            return f"{self.cdn_base_url}/{filename}"
        else:
            return f"https://{self.bucket_name}.s3.{settings.S3_REGION}.amazonaws.com/{filename}"


# Create singleton instance
image_service = ImageService()
