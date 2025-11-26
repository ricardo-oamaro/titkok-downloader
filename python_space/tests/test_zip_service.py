import pytest
import zipfile
from pathlib import Path
from app.services.zip_service import zip_service


def test_create_package(sample_video_file, sample_comments_txt, temp_dir):
    """Test creating a complete ZIP package"""
    # Create some dummy image files
    image_paths = []
    for i in range(1, 4):
        img_path = temp_dir / f"instagram_{i:02d}.png"
        img_path.write_bytes(b"fake png data")
        image_paths.append(img_path)
    
    zip_path = temp_dir / "test_package.zip"
    
    result_path = zip_service.create_package(
        video_path=sample_video_file,
        comments_txt_path=sample_comments_txt,
        image_paths=image_paths,
        output_path=zip_path
    )
    
    assert result_path.exists()
    assert result_path == zip_path
    
    # Verify ZIP contents
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        files = zipf.namelist()
        
        assert "video.mp4" in files  # Fixed name regardless of input filename
        assert "comentarios.txt" in files
        assert "README.txt" in files
        assert "instagram_01.png" in files
        assert "instagram_02.png" in files
        assert "instagram_03.png" in files
        
        # Verify README content
        readme_content = zipf.read("README.txt").decode('utf-8')
        assert "INTELIGÊNCIA ARTIFICIAL" in readme_content
        assert "AVISO IMPORTANTE" in readme_content


def test_generate_readme():
    """Test README generation"""
    readme = zip_service._generate_readme()
    
    assert "INTELIGÊNCIA ARTIFICIAL" in readme
    assert "AVISO IMPORTANTE" in readme
    assert "Ollama" in readme
    assert "Gerado em:" in readme
    assert "TikTok Downloader" in readme


def test_cleanup_temp_files(temp_dir):
    """Test cleanup of temporary files"""
    # Create some temp files
    file1 = temp_dir / "temp1.txt"
    file2 = temp_dir / "temp2.txt"
    file1.write_text("test")
    file2.write_text("test")
    
    assert file1.exists()
    assert file2.exists()
    
    zip_service.cleanup_temp_files([file1, file2])
    
    assert not file1.exists()
    assert not file2.exists()


def test_cleanup_nonexistent_files():
    """Test cleanup with non-existent files (should not raise error)"""
    fake_paths = [Path("/fake/path1.txt"), Path("/fake/path2.txt")]
    
    # Should not raise exception
    zip_service.cleanup_temp_files(fake_paths)

