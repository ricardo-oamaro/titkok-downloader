"""
Schemas for video editing functionality
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from enum import Enum


class EditStyle(str, Enum):
    """Estilos de edição disponíveis"""
    VIRAL = "viral"  # Cortes rápidos, efeitos trending
    STORYTELLING = "storytelling"  # Legendas completas, transições suaves
    EDUCATIONAL = "educational"  # Texto explicativo, pausas estratégicas
    COMPILATION = "compilation"  # Mix de vários vídeos
    MINIMAL = "minimal"  # Sem efeitos, apenas cortes


class VideoEditRequest(BaseModel):
    """Request para edição de vídeo"""
    video_path: str = Field(..., description="Caminho do vídeo a ser editado")
    style: EditStyle = Field(default=EditStyle.VIRAL, description="Estilo de edição")
    add_subtitles: bool = Field(default=True, description="Adicionar legendas")
    add_music: bool = Field(default=False, description="Adicionar música de fundo")
    add_effects: bool = Field(default=True, description="Adicionar efeitos visuais")
    target_duration: Optional[int] = Field(None, description="Duração alvo em segundos")
    
    class Config:
        json_schema_extra = {
            "example": {
                "video_path": "/path/to/video.mp4",
                "style": "viral",
                "add_subtitles": True,
                "add_music": False,
                "add_effects": True,
                "target_duration": 60
            }
        }


class SubtitleConfig(BaseModel):
    """Configuração de legendas"""
    text: str = Field(..., description="Texto da legenda")
    start_time: float = Field(..., description="Tempo de início em segundos")
    duration: float = Field(default=2.5, description="Duração da legenda")
    style: Literal["bold", "outline", "shadow", "minimal"] = Field(default="bold")
    position: Literal["top", "center", "bottom"] = Field(default="center")


class VideoEffect(BaseModel):
    """Efeito de vídeo"""
    name: str = Field(..., description="Nome do efeito")
    start_time: float = Field(..., description="Tempo de início")
    duration: float = Field(..., description="Duração do efeito")
    intensity: float = Field(default=1.0, ge=0.0, le=1.0, description="Intensidade (0-1)")


class Transition(BaseModel):
    """Transição entre clipes"""
    type: Literal["fade", "dissolve", "wipe", "zoom", "slide"] = Field(default="fade")
    duration: float = Field(default=0.5, description="Duração da transição")
    position: float = Field(..., description="Posição na timeline")


class KeyMoment(BaseModel):
    """Momento-chave detectado no vídeo"""
    timestamp: float = Field(..., description="Timestamp em segundos")
    type: Literal["scene_change", "face_detection", "motion_peak", "silence"] = Field(...)
    confidence: float = Field(ge=0.0, le=1.0, description="Confiança da detecção")
    description: Optional[str] = None


class EditedVideoResult(BaseModel):
    """Resultado da edição de vídeo"""
    video_path: str = Field(..., description="Caminho do vídeo editado")
    original_path: str = Field(..., description="Caminho do vídeo original")
    style_applied: EditStyle = Field(..., description="Estilo aplicado")
    duration_original: float = Field(..., description="Duração original em segundos")
    duration_edited: float = Field(..., description="Duração editada em segundos")
    effects_applied: List[str] = Field(default_factory=list, description="Efeitos aplicados")
    subtitles_count: int = Field(default=0, description="Número de legendas adicionadas")
    file_size_mb: float = Field(..., description="Tamanho do arquivo em MB")
    
    class Config:
        json_schema_extra = {
            "example": {
                "video_path": "/downloads/edited_video.mp4",
                "original_path": "/downloads/video.mp4",
                "style_applied": "viral",
                "duration_original": 45.5,
                "duration_edited": 30.0,
                "effects_applied": ["zoom", "glitch", "speed_ramp"],
                "subtitles_count": 5,
                "file_size_mb": 15.2
            }
        }


class CompilationRequest(BaseModel):
    """Request para criar compilação de vídeos"""
    video_paths: List[str] = Field(..., min_length=2, description="Lista de vídeos")
    theme: str = Field(default="trending", description="Tema da compilação")
    max_duration: int = Field(default=60, description="Duração máxima em segundos")
    add_intro: bool = Field(default=True, description="Adicionar intro")
    add_outro: bool = Field(default=True, description="Adicionar outro")
    
    class Config:
        json_schema_extra = {
            "example": {
                "video_paths": ["/path/video1.mp4", "/path/video2.mp4"],
                "theme": "trending",
                "max_duration": 60,
                "add_intro": True,
                "add_outro": True
            }
        }


class AnalysisResult(BaseModel):
    """Resultado da análise de vídeo"""
    video_path: str
    duration: float
    resolution: str  # "1920x1080"
    fps: float
    has_audio: bool
    key_moments: List[KeyMoment]
    scene_changes: List[float]  # timestamps
    average_brightness: float
    motion_intensity: float  # 0-1

