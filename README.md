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

## 🏗️ Arquitetura

O projeto possui **duas implementações**:

### 1. **Node.js/NestJS** (`nodejs_space/`)
- Framework: NestJS
- Download: `yt-dlp` via child_process
- Status: Funcional (sem geração de imagens)

### 2. **Python/FastAPI** (`python_space/`) ⭐ **RECOMENDADO**
- Framework: FastAPI
- Download: `yt-dlp` (biblioteca Python)
- IA: Ollama (Llama 3)
- Imagens: Pillow (PIL)
- Status: Completo com todas as funcionalidades

## 🚀 Quick Start (Python/FastAPI)

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
git clone https://github.com/seu-usuario/tiktok_downloader_service.git
cd tiktok_downloader_service/python_space

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
├── nodejs_space/           # Implementação Node.js/NestJS
│   ├── src/
│   ├── public/            # Interface web
│   └── package.json
│
└── python_space/          # Implementação Python/FastAPI ⭐
    ├── app/
    │   ├── main.py        # Aplicação FastAPI
    │   ├── config.py      # Configurações
    │   ├── models/        # Schemas Pydantic
    │   ├── services/      # Lógica de negócio
    │   │   ├── download_service.py
    │   │   ├── ai_comments_service.py
    │   │   ├── image_generator_service.py
    │   │   └── zip_service.py
    │   └── static/        # Interface web
    ├── tests/             # Testes unitários e integração
    └── requirements.txt
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

1. **Ollama** extrai metadados do vídeo (título, descrição, hashtags)
2. **Llama 3** gera 15 comentários realistas baseados no contexto
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

## 🛠️ Tecnologias

### Backend
- **Python 3.11+** - Linguagem principal
- **FastAPI** - Framework web moderno
- **yt-dlp** - Download de vídeos
- **Ollama** - IA local para geração de comentários
- **Pillow (PIL)** - Geração de imagens

### Frontend
- **HTML5/CSS3/JavaScript** - Interface web responsiva
- **Vanilla JS** - Sem frameworks pesados

### DevOps
- **pytest** - Testes unitários e integração
- **slowapi** - Rate limiting
- **pydantic** - Validação de dados

## 📝 Documentação Adicional

- 📖 **[Guia de Autenticação TikTok](python_space/TIKTOK_AUTH_GUIDE.md)**
- ⚠️ **[Limitações de Comentários](python_space/COMMENTS_LIMITATION.md)**
- 🔧 **[Correções Aplicadas](python_space/FIXES_APPLIED.md)**
- 🚀 **[Quick Start Node.js](nodejs_space/QUICK_START.md)**

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

Encontrou um bug? Abra uma issue no GitHub!

## ✨ Autor

Desenvolvido com ❤️ usando Python, FastAPI e Ollama

---

**⚠️ Disclaimer:** Este projeto não é afiliado, associado ou endossado pelo TikTok. Use de forma responsável e ética.

