"""
Video Analysis Service - Detecta momentos-chave e características do vídeo
"""
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple
import logging
from app.models.video_edit_schemas import KeyMoment, AnalysisResult

logger = logging.getLogger(__name__)


class VideoAnalyzerService:
    """Serviço para análise de vídeos e detecção de momentos-chave"""
    
    def __init__(self):
        self.scene_threshold = 30.0  # Threshold para mudança de cena
        self.motion_threshold = 0.3  # Threshold para detecção de movimento
    
    async def analyze_video(self, video_path: Path) -> AnalysisResult:
        """
        Analisa vídeo e retorna características e momentos-chave
        
        Args:
            video_path: Caminho do vídeo
            
        Returns:
            AnalysisResult com dados da análise
        """
        try:
            cap = cv2.VideoCapture(str(video_path))
            
            # Extrair informações básicas
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Detectar momentos-chave
            key_moments = await self._detect_key_moments(cap, fps)
            scene_changes = await self._detect_scene_changes(cap, fps)
            
            # Calcular métricas
            avg_brightness = await self._calculate_average_brightness(cap)
            motion_intensity = await self._calculate_motion_intensity(cap)
            
            cap.release()
            
            return AnalysisResult(
                video_path=str(video_path),
                duration=duration,
                resolution=f"{width}x{height}",
                fps=fps,
                has_audio=self._has_audio(video_path),
                key_moments=key_moments,
                scene_changes=scene_changes,
                average_brightness=avg_brightness,
                motion_intensity=motion_intensity
            )
            
        except Exception as e:
            logger.error(f"Erro ao analisar vídeo {video_path}: {e}")
            raise
    
    async def _detect_key_moments(
        self,
        cap: cv2.VideoCapture,
        fps: float
    ) -> List[KeyMoment]:
        """Detecta momentos-chave no vídeo"""
        key_moments = []
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        frame_idx = 0
        prev_frame = None
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Converter para escala de cinza
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detectar mudança de cena
            if prev_frame is not None:
                diff = cv2.absdiff(gray, prev_frame)
                mean_diff = np.mean(diff)
                
                if mean_diff > self.scene_threshold:
                    timestamp = frame_idx / fps
                    key_moments.append(KeyMoment(
                        timestamp=timestamp,
                        type="scene_change",
                        confidence=min(mean_diff / 100.0, 1.0),
                        description=f"Scene change at {timestamp:.2f}s"
                    ))
            
            prev_frame = gray
            frame_idx += 1
            
            # Processar apenas a cada 10 frames para performance
            if frame_idx % 10 != 0:
                continue
        
        return key_moments[:20]  # Limitar a 20 momentos-chave
    
    async def _detect_scene_changes(
        self,
        cap: cv2.VideoCapture,
        fps: float
    ) -> List[float]:
        """Detecta timestamps de mudanças de cena"""
        scene_changes = []
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        frame_idx = 0
        prev_frame = None
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if prev_frame is not None:
                diff = cv2.absdiff(gray, prev_frame)
                mean_diff = np.mean(diff)
                
                if mean_diff > self.scene_threshold:
                    timestamp = frame_idx / fps
                    scene_changes.append(round(timestamp, 2))
            
            prev_frame = gray
            frame_idx += 10  # Skip frames
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        
        return scene_changes[:15]  # Limitar a 15 mudanças
    
    async def _calculate_average_brightness(
        self,
        cap: cv2.VideoCapture
    ) -> float:
        """Calcula brilho médio do vídeo"""
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        brightness_values = []
        
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        sample_frames = min(20, frame_count)  # Sample 20 frames
        step = max(1, frame_count // sample_frames)
        
        for i in range(0, frame_count, step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                brightness_values.append(np.mean(gray))
        
        return float(np.mean(brightness_values)) if brightness_values else 0.0
    
    async def _calculate_motion_intensity(
        self,
        cap: cv2.VideoCapture
    ) -> float:
        """Calcula intensidade de movimento no vídeo (0-1)"""
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        motion_values = []
        
        prev_frame = None
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        sample_frames = min(30, frame_count)
        step = max(1, frame_count // sample_frames)
        
        for i in range(0, frame_count, step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                if prev_frame is not None:
                    diff = cv2.absdiff(gray, prev_frame)
                    motion_values.append(np.mean(diff))
                
                prev_frame = gray
        
        if motion_values:
            avg_motion = np.mean(motion_values)
            # Normalizar para 0-1
            return min(avg_motion / 50.0, 1.0)
        return 0.0
    
    def _has_audio(self, video_path: Path) -> bool:
        """Verifica se o vídeo tem áudio"""
        try:
            # Simples verificação com opencv (não é 100% precisa)
            cap = cv2.VideoCapture(str(video_path))
            # OpenCV não detecta áudio diretamente, retornar True por padrão
            # Em produção, usar ffprobe ou moviepy para detecção precisa
            cap.release()
            return True
        except:
            return False
    
    async def find_best_cuts(
        self,
        video_path: Path,
        target_duration: int
    ) -> List[Tuple[float, float]]:
        """
        Encontra os melhores cortes para atingir duração alvo
        
        Args:
            video_path: Caminho do vídeo
            target_duration: Duração desejada em segundos
            
        Returns:
            Lista de tuplas (start_time, end_time)
        """
        analysis = await self.analyze_video(video_path)
        
        if analysis.duration <= target_duration:
            # Vídeo já está dentro da duração alvo
            return [(0.0, analysis.duration)]
        
        # Usar mudanças de cena para criar cortes inteligentes
        scene_changes = analysis.scene_changes
        
        if not scene_changes:
            # Se não há mudanças de cena, dividir igualmente
            num_segments = int(analysis.duration / target_duration) + 1
            segment_duration = analysis.duration / num_segments
            return [(i * segment_duration, (i + 1) * segment_duration) 
                    for i in range(num_segments)]
        
        # Selecionar os segmentos mais dinâmicos
        cuts = []
        current_time = 0.0
        remaining_duration = target_duration
        
        for scene_time in scene_changes:
            if remaining_duration <= 0:
                break
            
            segment_duration = min(
                scene_time - current_time,
                remaining_duration
            )
            
            if segment_duration > 1.0:  # Mínimo de 1 segundo
                cuts.append((current_time, current_time + segment_duration))
                remaining_duration -= segment_duration
                current_time = scene_time
        
        return cuts if cuts else [(0.0, target_duration)]

