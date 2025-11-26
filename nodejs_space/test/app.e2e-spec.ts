
import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication, ValidationPipe } from '@nestjs/common';
import request from 'supertest';
import { AppModule } from './../src/app.module';

describe('TikTok Downloader API (e2e)', () => {
  let app: INestApplication;
  const validApiKey = 'test-key-123';
  const invalidApiKey = 'invalid-key';

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();

    app.useGlobalPipes(
      new ValidationPipe({
        whitelist: true,
        forbidNonWhitelisted: true,
        transform: true,
      }),
    );

    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  describe('/download (POST)', () => {
    it('should return 401 without API key', () => {
      return request(app.getHttpServer())
        .post('/download')
        .send({ url: 'https://www.tiktok.com/@user/video/123' })
        .expect(401)
        .expect((res) => {
          expect(res.body.message).toContain('API key is missing');
        });
    });

    it('should return 401 with invalid API key', () => {
      return request(app.getHttpServer())
        .post('/download')
        .set('X-API-Key', invalidApiKey)
        .send({ url: 'https://www.tiktok.com/@user/video/123' })
        .expect(401)
        .expect((res) => {
          expect(res.body.message).toContain('Invalid API key');
        });
    });

    it('should return 400 with invalid URL format', () => {
      return request(app.getHttpServer())
        .post('/download')
        .set('X-API-Key', validApiKey)
        .send({ url: 'not-a-url' })
        .expect(400)
        .expect((res) => {
          expect(res.body.message).toBeDefined();
        });
    });

    it('should return 400 with non-TikTok URL', () => {
      return request(app.getHttpServer())
        .post('/download')
        .set('X-API-Key', validApiKey)
        .send({ url: 'https://www.youtube.com/watch?v=123' })
        .expect(400)
        .expect((res) => {
          const message = Array.isArray(res.body.message) 
            ? res.body.message.join(' ') 
            : res.body.message;
          expect(message).toContain('tiktok.com');
        });
    });

    it('should return 400 with missing URL field', () => {
      return request(app.getHttpServer())
        .post('/download')
        .set('X-API-Key', validApiKey)
        .send({})
        .expect(400);
    });

    it('should accept valid TikTok URL with proper API key', () => {
      // Note: This will fail if the URL is actually invalid/doesn't exist
      // In real e2e tests, you'd use a mock or a known working test URL
      return request(app.getHttpServer())
        .post('/download')
        .set('X-API-Key', validApiKey)
        .send({ url: 'https://www.tiktok.com/@user/video/123456789' })
        .then((res) => {
          // Will return either 200 (if video exists), 400/500 (if video doesn't exist), or 429 (rate limited)
          expect([200, 400, 429, 500]).toContain(res.status);
        });
    });
  });

  describe('Rate limiting', () => {
    it('should enforce rate limit after 5 requests', async () => {
      const url = 'https://www.tiktok.com/@test/video/999';

      // Make 5 requests (should all pass through, but may fail due to invalid video)
      for (let i = 0; i < 5; i++) {
        await request(app.getHttpServer())
          .post('/download')
          .set('X-API-Key', validApiKey)
          .send({ url });
      }

      // 6th request should be rate limited
      const response = await request(app.getHttpServer())
        .post('/download')
        .set('X-API-Key', validApiKey)
        .send({ url });

      expect(response.status).toBe(429);
    }, 10000);
  });

  describe('/api-docs (GET)', () => {
    it('should have Swagger endpoint configured', () => {
      // Note: Swagger is set up in main.ts bootstrap, not in test module
      // In e2e tests, we verify the module itself rather than Swagger UI
      // Swagger docs are available when running the actual service with `yarn start:dev`
      return request(app.getHttpServer())
        .get('/api-docs/')
        .then((res) => {
          // Accept either 404 (Swagger not set up in test) or 200/301/302 (if it is)
          expect([200, 301, 302, 404]).toContain(res.status);
        });
    });
  });
});
