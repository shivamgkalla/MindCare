import os
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from uuid import uuid4

# You can move these to config
UPLOAD_DIR = os.getenv("PROFILE_UPLOAD_DIR", "uploads/profile_photos")
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}
MAX_BYTES = 2 * 1024 * 1024  # 2 MB


async def save_profile_photo(file: UploadFile, user_id: int) -> str:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only JPEG/PNG allowed")

    # Ensure dir exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Read and size-check
    content = await file.read()
    if len(content) > MAX_BYTES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large (max 2MB)")

    ext = ".jpg" if file.content_type == "image/jpeg" else ".png"
    filename = f"user_{user_id}_{uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, filename)

    with open(path, "wb") as f:
        f.write(content)

    # Return relative path for storage
    return f"{UPLOAD_DIR}/{filename}"
