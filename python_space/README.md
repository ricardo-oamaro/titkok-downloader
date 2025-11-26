# 🎬 TikTok Video Downloader API - Python FastAPI

Serviço REST API **em Python** para download de vídeos do TikTok com autenticação via cookies do navegador e rate limiting.

✨ **NOVO:** Sistema de **geração de comentários com IA (Ollama)** + **imagens estilo Instagram**!

⚠️ **Nota:** Comentários reais do TikTok estão bloqueados. Em vez disso, geramos comentários realistas com IA baseados no contexto do vídeo.

## 🚀 Por Que Python?

- ✅ **yt-dlp nativo**: Biblioteca Python integrada diretamente
- ✅ **Melhor controle**: Acesso direto aos dados do yt-dlp
- ✅ **Mais opções**: TikTokApi, Playwright, scraping avançado
- ✅ **Debug mais fácil**: Logs detalhados e tratamento de erros
- ✅ **FastAPI**: Performance similar ao Node.js + documentação automática

## ✨ Funcionalidades

### 🎥 Download de Vídeo
- Download de vídeos públicos do TikTok em alta qualidade (MP4)
- Suporte a autenticação via cookies do navegador
- Contorna proteções anti-bot com `curl-cffi`

### 🤖 Geração de Comentários com IA
- **15 comentários realistas** gerados por Ollama (Llama 3)
- Baseados no contexto do vídeo (título, descrição, hashtags)
- Comentários variados: elogios, perguntas, críticas, emojis
- Salvos em arquivo `comentarios.txt`

### 🎨 Imagens Estilo Instagram
- **15 imagens PNG** (1080x200px) estilo Instagram
- Layout autêntico com avatares, usernames, likes, timestamps
- Marca d'água "Gerado por IA" em todas as imagens
- Cores e iniciais baseadas no nome do usuário

### 📦 Pacote Completo
- Retorna **arquivo ZIP** contendo:
  - `video.mp4` - Vídeo original do TikTok
  - `comentarios.txt` - 15 comentários gerados
  - `instagram_01.png` até `instagram_15.png` - Imagens dos comentários
  - `README.txt` - Disclaimer sobre conteúdo gerado por IA

### 🔒 Segurança
- API Key authentication
- Rate limiting (5 requests/minuto padrão)
- CORS configurável

## 📋 Prerequisites

- Python 3.9+
- pip ou poetry
- yt-dlp (instalado automaticamente)
- **Ollama** (para geração de comentários com IA) - [Download](https://ollama.ai/)

## 🔧 Instalação

### 1. Criar ambiente virtual (recomendado)

```bash
cd python_space
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Edite o .env conforme necessário
```

### 4. Instalar e configurar Ollama (para comentários com IA)

```bash
# MacOS
brew install ollama

# Linux
curl https://ollama.ai/install.sh | sh

# Iniciar servidor Ollama
ollama serve

# Em outro terminal, baixar modelo Llama 3
ollama pull llama3
```

**Configuração no `.env`:**
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

### 5. Preparar playwright (se usar scraping - opcional)

```bash
playwright install chromium
```

## 🏃 Executar

### Modo desenvolvimento

```bash
# Com uvicorn direto
uvicorn app.main:app --reload --port 8000

# Ou usando o módulo
python -m app.main
```

### Modo produção

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🌐 Acessar

- **Interface Web**: http://localhost:8000/
- **API Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📖 API Endpoints

### POST /download

Baixa vídeo do TikTok + gera comentários com IA + cria imagens Instagram.

**Headers:**
```
X-API-Key: test-key-123
Content-Type: application/json
```

**Body:**
```json
{
  "url": "https://www.tiktok.com/@username/video/123456789"
}
```

**Response:**
- 📦 **Arquivo ZIP** contendo:
  - `video.mp4` - Vídeo do TikTok
  - `comentarios.txt` - 15 comentários gerados por IA
  - `instagram_01.png` até `instagram_15.png` - Imagens dos comentários
  - `README.txt` - Disclaimer

**Exemplo com cURL:**
```bash
curl -X POST http://localhost:8000/download \
  -H "X-API-Key: test-key-123" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.tiktok.com/@user/video/123"}' \
  -o video_package.zip
```

**Exemplo com Python:**
```python
import requests

response = requests.post(
    'http://localhost:8000/download',
    headers={'X-API-Key': 'test-key-123'},
    json={'url': 'https://www.tiktok.com/@user/video/123'}
)

with open('video_package.zip', 'wb') as f:
    f.write(response.content)
```

### GET /health

Health check do serviço.

## 🔑 Autenticação

API keys configuradas no `.env`:

```env
API_KEYS=test-key-123,production-key-456
```

## ⚡ Rate Limiting

Padrão: 5 requisições por minuto por IP.

Configurável em `.env`:
```env
RATE_LIMIT=10/minute
```

## 🎯 Extração de Comentários

O serviço Python usa **yt-dlp com flag `getcomments`** para extrair comentários diretamente:

- ✅ 15 comentários mais relevantes (ordenados por likes)
- ✅ Cada comentário limitado a 200 caracteres
- ✅ Total limitado a 5KB para evitar problemas de headers
- ✅ Download automático de arquivo .txt separado

## 📊 Estrutura do Projeto

```
python_space/
├── app/
│   ├── main.py              # FastAPI app principal
│   ├── config.py            # Configurações
│   ├── middleware/
│   │   └── auth.py          # Autenticação API Key
│   ├── models/
│   │   └── schemas.py       # Modelos Pydantic
│   ├── services/
│   │   └── download_service.py  # Lógica de download e comentários
│   └── static/
│       ├── index.html       # Interface web
│       ├── styles.css       # Estilos
│       └── script.js        # JavaScript
├── requirements.txt         # Dependências Python
├── .env                     # Variáveis de ambiente
└── README.md               # Este arquivo
```

## 🧪 Testes

### Teste rápido via cURL

```bash
curl -X POST http://localhost:8000/download \
  -H "X-API-Key: test-key-123" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.tiktok.com/@alma.gospell/video/7552463526804114744"}' \
  --output video.mp4
```

### Teste na interface web

1. Abra http://localhost:8000/
2. Cole uma URL do TikTok
3. Clique em "Baixar Vídeo"
4. Vídeo e comentários serão baixados automaticamente

## 🔧 Troubleshooting

### Comentários não são extraídos

```bash
# Teste manual
python3 -c "
import yt_dlp
ydl_opts = {'skip_download': True, 'getcomments': True, 'cookiesfrombrowser': ('chrome',)}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info('URL_DO_TIKTOK', download=False)
    print(f'Comments: {len(info.get(\"comments\", []))}')
"
```

### Erro de cookies

Certifique-se de estar logado no TikTok no navegador especificado (Chrome por padrão).

## 📚 Dependências Principais

- **FastAPI**: Framework web moderno
- **uvicorn**: Servidor ASGI
- **yt-dlp**: Download de vídeos
- **slowapi**: Rate limiting
- **pydantic**: Validação de dados

## 🚀 Deploy

### Docker (recomendado)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build e run:

```bash
docker build -t tiktok-downloader-python .
docker run -p 8000:8000 --env-file .env tiktok-downloader-python
```

## ⚖️ Legal

- Use apenas para vídeos que você tem permissão para baixar
- Respeite os termos de serviço do TikTok
- Uso educacional/pessoal apenas

---

**⚡ Powered by Python + FastAPI + yt-dlp**

