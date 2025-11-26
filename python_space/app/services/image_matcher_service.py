import logging
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import asyncio
import ollama

from app.models.story_video_schemas import (
    TranscriptionSegment,
    ImageInfo,
    ImageMatch
)
from app.config import settings

logger = logging.getLogger(__name__)


# Stopwords comuns em português
PORTUGUESE_STOPWORDS = {
    'a', 'o', 'e', 'de', 'da', 'do', 'em', 'um', 'uma', 'os', 'as', 'dos', 'das',
    'para', 'com', 'por', 'na', 'no', 'ao', 'aos', 'à', 'às', 'pelo', 'pela',
    'este', 'esta', 'esse', 'essa', 'isto', 'isso', 'aquele', 'aquela', 'aquilo',
    'meu', 'minha', 'seu', 'sua', 'nosso', 'nossa', 'dele', 'dela',
    'que', 'qual', 'quais', 'quando', 'onde', 'como', 'porque', 'se',
    'mais', 'menos', 'muito', 'pouco', 'todo', 'toda', 'tudo',
    'já', 'ainda', 'também', 'apenas', 'só', 'sempre', 'nunca'
}


class ImageMatcherService:
    """Serviço para fazer matching entre transcrição e imagens usando Ollama"""
    
    def __init__(self, min_confidence: float = 0.3):
        """
        Inicializa o serviço de matching
        
        Args:
            min_confidence: Score mínimo para considerar um match válido (0-1)
        """
        self.min_confidence = min_confidence
        self.supported_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'}
    
    def find_images(self, images_dir: Path) -> List[ImageInfo]:
        """
        Encontra todas as imagens em um diretório
        
        Args:
            images_dir: Diretório para buscar imagens
            
        Returns:
            Lista de ImageInfo
        """
        if not images_dir.exists():
            raise FileNotFoundError(f"Images directory not found: {images_dir}")
        
        images = []
        for ext in self.supported_extensions:
            for img_path in images_dir.rglob(f"*{ext}"):
                if img_path.is_file():
                    keywords = self.extract_keywords_from_filename(img_path.name)
                    images.append(ImageInfo(
                        path=str(img_path),
                        filename=img_path.name,
                        keywords=keywords
                    ))
        
        # Ordenar por nome
        images.sort(key=lambda x: x.filename)
        
        logger.info(f"Found {len(images)} images in {images_dir}")
        return images
    
    def extract_keywords_from_filename(self, filename: str) -> List[str]:
        """
        Extrai keywords do nome do arquivo
        
        Args:
            filename: Nome do arquivo (ex: "meu_carro_vermelho_2024.jpg")
            
        Returns:
            Lista de keywords (ex: ["carro", "vermelho", "2024"])
        """
        # Remove extensão
        name = Path(filename).stem
        
        # Substitui separadores por espaços
        name = re.sub(r'[_\-\.]', ' ', name)
        
        # Remove caracteres especiais
        name = re.sub(r'[^\w\s]', '', name)
        
        # Split e normaliza
        words = name.lower().split()
        
        # Remove stopwords e palavras muito curtas
        keywords = [
            w for w in words
            if len(w) > 2 and w not in PORTUGUESE_STOPWORDS
        ]
        
        return keywords
    
    async def find_best_matches(
        self,
        segments: List[TranscriptionSegment],
        available_images: List[ImageInfo]
    ) -> List[ImageMatch]:
        """
        Encontra as melhores imagens para cada segmento de transcrição
        
        Args:
            segments: Lista de segmentos transcritos
            available_images: Lista de imagens disponíveis
            
        Returns:
            Lista de ImageMatch com os melhores matches
        """
        if not available_images:
            raise ValueError("No images available for matching")
        
        logger.info(f"Matching {len(segments)} segments with {len(available_images)} images")
        
        matches = []
        used_images = {}  # Track usage count for each image
        
        for i, segment in enumerate(segments):
            logger.debug(f"Processing segment {i+1}/{len(segments)}: {segment.text[:50]}...")
            
            # Encontrar melhor imagem para este segmento
            match = await self._match_segment_to_image(
                segment,
                available_images,
                used_images
            )
            
            matches.append(match)
            
            # Incrementar contador de uso
            image_path = match.image.path
            used_images[image_path] = used_images.get(image_path, 0) + 1
        
        # Log estatísticas
        unique_images = len(used_images)
        total_uses = len(matches)
        avg_confidence = sum(m.confidence_score for m in matches) / len(matches)
        
        logger.info(
            f"Matching complete: {unique_images} unique images used, "
            f"{total_uses} total uses, avg confidence: {avg_confidence:.2f}"
        )
        
        return matches
    
    async def _match_segment_to_image(
        self,
        segment: TranscriptionSegment,
        available_images: List[ImageInfo],
        used_images: Dict[str, int]
    ) -> ImageMatch:
        """
        Encontra a melhor imagem para um segmento específico
        
        Args:
            segment: Segmento de transcrição
            available_images: Imagens disponíveis
            used_images: Dicionário com contagem de uso de cada imagem
            
        Returns:
            ImageMatch com a melhor correspondência
        """
        # Tentar match com Ollama
        best_image, confidence = await self._ollama_match(segment, available_images)
        
        # Se confidence muito baixa, usar fallback
        if confidence < self.min_confidence:
            logger.warning(
                f"Low confidence ({confidence:.2f}) for segment: {segment.text[:30]}... "
                "Using fallback strategy"
            )
            best_image, confidence = self._fallback_match(
                segment,
                available_images,
                used_images
            )
        
        return ImageMatch(
            segment=segment,
            image=best_image,
            confidence_score=confidence
        )
    
    async def _ollama_match(
        self,
        segment: TranscriptionSegment,
        available_images: List[ImageInfo]
    ) -> Tuple[ImageInfo, float]:
        """
        Usa Ollama para fazer matching semântico
        
        Returns:
            Tuple (melhor_imagem, confidence_score)
        """
        # Preparar lista de imagens para o prompt
        image_list = "\n".join([
            f"{i+1}. {img.filename} (keywords: {', '.join(img.keywords)})"
            for i, img in enumerate(available_images[:20])  # Limitar a 20 para o prompt
        ])
        
        prompt = f"""Você está ajudando a criar um vídeo sincronizado com narração.

Texto falado: "{segment.text}"

Imagens disponíveis:
{image_list}

Qual imagem é mais relevante para o texto? 
Responda APENAS com: número|score

Onde:
- número: o número da imagem (1-{min(len(available_images), 20)})
- score: confiança de 0.0 a 1.0

Exemplo: 3|0.85

Se nenhuma imagem for relevante, use score baixo (0.1-0.3) e escolha a mais genérica."""
        
        try:
            # Chamar Ollama em thread separada
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: ollama.generate(
                    model=settings.OLLAMA_MODEL,
                    prompt=prompt,
                    options={"temperature": 0.3}  # Baixa temperatura para respostas mais determinísticas
                )
            )
            
            # Parsear resposta
            response_text = response['response'].strip()
            logger.debug(f"Ollama response: {response_text}")
            
            # Extrair número e score
            match = re.search(r'(\d+)\s*\|\s*([\d.]+)', response_text)
            if match:
                image_idx = int(match.group(1)) - 1  # Convert to 0-indexed
                score = float(match.group(2))
                
                # Validar índice
                if 0 <= image_idx < len(available_images):
                    return available_images[image_idx], score
                else:
                    logger.warning(f"Invalid image index: {image_idx}")
            else:
                logger.warning(f"Could not parse Ollama response: {response_text}")
        
        except Exception as e:
            logger.error(f"Ollama matching failed: {e}")
        
        # Fallback: primeira imagem com score baixo
        return available_images[0], 0.2
    
    def _fallback_match(
        self,
        segment: TranscriptionSegment,
        available_images: List[ImageInfo],
        used_images: Dict[str, int]
    ) -> Tuple[ImageInfo, float]:
        """
        Estratégia de fallback quando Ollama falha ou retorna score baixo
        
        Prioriza:
        1. Imagens menos usadas
        2. Similaridade léxica simples
        """
        # Calcular scores simples baseado em keywords
        scores = []
        for img in available_images:
            # Score base: penaliza imagens já usadas
            usage_count = used_images.get(img.path, 0)
            usage_penalty = 1.0 / (1 + usage_count * 0.5)
            
            # Score de keywords: conta quantas keywords da imagem aparecem no texto
            segment_text_lower = segment.text.lower()
            keyword_matches = sum(
                1 for keyword in img.keywords
                if keyword in segment_text_lower
            )
            keyword_score = keyword_matches / max(len(img.keywords), 1)
            
            # Score final
            final_score = usage_penalty * (0.3 + keyword_score * 0.7)
            scores.append((img, final_score))
        
        # Ordenar por score
        scores.sort(key=lambda x: x[1], reverse=True)
        
        best_image, best_score = scores[0]
        
        logger.debug(
            f"Fallback selected: {best_image.filename} "
            f"(score: {best_score:.2f}, usage: {used_images.get(best_image.path, 0)})"
        )
        
        return best_image, min(best_score, 0.5)  # Cap at 0.5 for fallback

