
# 🎬 TikTok Video Downloader API

A production-grade REST API service for downloading TikTok videos with authentication, rate limiting, and comprehensive security features.

## 🚀 Quick Start

**Your API is ready to use!**

```bash
# Example: Download a TikTok video
curl -X POST http://localhost:3000/download \
  -H "X-API-Key: test-key-123" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.tiktok.com/@username/video/1234567890123456789"}' \
  --output video.mp4
```

**Your API Keys (configured):**
- `test-key-123` (for testing)
- `production-key-456` (for production)

**Access Swagger UI:** http://localhost:3000/api-docs

## 🚀 Features

- **Video Download**: Download TikTok videos using yt-dlp and receive them as binary streams
- **Web Interface**: Simple web UI for easy video downloads at `/`
- **TikTok Authentication**: Cookie-based authentication support for restricted videos
- **API Authentication**: Secure API key-based authentication via headers
- **Rate Limiting**: 5 requests per minute per API key to prevent abuse
- **URL Validation**: Validates TikTok URLs before processing
- **Auto Cleanup**: Temporary files are automatically deleted after streaming
- **Swagger Documentation**: Interactive API documentation at `/api-docs`
- **Error Handling**: Comprehensive error messages for various failure scenarios
- **Logging**: Request logging for monitoring and debugging

## 📋 Prerequisites

- Node.js 18+ and Yarn
- Python 3.x with pip
- yt-dlp (automatically installed during setup)

## 🔧 Installation

1. **Install dependencies:**
   ```bash
   yarn install
   ```

2. **Install yt-dlp:**
   ```bash
   pip3 install -U yt-dlp
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set your API keys:
   ```env
   API_KEYS=your-secret-key-1,your-secret-key-2
   THROTTLE_TTL=60000
   THROTTLE_LIMIT=5
   PORT=3000
   DOWNLOADS_DIR=./tmp/downloads
   
   # Optional: For TikTok videos requiring authentication
   YTDLP_COOKIES_BROWSER=chrome
   ```

4. **Configure TikTok Authentication (if needed):**
   
   Many TikTok videos now require authentication. See [TIKTOK_AUTH_SETUP.md](TIKTOK_AUTH_SETUP.md) for detailed instructions.

## 🏃 Running the Service

### Development mode
```bash
yarn start:dev
```

### Production mode
```bash
yarn build
yarn start:prod
```

The service will be available at `http://localhost:3000`

## 🌐 Web Interface

Access the simple web interface at:
```
http://localhost:3000/
```

Features:
- Input field for TikTok URL
- One-click download button
- Progress indicator
- Error handling with helpful messages
- Mobile-responsive design

## 📖 API Documentation

### Swagger UI
Once the service is running, access interactive documentation at:
```
http://localhost:3000/api-docs
```

### Endpoint: POST /download

**Description**: Downloads a TikTok video and returns it as a binary stream

**Headers:**
- `X-API-Key` (required): Your API key for authentication
- `Content-Type`: `application/json`

**Request Body:**
```json
{
  "url": "https://www.tiktok.com/@username/video/1234567890123456789"
}
```

**Success Response (200):**
- Content-Type: `video/mp4`
- Content-Disposition: `attachment; filename="tiktok_<uuid>.mp4"`
- Body: Binary video file stream

**Error Responses:**

| Status Code | Description |
|-------------|-------------|
| 400 | Invalid URL format or video unavailable |
| 401 | Missing or invalid API key |
| 429 | Rate limit exceeded (5 requests per minute) |
| 500 | Internal server error during download |

## 🔐 Authentication

The API uses API key authentication via the `X-API-Key` header.

### Generating API Keys

1. Generate a secure random key:
   ```bash
   node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
   ```

2. Add the key to your `.env` file:
   ```env
   API_KEYS=key1,key2,key3
   ```

3. Share the key securely with authorized users

## 📝 Usage Examples

### Using cURL

```bash
curl -X POST http://localhost:3000/download \
  -H "X-API-Key: your-secret-key-1" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.tiktok.com/@username/video/1234567890123456789"}' \
  --output video.mp4
```

### Using Postman

1. **Method**: POST
2. **URL**: `http://localhost:3000/download`
3. **Headers**:
   - `X-API-Key`: `your-secret-key-1`
   - `Content-Type`: `application/json`
4. **Body** (raw JSON):
   ```json
   {
     "url": "https://www.tiktok.com/@username/video/1234567890123456789"
   }
   ```
5. **Send & Download**: Click "Send and Download" to save the video file

### Using JavaScript/Node.js

```javascript
const axios = require('axios');
const fs = require('fs');

async function downloadTikTokVideo(url) {
  try {
    const response = await axios({
      method: 'post',
      url: 'http://localhost:3000/download',
      headers: {
        'X-API-Key': 'your-secret-key-1',
        'Content-Type': 'application/json'
      },
      data: { url },
      responseType: 'stream'
    });

    const writer = fs.createWriteStream('video.mp4');
    response.data.pipe(writer);

    return new Promise((resolve, reject) => {
      writer.on('finish', resolve);
      writer.on('error', reject);
    });
  } catch (error) {
    console.error('Download failed:', error.response?.data || error.message);
  }
}

downloadTikTokVideo('https://www.tiktok.com/@username/video/1234567890123456789');
```

### Using Python

```python
import requests

def download_tiktok_video(url, api_key, output_file='video.mp4'):
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    data = {'url': url}
    
    response = requests.post(
        'http://localhost:3000/download',
        headers=headers,
        json=data,
        stream=True
    )
    
    if response.status_code == 200:
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f'Video saved to {output_file}')
    else:
        print(f'Error: {response.json()}')

download_tiktok_video(
    'https://www.tiktok.com/@username/video/1234567890123456789',
    'your-secret-key-1'
)
```

## 🧪 Testing

### Run unit tests
```bash
yarn test
```

### Run end-to-end tests
```bash
yarn test:e2e
```

### Run tests with coverage
```bash
yarn test:cov
```

## ⚠️ Important Notes

### Legal Considerations
- **Respect Copyright**: Only download videos you have permission to download
- **TikTok Terms of Service**: Review TikTok's ToS before using this service
- **Fair Use**: Ensure your usage complies with applicable laws and regulations
- **User Consent**: Only download content with proper authorization

### Rate Limiting
- Default: 5 requests per minute per API key
- Configure in `.env` via `THROTTLE_TTL` and `THROTTLE_LIMIT`
- Rate limits reset automatically after the TTL expires

### Limitations
- Only supports public TikTok videos
- Video quality depends on availability from TikTok
- Large videos may take longer to download
- Private or restricted videos will return an error

### Security Best Practices
- **Never commit** `.env` file to version control
- **Rotate API keys** regularly
- **Use HTTPS** in production environments
- **Monitor logs** for suspicious activity
- **Implement additional authentication** for production use (OAuth, JWT, etc.)

## 🐛 Troubleshooting

### "yt-dlp command not found"
```bash
pip3 install -U yt-dlp
# Or ensure yt-dlp is in your PATH
export PATH="$HOME/.local/bin:$PATH"
```

### "Video unavailable"
- Verify the video URL is correct and accessible
- Check if the video is public (not private/deleted)
- TikTok may have geo-restrictions on certain content

### "Rate limit exceeded"
- Wait for the rate limit window to reset (60 seconds by default)
- Use a different API key if available
- Contact the administrator to adjust rate limits

### Port already in use
```bash
# Change PORT in .env file
PORT=3001
```

## 📊 Monitoring

The service logs all requests with timestamps:
- Successful downloads
- Failed attempts with error details
- Rate limit violations
- Authentication failures

Check logs for monitoring and debugging:
```bash
# Development mode shows console logs
yarn start:dev
```

## 🔄 Updates

Keep yt-dlp updated for best compatibility:
```bash
pip3 install -U yt-dlp
```

## 📄 License

This project is for educational and personal use only. Users are responsible for ensuring compliance with all applicable laws and terms of service.

## 🤝 Support

For issues, questions, or contributions:
- Check existing documentation
- Review error messages carefully
- Test with known working TikTok URLs
- Verify API key and network connectivity

---

**⚡ Built with NestJS, TypeScript, and yt-dlp**
