#!/usr/bin/env python3
"""
Script para verificar se a autenticação do TikTok está funcionando
"""

import yt_dlp
import sys
from pathlib import Path

def check_tiktok_auth(browser='chrome'):
    """
    Testa se conseguimos acessar vídeos do TikTok usando cookies do navegador
    """
    print("=" * 60)
    print("🔍 Verificador de Autenticação TikTok")
    print("=" * 60)
    print()
    
    # URL de teste do TikTok (pode usar qualquer vídeo público)
    test_url = "https://www.tiktok.com/@tiktok/video/7041997751718792498"
    
    print(f"🌐 Navegador configurado: {browser}")
    print(f"🎬 URL de teste: {test_url}")
    print()
    
    # Configuração mínima do yt-dlp
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,  # Não baixar, só extrair info
        'cookiesfrombrowser': (browser, None, None, None),
    }
    
    print("⏳ Tentando acessar TikTok com cookies do navegador...")
    print()
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(test_url, download=False)
            
            if info:
                print("✅ SUCESSO! Autenticação funcionando!")
                print()
                print("📊 Informações do vídeo:")
                print(f"   Título: {info.get('title', 'N/A')}")
                print(f"   Autor: {info.get('uploader', 'N/A')}")
                print(f"   Views: {info.get('view_count', 'N/A'):,}")
                print(f"   Likes: {info.get('like_count', 'N/A'):,}")
                print()
                print("🎉 Você pode baixar vídeos do TikTok!")
                return True
                
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        print("❌ FALHA na autenticação!")
        print()
        
        if "requiring login" in error_msg.lower() or "use --cookies" in error_msg.lower():
            print("🔴 Problema: TikTok requer login")
            print()
            print("📋 Como resolver:")
            print(f"   1. Abra o {browser.title()}")
            print("   2. Acesse: https://www.tiktok.com")
            print("   3. Faça login com sua conta TikTok")
            print("   4. Deixe o navegador aberto")
            print("   5. Execute este script novamente")
            print()
        elif "could not find" in error_msg.lower() or "failed to get cookie" in error_msg.lower():
            print("🔴 Problema: Não conseguiu acessar cookies do navegador")
            print()
            print("📋 Como resolver:")
            print(f"   1. Certifique-se de que o {browser.title()} está instalado")
            print("   2. Feche TODAS as janelas do navegador")
            print("   3. Abra o navegador novamente")
            print("   4. Faça login no TikTok")
            print("   5. Execute este script novamente")
            print()
        else:
            print(f"🔴 Erro: {error_msg}")
            print()
        
        return False
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Verificar autenticação do TikTok via cookies do navegador"
    )
    parser.add_argument(
        '--browser',
        default='chrome',
        choices=['chrome', 'firefox', 'edge', 'safari', 'brave', 'chromium', 'opera'],
        help='Navegador a ser usado (padrão: chrome)'
    )
    
    args = parser.parse_args()
    
    success = check_tiktok_auth(args.browser)
    
    print()
    print("=" * 60)
    
    if success:
        print("✅ Status: PRONTO PARA USO")
        sys.exit(0)
    else:
        print("❌ Status: REQUER CONFIGURAÇÃO")
        print()
        print("📖 Veja mais detalhes em: TIKTOK_AUTH_GUIDE.md")
        sys.exit(1)


if __name__ == "__main__":
    main()



