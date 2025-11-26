import re
import logging
from pathlib import Path
from typing import List
from app.models.comment_schemas import GeneratedComment

logger = logging.getLogger(__name__)


class TextParserService:
    """Service for parsing comments from TXT file"""
    
    def parse_comments_file(self, file_path: str) -> List[GeneratedComment]:
        """
        Parse comments from TXT file
        
        Expected format:
        1. @username (123 likes, 2h): Comment text here
        2. @another_user (45 likes, 5 min): Another comment
        
        Args:
            file_path: Path to comentarios.txt file
            
        Returns:
            List of GeneratedComment objects
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.strip().split('\n')
            
            comments = []
            for line_num, line in enumerate(lines, 1):
                comment = self._parse_line(line, line_num)
                if comment:
                    comments.append(comment)
            
            logger.info(f"Successfully parsed {len(comments)} comments from {file_path}")
            return comments
            
        except Exception as e:
            logger.error(f"Error parsing comments file {file_path}: {str(e)}")
            return []
    
    def _parse_line(self, line: str, line_num: int) -> GeneratedComment | None:
        """
        Parse a single line into a GeneratedComment
        
        Format: N. @username (LIKES likes, TIMESTAMP): Comment text
        Example: 1. @maria_silva (150 likes, 2h): Que vídeo incrível! ❤️
        """
        try:
            # Pattern: number. @username (likes likes, timestamp): text
            pattern = r'^\d+\.\s*@(\w+)\s*\((\d+)\s*likes?,\s*([^)]+)\):\s*(.+)$'
            match = re.match(pattern, line.strip())
            
            if match:
                username = match.group(1)
                likes = int(match.group(2))
                timestamp = match.group(3).strip()
                text = match.group(4).strip()
                
                # Generate author name from username
                author = self._username_to_author(username)
                
                return GeneratedComment(
                    author=author,
                    username=username,
                    text=text,
                    likes=likes,
                    timestamp=timestamp
                )
            else:
                logger.warning(f"Line {line_num} doesn't match expected format: {line[:50]}...")
                return None
                
        except Exception as e:
            logger.warning(f"Error parsing line {line_num}: {str(e)}")
            return None
    
    def _username_to_author(self, username: str) -> str:
        """Convert username to a readable author name"""
        # Replace underscores with spaces and capitalize
        parts = username.replace('_', ' ').split()
        author = ' '.join(word.capitalize() for word in parts)
        return author


# Singleton instance
text_parser_service = TextParserService()


