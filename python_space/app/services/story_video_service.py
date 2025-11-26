import logging
import uuid
from pathlib import Path
from typing import List, Tuple, Dict
import numpy as np
from PIL import Image
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from moviepy.video.fx.all import fadein, fadeout

from app.models.story_video_schemas import (
    TranscriptionSegment,
    ImageInfo,
    ImageMatch,
    TimelineItem,
    StoryVideoResult
)
from app.services.audio_transcription_service import AudioTranscriptionService
from app.services.image_matcher_service import ImageMatcherService
from app.config import settings

logger = logging.getLogger(__name__)


class StoryVideoService:
    """Serviço principal para criar vídeos a partir de narração + imagens"""
    
    def __init__(self):
        self.temp_dir = Path(settings.DOWNLOADS_DIR) / "story_videos"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        self.transcription_service = AudioTranscriptionService(
            model_size=getattr(settings, 'WHISPER_MODEL', 'base'),
            device=getattr(settings, 'WHISPER_DEVICE', 'cpu'),
            compute_type=getattr(settings, 'WHISPER_COMPUTE_TYPE', 'int8')
        )
        
        self.matcher_service = ImageMatcherService(min_confidence=0.3)
    
    async def create_story_video(
        self,
        images_dir: Path,
        audio_file: Path,
        style: str = "smooth",
        resolution: Tuple[int, int] = (1080, 1920)
    ) -> StoryVideoResult:
        """
        Cria vídeo completo a partir de narração e imagens
        
        Args:
            images_dir: Diretório com imagens
            audio_file: Arquivo de áudio com narração
            style: Estilo de edição (smooth, dynamic, ken_burns)
            resolution: Resolução do vídeo (width, height)
            
        Returns:
            StoryVideoResult com informações do vídeo criado
        """
        logger.info(f"Creating story video: audio={audio_file}, images={images_dir}, style={style}")
        
        # 1. Validar arquivos
        if not images_dir.exists():
            raise FileNotFoundError(f"Images directory not found: {images_dir}")
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file}")
        
        # 2. Transcrever áudio
        logger.info("Step 1/5: Transcribing audio...")
        segments = await self.transcription_service.transcribe_audio(audio_file)
        
        if not segments:
            raise ValueError("No speech segments found in audio")
        
        # 3. Encontrar imagens disponíveis
        logger.info("Step 2/5: Finding available images...")
        available_images = self.matcher_service.find_images(images_dir)
        
        if not available_images:
            raise ValueError(f"No images found in {images_dir}")
        
        # 4. Fazer matching inteligente
        logger.info("Step 3/5: Matching segments with images using AI...")
        matches = await self.matcher_service.find_best_matches(segments, available_images)
        
        # 5. Construir timeline
        logger.info("Step 4/5: Building video timeline...")
        timeline = self._build_timeline(matches)
        
        # 6. Gerar vídeo
        logger.info("Step 5/5: Generating video with MoviePy...")
        output_path = self.temp_dir / f"story_video_{uuid.uuid4().hex[:8]}.mp4"
        
        audio_duration = self.transcription_service.get_audio_duration(audio_file)
        
        await self._generate_video(
            timeline=timeline,
            audio_file=audio_file,
            output_path=output_path,
            style=style,
            resolution=resolution
        )
        
        # 7. Calcular estatísticas
        unique_images = len(set(item.image_path for item in timeline))
        avg_confidence = sum(item.confidence for item in timeline) / len(timeline)
        
        result = StoryVideoResult(
            video_path=str(output_path),
            duration=audio_duration,
            segments_count=len(segments),
            images_used=len(timeline),
            unique_images=unique_images,
            timeline=timeline,
            average_confidence=avg_confidence
        )
        
        logger.info(
            f"Story video created successfully: {output_path.name} "
            f"({unique_images} unique images, {len(timeline)} segments, "
            f"avg confidence: {avg_confidence:.2f})"
        )
        
        return result
    
    def _build_timeline(self, matches: List[ImageMatch]) -> List[TimelineItem]:
        """
        Constrói timeline do vídeo a partir dos matches
        
        Args:
            matches: Lista de ImageMatch
            
        Returns:
            Lista de TimelineItem ordenada por tempo
        """
        timeline = []
        
        for match in matches:
            item = TimelineItem(
                start_time=match.segment.start_time,
                end_time=match.segment.end_time,
                image_path=match.image.path,
                confidence=match.confidence_score
            )
            timeline.append(item)
        
        # Ordenar por tempo (já deve estar ordenado, mas garantir)
        timeline.sort(key=lambda x: x.start_time)
        
        # Log da timeline
        logger.debug("Video timeline:")
        for i, item in enumerate(timeline):
            duration = item.end_time - item.start_time
            logger.debug(
                f"  {i+1}. [{item.start_time:.1f}s - {item.end_time:.1f}s] "
                f"({duration:.1f}s) {Path(item.image_path).name} "
                f"(confidence: {item.confidence:.2f})"
            )
        
        return timeline
    
    async def _generate_video(
        self,
        timeline: List[TimelineItem],
        audio_file: Path,
        output_path: Path,
        style: str,
        resolution: Tuple[int, int]
    ):
        """
        Gera o vídeo final usando MoviePy
        
        Args:
            timeline: Timeline com imagens e timestamps
            audio_file: Arquivo de áudio
            output_path: Onde salvar o vídeo
            style: Estilo de edição
            resolution: Resolução do vídeo
        """
        # Carregar áudio
        audio = AudioFileClip(str(audio_file))
        
        # Criar clips para cada item da timeline
        clips = []
        for i, item in enumerate(timeline):
            duration = item.end_time - item.start_time
            
            # Criar clip de imagem
            clip = self._create_image_clip(
                image_path=Path(item.image_path),
                duration=duration,
                resolution=resolution,
                style=style,
                position=i
            )
            
            clips.append(clip)
        
        # Concatenar todos os clips
        logger.info(f"Concatenating {len(clips)} clips...")
        final_video = concatenate_videoclips(clips, method="compose")
        
        # Adicionar áudio
        final_video = final_video.set_audio(audio)
        
        # Aplicar fade geral no início e fim
        final_video = fadein(final_video, 0.5)
        final_video = fadeout(final_video, 0.5)
        
        # Exportar
        logger.info(f"Exporting video to {output_path}...")
        final_video.write_videofile(
            str(output_path),
            fps=30,
            codec='libx264',
            audio_codec='aac',
            preset='medium',
            threads=4,
            logger=None  # Suprimir logs verbosos do MoviePy
        )
        
        # Cleanup
        audio.close()
        final_video.close()
        for clip in clips:
            clip.close()
        
        logger.info("Video export complete")
    
    def _create_image_clip(
        self,
        image_path: Path,
        duration: float,
        resolution: Tuple[int, int],
        style: str,
        position: int
    ) -> ImageClip:
        """
        Cria um clip de imagem com efeitos
        
        Args:
            image_path: Caminho da imagem
            duration: Duração do clip em segundos
            resolution: Resolução alvo (width, height)
            style: Estilo de edição
            position: Posição na sequência (para alternar efeitos)
            
        Returns:
            ImageClip com efeitos aplicados
        """
        # Carregar e ajustar imagem
        img = Image.open(image_path)
        img = self._fit_image_to_resolution(img, resolution)
        
        # Criar clip
        clip = ImageClip(np.array(img), duration=duration)
        clip = clip.set_fps(30)
        
        # Aplicar efeitos baseado no estilo
        if style == "smooth":
            # Transições suaves e longas
            fade_duration = min(0.5, duration * 0.3)
            clip = fadein(clip, fade_duration)
            clip = fadeout(clip, fade_duration)
        
        elif style == "dynamic":
            # Transições rápidas + zoom leve
            fade_duration = min(0.3, duration * 0.2)
            clip = fadein(clip, fade_duration)
            clip = fadeout(clip, fade_duration)
            # Adicionar zoom sutil
            clip = clip.resize(lambda t: 1 + 0.05 * (t / duration))
        
        elif style == "ken_burns":
            # Efeito Ken Burns (zoom + pan)
            fade_duration = min(0.4, duration * 0.25)
            clip = fadein(clip, fade_duration)
            clip = fadeout(clip, fade_duration)
            
            # Alternar entre zoom in e zoom out
            if position % 2 == 0:
                # Zoom in
                clip = clip.resize(lambda t: 1 + 0.15 * (t / duration))
            else:
                # Zoom out
                clip = clip.resize(lambda t: 1.15 - 0.15 * (t / duration))
        
        else:
            # Default: fade simples
            fade_duration = min(0.3, duration * 0.2)
            clip = fadein(clip, fade_duration)
            clip = fadeout(clip, fade_duration)
        
        return clip
    
    def _fit_image_to_resolution(
        self,
        img: Image.Image,
        resolution: Tuple[int, int]
    ) -> Image.Image:
        """
        Ajusta imagem para caber na resolução mantendo aspect ratio
        
        Usa estratégia de "cover" - redimensiona para cobrir toda a área
        e faz crop no centro se necessário
        
        Args:
            img: Imagem PIL
            resolution: Resolução alvo (width, height)
            
        Returns:
            Imagem ajustada
        """
        target_w, target_h = resolution
        img_w, img_h = img.size
        
        # Calcular scale para cobrir toda a área (usar o maior)
        scale_w = target_w / img_w
        scale_h = target_h / img_h
        scale = max(scale_w, scale_h)
        
        # Redimensionar
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Crop para a resolução exata (centralizado)
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        img = img.crop((left, top, left + target_w, top + target_h))
        
        return img

