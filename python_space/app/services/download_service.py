import yt_dlp
import os
import uuid
import logging
import re
from pathlib import Path
from typing import Optional, Dict, List
from app.config import settings

# Try to import TikTokApi for comment extraction
try:
    from TikTokApi import TikTokApi as TikTokApiClass
    TIKTOK_API_AVAILABLE = True
except ImportError:
    TIKTOK_API_AVAILABLE = False
    logger.warning("TikTokApi not available. Comment extraction will be limited.")

logger = logging.getLogger(__name__)


class DownloadService:
    def __init__(self):
        self.downloads_dir = Path(settings.DOWNLOADS_DIR)
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Downloads directory ready: {self.downloads_dir}")
    
    async def download_video(self, url: str) -> Dict[str, any]:
        """
        Download TikTok video using yt-dlp
        Returns dict with file_path, filename, and size
        """
        video_id = str(uuid.uuid4())
        output_path = self.downloads_dir / f"{video_id}.mp4"
        
        logger.info(f"Starting download for video ID: {video_id}")
        
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': str(output_path.with_suffix('')),  # yt-dlp adds extension
            'merge_output_format': 'mp4',
            'no_warnings': True,
            'quiet': False,
        }
        
        # Add cookies if configured
        if settings.YTDLP_COOKIES_BROWSER:
            # Format: (browser, profile, keyring, container)
            # Profile 2 is where the user is logged into TikTok
            ydl_opts['cookiesfrombrowser'] = (settings.YTDLP_COOKIES_BROWSER, 'Profile 2', None, None)
            logger.info(f"Using cookies from browser: {settings.YTDLP_COOKIES_BROWSER} (Profile 2)")
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Find the actual downloaded file
                # Try multiple possibilities since yt-dlp behavior varies
                base_path = output_path.with_suffix('')  # Without extension
                possible_files = [
                    base_path,  # No extension (most common with outtmpl without extension)
                    output_path,  # With .mp4 extension
                    Path(str(base_path) + '.mp4'),
                    Path(str(base_path) + '.webm'),
                    Path(str(base_path) + '.mkv'),
                ]
                
                actual_file = None
                for test_path in possible_files:
                    if test_path.exists() and test_path.stat().st_size > 0:
                        actual_file = test_path
                        logger.info(f"Found downloaded file: {test_path.name}")
                        break
                
                if not actual_file or not actual_file.exists():
                    # List files in download directory for debugging
                    logger.error(f"Could not find downloaded file. Searched for: {[str(p) for p in possible_files]}")
                    raise FileNotFoundError(f"Downloaded file not found. Expected around: {output_path}")
                
                file_size = actual_file.stat().st_size
                
                if file_size == 0:
                    raise ValueError("Downloaded file is empty")
                
                logger.info(f"Video downloaded successfully: {actual_file.name} ({file_size} bytes)")
                
                return {
                    "file_path": str(actual_file),
                    "filename": f"tiktok_{video_id}.mp4",
                    "size": file_size,
                    "video_info": info
                }
                
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            logger.error(f"yt-dlp download error: {error_msg}")
            
            # Cleanup on error
            if output_path.exists():
                output_path.unlink()
            
            # Handle specific TikTok authentication errors
            if "requiring login" in error_msg.lower() or "use --cookies" in error_msg.lower():
                raise ValueError(
                    "❌ TikTok requer autenticação para este vídeo.\n\n"
                    "📋 Como resolver:\n"
                    "1. Abra o Chrome e faça login no TikTok (https://www.tiktok.com)\n"
                    "2. Certifique-se de estar logado\n"
                    "3. Tente novamente o download\n\n"
                    f"🔧 Navegador configurado: {settings.YTDLP_COOKIES_BROWSER}\n"
                    "💡 Dica: Se continuar falhando, tente fechar todos os Chrome e tentar novamente."
                )
            elif "video unavailable" in error_msg.lower() or "private video" in error_msg.lower():
                raise ValueError("Vídeo indisponível ou privado")
            elif "unsupported url" in error_msg.lower():
                raise ValueError("URL do TikTok inválida ou não suportada")
            elif "http error 404" in error_msg.lower():
                raise ValueError("Vídeo não encontrado (404)")
            elif "ip address is blocked" in error_msg.lower():
                raise ValueError("Seu IP está bloqueado pelo TikTok. Tente novamente mais tarde.")
            else:
                raise ValueError(f"Falha no download: {error_msg}")
        
        except Exception as e:
            logger.error(f"Download failed: {str(e)}")
            # Cleanup on error
            if output_path.exists():
                output_path.unlink()
            raise
    
    async def extract_comments_with_tiktokapi(self, video_id: str, max_comments: int = 15) -> Optional[str]:
        """
        Extract comments using TikTokApi library
        """
        if not TIKTOK_API_AVAILABLE:
            logger.warning("TikTokApi not available")
            return None
            
        try:
            logger.info(f"Attempting to extract comments with TikTokApi for video: {video_id}")
            
            async with TikTokApiClass() as api:
                await api.create_sessions(num_sessions=1, sleep_after=3, headless=True)
                
                video = api.video(id=video_id)
                comments_list = []
                
                async for comment in video.comments(count=max_comments):
                    comments_list.append(comment)
                    if len(comments_list) >= max_comments:
                        break
                
                if not comments_list:
                    logger.warning(f"TikTokApi: No comments found for video {video_id}")
                    return None
                
                # Format comments
                formatted_lines = []
                for i, comment in enumerate(comments_list, 1):
                    author = comment.get('user', {}).get('uniqueId', 'Unknown')
                    text = comment.get('text', '')
                    likes = comment.get('digg_count', 0)
                    
                    # Limit comment length
                    if len(text) > 200:
                        text = text[:200] + '...'
                    
                    formatted_lines.append(f"{i}. @{author} ({likes} likes): {text}")
                
                content = '\n\n'.join(formatted_lines)
                
                # Limit total size
                max_size = 5000
                if len(content) > max_size:
                    content = content[:max_size] + '\n\n[... comentários truncados devido ao tamanho]'
                
                logger.info(f"TikTokApi: Successfully extracted {len(comments_list)} comments")
                return content
                
        except Exception as e:
            logger.error(f"TikTokApi comment extraction failed: {str(e)}")
            return None
    
    async def extract_comments(self, url: str, max_comments: int = 15) -> Optional[str]:
        """
        Extract comments from TikTok video
        Tries yt-dlp first, then falls back to TikTokApi
        Returns formatted text content or None
        """
        logger.info(f"Starting comment extraction for URL: {url}")
        
        # Method 1: Try yt-dlp first (faster if it works)
        video_id_temp = str(uuid.uuid4())
        ydl_opts = {
            'skip_download': True,
            'writeinfojson': True,
            'getcomments': True,
            'outtmpl': str(self.downloads_dir / video_id_temp),
            'no_warnings': True,
            'quiet': True,
        }
        
        if settings.YTDLP_COOKIES_BROWSER:
            ydl_opts['cookiesfrombrowser'] = (settings.YTDLP_COOKIES_BROWSER, 'Profile 2', None, None)
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                comments = info.get('comments', [])
                
                if comments:
                    logger.info("yt-dlp: Comments found, using yt-dlp extraction")
                    sorted_comments = sorted(
                        comments, 
                        key=lambda x: x.get('like_count', 0), 
                        reverse=True
                    )[:max_comments]
                    
                    formatted_lines = []
                    for i, comment in enumerate(sorted_comments, 1):
                        author = comment.get('author', 'Unknown')
                        text = comment.get('text', '')
                        if len(text) > 200:
                            text = text[:200] + '...'
                        formatted_lines.append(f"{i}. {author}: {text}")
                    
                    content = '\n\n'.join(formatted_lines)
                    if len(content) > 5000:
                        content = content[:5000] + '\n\n[... comentários truncados]'
                    
                    logger.info(f"yt-dlp: Successfully extracted {len(sorted_comments)} comments")
                    return content
                else:
                    logger.warning(f"yt-dlp: No comments in response. Count: {info.get('comment_count', 0)}")
        except Exception as e:
            logger.warning(f"yt-dlp comment extraction failed: {str(e)}")
        
        # Method 2: Fallback to TikTokApi
        logger.info("Falling back to TikTokApi for comment extraction")
        
        # Extract video ID from URL
        video_id_match = re.search(r'/video/(\d+)', url)
        if video_id_match:
            video_id = video_id_match.group(1)
            result = await self.extract_comments_with_tiktokapi(video_id, max_comments)
            if result:
                return result
        else:
            logger.error(f"Could not extract video ID from URL: {url}")
        
        logger.warning("All comment extraction methods failed")
        return None
    
    def get_metadata(self, video_info: dict) -> dict:
        """
        Extract metadata from video info for AI comment generation
        
        Args:
            video_info: Video info dict from yt-dlp
            
        Returns:
            Dict with title, description, and hashtags
        """
        try:
            title = video_info.get('title', '') or video_info.get('fulltitle', '') or ''
            description = video_info.get('description', '') or ''
            
            # Extract hashtags from description
            hashtags = []
            if description:
                import re
                hashtag_pattern = r'#(\w+)'
                found_tags = re.findall(hashtag_pattern, description)
                hashtags = [f"#{tag}" for tag in found_tags[:10]]  # Limit to 10 hashtags
            
            # Also check tags field
            if not hashtags and 'tags' in video_info and video_info['tags']:
                hashtags = [f"#{tag}" for tag in video_info['tags'][:10]]
            
            metadata = {
                'title': title[:200],  # Limit length
                'description': description[:500],  # Limit length
                'hashtags': hashtags
            }
            
            logger.info(f"Extracted metadata: title='{title[:50]}...', {len(hashtags)} hashtags")
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            return {
                'title': 'Video do TikTok',
                'description': '',
                'hashtags': []
            }
    
    def cleanup_file(self, file_path: str):
        """Remove temporary file"""
        try:
            Path(file_path).unlink()
            logger.info(f"Cleaned up file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to cleanup file {file_path}: {str(e)}")


# Singleton instance
download_service = DownloadService()

