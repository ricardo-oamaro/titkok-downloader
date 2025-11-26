import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from PIL import Image
import numpy as np

from app.services.story_video_service import StoryVideoService
from app.models.story_video_schemas import (
    TranscriptionSegment,
    ImageInfo,
    ImageMatch,
    TimelineItem,
    StoryVideoResult
)


@pytest.fixture
def story_service():
    """Fixture para o serviço de criação de vídeos"""
    return StoryVideoService()


@pytest.fixture
def mock_audio_file(tmp_path):
    """Cria um arquivo de áudio mock"""
    audio_file = tmp_path / "narration.mp3"
    audio_file.write_text("mock audio")
    return audio_file


@pytest.fixture
def mock_images_dir(tmp_path):
    """Cria diretório com imagens mock"""
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    
    # Criar imagens reais para teste
    for i, name in enumerate(["intro.jpg", "middle.jpg", "end.jpg"]):
        img = Image.new('RGB', (100, 100), color=(i * 50, 100, 150))
        img.save(images_dir / name)
    
    return images_dir


@pytest.fixture
def mock_segments():
    """Segmentos de transcrição mock"""
    return [
        TranscriptionSegment(
            text="Esta é a introdução do vídeo",
            start_time=0.0,
            end_time=5.0,
            keywords=["introdução", "vídeo"]
        ),
        TranscriptionSegment(
            text="Agora a parte do meio com mais detalhes",
            start_time=5.0,
            end_time=12.0,
            keywords=["parte", "meio", "detalhes"]
        ),
        TranscriptionSegment(
            text="E finalmente a conclusão",
            start_time=12.0,
            end_time=16.0,
            keywords=["finalmente", "conclusão"]
        ),
    ]


@pytest.fixture
def mock_images():
    """Imagens mock"""
    return [
        ImageInfo(
            path="/fake/intro.jpg",
            filename="intro.jpg",
            keywords=["intro"]
        ),
        ImageInfo(
            path="/fake/middle.jpg",
            filename="middle.jpg",
            keywords=["middle", "meio"]
        ),
        ImageInfo(
            path="/fake/end.jpg",
            filename="end.jpg",
            keywords=["end", "fim"]
        ),
    ]


@pytest.fixture
def mock_matches(mock_segments, mock_images):
    """Matches mock"""
    return [
        ImageMatch(
            segment=mock_segments[0],
            image=mock_images[0],
            confidence_score=0.85
        ),
        ImageMatch(
            segment=mock_segments[1],
            image=mock_images[1],
            confidence_score=0.90
        ),
        ImageMatch(
            segment=mock_segments[2],
            image=mock_images[2],
            confidence_score=0.75
        ),
    ]


def test_build_timeline(story_service, mock_matches):
    """Testa construção da timeline"""
    timeline = story_service._build_timeline(mock_matches)
    
    assert len(timeline) == 3
    assert all(isinstance(item, TimelineItem) for item in timeline)
    
    # Verificar ordenação por tempo
    for i in range(len(timeline) - 1):
        assert timeline[i].start_time <= timeline[i+1].start_time
    
    # Verificar dados
    assert timeline[0].start_time == 0.0
    assert timeline[0].end_time == 5.0
    assert timeline[0].confidence == 0.85
    
    assert timeline[1].start_time == 5.0
    assert timeline[1].end_time == 12.0
    
    assert timeline[2].start_time == 12.0
    assert timeline[2].end_time == 16.0


def test_fit_image_to_resolution_portrait(story_service):
    """Testa ajuste de imagem para resolução vertical (TikTok)"""
    # Criar imagem horizontal
    img = Image.new('RGB', (1920, 1080), color=(255, 0, 0))
    
    # Ajustar para vertical TikTok
    result = story_service._fit_image_to_resolution(img, (1080, 1920))
    
    assert result.size == (1080, 1920)


def test_fit_image_to_resolution_landscape(story_service):
    """Testa ajuste de imagem horizontal"""
    # Criar imagem vertical
    img = Image.new('RGB', (1080, 1920), color=(0, 255, 0))
    
    # Ajustar para horizontal
    result = story_service._fit_image_to_resolution(img, (1920, 1080))
    
    assert result.size == (1920, 1080)


def test_create_image_clip_smooth_style(story_service, mock_images_dir):
    """Testa criação de clip com estilo smooth"""
    img_path = list(mock_images_dir.glob("*.jpg"))[0]
    
    clip = story_service._create_image_clip(
        image_path=img_path,
        duration=5.0,
        resolution=(1080, 1920),
        style="smooth",
        position=0
    )
    
    assert clip.duration == 5.0
    assert clip.fps == 30


def test_create_image_clip_dynamic_style(story_service, mock_images_dir):
    """Testa criação de clip com estilo dynamic"""
    img_path = list(mock_images_dir.glob("*.jpg"))[0]
    
    clip = story_service._create_image_clip(
        image_path=img_path,
        duration=5.0,
        resolution=(1080, 1920),
        style="dynamic",
        position=0
    )
    
    assert clip.duration == 5.0
    assert clip.fps == 30


def test_create_image_clip_ken_burns_style(story_service, mock_images_dir):
    """Testa criação de clip com estilo ken_burns"""
    img_path = list(mock_images_dir.glob("*.jpg"))[0]
    
    # Testar zoom in (posição par)
    clip_zoom_in = story_service._create_image_clip(
        image_path=img_path,
        duration=5.0,
        resolution=(1080, 1920),
        style="ken_burns",
        position=0
    )
    
    assert clip_zoom_in.duration == 5.0
    
    # Testar zoom out (posição ímpar)
    clip_zoom_out = story_service._create_image_clip(
        image_path=img_path,
        duration=5.0,
        resolution=(1080, 1920),
        style="ken_burns",
        position=1
    )
    
    assert clip_zoom_out.duration == 5.0


@pytest.mark.asyncio
async def test_create_story_video_validates_paths(story_service, tmp_path):
    """Testa validação de caminhos inexistentes"""
    fake_images = tmp_path / "nonexistent_images"
    fake_audio = tmp_path / "nonexistent_audio.mp3"
    
    with pytest.raises(FileNotFoundError):
        await story_service.create_story_video(
            images_dir=fake_images,
            audio_file=fake_audio
        )


@pytest.mark.asyncio
async def test_create_story_video_no_segments(story_service, mock_images_dir, mock_audio_file):
    """Testa erro quando não há segmentos de fala"""
    with patch.object(story_service.transcription_service, 'transcribe_audio') as mock_transcribe:
        mock_transcribe.return_value = []  # Sem segmentos
        
        with pytest.raises(ValueError, match="No speech segments found"):
            await story_service.create_story_video(
                images_dir=mock_images_dir,
                audio_file=mock_audio_file
            )


@pytest.mark.asyncio
async def test_create_story_video_no_images(story_service, mock_audio_file, tmp_path):
    """Testa erro quando não há imagens"""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    
    mock_segments = [
        TranscriptionSegment(
            text="Teste",
            start_time=0.0,
            end_time=1.0,
            keywords=["teste"]
        )
    ]
    
    with patch.object(story_service.transcription_service, 'transcribe_audio') as mock_transcribe:
        mock_transcribe.return_value = mock_segments
        
        with pytest.raises(ValueError, match="No images found"):
            await story_service.create_story_video(
                images_dir=empty_dir,
                audio_file=mock_audio_file
            )


@pytest.mark.asyncio
async def test_create_story_video_integration(
    story_service, 
    mock_images_dir, 
    mock_audio_file,
    mock_segments,
    mock_matches
):
    """Teste de integração completo (com mocks)"""
    
    # Mock dos serviços internos
    with patch.object(story_service.transcription_service, 'transcribe_audio') as mock_transcribe:
        with patch.object(story_service.matcher_service, 'find_images') as mock_find:
            with patch.object(story_service.matcher_service, 'find_best_matches') as mock_match:
                with patch.object(story_service.transcription_service, 'get_audio_duration') as mock_duration:
                    with patch.object(story_service, '_generate_video') as mock_generate:
                        # Setup mocks
                        mock_transcribe.return_value = mock_segments
                        mock_find.return_value = [
                            ImageInfo(path=str(p), filename=p.name, keywords=[])
                            for p in mock_images_dir.glob("*.jpg")
                        ]
                        mock_match.return_value = mock_matches
                        mock_duration.return_value = 16.0
                        
                        # Executar
                        result = await story_service.create_story_video(
                            images_dir=mock_images_dir,
                            audio_file=mock_audio_file,
                            style="smooth"
                        )
                        
                        # Verificar
                        assert isinstance(result, StoryVideoResult)
                        assert result.duration == 16.0
                        assert result.segments_count == 3
                        assert result.images_used == 3
                        assert result.unique_images == 3
                        assert 0 <= result.average_confidence <= 1
                        
                        # Verificar que video foi gerado
                        mock_generate.assert_called_once()


def test_timeline_item_duration():
    """Testa cálculo de duração de um item da timeline"""
    item = TimelineItem(
        start_time=5.0,
        end_time=12.0,
        image_path="/fake/image.jpg",
        confidence=0.8
    )
    
    duration = item.end_time - item.start_time
    assert duration == 7.0

