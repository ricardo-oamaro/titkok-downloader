# 🎬 TikTok Video Downloader Service

Serviço completo para download de vídeos do TikTok com geração de comentários inteligentes via IA e imagens estilo Instagram.

## 🌟 Funcionalidades

- ✅ **Download de vídeos** do TikTok em alta qualidade via `yt-dlp`
- 🤖 **Geração de comentários** realistas usando IA local (Ollama)
- 🎨 **Criação de imagens** estilo Instagram com os comentários gerados
- 📦 **Empacotamento ZIP** com vídeo + comentários + 15 imagens
- 🎬 **NOVO: Edição automática de vídeos** com IA
  - Cortes inteligentes baseados em mudanças de cena
  - Legendas automáticas com os comentários gerados
  - Efeitos visuais (zoom, fade, speed ramp)
  - 4 estilos de edição: Viral, Storytelling, Educational, Minimal
  - Análise de vídeo (momentos-chave, movimento, brilho)
  - Criação de compilações automáticas
- 🔐 **Autenticação via API Key** para segurança
- ⚡ **Rate limiting** para prevenir abuso
- 🌐 **Interface web** simples e moderna
- 📖 **API RESTful** documentada com Swagger/OpenAPI

## 🏗️ Tecnologias

- **Python 3.11+** - Linguagem principal
- **FastAPI** - Framework web moderno e rápido
- **yt-dlp** - Download de vídeos do TikTok
- **Ollama (Llama 3)** - IA local para geração de comentários
- **MoviePy** - Edição programática de vídeos
- **OpenCV** - Análise de vídeo e detecção de cenas
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

### 1. Download de Vídeo + Comentários + Imagens

```bash
curl -X POST "http://localhost:8000/download" \
  -H "Content-Type: application/json" \
  -H "x-api-key: sua-api-key" \
  -d '{"url": "https://www.tiktok.com/@user/video/123456789"}' \
  --output video_package.zip
```

**Resposta:** ZIP contendo:
- `video.mp4` - Vídeo do TikTok
- `comentarios.txt` - 15 comentários gerados por IA
- `instagram_01.png` até `instagram_15.png` - Imagens dos comentários
- `README.txt` - Disclaimer

---

### 2. Edição Automática de Vídeo ⭐ NOVO

```bash
curl -X POST "http://localhost:8000/edit-video" \
  -H "Content-Type: application/json" \
  -H "x-api-key: sua-api-key" \
  -d '{
    "url": "https://www.tiktok.com/@user/video/123456789",
    "style": "viral",
    "add_subtitles": true,
    "target_duration": 30
  }'
```

**Estilos disponíveis:**
- `viral` - Cortes rápidos, efeitos trending, acelera 10%
- `storytelling` - Transições suaves, legendas completas
- `educational` - Texto explicativo, sem acelerações
- `minimal` - Apenas cortes, sem efeitos

**Resposta:** JSON com informações do vídeo editado

---

### 3. Análise de Vídeo

```bash
curl -X POST "http://localhost:8000/analyze-video" \
  -H "Content-Type: application/json" \
  -H "x-api-key: sua-api-key" \
  -d '{"url": "https://www.tiktok.com/@user/video/123456789"}'
```

**Retorna:**
- Momentos-chave detectados
- Mudanças de cena
- Intensidade de movimento
- Brilho médio
- Sugestões de cortes

---

### 4. Criação de Compilação

```bash
curl -X POST "http://localhost:8000/create-compilation" \
  -H "Content-Type: application/json" \
  -H "x-api-key: sua-api-key" \
  -d '{
    "video_paths": [
      "https://www.tiktok.com/@user/video/111",
      "https://www.tiktok.com/@user/video/222",
      "https://www.tiktok.com/@user/video/333"
    ],
    "theme": "trending",
    "max_duration": 60,
    "add_intro": true,
    "add_outro": true
  }'
```

**Resposta:** Vídeo compilado com transições suaves

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
    │   ├── main.py                      # Aplicação FastAPI + novos endpoints
    │   ├── config.py                    # Configurações
    │   ├── models/                      # Schemas Pydantic
    │   │   ├── schemas.py
    │   │   ├── comment_schemas.py
    │   │   └── video_edit_schemas.py    # ⭐ NOVO: Schemas de edição
    │   ├── services/                    # Lógica de negócio
    │   │   ├── download_service.py
    │   │   ├── ai_comments_service.py
    │   │   ├── image_generator_service.py
    │   │   ├── text_parser_service.py
    │   │   ├── zip_service.py
    │   │   ├── capcut_service.py        # ⭐ NOVO: Automação de edição
    │   │   └── video_analyzer_service.py # ⭐ NOVO: Análise de vídeo
    │   ├── middleware/                  # Autenticação
    │   │   └── auth.py
    │   └── static/                      # Interface web
    │       ├── index.html
    │       ├── styles.css
    │       └── script.js
    ├── tests/                           # Testes unitários e integração
    │   ├── conftest.py
    │   ├── test_ai_comments_service.py
    │   ├── test_image_generator_service.py
    │   ├── test_text_parser_service.py
    │   ├── test_zip_service.py
    │   ├── test_integration_comments.py
    │   └── test_video_editing.py        # ⭐ NOVO: Testes de edição
    ├── requirements.txt                 # Dependências Python (atualizado)
    ├── .env.example                     # Exemplo de configuração
    ├── README.md                        # Documentação
    ├── TIKTOK_AUTH_GUIDE.md             # Guia de autenticação
    ├── COMMENTS_LIMITATION.MD           # Limitações conhecidas
    └── FIXES_APPLIED.md                 # Histórico de correções
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

## 🎯 Casos de Uso - Edição Automática

### 1. Criador de Clipes Virais
```python
# Download TikTok → Detectar momentos-chave → Cortes automáticos
# → Legendas virais → Efeitos trending → Exportar múltiplas versões

POST /edit-video
{
  "url": "tiktok.com/@user/video/123",
  "style": "viral",
  "target_duration": 15,
  "add_subtitles": true
}
```

**Resultado:** Vídeo otimizado para máximo engajamento

---

### 2. Compilações Automáticas
```python
# Download 10 vídeos → Análise de tema → Ordenar por relevância
# → Transições suaves → Música unificada → Intro/Outro

POST /create-compilation
{
  "video_paths": ["url1", "url2", "url3"],
  "theme": "trending",
  "max_duration": 60
}
```

**Resultado:** Compilação profissional em segundos

---

### 3. Conteúdo Educacional
```python
# Download tutorial → Legendas com IA → Marcadores de capítulos
# → Zoom em pontos-chave → Pausas estratégicas

POST /edit-video
{
  "url": "tiktok.com/@teacher/video/456",
  "style": "educational",
  "add_subtitles": true
}
```

**Resultado:** Vídeo didático com legendas e destaques

---

### 4. Análise para Estratégia
```python
# Analisar concorrentes → Identificar padrões de cortes
# → Detectar momentos de pico → Replicar estratégia

POST /analyze-video
{
  "url": "tiktok.com/@viral/video/789"
}
```

**Resultado:** Insights sobre estrutura e timing

---

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
