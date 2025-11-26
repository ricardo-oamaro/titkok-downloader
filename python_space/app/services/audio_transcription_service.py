import logging
from pathlib import Path
from typing import List, Optional
import asyncio
from functools import partial

from app.models.story_video_schemas import TranscriptionSegment

logger = logging.getLogger(__name__)


class AudioTranscriptionService:
    """Serviço para transcrição de áudio usando Whisper"""
    
    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8"
    ):
        """
        Inicializa o serviço de transcrição
        
        Args:
            model_size: Tamanho do modelo (tiny, base, small, medium, large)
            device: Dispositivo (cpu, cuda)
            compute_type: Tipo de computação (int8, float16, float32)
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model = None
    
    def _load_model(self):
        """Carrega o modelo Whisper (lazy loading)"""
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
                logger.info(f"Loading Whisper model: {self.model_size}")
                self._model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type
                )
                logger.info("Whisper model loaded successfully")
            except ImportError:
                logger.error("faster-whisper not installed. Install with: pip install faster-whisper")
                raise
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                raise
        return self._model
    
    async def transcribe_audio(
        self,
        audio_path: Path,
        language: Optional[str] = None
    ) -> List[TranscriptionSegment]:
        """
        Transcreve áudio e retorna segmentos com timestamps
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            language: Idioma (pt, en, es, etc). None para detecção automática
        
        Returns:
            Lista de TranscriptionSegment com texto e timestamps
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        logger.info(f"Transcribing audio: {audio_path}")
        
        # Executar transcrição em thread separada (blocking I/O)
        loop = asyncio.get_event_loop()
        transcribe_func = partial(self._transcribe_sync, audio_path, language)
        segments = await loop.run_in_executor(None, transcribe_func)
        
        logger.info(f"Transcription complete: {len(segments)} segments")
        return segments
    
    def _transcribe_sync(
        self,
        audio_path: Path,
        language: Optional[str]
    ) -> List[TranscriptionSegment]:
        """Transcrição síncrona (blocking)"""
        model = self._load_model()
        
        # Parâmetros de transcrição
        transcribe_params = {
            "audio": str(audio_path),
            "language": language,
            "word_timestamps": False,  # Timestamps por segmento (mais rápido)
            "vad_filter": True,  # Voice Activity Detection
            "vad_parameters": {
                "threshold": 0.5,
                "min_speech_duration_ms": 250,
            }
        }
        
        segments_result, info = model.transcribe(**transcribe_params)
        
        logger.info(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
        
        # Converter segmentos para nosso modelo
        segments = []
        for segment in segments_result:
            # Extrair keywords básicas (palavras > 3 caracteres)
            words = segment.text.lower().split()
            keywords = [w.strip('.,!?;:') for w in words if len(w.strip('.,!?;:')) > 3]
            
            seg = TranscriptionSegment(
                text=segment.text.strip(),
                start_time=segment.start,
                end_time=segment.end,
                keywords=keywords
            )
            segments.append(seg)
            
            logger.debug(f"[{seg.start_time:.1f}s - {seg.end_time:.1f}s] {seg.text}")
        
        return segments
    
    def get_audio_duration(self, audio_path: Path) -> float:
        """
        Obtém duração do áudio em segundos
        
        Args:
            audio_path: Caminho do arquivo de áudio
            
        Returns:
            Duração em segundos
        """
        try:
            import soundfile as sf
            info = sf.info(str(audio_path))
            return info.duration
        except ImportError:
            logger.warning("soundfile not installed, falling back to moviepy")
            try:
                from moviepy.editor import AudioFileClip
                audio = AudioFileClip(str(audio_path))
                duration = audio.duration
                audio.close()
                return duration
            except Exception as e:
                logger.error(f"Failed to get audio duration: {e}")
                raise

