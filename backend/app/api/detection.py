from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from beanie import PydanticObjectId
from app.models.user import User
from app.models.detection import DetectionRun
from app.api.deps import get_current_user
from app.services.vision_service import detect_ingredients_from_image

router = APIRouter()

@router.post("/ingredients")
async def detect_ingredients(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # Read the file bytes
    image_bytes = await file.read()
    
    # Call the vision service (simulated YOLOv8)
    detection_results = await detect_ingredients_from_image(image_bytes)
    
    # Save the run
    run = DetectionRun(
        user_id=current_user.id,
        ingredients=detection_results["ingredients"],
        confidence_scores=detection_results["confidence_scores"],
        bounding_boxes=detection_results["bounding_boxes"]
    )
    await run.insert()
    
    return {
        "run_id": str(run.id),
        "ingredients": run.ingredients,
        "confidence_scores": run.confidence_scores,
        "bounding_boxes": run.bounding_boxes
    }

@router.get("/{run_id}")
async def get_detection_run(
    run_id: PydanticObjectId,
    current_user: User = Depends(get_current_user)
):
    run = await DetectionRun.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Detection run not found")
        
    if run.user_id.ref.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this run")
        
    return run
