import hashlib
import logging
from pathlib import Path
from typing import List
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from app.models.comment_schemas import GeneratedComment

logger = logging.getLogger(__name__)


class InstagramCommentImageGenerator:
    """Service for generating Instagram-style comment images"""
    
    # Image dimensions
    WIDTH = 1080
    HEIGHT = 200
    AVATAR_SIZE = 60
    
    # Colors (Instagram style)
    COLOR_BG = (255, 255, 255)  # White
    COLOR_TEXT = (38, 38, 38)  # Dark gray
    COLOR_USERNAME = (38, 38, 38)  # Dark gray
    COLOR_META = (142, 142, 142)  # Light gray
    COLOR_WATERMARK = (199, 199, 199)  # Very light gray
    
    # Avatar colors (for initials)
    AVATAR_COLORS = [
        (255, 87, 87),   # Red
        (87, 117, 255),  # Blue
        (255, 184, 77),  # Orange
        (92, 225, 230),  # Cyan
        (255, 138, 212), # Pink
        (165, 94, 234),  # Purple
        (46, 213, 115),  # Green
        (255, 159, 67),  # Yellow-orange
        (72, 219, 251),  # Light blue
        (253, 121, 168), # Hot pink
    ]
    
    def __init__(self):
        """Initialize image generator with fonts"""
        self.fonts_dir = Path(__file__).parent.parent / "static" / "fonts"
        
        try:
            self.font_regular = ImageFont.truetype(
                str(self.fonts_dir / "Roboto-Regular.ttf"), 28
            )
            self.font_bold = ImageFont.truetype(
                str(self.fonts_dir / "Roboto-Bold.ttf"), 30
            )
            self.font_small = ImageFont.truetype(
                str(self.fonts_dir / "Roboto-Regular.ttf"), 24
            )
            logger.info("Fonts loaded successfully")
        except Exception as e:
            logger.error(f"Error loading fonts: {str(e)}")
            # Fallback to default font
            self.font_regular = ImageFont.load_default()
            self.font_bold = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
    
    def generate_comment_image(self, comment: GeneratedComment, output_path: Path) -> Path:
        """
        Generate a single Instagram-style comment image
        
        Args:
            comment: GeneratedComment object
            output_path: Path to save the PNG file
            
        Returns:
            Path to the generated image
        """
        try:
            # Create blank image
            img = Image.new('RGB', (self.WIDTH, self.HEIGHT), color=self.COLOR_BG)
            draw = ImageDraw.Draw(img)
            
            # 1. Draw avatar (circular with initials)
            avatar = self._create_avatar(comment.author)
            img.paste(avatar, (30, 70), avatar)  # Use alpha channel for transparency
            
            # 2. Draw username (bold)
            username_x = 120
            username_y = 50
            draw.text(
                (username_x, username_y),
                comment.username,
                font=self.font_bold,
                fill=self.COLOR_USERNAME
            )
            
            # 3. Draw comment text
            comment_x = 120
            comment_y = 85
            wrapped_text = self._wrap_text(comment.text, max_width=900)
            draw.text(
                (comment_x, comment_y),
                wrapped_text,
                font=self.font_regular,
                fill=self.COLOR_TEXT
            )
            
            # 4. Draw metadata (timestamp and likes)
            meta_x = 120
            meta_y = 150
            meta_text = f"{comment.timestamp} • {comment.likes} curtidas"
            draw.text(
                (meta_x, meta_y),
                meta_text,
                font=self.font_small,
                fill=self.COLOR_META
            )
            
            # 5. Draw heart icon (simplified)
            self._draw_heart_icon(draw, (950, 75))
            
            # 6. Draw watermark (discrete)
            watermark_text = "Gerado por IA"
            watermark_x = self.WIDTH - 180
            watermark_y = self.HEIGHT - 35
            draw.text(
                (watermark_x, watermark_y),
                watermark_text,
                font=self.font_small,
                fill=self.COLOR_WATERMARK
            )
            
            # Save image
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Add EXIF metadata
            exif_data = img.getexif()
            exif_data[0x010E] = "AI Generated - Not Real Screenshot"  # ImageDescription
            exif_data[0x0131] = "TikTok Downloader + AI Comments"  # Software
            
            img.save(output_path, "PNG", exif=exif_data)
            logger.info(f"Generated image: {output_path.name}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating image for comment: {str(e)}")
            raise
    
    def generate_images_from_comments(
        self, 
        comments: List[GeneratedComment], 
        output_dir: Path
    ) -> List[Path]:
        """
        Generate images for all comments
        
        Args:
            comments: List of GeneratedComment objects
            output_dir: Directory to save images
            
        Returns:
            List of paths to generated images
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        image_paths = []
        for i, comment in enumerate(comments, 1):
            output_path = output_dir / f"instagram_{i:02d}.png"
            try:
                path = self.generate_comment_image(comment, output_path)
                image_paths.append(path)
            except Exception as e:
                logger.error(f"Failed to generate image {i}: {str(e)}")
                continue
        
        logger.info(f"Generated {len(image_paths)} images in {output_dir}")
        return image_paths
    
    def _create_avatar(self, name: str) -> Image.Image:
        """Create circular avatar with initials"""
        # Create square image
        avatar = Image.new('RGBA', (self.AVATAR_SIZE, self.AVATAR_SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(avatar)
        
        # Get color based on name
        color = self._get_color_from_name(name)
        
        # Draw circle
        draw.ellipse(
            [(0, 0), (self.AVATAR_SIZE, self.AVATAR_SIZE)],
            fill=color
        )
        
        # Get initials
        initials = self._get_initials(name)
        
        # Draw initials
        # Try to center text (approximate)
        bbox = draw.textbbox((0, 0), initials, font=self.font_bold)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (self.AVATAR_SIZE - text_width) // 2
        y = (self.AVATAR_SIZE - text_height) // 2 - 5  # Slight adjustment
        
        draw.text(
            (x, y),
            initials,
            font=self.font_bold,
            fill=(255, 255, 255)  # White text
        )
        
        return avatar
    
    def _get_initials(self, name: str) -> str:
        """Get initials from name (first letter of first and last name)"""
        parts = name.strip().split()
        if len(parts) == 0:
            return "?"
        elif len(parts) == 1:
            return parts[0][0].upper()
        else:
            return (parts[0][0] + parts[-1][0]).upper()
    
    def _get_color_from_name(self, name: str) -> tuple:
        """Generate consistent color based on name hash"""
        hash_value = int(hashlib.md5(name.encode()).hexdigest(), 16)
        return self.AVATAR_COLORS[hash_value % len(self.AVATAR_COLORS)]
    
    def _wrap_text(self, text: str, max_width: int) -> str:
        """Wrap text to fit within max width (simple word wrap)"""
        # For simplicity, we'll limit to 2 lines
        if len(text) <= 80:
            return text
        
        # Try to break at a good point
        words = text.split()
        line1 = []
        line2 = []
        current_line = line1
        char_count = 0
        
        for word in words:
            if char_count + len(word) + 1 > 80 and current_line == line1:
                current_line = line2
                char_count = 0
            
            current_line.append(word)
            char_count += len(word) + 1
        
        result = ' '.join(line1)
        if line2:
            result += '\n' + ' '.join(line2)
            # Limit second line
            if len(' '.join(line2)) > 80:
                result = result[:160] + '...'
        
        return result
    
    def _draw_heart_icon(self, draw: ImageDraw.Draw, position: tuple):
        """Draw a simple heart icon"""
        x, y = position
        size = 24
        
        # Simple heart shape using circle approximation
        # Top two circles
        draw.ellipse(
            [(x - size//4, y), (x + size//4, y + size//2)],
            outline=self.COLOR_TEXT,
            width=2
        )
        draw.ellipse(
            [(x, y), (x + size//2, y + size//2)],
            outline=self.COLOR_TEXT,
            width=2
        )
        
        # Bottom triangle (simplified)
        draw.line(
            [(x - size//4, y + size//4), (x + size//4, y + size)],
            fill=self.COLOR_TEXT,
            width=2
        )
        draw.line(
            [(x + size//2, y + size//4), (x + size//4, y + size)],
            fill=self.COLOR_TEXT,
            width=2
        )


# Singleton instance
image_generator_service = InstagramCommentImageGenerator()


