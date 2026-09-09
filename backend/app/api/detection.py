from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from beanie import PydanticObjectId
import logging

from app.models.user import User
from app.models.detection import DetectionRun
from app.api.deps import get_current_user
from app.services.image_processing_service import image_processor
from app.services.vision_service import detect_ingredients_from_image
from app.services.llm_detection_verifier import verify_and_prioritize_ingredients_with_llm

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/ingredients")
async def detect_ingredients(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    1. Reads uploaded image.
    2. Processes and reduces image locally (resizing, RGB normalize, compression)
       to minimize token usage and API payload size.
    3. Runs object detection (YOLOv8 vision service) for candidate ingredients.
    4. Submits candidates + compressed image to LLM for culinary verification.
    5. Prioritizes LLM's authoritative confirmed ingredients over raw detector output.
    """
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Step 1: Local Image Processing & Reduction
    try:
        processed = image_processor.process_and_reduce_image(
            image_bytes=image_bytes,
            max_dimension=800,
            quality=80
        )
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as err:
        logger.error(f"Image preprocessing failed: {err}")
        raise HTTPException(status_code=500, detail="Failed to process image locally.")

    # Step 2: Vision Model Detection (YOLOv8 / Vision Service)
    try:
        detection_results = await detect_ingredients_from_image(processed["optimized_bytes"])
    except Exception as err:
        logger.error(f"Vision detection failed: {err}")
        raise HTTPException(status_code=500, detail="Object detection service failed.")

    raw_candidates = detection_results.get("ingredients", [])
    confidence_scores = detection_results.get("confidence_scores", [])
    bounding_boxes = detection_results.get("bounding_boxes", [])

    # Step 3: LLM Confirmation & Priority Resolution
    llm_verif = await verify_and_prioritize_ingredients_with_llm(
        candidate_ingredients=raw_candidates,
        image_data_uri=processed["data_uri"],
        confidence_scores=confidence_scores
    )

    # Step 4: Persist Detection Run (LLM given priority for final ingredients)
    final_ingredients = llm_verif["confirmed_ingredients"]

    run = DetectionRun(
        user_id=current_user.id,
        ingredients=final_ingredients,
        raw_ingredients=raw_candidates,
        confidence_scores=confidence_scores,
        bounding_boxes=bounding_boxes,
        llm_confirmed=llm_verif["llm_confirmed"],
        llm_reasoning=llm_verif.get("reasoning"),
        llm_removed=llm_verif.get("removed_candidates", []),
        llm_added=llm_verif.get("added_ingredients", []),
        model_used=llm_verif.get("model_used"),
        image_meta=processed.get("metadata")
    )
    await run.insert()

    return {
        "run_id": str(run.id),
        "ingredients": run.ingredients,
        "raw_detector_ingredients": run.raw_ingredients,
        "llm_confirmed": run.llm_confirmed,
        "llm_reasoning": run.llm_reasoning,
        "llm_removed": run.llm_removed,
        "llm_added": run.llm_added,
        "model_used": run.model_used,
        "confidence_scores": run.confidence_scores,
        "bounding_boxes": run.bounding_boxes,
        "image_reduction": run.image_meta
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
