from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import base64
import logging
import uuid
from pathlib import Path
from typing import Optional

from app.config import settings
from app.models.schemas import DownloadRequest, ErrorResponse
from app.models.video_edit_schemas import EditStyle, CompilationRequest, EditedVideoResult
from app.middleware.auth import verify_api_key
from app.services.download_service import download_service
from app.services.ai_comments_service import ai_comments_service
from app.services.text_parser_service import text_parser_service
from app.services.image_generator_service import image_generator_service
from app.services.zip_service import zip_service
from app.services.capcut_service import CapCutAutomationService
from app.services.video_analyzer_service import VideoAnalyzerService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="TikTok Video Downloader API",
    description="REST API for downloading TikTok videos with authentication and rate limiting",
    version="2.0.0",
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (HTML interface)
static_path = Path(__file__).parent / "static"


@app.post(
    "/download",
    response_class=FileResponse,
    responses={
        200: {"description": "ZIP package downloaded successfully"},
        400: {"model": ErrorResponse, "description": "Invalid URL or video not available"},
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid or missing API key"},
        429: {"model": ErrorResponse, "description": "Too many requests - Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error during download"},
    }
)
@limiter.limit(settings.RATE_LIMIT)
async def download_video(
    request: Request,
    download_request: DownloadRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    Download TikTok video + generate AI comments + create Instagram images.
    
    Returns a ZIP package containing:
    - video.mp4
    - comentarios.txt (15 AI-generated comments)
    - instagram_01.png to instagram_15.png (comment images)
    - README.txt (disclaimer)
    """
    url = str(download_request.url)
    logger.info(f"Download requested for URL: {url}")
    
    # Generate unique ID for this download
    download_id = str(uuid.uuid4())
    temp_dir = Path(settings.DOWNLOADS_DIR) / download_id
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    temp_files = []
    
    try:
        # 1. Download video
        logger.info("Step 1/5: Downloading video...")
        result = await download_service.download_video(url)
        video_path = Path(result["file_path"])
        video_info = result["video_info"]
        temp_files.append(video_path)
        
        # 2. Extract metadata for AI
        logger.info("Step 2/5: Extracting metadata...")
        metadata = download_service.get_metadata(video_info)
        
        # 3. Generate 15 comments with AI
        logger.info("Step 3/5: Generating AI comments...")
        comments_txt_path = temp_dir / "comentarios.txt"
        comments, txt_path = await ai_comments_service.generate_comments(
            video_title=metadata['title'],
            video_description=metadata['description'],
            hashtags=metadata['hashtags'],
            num_comments=15,
            output_file=comments_txt_path
        )
        temp_files.append(Path(txt_path))
        
        # 4. Parse comments and generate 15 Instagram images
        logger.info("Step 4/5: Generating Instagram images...")
        parsed_comments = text_parser_service.parse_comments_file(txt_path)
        
        if not parsed_comments:
            logger.warning("No comments parsed, using generated comments directly")
            parsed_comments = comments
        
        # Ensure we have exactly 15 comments
        parsed_comments = parsed_comments[:15]
        
        # Generate images
        images_dir = temp_dir / "images"
        image_paths = image_generator_service.generate_images_from_comments(
            parsed_comments,
            images_dir
        )
        temp_files.extend(image_paths)
        
        # 5. Create ZIP package
        logger.info("Step 5/5: Creating ZIP package...")
        zip_filename = f"tiktok_{download_id}.zip"
        zip_path = temp_dir / zip_filename
        
        final_zip = zip_service.create_package(
            video_path=video_path,
            comments_txt_path=Path(txt_path),
            image_paths=image_paths,
            output_path=zip_path
        )
        
        logger.info(f"ZIP package created successfully: {zip_filename}")
        
        # Return ZIP file
        def cleanup_after_send():
            """Cleanup files after sending"""
            try:
                # Clean up all temp files
                for file in temp_files:
                    if file.exists():
                        file.unlink()
                # Clean up ZIP
                if final_zip.exists():
                    final_zip.unlink()
                # Clean up directories
                if images_dir.exists():
                    import shutil
                    shutil.rmtree(images_dir, ignore_errors=True)
                if temp_dir.exists():
                    import shutil
                    shutil.rmtree(temp_dir, ignore_errors=True)
                logger.info("Cleaned up temporary files")
            except Exception as e:
                logger.error(f"Error during cleanup: {str(e)}")
        
        return FileResponse(
            path=str(final_zip),
            media_type="application/zip",
            filename=zip_filename,
            background=cleanup_after_send
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        # Cleanup on error
        zip_service.cleanup_temp_files(temp_files)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        # Cleanup on error
        zip_service.cleanup_temp_files(temp_files)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video is unavailable or private"
        )
    except Exception as e:
        logger.error(f"Download failed: {str(e)}", exc_info=True)
        # Cleanup on error
        zip_service.cleanup_temp_files(temp_files)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process video: {str(e)}"
        )


@app.post(
    "/edit-video",
    response_model=EditedVideoResult,
    responses={
        200: {"description": "Video edited successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
@limiter.limit(settings.RATE_LIMIT)
async def edit_video_endpoint(
    request: Request,
    url: str,
    style: EditStyle = EditStyle.VIRAL,
    add_subtitles: bool = True,
    target_duration: Optional[int] = None,
    api_key: str = Depends(verify_api_key),
):
    """
    Download and automatically edit a TikTok video.
    
    Applies:
    - Intelligent cuts based on scene changes
    - AI-generated subtitles
    - Visual effects matching the selected style
    - Speed adjustments
    - Watermark
    
    Styles available:
    - viral: Fast cuts, trending effects
    - storytelling: Smooth transitions, full subtitles
    - educational: Explanatory text, strategic pauses
    - minimal: No effects, basic cuts only
    """
    logger.info(f"Edit video requested: URL={url}, style={style}")
    
    download_id = str(uuid.uuid4())
    temp_dir = Path(settings.DOWNLOADS_DIR) / download_id
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_files = []
    
    try:
        # 1. Download video
        logger.info("Downloading video...")
        result = await download_service.download_video(url)
        video_path = Path(result["file_path"])
        video_info = result["video_info"]
        temp_files.append(video_path)
        
        # 2. Extract metadata
        metadata = download_service.get_metadata(video_info)
        
        # 3. Generate AI comments for subtitles
        logger.info("Generating AI comments...")
        comments, _ = await ai_comments_service.generate_comments(
            video_title=metadata['title'],
            video_description=metadata['description'],
            hashtags=metadata['hashtags'],
            num_comments=5,  # Only 5 for subtitles
            output_file=None
        )
        
        # 4. Edit video
        logger.info("Editing video...")
        capcut_service = CapCutAutomationService()
        edited_result = await capcut_service.edit_video(
            video_path=video_path,
            comments=comments,
            metadata=metadata,
            style=style,
            add_subtitles=add_subtitles,
            target_duration=target_duration
        )
        
        logger.info(f"Video edited successfully: {edited_result.video_path}")
        return edited_result
        
    except Exception as e:
        logger.error(f"Edit video failed: {str(e)}", exc_info=True)
        zip_service.cleanup_temp_files(temp_files)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to edit video: {str(e)}"
        )


@app.post(
    "/analyze-video",
    responses={
        200: {"description": "Video analyzed successfully"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
@limiter.limit(settings.RATE_LIMIT)
async def analyze_video_endpoint(
    request: Request,
    url: str,
    api_key: str = Depends(verify_api_key),
):
    """
    Analyze a TikTok video to detect:
    - Key moments and scene changes
    - Motion intensity
    - Brightness levels
    - Optimal cut points
    
    Useful for understanding video structure before editing.
    """
    logger.info(f"Analyze video requested: URL={url}")
    
    temp_files = []
    
    try:
        # Download video
        result = await download_service.download_video(url)
        video_path = Path(result["file_path"])
        temp_files.append(video_path)
        
        # Analyze
        analyzer = VideoAnalyzerService()
        analysis = await analyzer.analyze_video(video_path)
        
        # Cleanup
        zip_service.cleanup_temp_files(temp_files)
        
        return analysis
        
    except Exception as e:
        logger.error(f"Analyze video failed: {str(e)}", exc_info=True)
        zip_service.cleanup_temp_files(temp_files)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze video: {str(e)}"
        )


@app.post(
    "/create-compilation",
    response_model=EditedVideoResult,
    responses={
        200: {"description": "Compilation created successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
@limiter.limit(settings.RATE_LIMIT)
async def create_compilation_endpoint(
    request: Request,
    compilation_request: CompilationRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    Create a compilation from multiple TikTok video URLs.
    
    Downloads all videos and creates a single compiled video with:
    - Smooth transitions between clips
    - Optional intro/outro
    - Unified theme
    - Maximum duration control
    """
    logger.info(f"Compilation requested: {len(compilation_request.video_paths)} videos")
    
    temp_files = []
    downloaded_paths = []
    
    try:
        # Download all videos
        for i, url in enumerate(compilation_request.video_paths):
            logger.info(f"Downloading video {i+1}/{len(compilation_request.video_paths)}...")
            result = await download_service.download_video(url)
            video_path = Path(result["file_path"])
            temp_files.append(video_path)
            downloaded_paths.append(video_path)
        
        # Create compilation
        logger.info("Creating compilation...")
        capcut_service = CapCutAutomationService()
        compilation_result = await capcut_service.create_compilation(
            video_paths=downloaded_paths,
            theme=compilation_request.theme,
            max_duration=compilation_request.max_duration
        )
        
        logger.info(f"Compilation created: {compilation_result.video_path}")
        return compilation_result
        
    except Exception as e:
        logger.error(f"Create compilation failed: {str(e)}", exc_info=True)
        zip_service.cleanup_temp_files(temp_files)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create compilation: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0"}


# Mount static files at root (must be after all API routes)
if static_path.exists():
    app.mount("/", StaticFiles(directory=str(static_path), html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )

