import pytest
import tempfile
import shutil
from pathlib import Path
from app.models.comment_schemas import GeneratedComment


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    tmpdir = tempfile.mkdtemp()
    yield Path(tmpdir)
    # Cleanup
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def sample_video_info():
    """Sample video info from yt-dlp"""
    return {
        "title": "Test TikTok Video - Como fazer bolo de chocolate",
        "fulltitle": "Test TikTok Video - Como fazer bolo de chocolate",
        "description": "Aprenda a fazer um bolo delicioso! #receita #bolo #chocolate #tutorial",
        "tags": ["receita", "bolo", "chocolate"],
        "id": "1234567890",
        "duration": 60,
        "view_count": 10000,
        "like_count": 500,
    }


@pytest.fixture
def sample_metadata():
    """Sample extracted metadata"""
    return {
        "title": "Test TikTok Video - Como fazer bolo de chocolate",
        "description": "Aprenda a fazer um bolo delicioso!",
        "hashtags": ["#receita", "#bolo", "#chocolate", "#tutorial"]
    }


@pytest.fixture
def sample_comments():
    """Sample generated comments"""
    return [
        GeneratedComment(
            author="Maria Silva",
            username="maria_silva",
            text="Que vídeo incrível! Amei demais ❤️",
            likes=150,
            timestamp="2h"
        ),
        GeneratedComment(
            author="João Pedro",
            username="joao_pedro",
            text="Como faz isso? Me ensina!",
            likes=45,
            timestamp="5 min"
        ),
        GeneratedComment(
            author="Ana Costa",
            username="ana_costa",
            text="Salvei pra fazer depois 🔖",
            likes=320,
            timestamp="1d"
        ),
    ]


@pytest.fixture
def sample_comments_txt(temp_dir):
    """Create a sample comentarios.txt file"""
    txt_path = temp_dir / "comentarios.txt"
    content = """1. @maria_silva (150 likes, 2h): Que vídeo incrível! Amei demais ❤️
2. @joao_pedro (45 likes, 5 min): Como faz isso? Me ensina!
3. @ana_costa (320 likes, 1d): Salvei pra fazer depois 🔖
4. @carlos_mendes (234 likes, 3h): Top demais! 🔥
5. @juliana_alves (567 likes, 2d): Perfeito! Já fiz 3 vezes 😍
6. @roberto_dias (23 likes, 4h): Adorei! Vou tentar
7. @beatriz_rocha (178 likes, 6h): Ficou lindo! 💚
8. @lucas_oliveira (92 likes, 1d): Parabéns pelo trabalho!
9. @camila_fernandes (145 likes, 3h): Maravilhoso ✨
10. @gabriel_souza (67 likes, 2h): Muito show! 👌
11. @patricia_costa (289 likes, 5h): Isso sim é conteúdo de qualidade
12. @rafael_martins (34 likes, 1h): Salvando pra assistir depois 📌
13. @fernanda_lima (456 likes, 3d): Sensacional! 🎉
14. @thiago_pereira (123 likes, 4h): Melhor vídeo que vi hoje!
15. @amanda_santos (201 likes, 2h): Vou fazer agora mesmo! ❤️"""
    
    txt_path.write_text(content, encoding='utf-8')
    return txt_path


@pytest.fixture
def mock_ollama_response():
    """Mock Ollama API response"""
    return {
        "response": '''
{
  "comments": [
    {
      "author": "Maria Silva",
      "username": "maria_silva",
      "text": "Que vídeo incrível! Amei demais ❤️",
      "likes": 150,
      "timestamp": "2h"
    },
    {
      "author": "João Pedro",
      "username": "joao_pedro",
      "text": "Como faz isso? Me ensina!",
      "likes": 45,
      "timestamp": "5 min"
    }
  ]
}
        ''',
        "model": "llama3",
        "done": True
    }


@pytest.fixture
def sample_video_file(temp_dir):
    """Create a dummy video file for testing"""
    video_path = temp_dir / "test_video.mp4"
    # Create a minimal valid MP4 file (just header)
    video_path.write_bytes(b'\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom')
    return video_path


