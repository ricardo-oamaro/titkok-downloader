import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from app.services.audio_transcription_service import AudioTranscriptionService
from app.models.story_video_schemas import TranscriptionSegment


@pytest.fixture
def transcription_service():
    """Fixture para o serviço de transcrição"""
    return AudioTranscriptionService(model_size="tiny", device="cpu", compute_type="int8")


@pytest.fixture
def mock_audio_file(tmp_path):
    """Cria um arquivo de áudio mock"""
    audio_file = tmp_path / "test_audio.mp3"
    audio_file.write_text("mock audio content")
    return audio_file


@pytest.fixture
def mock_whisper_segments():
    """Mock de segmentos retornados pelo Whisper"""
    segment1 = Mock()
    segment1.text = "Olá, este é o primeiro segmento do áudio."
    segment1.start = 0.0
    segment1.end = 3.5
    
    segment2 = Mock()
    segment2.text = "Aqui temos o segundo segmento com mais informações."
    segment2.start = 3.5
    segment2.end = 8.2
    
    return [segment1, segment2]


@pytest.mark.asyncio
async def test_transcribe_audio_success(transcription_service, mock_audio_file, mock_whisper_segments):
    """Testa transcrição bem-sucedida de áudio"""
    mock_model = MagicMock()
    mock_info = Mock()
    mock_info.language = "pt"
    mock_info.language_probability = 0.95
    
    mock_model.transcribe.return_value = (mock_whisper_segments, mock_info)
    
    with patch.object(transcription_service, '_load_model', return_value=mock_model):
        segments = await transcription_service.transcribe_audio(mock_audio_file)
    
    assert len(segments) == 2
    assert isinstance(segments[0], TranscriptionSegment)
    assert segments[0].text == "Olá, este é o primeiro segmento do áudio."
    assert segments[0].start_time == 0.0
    assert segments[0].end_time == 3.5
    assert len(segments[0].keywords) > 0
    
    assert segments[1].text == "Aqui temos o segundo segmento com mais informações."
    assert segments[1].start_time == 3.5
    assert segments[1].end_time == 8.2


@pytest.mark.asyncio
async def test_transcribe_audio_file_not_found(transcription_service):
    """Testa erro quando arquivo de áudio não existe"""
    fake_path = Path("/nonexistent/audio.mp3")
    
    with pytest.raises(FileNotFoundError):
        await transcription_service.transcribe_audio(fake_path)


@pytest.mark.asyncio
async def test_transcribe_extracts_keywords(transcription_service, mock_audio_file):
    """Testa extração de keywords dos segmentos"""
    mock_segment = Mock()
    mock_segment.text = "Este é um teste com palavras importantes e relevantes"
    mock_segment.start = 0.0
    mock_segment.end = 5.0
    
    mock_model = MagicMock()
    mock_info = Mock()
    mock_info.language = "pt"
    mock_info.language_probability = 0.9
    
    mock_model.transcribe.return_value = ([mock_segment], mock_info)
    
    with patch.object(transcription_service, '_load_model', return_value=mock_model):
        segments = await transcription_service.transcribe_audio(mock_audio_file)
    
    # Deve extrair palavras > 3 caracteres
    keywords = segments[0].keywords
    assert "teste" in keywords
    assert "palavras" in keywords
    assert "importantes" in keywords
    assert "relevantes" in keywords
    # Palavras curtas não devem estar
    assert "é" not in keywords
    assert "um" not in keywords


def test_get_audio_duration_with_soundfile(transcription_service, mock_audio_file):
    """Testa obtenção de duração do áudio usando soundfile"""
    mock_info = Mock()
    mock_info.duration = 45.5
    
    with patch('app.services.audio_transcription_service.sf') as mock_sf:
        mock_sf.info.return_value = mock_info
        duration = transcription_service.get_audio_duration(mock_audio_file)
    
    assert duration == 45.5


def test_get_audio_duration_fallback_moviepy(transcription_service, mock_audio_file):
    """Testa fallback para MoviePy quando soundfile não disponível"""
    mock_audio = Mock()
    mock_audio.duration = 60.0
    
    with patch('app.services.audio_transcription_service.sf', side_effect=ImportError):
        with patch('app.services.audio_transcription_service.AudioFileClip') as mock_clip:
            mock_clip.return_value = mock_audio
            duration = transcription_service.get_audio_duration(mock_audio_file)
    
    assert duration == 60.0
    mock_audio.close.assert_called_once()


@pytest.mark.asyncio
async def test_transcribe_with_specific_language(transcription_service, mock_audio_file, mock_whisper_segments):
    """Testa transcrição com idioma específico"""
    mock_model = MagicMock()
    mock_info = Mock()
    mock_info.language = "en"
    mock_info.language_probability = 0.98
    
    mock_model.transcribe.return_value = (mock_whisper_segments, mock_info)
    
    with patch.object(transcription_service, '_load_model', return_value=mock_model):
        await transcription_service.transcribe_audio(mock_audio_file, language="en")
    
    # Verificar que foi chamado com o idioma correto
    call_args = mock_model.transcribe.call_args
    assert call_args.kwargs['language'] == "en"

