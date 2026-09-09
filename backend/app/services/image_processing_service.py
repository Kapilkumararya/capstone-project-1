import io
import base64
import logging
from typing import Dict, Any, Tuple
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)

class ImageProcessingService:
    """
    Local image processing service to optimize, compress, and reduce
    uploaded images before feeding them to vision detectors or LLM APIs.
    """

    @staticmethod
    def process_and_reduce_image(
        image_bytes: bytes,
        max_dimension: int = 800,
        quality: int = 80
    ) -> Dict[str, Any]:
        """
        Process the image locally:
        1. Validates image integrity.
        2. Auto-orients based on EXIF (e.g. mobile phone orientation).
        3. Normalizes color channels to RGB (handling RGBA, CMYK, Palette).
        4. Resizes/downscales proportionally if dimensions exceed max_dimension.
        5. Compresses to JPEG with stripped metadata and specified quality.
        6. Computes compression metrics (bytes saved, reduction ratio).
        
        Returns:
            Dict containing:
                - optimized_bytes: bytes of compressed image
                - base64_image: base64 encoded string (without prefix)
                - data_uri: complete data URI string (data:image/jpeg;base64,...)
                - metadata: dict with width, height, original_size, optimized_size, reduction_pct
        """
        original_size = len(image_bytes)
        if original_size == 0:
            raise ValueError("Empty image bytes received")

        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                # 1. Handle EXIF orientation
                try:
                    img = ImageOps.exif_transpose(img)
                except Exception as e:
                    logger.warning(f"EXIF transpose skipped: {e}")

                # 2. Normalize to RGB
                if img.mode in ("RGBA", "LA", "P"):
                    # Create white background for transparent images
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    background.paste(img, mask=img.split()[-1] if "A" in img.mode else None)
                    img = background
                elif img.mode != "RGB":
                    img = img.convert("RGB")

                orig_width, orig_height = img.size

                # 3. Downscale proportionally if larger than max_dimension
                if max(orig_width, orig_height) > max_dimension:
                    img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                
                final_width, final_height = img.size

                # 4. Save to optimized JPEG in memory (strips EXIF automatically)
                output_buffer = io.BytesIO()
                img.save(
                    output_buffer,
                    format="JPEG",
                    quality=quality,
                    optimize=True,
                    progressive=True
                )
                optimized_bytes = output_buffer.getvalue()

        except Exception as err:
            logger.error(f"Image processing error: {err}")
            raise ValueError(f"Failed to process image: {str(err)}")

        optimized_size = len(optimized_bytes)
        reduction_pct = round(max(0.0, (1 - (optimized_size / original_size)) * 100), 2)
        
        b64_str = base64.b64encode(optimized_bytes).decode("utf-8")
        data_uri = f"data:image/jpeg;base64,{b64_str}"

        logger.info(
            f"Image reduced: {original_size / 1024:.1f}KB -> {optimized_size / 1024:.1f}KB "
            f"(-{reduction_pct}%), dims: {orig_width}x{orig_height} -> {final_width}x{final_height}"
        )

        return {
            "optimized_bytes": optimized_bytes,
            "base64_image": b64_str,
            "data_uri": data_uri,
            "metadata": {
                "original_size_bytes": original_size,
                "optimized_size_bytes": optimized_size,
                "reduction_percentage": reduction_pct,
                "original_dimensions": [orig_width, orig_height],
                "final_dimensions": [final_width, final_height],
                "format": "JPEG"
            }
        }


# Global helper instance
image_processor = ImageProcessingService()
