import cloudinary
import cloudinary.uploader

from app.core.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)


async def upload_profile_picture(content: bytes, user_id: str) -> str:
    """Upload image bytes to Cloudinary and return the secure URL."""
    result = cloudinary.uploader.upload(
        content,
        folder="mikrotik/profile_pictures",
        public_id=user_id,  # use user_id as public_id so re-uploading replaces the old one
        overwrite=True,
        resource_type="image",
        transformation=[
            {"width": 500, "height": 500, "crop": "fill", "gravity": "face"},
            {"quality": "auto", "fetch_format": "auto"},
        ],
    )
    return result["secure_url"]


async def delete_profile_picture(user_id: str) -> None:
    """Delete the user's profile picture from Cloudinary."""
    cloudinary.uploader.destroy(f"profile_pictures/{user_id}", resource_type="image")
