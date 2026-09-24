import tempfile
import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Lazy-load the YOLO model to avoid slow import on every request
_yolo_model = None

# Mapping of COCO class IDs to food/ingredient categories
# YOLOv8 is trained on COCO which includes some food classes.
# We map relevant COCO class names to standardized ingredient names.
COCO_FOOD_CLASSES = {
    "banana": "banana",
    "apple": "apple",
    "sandwich": "sandwich",
    "orange": "orange",
    "broccoli": "broccoli",
    "carrot": "carrot",
    "hot dog": "hot dog",
    "pizza": "pizza",
    "donut": "donut",
    "cake": "cake",
    # Non-food items we want to filter out
}

# Additional items that YOLO may detect that are NOT ingredients
NON_INGREDIENT_CLASSES = {
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train",
    "truck", "boat", "traffic light", "fire hydrant", "stop sign",
    "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep",
    "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
    "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard",
    "sports ball", "kite", "baseball bat", "baseball glove", "skateboard",
    "surfboard", "tennis racket", "bottle", "wine glass", "cup", "fork",
    "knife", "spoon", "bowl", "chair", "couch", "potted plant", "bed",
    "dining table", "toilet", "tv", "laptop", "mouse", "remote",
    "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "book", "clock", "vase", "scissors", "teddy bear",
    "hair drier", "toothbrush",
}


def _load_yolo_model():
    """Lazy-load YOLOv8 model on first use."""
    global _yolo_model
    if _yolo_model is None:
        try:
            from ultralytics import YOLO
            # Use the nano model for speed; upgrade to yolov8s/m/l for accuracy
            _yolo_model = YOLO("yolov8n.pt")
            logger.info("YOLOv8n model loaded successfully.")
        except ImportError:
            logger.error(
                "ultralytics package not installed. "
                "Run: pip install ultralytics"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to load YOLOv8 model: {e}")
            raise
    return _yolo_model


async def detect_ingredients_from_image(image_bytes: bytes) -> Dict[str, Any]:
    """
    Runs YOLOv8 inference on the provided image bytes.
    
    Returns detected objects with:
      - ingredients: list of detected food item names
      - confidence_scores: corresponding confidence values
      - bounding_boxes: list of {label, box, confidence} dicts
      - all_detections: every detection including non-food items (for debugging)
    """
    if not image_bytes:
        raise ValueError("Empty image bytes received")

    # Write image to a temp file for YOLO inference
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(image_bytes)
        tmp_path = tmp.name

    try:
        model = _load_yolo_model()
        
        # Run inference
        results = model(tmp_path, verbose=False)
        
        ingredients = []
        confidence_scores = []
        bounding_boxes = []
        all_detections = []

        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
                
            for i in range(len(boxes)):
                cls_id = int(boxes.cls[i].item())
                conf = float(boxes.conf[i].item())
                xyxy = boxes.xyxy[i].tolist()  # [x1, y1, x2, y2]
                
                # Get class name from model
                class_name = model.names.get(cls_id, f"class_{cls_id}").lower()
                
                detection = {
                    "label": class_name,
                    "box": [int(c) for c in xyxy],
                    "confidence": round(conf, 4)
                }
                all_detections.append(detection)
                
                # Filter: only keep food-related detections
                if class_name in NON_INGREDIENT_CLASSES:
                    continue
                
                # Only keep detections with reasonable confidence
                if conf < 0.25:
                    continue
                
                # Standardize the name if we have a mapping
                ingredient_name = COCO_FOOD_CLASSES.get(class_name, class_name)
                
                # Avoid duplicates
                if ingredient_name not in ingredients:
                    ingredients.append(ingredient_name)
                    confidence_scores.append(round(conf, 4))
                    bounding_boxes.append(detection)

        logger.info(
            f"YOLOv8 detected {len(all_detections)} objects total, "
            f"{len(ingredients)} food ingredients: {ingredients}"
        )

        return {
            "ingredients": ingredients,
            "confidence_scores": confidence_scores,
            "bounding_boxes": bounding_boxes,
            "all_detections": all_detections,
        }

    except ImportError:
        # ultralytics not installed — return empty results gracefully
        logger.warning("ultralytics not available. Returning empty detection.")
        return {
            "ingredients": [],
            "confidence_scores": [],
            "bounding_boxes": [],
            "all_detections": [],
        }

    finally:
        # Ensure temp file cleanup
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
