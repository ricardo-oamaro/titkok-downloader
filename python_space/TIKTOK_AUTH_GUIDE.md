# 🔐 Guia de Autenticação TikTok

## ⚠️ Por que preciso fazer login?

Muitos vídeos do TikTok agora requerem que você esteja logado para visualizá-los. O serviço usa cookies do seu navegador para autenticar as requisições.

---

## ✅ Como Configurar (Passo a Passo)

### **1. Faça Login no TikTok no Chrome**

1. Abra o **Google Chrome**
2. Acesse: https://www.tiktok.com
3. Clique em **"Entrar"** (canto superior direito)
4. Faça login com sua conta TikTok
5. Certifique-se de que está **completamente logado**
6. **Deixe o Chrome aberto** (pelo menos em background)

---

### **2. Verifique a Configuração do Servidor**

O arquivo `.env` deve ter:

```env
YTDLP_COOKIES_BROWSER=chrome
```

**Navegadores suportados:**
- `chrome` (Google Chrome) ✅ **Recomendado**
- `firefox` (Mozilla Firefox)
- `edge` (Microsoft Edge)
- `safari` (Safari - macOS)
- `brave` (Brave Browser)
- `chromium` (Chromium)
- `opera` (Opera)

---

### **3. Reinicie o Servidor**

Se você acabou de fazer login, reinicie o servidor:

```bash
# Parar servidor (Ctrl+C ou)
lsof -ti:8000 | xargs kill -9

# Reiniciar
cd python_space
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

### **4. Teste o Download**

Acesse: http://localhost:8000/

Tente baixar um vídeo do TikTok!

---

## 🐛 Troubleshooting

### **"TikTok requer autenticação para este vídeo"**

**Causas possíveis:**
1. ❌ Você não está logado no TikTok no Chrome
2. ❌ Chrome está fechado
3. ❌ Cookies expirados
4. ❌ Navegador errado configurado no `.env`

**Soluções:**
- ✅ Faça login novamente no TikTok
- ✅ Mantenha o Chrome aberto
- ✅ Limpe cookies e faça login novamente
- ✅ Verifique se o `YTDLP_COOKIES_BROWSER` está correto

---

### **"Failed to get cookie from chrome" ou "Could not find cookies database"**

**Causa:** Chrome está com perfil bloqueado ou inacessível

**Solução:**
1. Feche **TODAS** as janelas do Chrome
2. Abra o Chrome novamente
3. Faça login no TikTok
4. Reinicie o servidor Python

---

### **"Seu IP está bloqueado pelo TikTok"**

**Causa:** TikTok bloqueou temporariamente seu IP

**Soluções:**
- ⏱️ Aguarde alguns minutos ou horas
- 🌐 Use uma VPN (se apropriado)
- 📱 Tente em outra rede

---

### **Vídeo privado ou indisponível**

Alguns vídeos são:
- 🔒 Privados (só o autor pode ver)
- 🌍 Bloqueados geograficamente
- 🗑️ Deletados

Nestes casos, o download não é possível mesmo com autenticação.

---

## 🔄 Usando Outro Navegador

Se você prefere usar **Firefox** ao invés de Chrome:

1. Faça login no TikTok no Firefox
2. Edite `.env`:
   ```env
   YTDLP_COOKIES_BROWSER=firefox
   ```
3. Reinicie o servidor

---

## 🔍 Verificar se Está Funcionando

### **Teste rápido via cURL:**

```bash
curl -X POST http://localhost:8000/download \
  -H "X-API-Key: test-key-123" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.tiktok.com/@usuario/video/1234567890"}' \
  -o video.mp4
```

Se funcionar, você verá o download do vídeo começar!

---

## 📖 Mais Informações

- **yt-dlp Cookies FAQ**: https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp
- **TikTok Terms of Service**: https://www.tiktok.com/legal/terms-of-service

---

## ⚖️ Aviso Legal

- ✅ Use apenas para vídeos que você tem permissão para baixar
- ✅ Respeite os Termos de Serviço do TikTok
- ✅ Respeite direitos autorais e propriedade intelectual
- ✅ Não redistribua conteúdo sem autorização

---

**💡 Dica:** Se você continua tendo problemas, verifique os logs do servidor para mensagens de erro mais detalhadas.



