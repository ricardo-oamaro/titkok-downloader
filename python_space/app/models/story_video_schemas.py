from pydantic import BaseModel, Field
from typing import List, Tuple, Optional
from pathlib import Path


class TranscriptionSegment(BaseModel):
    """Segmento de transcrição com timestamps"""
    text: str = Field(..., description="Texto transcrito")
    start_time: float = Field(..., description="Tempo de início em segundos")
    end_time: float = Field(..., description="Tempo de fim em segundos")
    keywords: List[str] = Field(default_factory=list, description="Palavras-chave extraídas")


class ImageInfo(BaseModel):
    """Informações sobre uma imagem disponível"""
    path: str = Field(..., description="Caminho completo da imagem")
    filename: str = Field(..., description="Nome do arquivo")
    keywords: List[str] = Field(default_factory=list, description="Keywords extraídas do nome")


class ImageMatch(BaseModel):
    """Resultado do matching entre segmento e imagem"""
    segment: TranscriptionSegment = Field(..., description="Segmento de transcrição")
    image: ImageInfo = Field(..., description="Imagem selecionada")
    confidence_score: float = Field(..., description="Score de confiança (0-1)")


class TimelineItem(BaseModel):
    """Item da timeline do vídeo"""
    start_time: float = Field(..., description="Início em segundos")
    end_time: float = Field(..., description="Fim em segundos")
    image_path: str = Field(..., description="Caminho da imagem")
    confidence: float = Field(..., description="Confiança do match")


class StoryVideoRequest(BaseModel):
    """Requisição para criar vídeo a partir de narração"""
    images_dir: str = Field(..., description="Diretório com as imagens")
    audio_file: str = Field(..., description="Arquivo de áudio com narração")
    style: str = Field(default="smooth", description="Estilo de edição (smooth, dynamic, ken_burns)")
    resolution: Tuple[int, int] = Field(default=(1080, 1920), description="Resolução do vídeo (width, height)")


class StoryVideoResult(BaseModel):
    """Resultado da criação do vídeo"""
    video_path: str = Field(..., description="Caminho do vídeo gerado")
    duration: float = Field(..., description="Duração total em segundos")
    segments_count: int = Field(..., description="Número de segmentos transcritos")
    images_used: int = Field(..., description="Número total de imagens usadas")
    unique_images: int = Field(..., description="Número de imagens únicas")
    timeline: List[TimelineItem] = Field(default_factory=list, description="Timeline completa")
    average_confidence: float = Field(..., description="Confiança média dos matches")

