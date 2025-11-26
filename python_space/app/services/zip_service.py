import zipfile
import logging
from pathlib import Path
from typing import List
from datetime import datetime

logger = logging.getLogger(__name__)


class ZipService:
    """Service for creating ZIP packages with video, comments, and images"""
    
    def create_package(
        self,
        video_path: Path,
        comments_txt_path: Path,
        image_paths: List[Path],
        output_path: Path
    ) -> Path:
        """
        Create a ZIP package containing video, comments txt, images, and README
        
        Args:
            video_path: Path to video file
            comments_txt_path: Path to comentarios.txt
            image_paths: List of paths to Instagram PNG images
            output_path: Path for the output ZIP file
            
        Returns:
            Path to the created ZIP file
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add video with fixed name "video.mp4"
                if video_path.exists():
                    zipf.write(video_path, "video.mp4")
                    logger.info("Added video.mp4 to ZIP")
                else:
                    logger.warning(f"Video file not found: {video_path}")
                
                # Add comments txt
                if comments_txt_path.exists():
                    zipf.write(comments_txt_path, "comentarios.txt")
                    logger.info("Added comentarios.txt to ZIP")
                else:
                    logger.warning(f"Comments file not found: {comments_txt_path}")
                
                # Add all images
                for i, image_path in enumerate(image_paths, 1):
                    if image_path.exists():
                        zipf.write(image_path, image_path.name)
                    else:
                        logger.warning(f"Image file not found: {image_path}")
                
                logger.info(f"Added {len(image_paths)} images to ZIP")
                
                # Add README disclaimer
                readme_content = self._generate_readme()
                zipf.writestr("README.txt", readme_content)
                logger.info("Added README.txt to ZIP")
            
            logger.info(f"ZIP package created successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating ZIP package: {str(e)}")
            raise
    
    def _generate_readme(self) -> str:
        """Generate README content with disclaimer"""
        return f"""╔═══════════════════════════════════════════════════════════════╗
║          CONTEÚDO GERADO POR INTELIGÊNCIA ARTIFICIAL          ║
╚═══════════════════════════════════════════════════════════════╝

AVISO IMPORTANTE:
═══════════════════════════════════════════════════════════════

Este pacote contém:
- Vídeo original baixado do TikTok
- Comentários GERADOS POR IA (não são comentários reais)
- Imagens de comentários GERADAS (não são screenshots reais)

⚠️  OS COMENTÁRIOS E IMAGENS NÃO SÃO REAIS!

Os comentários foram criados por Inteligência Artificial (Ollama/Llama 3)
baseados no contexto do vídeo. As imagens foram geradas programaticamente
para simular a aparência de comentários do Instagram.

═══════════════════════════════════════════════════════════════
USO DESTINADO
═══════════════════════════════════════════════════════════════

✅ Casos de uso apropriados:
   - Mockups e protótipos
   - Apresentações e demonstrações
   - Material educacional e exemplos
   - Testes de interface
   - Portfólio profissional

❌ NÃO use para:
   - Criar "provas falsas" de engajamento
   - Enganar clientes sobre resultados reais
   - Manipular percepção social
   - Fraude ou desinformação
   - Fabricar evidências

═══════════════════════════════════════════════════════════════
MARCAS D'ÁGUA
═══════════════════════════════════════════════════════════════

Todas as imagens contêm a marca d'água "Gerado por IA" no
canto inferior direito e metadados EXIF indicando que foram
geradas artificialmente.

═══════════════════════════════════════════════════════════════
INFORMAÇÕES TÉCNICAS
═══════════════════════════════════════════════════════════════

Gerado em: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Ferramenta: TikTok Downloader + AI Comments
IA: Ollama (Llama 3)
Imagens: Pillow (Python Imaging Library)

═══════════════════════════════════════════════════════════════

Para mais informações ou suporte, consulte a documentação do projeto.

═══════════════════════════════════════════════════════════════
"""
    
    def cleanup_temp_files(self, file_paths: List[Path]):
        """
        Clean up temporary files after ZIP creation
        
        Args:
            file_paths: List of file paths to delete
        """
        for file_path in file_paths:
            try:
                file_path = Path(file_path)
                if file_path.exists():
                    file_path.unlink()
                    logger.debug(f"Deleted temp file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temp file {file_path}: {str(e)}")


# Singleton instance
zip_service = ZipService()

