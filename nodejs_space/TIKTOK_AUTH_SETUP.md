# 🔐 Configuração de Autenticação TikTok

## Problema

O TikTok agora exige autenticação para baixar muitos vídeos. Você pode estar vendo este erro:

```
TikTok is requiring login for access to this content
```

## Solução

O serviço agora suporta usar cookies de um navegador onde você já está logado no TikTok.

---

## 📋 Passos para Configurar

### 1. **Faça Login no TikTok em seu Navegador**

Abra seu navegador preferido (Chrome, Firefox, Safari, Edge, etc.) e:
- Acesse https://www.tiktok.com
- Faça login com sua conta TikTok
- Navegue normalmente para confirmar que está autenticado

### 2. **Configure a Variável de Ambiente**

O arquivo `.env` já está configurado com:

```env
YTDLP_COOKIES_BROWSER=chrome
```

**Navegadores Suportados:**
- `chrome` - Google Chrome
- `firefox` - Mozilla Firefox
- `safari` - Safari (macOS)
- `edge` - Microsoft Edge
- `chromium` - Chromium
- `opera` - Opera
- `brave` - Brave Browser

**Para usar outro navegador**, edite o `.env`:

```env
# Por exemplo, para usar Firefox:
YTDLP_COOKIES_BROWSER=firefox

# Ou Safari:
YTDLP_COOKIES_BROWSER=safari
```

### 3. **Reinicie o Servidor**

Após editar o `.env`, reinicie o servidor para aplicar as mudanças:

```bash
# Pare o servidor atual (Ctrl+C no terminal)
# Depois inicie novamente:
yarn start:dev
```

---

## 🧪 Teste

Após configurar:

1. Acesse http://localhost:3000/
2. Cole uma URL do TikTok
3. Clique em "Baixar Vídeo"
4. O vídeo deve ser baixado com sucesso!

---

## ⚠️ Importante

### Requisitos
- Você DEVE estar logado no TikTok no navegador especificado
- O navegador deve ter cookies válidos e ativos
- Mantenha seu navegador atualizado

### Privacidade
- Os cookies são lidos apenas localmente pelo yt-dlp
- Nenhuma informação é enviada para servidores externos
- Os cookies não são armazenados ou transmitidos

### Problemas Comuns

**1. "Could not find browser"**
- Certifique-se de que o navegador especificado está instalado
- Use o caminho completo se necessário

**2. "No cookies found"**
- Faça login no TikTok no navegador especificado
- Limpe o cache e faça login novamente
- Tente usar outro navegador

**3. Ainda não funciona?**
- Verifique se está usando a versão mais recente do yt-dlp:
  ```bash
  brew upgrade yt-dlp
  ```
- Teste com diferentes navegadores
- Verifique os logs do servidor para mais detalhes

---

## 🔄 Desabilitar Cookies (Opcional)

Para tentar baixar sem autenticação (pode falhar para alguns vídeos):

```env
# Comente ou remova a linha:
# YTDLP_COOKIES_BROWSER=chrome
```

Ou deixe vazia:
```env
YTDLP_COOKIES_BROWSER=
```

---

## 📚 Mais Informações

- [yt-dlp FAQ sobre Cookies](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp)
- [Documentação yt-dlp](https://github.com/yt-dlp/yt-dlp)

---

## ✅ Verificação Rápida

Execute este comando para testar se o yt-dlp consegue acessar cookies:

```bash
yt-dlp --cookies-from-browser chrome --list-formats "https://www.tiktok.com/@test/video/123"
```

Se listar formatos, está funcionando! ✨



