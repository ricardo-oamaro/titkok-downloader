
# 🚀 TikTok Downloader API - Quick Start Guide

## ✅ Service Status
Your TikTok Video Downloader API is **RUNNING** and ready to use!

## 📍 Access Points
- **API Endpoint**: `http://localhost:3000/download`
- **Swagger Documentation**: `http://localhost:3000/api-docs`

## 🔑 Your API Keys
The following API keys are pre-configured and ready to use:
- `test-key-123` (for testing)
- `production-key-456` (for production use)

## 💡 How to Use

### Option 1: Using cURL (Terminal)
```bash
curl -X POST http://localhost:3000/download \
  -H "X-API-Key: test-key-123" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.tiktok.com/@username/video/1234567890123456789"}' \
  --output meu_video.mp4
```

### Option 2: Using Python
```python
import requests

def download_tiktok(url, api_key='test-key-123'):
    response = requests.post(
        'http://localhost:3000/download',
        headers={
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        },
        json={'url': url},
        stream=True
    )
    
    if response.status_code == 200:
        with open('video.mp4', 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print('✅ Download concluído: video.mp4')
    else:
        print(f'❌ Erro: {response.json()}')

# Example usage
download_tiktok('https://www.tiktok.com/@username/video/1234567890123456789')
```

### Option 3: Using JavaScript/Node.js
```javascript
const axios = require('axios');
const fs = require('fs');

async function downloadTikTok(url, apiKey = 'test-key-123') {
    try {
        const response = await axios({
            method: 'post',
            url: 'http://localhost:3000/download',
            headers: {
                'X-API-Key': apiKey,
                'Content-Type': 'application/json'
            },
            data: { url },
            responseType: 'stream'
        });

        const writer = fs.createWriteStream('video.mp4');
        response.data.pipe(writer);

        return new Promise((resolve, reject) => {
            writer.on('finish', () => {
                console.log('✅ Download concluído: video.mp4');
                resolve();
            });
            writer.on('error', reject);
        });
    } catch (error) {
        console.error('❌ Erro:', error.response?.data || error.message);
    }
}

// Example usage
downloadTikTok('https://www.tiktok.com/@username/video/1234567890123456789');
```

### Option 4: Using Swagger UI (Browser)
1. Open: http://localhost:3000/api-docs
2. Click on **"Authorize"** button (top right)
3. Enter your API key: `test-key-123`
4. Click **"Authorize"** and close
5. Expand the **POST /download** endpoint
6. Click **"Try it out"**
7. Enter a TikTok URL in the request body
8. Click **"Execute"**
9. Click **"Download file"** button to save the video

## 🎯 API Response Codes

| Code | Description |
|------|-------------|
| 200  | ✅ Success - Video downloaded |
| 400  | ❌ Invalid URL or video unavailable |
| 401  | ❌ Missing or invalid API key |
| 429  | ⏱️ Rate limit exceeded (wait 1 minute) |
| 500  | ❌ Server error |

## 🔒 Security Features
- ✅ **API Key Authentication**: Every request requires a valid API key
- ✅ **Rate Limiting**: Maximum 5 requests per minute per API key
- ✅ **URL Validation**: Only TikTok URLs are accepted
- ✅ **Auto Cleanup**: Downloaded files are automatically deleted after sending

## 📊 Rate Limiting
- **Limit**: 5 requests per minute
- **Per**: API key
- **Reset**: Automatic after 60 seconds

If you hit the rate limit, you'll receive a `429 Too Many Requests` error. Wait 60 seconds and try again.

## 🔧 Configuration

### Add New API Keys
Edit the `.env` file:
```env
API_KEYS=test-key-123,production-key-456,new-key-789
```

### Change Rate Limit
Edit the `.env` file:
```env
THROTTLE_LIMIT=10    # Allow 10 requests
THROTTLE_TTL=60000   # Per 60 seconds (60000ms)
```

### Change Port
Edit the `.env` file:
```env
PORT=8080
```

Then restart the service:
```bash
yarn start:dev
```

## 🧪 Testing

Test the API without downloading:
```bash
# Test authentication (should return 401)
curl -X POST http://localhost:3000/download \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.tiktok.com/@test/video/123"}'

# Test with valid key but invalid URL (should return 400)
curl -X POST http://localhost:3000/download \
  -H "X-API-Key: test-key-123" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://youtube.com/watch?v=123"}'
```

## ⚠️ Important Notes

### Legal Considerations
- **Only download videos you have permission to download**
- **Respect TikTok's Terms of Service**
- **Don't download copyrighted content without authorization**
- **This tool is for personal/educational use only**

### Limitations
- Only works with **public TikTok videos**
- **Private or deleted videos** will fail
- **Geo-restricted content** may not be accessible
- Video quality depends on TikTok's availability

## 🆘 Troubleshooting

### "API key is missing"
➜ Add the `X-API-Key` header to your request

### "Invalid API key"
➜ Use one of the configured keys: `test-key-123` or `production-key-456`

### "URL must be from tiktok.com domain"
➜ Make sure the URL starts with `https://www.tiktok.com/` or `https://vm.tiktok.com/`

### "Rate limit exceeded"
➜ Wait 60 seconds before making another request

### "Video unavailable"
➜ Check if the video is public and accessible in your region

## 📚 Full Documentation
See [README.md](README.md) for complete documentation.

## 🎉 Ready to Use!
Your API is fully configured and ready to download TikTok videos. Start making requests using any of the methods above!

---
**Built with ❤️ using NestJS + TypeScript + yt-dlp**
