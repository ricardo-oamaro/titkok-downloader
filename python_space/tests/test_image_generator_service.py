import pytest
from pathlib import Path
from app.services.image_generator_service import image_generator_service
from PIL import Image


def test_generate_comment_image(sample_comments, temp_dir):
    """Test generating a single comment image"""
    comment = sample_comments[0]
    output_path = temp_dir / "test_comment.png"
    
    result_path = image_generator_service.generate_comment_image(comment, output_path)
    
    assert result_path.exists()
    assert result_path == output_path
    
    # Verify image properties
    img = Image.open(result_path)
    assert img.size == (1080, 200)
    assert img.format == "PNG"


def test_generate_images_from_comments(sample_comments, temp_dir):
    """Test generating multiple images"""
    image_paths = image_generator_service.generate_images_from_comments(
        sample_comments,
        temp_dir
    )
    
    assert len(image_paths) == 3
    
    for i, path in enumerate(image_paths, 1):
        assert path.exists()
        assert path.name == f"instagram_{i:02d}.png"
        
        # Verify each image
        img = Image.open(path)
        assert img.size == (1080, 200)


def test_get_initials():
    """Test getting initials from names"""
    assert image_generator_service._get_initials("Maria Silva") == "MS"
    assert image_generator_service._get_initials("João") == "J"
    assert image_generator_service._get_initials("Ana Maria Costa") == "AC"
    assert image_generator_service._get_initials("") == "?"


def test_get_color_from_name():
    """Test color generation from name"""
    color1 = image_generator_service._get_color_from_name("Maria Silva")
    color2 = image_generator_service._get_color_from_name("Maria Silva")
    color3 = image_generator_service._get_color_from_name("João Pedro")
    
    # Same name should always generate same color
    assert color1 == color2
    # Different names should (likely) generate different colors
    assert isinstance(color1, tuple)
    assert len(color1) == 3


def test_wrap_text():
    """Test text wrapping"""
    short_text = "Texto curto"
    long_text = "Este é um texto muito longo que deveria ser quebrado em múltiplas linhas para caber adequadamente na imagem sem ultrapassar os limites estabelecidos"
    
    wrapped_short = image_generator_service._wrap_text(short_text, 900)
    wrapped_long = image_generator_service._wrap_text(long_text, 900)
    
    assert wrapped_short == short_text
    assert len(wrapped_long) <= 163  # 160 chars + "..."


