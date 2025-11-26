import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from app.services.image_matcher_service import ImageMatcherService, PORTUGUESE_STOPWORDS
from app.models.story_video_schemas import TranscriptionSegment, ImageInfo, ImageMatch


@pytest.fixture
def matcher_service():
    """Fixture para o serviço de matching"""
    return ImageMatcherService(min_confidence=0.3)


@pytest.fixture
def sample_images(tmp_path):
    """Cria imagens de exemplo"""
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    
    (images_dir / "carro_vermelho.jpg").write_text("fake image")
    (images_dir / "paisagem_praia.png").write_text("fake image")
    (images_dir / "pessoa_correndo.jpg").write_text("fake image")
    
    return images_dir


@pytest.fixture
def sample_segments():
    """Cria segmentos de exemplo"""
    return [
        TranscriptionSegment(
            text="Primeiro vamos falar sobre o carro vermelho",
            start_time=0.0,
            end_time=5.0,
            keywords=["primeiro", "falar", "carro", "vermelho"]
        ),
        TranscriptionSegment(
            text="Agora veja esta linda paisagem da praia",
            start_time=5.0,
            end_time=10.0,
            keywords=["agora", "veja", "linda", "paisagem", "praia"]
        ),
    ]


def test_extract_keywords_from_filename(matcher_service):
    """Testa extração de keywords do nome do arquivo"""
    keywords = matcher_service.extract_keywords_from_filename("meu_carro_vermelho_2024.jpg")
    
    assert "carro" in keywords
    assert "vermelho" in keywords
    assert "2024" in keywords
    assert "meu" not in keywords  # Stopword
    

def test_extract_keywords_removes_stopwords(matcher_service):
    """Testa remoção de stopwords"""
    keywords = matcher_service.extract_keywords_from_filename("o_meu_novo_carro_da_empresa.jpg")
    
    # Stopwords não devem estar presentes
    for stopword in ["o", "meu", "da"]:
        assert stopword not in keywords
    
    # Palavras relevantes devem estar
    assert "novo" in keywords
    assert "carro" in keywords
    assert "empresa" in keywords


def test_extract_keywords_handles_special_chars(matcher_service):
    """Testa tratamento de caracteres especiais"""
    keywords = matcher_service.extract_keywords_from_filename("foto-da-casa_nova!@#.png")
    
    assert "foto" in keywords
    assert "casa" in keywords
    assert "nova" in keywords


def test_find_images(matcher_service, sample_images):
    """Testa busca de imagens em diretório"""
    images = matcher_service.find_images(sample_images)
    
    assert len(images) == 3
    assert all(isinstance(img, ImageInfo) for img in images)
    
    # Verificar que keywords foram extraídas
    carro_img = next(img for img in images if "carro" in img.filename)
    assert "carro" in carro_img.keywords
    assert "vermelho" in carro_img.keywords


def test_find_images_directory_not_found(matcher_service):
    """Testa erro quando diretório não existe"""
    fake_dir = Path("/nonexistent/directory")
    
    with pytest.raises(FileNotFoundError):
        matcher_service.find_images(fake_dir)


@pytest.mark.asyncio
async def test_find_best_matches_with_ollama(matcher_service, sample_segments, sample_images):
    """Testa matching com Ollama"""
    available_images = matcher_service.find_images(sample_images)
    
    # Mock da resposta do Ollama
    mock_ollama_response_1 = {"response": "1|0.85"}  # carro_vermelho
    mock_ollama_response_2 = {"response": "2|0.92"}  # paisagem_praia
    
    with patch('app.services.image_matcher_service.ollama.generate') as mock_ollama:
        mock_ollama.side_effect = [mock_ollama_response_1, mock_ollama_response_2]
        
        matches = await matcher_service.find_best_matches(sample_segments, available_images)
    
    assert len(matches) == 2
    assert all(isinstance(m, ImageMatch) for m in matches)
    
    # Primeiro match deve ser carro
    assert "carro" in matches[0].image.filename
    assert matches[0].confidence_score == 0.85
    
    # Segundo match deve ser praia
    assert "praia" in matches[1].image.filename
    assert matches[1].confidence_score == 0.92


@pytest.mark.asyncio
async def test_find_best_matches_with_fallback(matcher_service, sample_segments, sample_images):
    """Testa fallback quando Ollama retorna score baixo"""
    available_images = matcher_service.find_images(sample_images)
    
    # Mock com score muito baixo
    mock_ollama_response = {"response": "1|0.15"}
    
    with patch('app.services.image_matcher_service.ollama.generate') as mock_ollama:
        mock_ollama.return_value = mock_ollama_response
        
        matches = await matcher_service.find_best_matches(sample_segments[:1], available_images)
    
    # Deve usar fallback (score <= 0.5)
    assert len(matches) == 1
    assert matches[0].confidence_score <= 0.5


@pytest.mark.asyncio
async def test_match_segment_prefers_less_used_images(matcher_service, sample_images):
    """Testa que fallback prefere imagens menos usadas"""
    available_images = matcher_service.find_images(sample_images)
    
    segment = TranscriptionSegment(
        text="Texto genérico sem match claro",
        start_time=0.0,
        end_time=5.0,
        keywords=["texto", "genérico"]
    )
    
    # Simular uso de imagens
    used_images = {
        available_images[0].path: 3,  # Muito usada
        available_images[1].path: 0,  # Nunca usada
    }
    
    # Mock Ollama com score baixo para forçar fallback
    with patch('app.services.image_matcher_service.ollama.generate') as mock_ollama:
        mock_ollama.return_value = {"response": "1|0.1"}
        
        match = await matcher_service._match_segment_to_image(
            segment, available_images, used_images
        )
    
    # Deve preferir imagem menos usada no fallback
    assert match.image.path in [img.path for img in available_images]


@pytest.mark.asyncio
async def test_ollama_match_handles_invalid_response(matcher_service, sample_segments, sample_images):
    """Testa tratamento de resposta inválida do Ollama"""
    available_images = matcher_service.find_images(sample_images)
    
    # Mock com resposta malformada
    with patch('app.services.image_matcher_service.ollama.generate') as mock_ollama:
        mock_ollama.return_value = {"response": "resposta inválida sem formato"}
        
        image, score = await matcher_service._ollama_match(sample_segments[0], available_images)
    
    # Deve retornar primeira imagem com score baixo
    assert image == available_images[0]
    assert score == 0.2


@pytest.mark.asyncio
async def test_find_best_matches_raises_error_no_images(matcher_service, sample_segments):
    """Testa erro quando não há imagens disponíveis"""
    with pytest.raises(ValueError, match="No images available"):
        await matcher_service.find_best_matches(sample_segments, [])

