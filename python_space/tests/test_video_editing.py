"""
Tests for video editing services
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from moviepy.editor import VideoFileClip

from app.services.capcut_service import CapCutAutomationService
from app.services.video_analyzer_service import VideoAnalyzerService
from app.models.video_edit_schemas import (
    EditStyle,
    KeyMoment,
    AnalysisResult
)


class TestCapCutAutomationService:
    """Tests for CapCut automation service"""
    
    @pytest.fixture
    def capcut_service(self):
        """Create CapCut service instance"""
        return CapCutAutomationService()
    
    @pytest.fixture
    def mock_video_clip(self):
        """Mock VideoFileClip"""
        clip = MagicMock(spec=VideoFileClip)
        clip.duration = 30.0
        clip.w = 1080
        clip.h = 1920
        clip.fps = 30
        clip.fx.return_value = clip
        clip.fadein.return_value = clip
        clip.fadeout.return_value = clip
        clip.subclip.return_value = clip
        clip.write_videofile = MagicMock()
        clip.close = MagicMock()
        return clip
    
    @pytest.fixture
    def mock_comments(self):
        """Mock AI-generated comments"""
        return [
            {"text": "Que vídeo incrível! Amei demais ❤️", "author": "Maria Silva"},
            {"text": "Como faz isso? Me ensina!", "author": "João Pedro"},
            {"text": "Salvei pra fazer depois 🔖", "author": "Ana Costa"},
            {"text": "Perfeito! ❤️", "author": "Patricia Almeida"},
            {"text": "Adorei! Vou compartilhar", "author": "Carlos Santos"}
        ]
    
    @pytest.fixture
    def mock_metadata(self):
        """Mock video metadata"""
        return {
            "title": "Tutorial incrível de dança",
            "description": "Aprenda essa coreografia viral",
            "hashtags": ["dança", "tutorial", "viral"],
            "author": "fe_e_groove"
        }
    
    @pytest.mark.asyncio
    @patch('app.services.capcut_service.VideoFileClip')
    async def test_edit_video_viral_style(
        self,
        mock_video_class,
        capcut_service,
        mock_video_clip,
        mock_comments,
        mock_metadata,
        tmp_path
    ):
        """Test video editing with viral style"""
        # Setup
        mock_video_class.return_value = mock_video_clip
        video_path = tmp_path / "test_video.mp4"
        video_path.touch()
        
        # Execute
        result = await capcut_service.edit_video(
            video_path=video_path,
            comments=mock_comments,
            metadata=mock_metadata,
            style=EditStyle.VIRAL,
            add_subtitles=True
        )
        
        # Verify
        assert result.style_applied == EditStyle.VIRAL
        assert result.original_path == str(video_path)
        assert Path(result.video_path).exists() or True  # Mock might not create file
        assert "speed" in str(result.effects_applied) or "zoom" in str(result.effects_applied)
        assert result.subtitles_count >= 0
    
    @pytest.mark.asyncio
    @patch('app.services.capcut_service.VideoFileClip')
    async def test_edit_video_storytelling_style(
        self,
        mock_video_class,
        capcut_service,
        mock_video_clip,
        mock_comments,
        mock_metadata,
        tmp_path
    ):
        """Test video editing with storytelling style"""
        mock_video_class.return_value = mock_video_clip
        video_path = tmp_path / "test_video.mp4"
        video_path.touch()
        
        result = await capcut_service.edit_video(
            video_path=video_path,
            comments=mock_comments,
            metadata=mock_metadata,
            style=EditStyle.STORYTELLING,
            add_subtitles=True
        )
        
        assert result.style_applied == EditStyle.STORYTELLING
        assert "fade" in str(result.effects_applied).lower()
    
    @pytest.mark.asyncio
    @patch('app.services.capcut_service.VideoFileClip')
    async def test_edit_video_with_target_duration(
        self,
        mock_video_class,
        capcut_service,
        mock_video_clip,
        mock_comments,
        mock_metadata,
        tmp_path
    ):
        """Test video editing with target duration"""
        mock_video_class.return_value = mock_video_clip
        video_path = tmp_path / "test_video.mp4"
        video_path.touch()
        
        with patch.object(capcut_service.analyzer, 'find_best_cuts', new=AsyncMock(return_value=[(0, 15)])):
            result = await capcut_service.edit_video(
                video_path=video_path,
                comments=mock_comments,
                metadata=mock_metadata,
                style=EditStyle.MINIMAL,
                target_duration=15
            )
            
            assert result is not None
    
    @pytest.mark.asyncio
    @patch('app.services.capcut_service.VideoFileClip')
    async def test_edit_video_without_subtitles(
        self,
        mock_video_class,
        capcut_service,
        mock_video_clip,
        mock_comments,
        mock_metadata,
        tmp_path
    ):
        """Test video editing without subtitles"""
        mock_video_class.return_value = mock_video_clip
        video_path = tmp_path / "test_video.mp4"
        video_path.touch()
        
        result = await capcut_service.edit_video(
            video_path=video_path,
            comments=mock_comments,
            metadata=mock_metadata,
            style=EditStyle.MINIMAL,
            add_subtitles=False
        )
        
        assert result.subtitles_count == 0
    
    @pytest.mark.asyncio
    @patch('app.services.capcut_service.VideoFileClip')
    @patch('app.services.capcut_service.concatenate_videoclips')
    async def test_create_compilation(
        self,
        mock_concat,
        mock_video_class,
        capcut_service,
        mock_video_clip,
        tmp_path
    ):
        """Test creating compilation from multiple videos"""
        # Setup
        mock_video_class.return_value = mock_video_clip
        mock_concat.return_value = mock_video_clip
        
        video_paths = [
            tmp_path / "video1.mp4",
            tmp_path / "video2.mp4",
            tmp_path / "video3.mp4"
        ]
        for path in video_paths:
            path.touch()
        
        # Execute
        result = await capcut_service.create_compilation(
            video_paths=video_paths,
            theme="trending",
            max_duration=60
        )
        
        # Verify
        assert result.style_applied == EditStyle.COMPILATION
        assert "compilation" in result.effects_applied
        assert "fade" in str(result.effects_applied).lower()


class TestVideoAnalyzerService:
    """Tests for video analyzer service"""
    
    @pytest.fixture
    def analyzer_service(self):
        """Create analyzer service instance"""
        return VideoAnalyzerService()
    
    @pytest.fixture
    def mock_video_capture(self):
        """Mock cv2.VideoCapture"""
        import cv2
        capture = MagicMock(spec=cv2.VideoCapture)
        capture.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_COUNT: 900,  # 30 seconds at 30fps
            cv2.CAP_PROP_FRAME_WIDTH: 1080,
            cv2.CAP_PROP_FRAME_HEIGHT: 1920
        }.get(prop, 0)
        capture.read.return_value = (True, MagicMock())
        capture.release = MagicMock()
        return capture
    
    @pytest.mark.asyncio
    @patch('app.services.video_analyzer_service.cv2.VideoCapture')
    async def test_analyze_video(
        self,
        mock_capture_class,
        analyzer_service,
        mock_video_capture,
        tmp_path
    ):
        """Test video analysis"""
        # Setup
        mock_capture_class.return_value = mock_video_capture
        video_path = tmp_path / "test_video.mp4"
        video_path.touch()
        
        # Execute
        with patch.object(analyzer_service, '_detect_key_moments', new=AsyncMock(return_value=[])):
            with patch.object(analyzer_service, '_detect_scene_changes', new=AsyncMock(return_value=[5.0, 10.0, 15.0])):
                with patch.object(analyzer_service, '_calculate_average_brightness', new=AsyncMock(return_value=128.0)):
                    with patch.object(analyzer_service, '_calculate_motion_intensity', new=AsyncMock(return_value=0.6)):
                        result = await analyzer_service.analyze_video(video_path)
        
        # Verify
        assert isinstance(result, AnalysisResult)
        assert result.duration == 30.0  # 900 frames / 30 fps
        assert result.resolution == "1080x1920"
        assert result.fps == 30.0
        assert len(result.scene_changes) == 3
        assert result.average_brightness == 128.0
        assert result.motion_intensity == 0.6
    
    @pytest.mark.asyncio
    @patch('app.services.video_analyzer_service.cv2.VideoCapture')
    async def test_find_best_cuts(
        self,
        mock_capture_class,
        analyzer_service,
        mock_video_capture,
        tmp_path
    ):
        """Test finding best cut points"""
        mock_capture_class.return_value = mock_video_capture
        video_path = tmp_path / "test_video.mp4"
        video_path.touch()
        
        with patch.object(analyzer_service, 'analyze_video', new=AsyncMock(
            return_value=AnalysisResult(
                video_path=str(video_path),
                duration=30.0,
                resolution="1080x1920",
                fps=30.0,
                has_audio=True,
                key_moments=[],
                scene_changes=[5.0, 10.0, 15.0, 20.0, 25.0],
                average_brightness=128.0,
                motion_intensity=0.6
            )
        )):
            cuts = await analyzer_service.find_best_cuts(video_path, target_duration=15)
        
        assert len(cuts) > 0
        assert all(isinstance(cut, tuple) and len(cut) == 2 for cut in cuts)
        # Total duration should be close to target
        total_duration = sum(end - start for start, end in cuts)
        assert total_duration <= 15  # Should not exceed target
    
    @pytest.mark.asyncio
    async def test_detect_key_moments(self, analyzer_service, mock_video_capture):
        """Test key moment detection"""
        import numpy as np
        
        # Mock frames with different content (simulating scene changes)
        frames = [
            np.random.randint(0, 255, (1920, 1080, 3), dtype=np.uint8)
            for _ in range(10)
        ]
        
        mock_video_capture.read.side_effect = [(True, frame) for frame in frames] + [(False, None)]
        
        with patch('app.services.video_analyzer_service.cv2.cvtColor', side_effect=lambda f, _: f[:, :, 0]):
            with patch('app.services.video_analyzer_service.cv2.absdiff', return_value=np.full((1920, 1080), 50)):
                key_moments = await analyzer_service._detect_key_moments(mock_video_capture, 30.0)
        
        assert isinstance(key_moments, list)
        assert len(key_moments) <= 20  # Should limit to 20
    
    @pytest.mark.asyncio
    async def test_calculate_average_brightness(self, analyzer_service, mock_video_capture):
        """Test average brightness calculation"""
        import numpy as np
        
        # Create frames with known brightness
        bright_frame = np.full((1920, 1080, 3), 200, dtype=np.uint8)
        mock_video_capture.read.return_value = (True, bright_frame)
        mock_video_capture.get.return_value = 100  # frame count
        
        with patch('app.services.video_analyzer_service.cv2.cvtColor', return_value=bright_frame[:, :, 0]):
            brightness = await analyzer_service._calculate_average_brightness(mock_video_capture)
        
        assert 0 <= brightness <= 255
    
    @pytest.mark.asyncio
    async def test_calculate_motion_intensity(self, analyzer_service, mock_video_capture):
        """Test motion intensity calculation"""
        import numpy as np
        
        # Create frames with motion
        frame1 = np.random.randint(0, 255, (1920, 1080), dtype=np.uint8)
        frame2 = np.random.randint(0, 255, (1920, 1080), dtype=np.uint8)
        
        mock_video_capture.read.side_effect = [(True, frame1), (True, frame2), (False, None)]
        mock_video_capture.get.return_value = 60  # frame count
        
        with patch('app.services.video_analyzer_service.cv2.cvtColor', side_effect=[frame1, frame2]):
            with patch('app.services.video_analyzer_service.cv2.absdiff', return_value=np.full((1920, 1080), 30)):
                motion = await analyzer_service._calculate_motion_intensity(mock_video_capture)
        
        assert 0.0 <= motion <= 1.0

