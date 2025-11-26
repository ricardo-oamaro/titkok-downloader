"""
CapCut Automation Service - Edição automática de vídeos
Usa MoviePy como backend confiável para edição programática
"""
from pathlib import Path
from typing import List, Optional
import logging
from moviepy.editor import (
    VideoFileClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
    AudioFileClip
)
from moviepy.video.fx import all as vfx
import uuid

from app.models.video_edit_schemas import (
    EditStyle,
    VideoEditRequest,
    SubtitleConfig,
    EditedVideoResult,
    CompilationRequest
)
from app.services.video_analyzer_service import VideoAnalyzerService

logger = logging.getLogger(__name__)


class CapCutAutomationService:
    """
    Serviço de automação de edição de vídeos
    Emula funcionalidades do CapCut usando MoviePy
    """
    
    def __init__(self):
        self.analyzer = VideoAnalyzerService()
        self.temp_dir = Path("python_space/downloads/temp")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurações de efeitos por estilo
        self.style_configs = {
            EditStyle.VIRAL: {
                "speed": 1.1,  # Acelerar 10%
                "transitions": True,
                "effects": ["zoom", "fade"],
                "subtitle_style": "bold"
            },
            EditStyle.STORYTELLING: {
                "speed": 0.95,  # Desacelerar 5%
                "transitions": True,
                "effects": ["fade"],
                "subtitle_style": "outline"
            },
            EditStyle.EDUCATIONAL: {
                "speed": 1.0,
                "transitions": False,
                "effects": [],
                "subtitle_style": "shadow"
            },
            EditStyle.MINIMAL: {
                "speed": 1.0,
                "transitions": False,
                "effects": [],
                "subtitle_style": "minimal"
            }
        }
    
    async def edit_video(
        self,
        video_path: Path,
        comments: List[dict],
        metadata: dict,
        style: EditStyle = EditStyle.VIRAL,
        add_subtitles: bool = True,
        target_duration: Optional[int] = None
    ) -> EditedVideoResult:
        """
        Edita vídeo automaticamente aplicando:
        - Cortes inteligentes
        - Legendas dos comentários
        - Efeitos visuais
        - Transições
        
        Args:
            video_path: Caminho do vídeo original
            comments: Lista de comentários gerados
            metadata: Metadados do vídeo
            style: Estilo de edição
            add_subtitles: Se deve adicionar legendas
            target_duration: Duração alvo em segundos
            
        Returns:
            EditedVideoResult com informações do vídeo editado
        """
        try:
            logger.info(f"Iniciando edição de vídeo: {video_path} (estilo: {style})")
            
            # Carregar vídeo
            clip = VideoFileClip(str(video_path))
            original_duration = clip.duration
            
            # Aplicar cortes se necessário
            if target_duration and target_duration < original_duration:
                cuts = await self.analyzer.find_best_cuts(video_path, target_duration)
                clip = await self._apply_cuts(clip, cuts)
            
            # Aplicar configurações de estilo
            config = self.style_configs[style]
            effects_applied = []
            
            # Ajustar velocidade
            if config["speed"] != 1.0:
                clip = clip.fx(vfx.speedx, config["speed"])
                effects_applied.append(f"speed_{config['speed']}x")
            
            # Aplicar efeitos
            if "zoom" in config["effects"]:
                clip = await self._apply_zoom_effect(clip)
                effects_applied.append("zoom")
            
            if "fade" in config["effects"]:
                clip = clip.fadein(0.5).fadeout(0.5)
                effects_applied.append("fade")
            
            # Adicionar legendas
            subtitles_count = 0
            if add_subtitles and comments:
                clip, subtitles_count = await self._add_subtitles(
                    clip,
                    comments[:5],  # Top 5 comentários
                    config["subtitle_style"]
                )
                effects_applied.append(f"subtitles_{subtitles_count}")
            
            # Adicionar marca d'água
            clip = await self._add_watermark(clip, metadata.get('author', ''))
            
            # Exportar vídeo editado
            output_filename = f"edited_{uuid.uuid4().hex[:8]}_{video_path.name}"
            output_path = self.temp_dir / output_filename
            
            clip.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                fps=30,
                preset='medium',
                threads=4
            )
            
            clip.close()
            
            # Calcular tamanho do arquivo
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            
            result = EditedVideoResult(
                video_path=str(output_path),
                original_path=str(video_path),
                style_applied=style,
                duration_original=original_duration,
                duration_edited=VideoFileClip(str(output_path)).duration,
                effects_applied=effects_applied,
                subtitles_count=subtitles_count,
                file_size_mb=round(file_size_mb, 2)
            )
            
            logger.info(f"Vídeo editado com sucesso: {output_path}")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao editar vídeo: {e}")
            raise
    
    async def _apply_cuts(
        self,
        clip: VideoFileClip,
        cuts: List[tuple]
    ) -> VideoFileClip:
        """Aplica cortes no vídeo"""
        segments = []
        for start, end in cuts:
            segment = clip.subclip(start, end)
            segments.append(segment)
        
        if len(segments) > 1:
            return concatenate_videoclips(segments, method="compose")
        return segments[0] if segments else clip
    
    async def _apply_zoom_effect(
        self,
        clip: VideoFileClip,
        zoom_factor: float = 1.1
    ) -> VideoFileClip:
        """Aplica efeito de zoom sutil"""
        try:
            # Zoom gradual do início ao fim
            def zoom(get_frame, t):
                frame = get_frame(t)
                # Zoom progressivo baseado no tempo
                progress = t / clip.duration
                current_zoom = 1.0 + (zoom_factor - 1.0) * progress
                
                h, w = frame.shape[:2]
                new_h, new_w = int(h / current_zoom), int(w / current_zoom)
                
                # Centralizar o crop
                top = (h - new_h) // 2
                left = (w - new_w) // 2
                
                cropped = frame[top:top+new_h, left:left+new_w]
                # Redimensionar de volta ao tamanho original
                import cv2
                resized = cv2.resize(cropped, (w, h))
                return resized
            
            return clip.fl(zoom)
        except Exception as e:
            logger.warning(f"Erro ao aplicar zoom: {e}, retornando clip original")
            return clip
    
    async def _add_subtitles(
        self,
        clip: VideoFileClip,
        comments: List[dict],
        style: str
    ) -> tuple[VideoFileClip, int]:
        """Adiciona legendas ao vídeo"""
        try:
            duration_per_subtitle = clip.duration / len(comments)
            subtitle_clips = []
            
            for i, comment in enumerate(comments):
                start_time = i * duration_per_subtitle
                
                # Criar texto da legenda
                text = comment.get('text', comment.get('comment', ''))
                if len(text) > 80:
                    text = text[:77] + "..."
                
                # Configurações de estilo
                font_configs = {
                    "bold": {"fontsize": 40, "color": "white", "stroke_color": "black", "stroke_width": 2},
                    "outline": {"fontsize": 38, "color": "white", "stroke_color": "blue", "stroke_width": 3},
                    "shadow": {"fontsize": 36, "color": "yellow", "stroke_color": "black", "stroke_width": 1},
                    "minimal": {"fontsize": 32, "color": "white", "stroke_color": None, "stroke_width": 0}
                }
                
                config = font_configs.get(style, font_configs["bold"])
                
                # Criar clip de texto
                txt_clip = TextClip(
                    text,
                    fontsize=config["fontsize"],
                    color=config["color"],
                    stroke_color=config["stroke_color"],
                    stroke_width=config["stroke_width"],
                    font='Arial-Bold',
                    method='caption',
                    size=(clip.w * 0.8, None)
                ).set_start(start_time).set_duration(min(2.5, duration_per_subtitle))
                
                # Posicionar na parte inferior
                txt_clip = txt_clip.set_position(('center', clip.h * 0.75))
                subtitle_clips.append(txt_clip)
            
            # Compor vídeo com legendas
            final_clip = CompositeVideoClip([clip] + subtitle_clips)
            return final_clip, len(subtitle_clips)
            
        except Exception as e:
            logger.warning(f"Erro ao adicionar legendas: {e}, retornando clip sem legendas")
            return clip, 0
    
    async def _add_watermark(
        self,
        clip: VideoFileClip,
        author: str
    ) -> VideoFileClip:
        """Adiciona marca d'água discreta"""
        try:
            watermark_text = f"@{author}" if author else "TikTok"
            
            txt_clip = TextClip(
                watermark_text,
                fontsize=24,
                color='white',
                font='Arial',
                stroke_color='black',
                stroke_width=1
            ).set_duration(clip.duration)
            
            # Posicionar no canto superior direito
            txt_clip = txt_clip.set_position((clip.w * 0.75, 20))
            
            return CompositeVideoClip([clip, txt_clip])
            
        except Exception as e:
            logger.warning(f"Erro ao adicionar watermark: {e}")
            return clip
    
    async def create_compilation(
        self,
        video_paths: List[Path],
        theme: str = "trending",
        max_duration: int = 60
    ) -> EditedVideoResult:
        """
        Cria compilação de múltiplos vídeos
        
        Args:
            video_paths: Lista de caminhos dos vídeos
            theme: Tema da compilação
            max_duration: Duração máxima em segundos
            
        Returns:
            EditedVideoResult da compilação
        """
        try:
            logger.info(f"Criando compilação de {len(video_paths)} vídeos")
            
            clips = []
            total_duration = 0
            
            for video_path in video_paths:
                if total_duration >= max_duration:
                    break
                
                clip = VideoFileClip(str(video_path))
                remaining = max_duration - total_duration
                
                if clip.duration > remaining:
                    clip = clip.subclip(0, remaining)
                
                # Adicionar transição fade
                clip = clip.fadein(0.5).fadeout(0.5)
                clips.append(clip)
                total_duration += clip.duration
            
            # Concatenar vídeos
            final_clip = concatenate_videoclips(clips, method="compose")
            
            # Exportar
            output_filename = f"compilation_{theme}_{uuid.uuid4().hex[:8]}.mp4"
            output_path = self.temp_dir / output_filename
            
            final_clip.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                fps=30
            )
            
            final_clip.close()
            for clip in clips:
                clip.close()
            
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            
            return EditedVideoResult(
                video_path=str(output_path),
                original_path=str(video_paths[0]),
                style_applied=EditStyle.COMPILATION,
                duration_original=sum(VideoFileClip(str(p)).duration for p in video_paths),
                duration_edited=total_duration,
                effects_applied=["compilation", "fade_transitions"],
                subtitles_count=0,
                file_size_mb=round(file_size_mb, 2)
            )
            
        except Exception as e:
            logger.error(f"Erro ao criar compilação: {e}")
            raise

