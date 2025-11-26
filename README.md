# 🎬 TikTok Video Downloader Service

Serviço completo para download de vídeos do TikTok com geração de comentários inteligentes via IA e imagens estilo Instagram.

## 🌟 Funcionalidades

- ✅ **Download de vídeos** do TikTok em alta qualidade via `yt-dlp`
- 🤖 **Geração de comentários** realistas usando IA local (Ollama)
- 🎨 **Criação de imagens** estilo Instagram com os comentários gerados
- 📦 **Empacotamento ZIP** com vídeo + comentários + 15 imagens
- 🔐 **Autenticação via API Key** para segurança
- ⚡ **Rate limiting** para prevenir abuso
- 🌐 **Interface web** simples e moderna
- 📖 **API RESTful** documentada com Swagger/OpenAPI

## 🏗️ Tecnologias

- **Python 3.11+** - Linguagem principal
- **FastAPI** - Framework web moderno e rápido
- **yt-dlp** - Download de vídeos do TikTok
- **Ollama (Llama 3)** - IA local para geração de comentários
- **Pillow (PIL)** - Geração de imagens estilo Instagram
- **Pydantic** - Validação de dados
- **pytest** - Testes unitários e integração

## 🚀 Quick Start

### Pré-requisitos

```bash
# 1. Python 3.11+
python3 --version

# 2. yt-dlp
pip install yt-dlp

# 3. Ollama (para geração de comentários com IA)
brew install ollama
ollama serve
ollama pull llama3
```

### Instalação

```bash
# Clone o repositório
git clone https://github.com/ricardo-oamaro/titkok-downloader.git
cd titkok-downloader/python_space

# Crie e ative o ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas configurações
```

### Configuração

Crie um arquivo `.env` no diretório `python_space/`:

```env
# API
API_KEY=sua-api-key-secreta-aqui
PORT=8000

# yt-dlp
YTDLP_COOKIES_BROWSER=chrome

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# Rate Limiting
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_PERIOD=60
```

### Execução

```bash
cd python_space
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Acesse:
- 🌐 **Interface Web**: http://localhost:8000
- 📖 **API Docs**: http://localhost:8000/docs

## 📡 Uso da API

### Download de Vídeo

```bash
curl -X POST "http://localhost:8000/download" \
  -H "Content-Type: application/json" \
  -H "x-api-key: sua-api-key" \
  -d '{"url": "https://www.tiktok.com/@user/video/123456789"}' \
  --output video_package.zip
```

### Resposta

Um arquivo ZIP contendo:
- `video.mp4` - Vídeo do TikTok
- `comentarios.txt` - 15 comentários gerados por IA
- `instagram_01.png` até `instagram_15.png` - Imagens dos comentários
- `README.txt` - Disclaimer sobre conteúdo gerado por IA

## 🧪 Testes

```bash
cd python_space

# Executar todos os testes
pytest

# Com cobertura
pytest --cov=app --cov-report=html

# Apenas testes unitários
pytest tests/test_ai_comments_service.py

# Apenas testes de integração
pytest tests/test_integration_comments.py
```

## 📁 Estrutura do Projeto

```
tiktok_downloader_service/
└── python_space/
    ├── app/
    │   ├── main.py              # Aplicação FastAPI
    │   ├── config.py            # Configurações
    │   ├── models/              # Schemas Pydantic
    │   │   ├── schemas.py
    │   │   └── comment_schemas.py
    │   ├── services/            # Lógica de negócio
    │   │   ├── download_service.py
    │   │   ├── ai_comments_service.py
    │   │   ├── image_generator_service.py
    │   │   ├── text_parser_service.py
    │   │   └── zip_service.py
    │   ├── middleware/          # Autenticação
    │   │   └── auth.py
    │   └── static/              # Interface web
    │       ├── index.html
    │       ├── styles.css
    │       └── script.js
    ├── tests/                   # Testes unitários e integração
    │   ├── conftest.py
    │   ├── test_ai_comments_service.py
    │   ├── test_image_generator_service.py
    │   ├── test_text_parser_service.py
    │   ├── test_zip_service.py
    │   └── test_integration_comments.py
    ├── requirements.txt         # Dependências Python
    ├── .env.example             # Exemplo de configuração
    ├── README.md                # Documentação
    ├── TIKTOK_AUTH_GUIDE.md     # Guia de autenticação
    ├── COMMENTS_LIMITATION.md   # Limitações conhecidas
    └── FIXES_APPLIED.md         # Histórico de correções
```

## 🔐 Autenticação do TikTok

O TikTok possui proteções anti-bot. Para downloads funcionarem:

1. **Faça login no TikTok** no seu navegador (Chrome recomendado)
2. Configure `YTDLP_COOKIES_BROWSER=chrome` no `.env`
3. O `yt-dlp` usará seus cookies automaticamente

**Consulte:** `python_space/TIKTOK_AUTH_GUIDE.md` para mais detalhes

## 🤖 Geração de Comentários com IA

### Por que não comentários reais?

TikTok bloqueia extração de comentários com proteções anti-bot. A solução:

1. **yt-dlp** extrai metadados do vídeo (título, descrição, hashtags)
2. **Ollama (Llama 3)** gera 15 comentários realistas baseados no contexto
3. Comentários são salvos em `comentarios.txt`
4. 15 imagens estilo Instagram são geradas automaticamente

### Características dos Comentários

- ✅ Nomes brasileiros variados
- ✅ Mix de reações (curtidas, perguntas, elogios)
- ✅ Emojis apropriados ao contexto
- ✅ Timestamps realistas (2h, 5min, 1d)
- ✅ Contagem de likes variada

### Marca d'água

Todas as imagens incluem:
- 🏷️ Texto discreto: **"Gerado por IA"**
- 📍 Localização: Canto inferior direito
- 🎨 Cor: `#c7c7c7` (cinza claro)
- 📄 **README.txt** no ZIP com disclaimer completo

## 🎨 Geração de Imagens

As imagens simulam o layout do Instagram:

- **Dimensões:** 1080x200px
- **Fonte:** Roboto (Bold para username, Regular para texto)
- **Avatar:** Círculo com iniciais e cor baseada no nome
- **Layout:** Username, comentário, likes, timestamp
- **Ícones:** Curtir e responder
- **Marca d'água:** Sempre presente

## ⚠️ Limitações Conhecidas

### Comentários do TikTok
❌ **Não é possível extrair comentários reais** devido a:
- Proteções anti-bot do TikTok
- Requisitos de autenticação complexos
- Rate limiting agressivo

**Solução:** Comentários gerados por IA local (Ollama)

### Vídeos Privados
❌ Não é possível baixar vídeos privados ou de contas bloqueadas

### Rate Limiting
⚠️ Respeite os limites da API (configurável via `.env`)

## 📝 Documentação Adicional

- 📖 **[Guia de Autenticação TikTok](python_space/TIKTOK_AUTH_GUIDE.md)**
- ⚠️ **[Limitações de Comentários](python_space/COMMENTS_LIMITATION.md)**
- 🔧 **[Correções Aplicadas](python_space/FIXES_APPLIED.md)**

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se livre para:
- 🐛 Reportar bugs
- 💡 Sugerir novas funcionalidades
- 🔀 Enviar Pull Requests

## ⚖️ Considerações Éticas

Este projeto é destinado a:
- ✅ Backup pessoal de conteúdo próprio
- ✅ Estudos e pesquisa
- ✅ Demonstrações e mockups

**NÃO use para:**
- ❌ Violação de direitos autorais
- ❌ Redistribuição não autorizada
- ❌ Desinformação ou manipulação

**Comentários e imagens gerados por IA:**
- ✅ Sempre incluem marca d'água
- ✅ Disclaimer claro no README.txt
- ✅ Metadados EXIF indicando "AI Generated"

## 📄 Licença

Este projeto é fornecido "como está", sem garantias. Use por sua conta e risco, respeitando os termos de serviço do TikTok.

## 🐛 Suporte

Encontrou um bug? Abra uma issue no [GitHub](https://github.com/ricardo-oamaro/titkok-downloader/issues)!

## ✨ Autor

Desenvolvido com ❤️ usando Python, FastAPI e Ollama

---

**⚠️ Disclaimer:** Este projeto não é afiliado, associado ou endossado pelo TikTok. Use de forma responsável e ética.
