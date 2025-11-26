// API Configuration
const API_KEY = 'test-key-123';
const API_ENDPOINT = '/download';

// DOM Elements
const form = document.getElementById('downloadForm');
const urlInput = document.getElementById('tiktokUrl');
const downloadBtn = document.getElementById('downloadBtn');
const btnText = document.querySelector('.btn-text');
const btnLoading = document.querySelector('.btn-loading');
const messageDiv = document.getElementById('message');
const progressContainer = document.getElementById('progressContainer');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');

// Form submission handler
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const url = urlInput.value.trim();
    
    if (!url) {
        showMessage('Por favor, insira uma URL do TikTok', 'error');
        return;
    }
    
    // Validate TikTok URL
    if (!url.includes('tiktok.com')) {
        showMessage('Por favor, insira uma URL válida do TikTok', 'error');
        return;
    }
    
    await downloadVideo(url);
});

// Download video function
async function downloadVideo(url) {
    try {
        // Update UI to loading state
        setLoadingState(true);
        hideMessage();
        showProgress('Iniciando download...');
        
        // Make API request
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': API_KEY
            },
            body: JSON.stringify({ url })
        });
        
        // Handle different response statuses
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            handleError(response.status, errorData);
            return;
        }
        
        // Update progress
        updateProgress(50, 'Recebendo vídeo...');
        
        // Get the blob from response
        const blob = await response.blob();
        
        // Update progress
        updateProgress(75, 'Preparando arquivo...');
        
        // Extract filename from Content-Disposition header or use default
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'tiktok_video.mp4';
        
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
            if (filenameMatch) {
                filename = filenameMatch[1];
            }
        }
        
        // Create download link and trigger download
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        
        // Cleanup
        window.URL.revokeObjectURL(downloadUrl);
        document.body.removeChild(a);
        
        // Check if comments are available
        const commentsAvailable = response.headers.get('X-Comments-Available');
        if (commentsAvailable === 'true') {
            updateProgress(85, 'Baixando comentários...');
            await downloadComments(response);
        }
        
        // Update progress
        updateProgress(100, 'Download concluído!');
        
        // Show success message
        const successMsg = commentsAvailable === 'true' 
            ? '✅ Vídeo e comentários baixados com sucesso!' 
            : '✅ Vídeo baixado com sucesso!';
        
        setTimeout(() => {
            hideProgress();
            showMessage(successMsg, 'success');
            urlInput.value = ''; // Clear input
        }, 1000);
        
    } catch (error) {
        console.error('Download error:', error);
        hideProgress();
        
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            showMessage('❌ Erro de conexão. Verifique se o servidor está rodando.', 'error');
        } else {
            showMessage('❌ Erro ao baixar o vídeo. Tente novamente.', 'error');
        }
    } finally {
        setLoadingState(false);
    }
}

// Download comments function
async function downloadComments(response) {
    try {
        const commentsData = response.headers.get('X-Comments-Data');
        const commentsFilename = response.headers.get('X-Comments-Filename') || 'comments.txt';
        
        if (!commentsData) {
            console.warn('Comments data not found in response headers');
            return;
        }
        
        // Decode base64 to text
        const commentsText = atob(commentsData);
        
        // Create blob and download
        const commentsBlob = new Blob([commentsText], { type: 'text/plain' });
        const downloadUrl = window.URL.createObjectURL(commentsBlob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = commentsFilename;
        document.body.appendChild(a);
        a.click();
        
        // Cleanup
        window.URL.revokeObjectURL(downloadUrl);
        document.body.removeChild(a);
        
        console.log('Comments downloaded successfully');
    } catch (error) {
        console.error('Failed to download comments:', error);
        // Don't throw - comments are optional
    }
}

// Handle API errors
function handleError(status, errorData) {
    hideProgress();
    let errorMessage = '❌ Erro ao baixar o vídeo.';
    
    switch (status) {
        case 400:
            errorMessage = '❌ URL inválida ou vídeo indisponível. Verifique o link.';
            if (errorData.message && Array.isArray(errorData.message)) {
                errorMessage += '\n' + errorData.message.join(', ');
            } else if (errorData.message) {
                errorMessage = '❌ ' + errorData.message;
                
                // Check if it's an authentication error
                if (errorData.message.includes('authentication') || errorData.message.includes('YTDLP_COOKIES_BROWSER')) {
                    errorMessage += '\n\n💡 Dica: Configure a autenticação com cookies do navegador.';
                    errorMessage += '\n📖 Veja: TIKTOK_AUTH_SETUP.md';
                }
            }
            break;
        case 401:
            errorMessage = '❌ Erro de autenticação. Chave API inválida.';
            break;
        case 429:
            errorMessage = '⏱️ Muitas requisições. Aguarde 1 minuto e tente novamente.';
            break;
        case 500:
            errorMessage = '❌ Erro no servidor. O vídeo pode estar privado ou indisponível.';
            if (errorData.message) {
                errorMessage += '\nDetalhes: ' + errorData.message;
            }
            break;
        default:
            errorMessage = `❌ Erro ${status}. Tente novamente.`;
    }
    
    showMessage(errorMessage, 'error');
}

// UI Helper Functions
function setLoadingState(isLoading) {
    downloadBtn.disabled = isLoading;
    btnText.style.display = isLoading ? 'none' : 'flex';
    btnLoading.style.display = isLoading ? 'flex' : 'none';
    urlInput.disabled = isLoading;
}

function showMessage(text, type = 'info') {
    messageDiv.textContent = text;
    messageDiv.className = `message ${type} show`;
}

function hideMessage() {
    messageDiv.className = 'message';
}

function showProgress(text) {
    progressContainer.style.display = 'block';
    progressText.textContent = text;
    progressFill.style.width = '0%';
}

function updateProgress(percent, text) {
    progressFill.style.width = percent + '%';
    progressText.textContent = text;
}

function hideProgress() {
    progressContainer.style.display = 'none';
    progressFill.style.width = '0%';
}

// Auto-focus input on page load
window.addEventListener('load', () => {
    urlInput.focus();
});

// Clear error message when user starts typing
urlInput.addEventListener('input', () => {
    if (messageDiv.classList.contains('error')) {
        hideMessage();
    }
});

// Paste event handler - auto-trim URLs
urlInput.addEventListener('paste', (e) => {
    setTimeout(() => {
        urlInput.value = urlInput.value.trim();
    }, 0);
});

console.log('🚀 TikTok Downloader Interface loaded successfully!');
console.log('📡 API Endpoint:', API_ENDPOINT);
console.log('🔑 Using API Key:', API_KEY.substring(0, 8) + '...');

