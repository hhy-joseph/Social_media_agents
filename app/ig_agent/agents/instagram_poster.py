import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger("ig_agent.instagram_poster")

class InstagramPoster:
    """
    Agent responsible for posting to Instagram
    """
    
    def __init__(self, username=None, password=None):
        """
        Initialize the InstagramPoster
        
        Args:
            username: Instagram username
            password: Instagram password
        """
        self.username = username or os.environ.get("INSTAGRAM_USERNAME")
        self.password = password or os.environ.get("INSTAGRAM_PASSWORD")
        
        # Check if instagrapi is installed
        try:
            import instagrapi
            self.has_instagrapi = True
        except ImportError:
            self.has_instagrapi = False
            logger.warning("instagrapi not installed. Instagram posting will be simulated.")
            logger.warning("Install with: pip install instagrapi")
        
        # Check if PIL is available for image conversion
        try:
            from PIL import Image
            self.has_pil = True
        except ImportError:
            self.has_pil = False
            logger.warning("PIL (Pillow) not installed. PNG to JPG conversion will be skipped.")
            logger.warning("Install with: pip install pillow")
    
    def convert_png_to_jpg(self, png_path: str) -> str:
        """
        Convert PNG image to JPG format
        
        Args:
            png_path: Path to PNG image
            
        Returns:
            Path to converted JPG image
        """
        if not self.has_pil:
            logger.warning("PIL not available, skipping PNG to JPG conversion")
            return png_path
            
        try:
            from PIL import Image
            
            png_path = Path(png_path)
            jpg_path = png_path.with_suffix('.jpg')
            
            img = Image.open(png_path)
            # Convert to RGB mode if the image has an alpha channel
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                bg = Image.new('RGB', img.size, (255, 255, 255))
                bg.paste(img, mask=img if img.mode == 'RGBA' else None)
                img = bg
            
            # Save as JPG with high quality
            img.save(jpg_path, 'JPEG', quality=95)
            logger.info(f"Converted {png_path} to {jpg_path}")
            
            return str(jpg_path)
        except Exception as e:
            logger.error(f"Failed to convert {png_path} to JPG: {str(e)}")
            return png_path  # Return original path on error
    
    def prepare_images_for_posting(self, image_paths: List[str]) -> List[str]:
        """
        Convert PNG images to JPG and ensure proper ordering
        
        Args:
            image_paths: Paths to images to post
            
        Returns:
            List of prepared image paths
        """
        try:
            # Convert PNG images to JPG
            converted_paths = []
            for path in image_paths:
                if Path(path).suffix.lower() == '.png':
                    converted_path = self.convert_png_to_jpg(path)
                    converted_paths.append(converted_path)
                else:
                    converted_paths.append(path)
            
            # Ensure proper ordering: cover first, then content pages in order
            ordered_paths = []
            
            # Find cover image
            cover_path = next((p for p in converted_paths if 'cover' in Path(p).stem.lower()), None)
            if cover_path:
                ordered_paths.append(cover_path)
                logger.info(f"Found cover image: {Path(cover_path).name}")
            
            # Find content images and sort by number
            content_paths = [p for p in converted_paths if 'content_' in Path(p).stem.lower()]
            # Sort by the numeric part of the filename
            content_paths.sort(key=lambda p: int(''.join(filter(str.isdigit, Path(p).stem.split('_')[-1])) or 0))
            
            ordered_paths.extend(content_paths)
            
            # Add any remaining images
            remaining_paths = [p for p in converted_paths if p not in ordered_paths]
            ordered_paths.extend(remaining_paths)
            
            logger.info(f"Images ordered for posting: {[Path(p).name for p in ordered_paths]}")
            
            return ordered_paths
        except Exception as e:
            logger.error(f"Failed to prepare images for posting: {str(e)}")
            return image_paths  # Return original paths on error
    
    def post_to_instagram(self, caption: str, image_paths: List[str]) -> Dict[str, Any]:
        """
        Post content to Instagram using instagrapi
        
        Args:
            caption: Post caption
            image_paths: Paths to images to post
            
        Returns:
            Dict with posting status
        """
        if not self.username or not self.password:
            logger.warning("Instagram credentials not provided")
            return {
                "posted": False,
                "error": "Instagram credentials not provided",
                "suggestion": "Provide username and password when initializing InstagramPoster or set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD environment variables"
            }
        
        if not self.has_instagrapi:
            logger.warning("instagrapi not installed, simulating post")
            return {
                "posted": False,
                "simulated": True,
                "caption": caption,
                "num_images": len(image_paths),
                "suggestion": "Install instagrapi with: pip install instagrapi"
            }
        
        try:
            # Prepare images (convert PNG to JPG and ensure proper ordering)
            prepared_paths = self.prepare_images_for_posting(image_paths)
            
            # Import here to avoid dependency if not needed
            from instagrapi import Client
            
            # Check if paths exist
            valid_paths = []
            for path in prepared_paths:
                if Path(path).exists():
                    valid_paths.append(path)
                else:
                    logger.warning(f"Image not found: {path}")
            
            if not valid_paths:
                raise ValueError("No valid image paths provided")
            
            # Connect to Instagram
            client = Client()
            client.login(self.username, self.password)
            
            # Check if we have multiple images for carousel or just one
            if len(valid_paths) > 1:
                # Upload as carousel
                try:
                    media = client.album_upload(
                        valid_paths,
                        caption=caption
                    )
                    
                    logger.info(f"Posted carousel to Instagram: {media.pk}")
                    return {
                        "posted": True,
                        "type": "carousel",
                        "media_id": media.pk,
                        "url": f"https://www.instagram.com/p/{media.code}/"
                    }
                except Exception as carousel_error:
                    # If carousel upload fails, try uploading the first image as a single post
                    logger.warning(f"Carousel upload failed: {str(carousel_error)}. Trying single image upload.")
                    media = client.photo_upload(
                        valid_paths[0],
                        caption=caption
                    )
                    
                    logger.info(f"Posted single image to Instagram: {media.pk}")
                    return {
                        "posted": True,
                        "type": "single",
                        "media_id": media.pk,
                        "url": f"https://www.instagram.com/p/{media.code}/",
                        "note": "Uploaded as single image due to carousel error"
                    }
            else:
                # Upload as single image
                media = client.photo_upload(
                    valid_paths[0],
                    caption=caption
                )
                
                logger.info(f"Posted single image to Instagram: {media.pk}")
                return {
                    "posted": True,
                    "type": "single",
                    "media_id": media.pk,
                    "url": f"https://www.instagram.com/p/{media.code}/"
                }
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"Failed to post to Instagram: {error_message}")
            return {
                "posted": False,
                "error": error_message,
                "suggestion": "Check your Instagram credentials and network connection"
            }