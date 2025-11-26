import pytest
from app.services.text_parser_service import text_parser_service


def test_parse_comments_file(sample_comments_txt):
    """Test parsing comments from TXT file"""
    comments = text_parser_service.parse_comments_file(str(sample_comments_txt))
    
    assert len(comments) == 15
    assert comments[0].username == "maria_silva"
    assert comments[0].author == "Maria Silva"
    assert comments[0].likes == 150
    assert comments[0].timestamp == "2h"
    assert "Que vídeo incrível" in comments[0].text


def test_parse_comments_file_not_found():
    """Test parsing non-existent file"""
    comments = text_parser_service.parse_comments_file("/non/existent/file.txt")
    
    assert len(comments) == 0


def test_parse_line_valid():
    """Test parsing a single valid line"""
    line = "1. @maria_silva (150 likes, 2h): Que vídeo incrível! ❤️"
    comment = text_parser_service._parse_line(line, 1)
    
    assert comment is not None
    assert comment.username == "maria_silva"
    assert comment.likes == 150
    assert comment.timestamp == "2h"


def test_parse_line_invalid():
    """Test parsing an invalid line"""
    line = "This is not a valid comment line"
    comment = text_parser_service._parse_line(line, 1)
    
    assert comment is None


def test_username_to_author():
    """Test username to author conversion"""
    assert text_parser_service._username_to_author("maria_silva") == "Maria Silva"
    assert text_parser_service._username_to_author("joao_pedro") == "Joao Pedro"
    assert text_parser_service._username_to_author("single") == "Single"


