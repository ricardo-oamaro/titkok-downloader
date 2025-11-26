import ollama
import logging
import json
import random
import re
from pathlib import Path
from typing import List, Optional
from app.models.comment_schemas import GeneratedComment
from app.config import settings

logger = logging.getLogger(__name__)


class AICommentsService:
    """Service for generating realistic comments using Ollama (local LLM)"""
    
    def __init__(self):
        self.model = settings.OLLAMA_MODEL
        self.base_url = settings.OLLAMA_BASE_URL
        logger.info(f"AICommentsService initialized with model: {self.model}")
    
    async def generate_comments(
        self,
        video_title: str,
        video_description: str = "",
        hashtags: List[str] = None,
        num_comments: int = 15,
        output_file: Optional[Path] = None
    ) -> tuple[List[GeneratedComment], str]:
        """
        Generate realistic comments using Ollama and save to TXT file
        
        Args:
            video_title: Title of the video
            video_description: Description of the video
            hashtags: List of hashtags
            num_comments: Number of comments to generate (default 15)
            output_file: Path to save comments.txt
            
        Returns:
            Tuple of (list of GeneratedComment objects, path to txt file)
        """
        logger.info(f"Generating {num_comments} comments for video: {video_title[:50]}...")
        
        hashtags = hashtags or []
        
        try:
            # Build context for AI
            context = self._build_context(video_title, video_description, hashtags)
            
            # Generate comments with Ollama
            comments = await self._generate_with_ollama(context, num_comments)
            
            # If Ollama fails, use fallback
            if not comments:
                logger.warning("Ollama generation failed, using fallback")
                comments = self._fallback_comments(num_comments)
            
            # Save to TXT file
            txt_path = self._save_to_txt(comments, output_file)
            
            logger.info(f"Successfully generated {len(comments)} comments and saved to {txt_path}")
            return comments, str(txt_path)
            
        except Exception as e:
            logger.error(f"Error generating comments: {str(e)}")
            # Use fallback on any error
            comments = self._fallback_comments(num_comments)
            txt_path = self._save_to_txt(comments, output_file)
            return comments, str(txt_path)
    
    def _build_context(self, title: str, description: str, hashtags: List[str]) -> str:
        """Build context string for AI prompt"""
        context_parts = [f"Título: {title}"]
        
        if description:
            context_parts.append(f"Descrição: {description}")
        
        if hashtags:
            context_parts.append(f"Hashtags: {', '.join(hashtags)}")
        
        return "\n".join(context_parts)
    
    async def _generate_with_ollama(self, context: str, num_comments: int) -> List[GeneratedComment]:
        """Generate comments using Ollama"""
        prompt = f"""Você é um gerador de comentários realistas para vídeos do TikTok/Instagram.

Gere EXATAMENTE {num_comments} comentários em português do Brasil para este vídeo:

{context}

REQUISITOS IMPORTANTES:
1. Comentários VARIADOS: alguns curtos (5-10 palavras), outros longos (20-40 palavras)
2. Misture: elogios entusiasmados, perguntas, críticas construtivas, piadas
3. Use emojis NATURALMENTE (não exagere, 1-3 por comentário)
4. Alguns comentários com erros de digitação sutis (ex: "vc" ao invés de "você")
5. Nomes brasileiros DIVERSOS (homens, mulheres, diferentes regiões)
6. Likes entre 0 e 5000 (maioria entre 10-500)
7. Timestamps variados: "agora", "5 min", "2h", "1d", "3d", "1sem"

FORMATO DE SAÍDA (JSON):
{{
  "comments": [
    {{
      "author": "Maria Silva",
      "username": "maria_silva",
      "text": "Que vídeo incrível! Amei demais ❤️",
      "likes": 150,
      "timestamp": "2h"
    }},
    ...
  ]
}}

Gere APENAS o JSON válido, sem texto adicional antes ou depois."""

        try:
            # Call Ollama API
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": 0.9,  # High creativity
                    "top_p": 0.95,
                    "num_predict": 2000,  # Max tokens
                }
            )
            
            response_text = response.get('response', '')
            
            # Extract JSON from response
            comments = self._parse_ollama_response(response_text, num_comments)
            
            if len(comments) < num_comments:
                logger.warning(f"Only generated {len(comments)}/{num_comments} comments, filling with fallback")
                # Fill remaining with fallback
                remaining = num_comments - len(comments)
                comments.extend(self._fallback_comments(remaining))
            
            return comments[:num_comments]  # Ensure exact count
            
        except Exception as e:
            logger.error(f"Ollama generation error: {str(e)}")
            return []
    
    def _parse_ollama_response(self, response_text: str, expected_count: int) -> List[GeneratedComment]:
        """Parse Ollama response and extract comments"""
        try:
            # Try to find JSON in response
            json_match = re.search(r'\{[\s\S]*"comments"[\s\S]*\}', response_text)
            
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                
                comments = []
                for item in data.get('comments', []):
                    try:
                        comment = GeneratedComment(
                            author=item.get('author', 'Usuário Anônimo'),
                            username=item.get('username', 'usuario'),
                            text=item.get('text', ''),
                            likes=item.get('likes', random.randint(0, 500)),
                            timestamp=item.get('timestamp', '2h')
                        )
                        comments.append(comment)
                    except Exception as e:
                        logger.warning(f"Failed to parse comment item: {e}")
                        continue
                
                return comments
            else:
                logger.warning("No JSON found in Ollama response")
                return []
                
        except Exception as e:
            logger.error(f"Error parsing Ollama response: {str(e)}")
            return []
    
    def _fallback_comments(self, num_comments: int) -> List[GeneratedComment]:
        """Generate fallback comments when AI fails"""
        logger.info(f"Using fallback comment generation for {num_comments} comments")
        
        templates = [
            ("João Silva", "joao_silva", "Muito bom! 👏", 120, "2h"),
            ("Maria Santos", "maria_santos", "Amei ❤️", 350, "1h"),
            ("Pedro Costa", "pedro_costa", "Que incrível! Como faz isso?", 89, "3h"),
            ("Ana Lima", "ana_lima", "Salvei pra fazer depois 🔖", 45, "5 min"),
            ("Carlos Mendes", "carlos_mendes", "Top demais! 🔥", 234, "1d"),
            ("Juliana Alves", "juliana_alves", "Perfeito! Já fiz 3 vezes 😍", 567, "2d"),
            ("Roberto Dias", "roberto_dias", "Adorei! Vou tentar", 23, "4h"),
            ("Beatriz Rocha", "beatriz_rocha", "Ficou lindo! 💚", 178, "6h"),
            ("Lucas Oliveira", "lucas_oliveira", "Parabéns pelo trabalho!", 92, "1d"),
            ("Camila Fernandes", "camila_fernandes", "Maravilhoso ✨", 145, "3h"),
            ("Gabriel Souza", "gabriel_souza", "Muito show! 👌", 67, "2h"),
            ("Patricia Costa", "patricia_costa", "Isso sim é conteúdo de qualidade", 289, "5h"),
            ("Rafael Martins", "rafael_martins", "Salvando pra assistir depois 📌", 34, "1h"),
            ("Fernanda Lima", "fernanda_lima", "Sensacional! 🎉", 456, "3d"),
            ("Thiago Pereira", "thiago_pereira", "Melhor vídeo que vi hoje!", 123, "4h"),
        ]
        
        comments = []
        for i in range(num_comments):
            template = templates[i % len(templates)]
            author, username, text, likes, timestamp = template
            
            # Add variation
            likes = likes + random.randint(-50, 50)
            likes = max(0, likes)
            
            comment = GeneratedComment(
                author=author,
                username=username,
                text=text,
                likes=likes,
                timestamp=timestamp
            )
            comments.append(comment)
        
        return comments
    
    def _save_to_txt(self, comments: List[GeneratedComment], output_file: Optional[Path] = None) -> Path:
        """Save comments to TXT file in the specified format"""
        if output_file is None:
            output_file = Path(settings.DOWNLOADS_DIR) / "comentarios.txt"
        
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        lines = []
        for i, comment in enumerate(comments, 1):
            line = f"{i}. @{comment.username} ({comment.likes} likes, {comment.timestamp}): {comment.text}"
            lines.append(line)
        
        content = "\n".join(lines)
        
        output_file.write_text(content, encoding='utf-8')
        logger.info(f"Saved {len(comments)} comments to {output_file}")
        
        return output_file


# Singleton instance
ai_comments_service = AICommentsService()


