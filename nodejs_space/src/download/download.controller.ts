
import {
  Controller,
  Post,
  Body,
  UseGuards,
  StreamableFile,
  Header,
  HttpStatus,
  HttpCode,
  Logger,
  Res,
} from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiSecurity,
  ApiHeader,
} from '@nestjs/swagger';
import type { Response } from 'express';
import { DownloadService } from './download.service';
import { DownloadRequestDto } from './dto/download-request.dto';
import { ErrorResponseDto } from './dto/error-response.dto';
import { ApiKeyGuard } from './guards/api-key.guard';
import { Throttle } from '@nestjs/throttler';

@ApiTags('Download')
@Controller('download')
@UseGuards(ApiKeyGuard)
@ApiSecurity('api-key')
export class DownloadController {
  private readonly logger = new Logger(DownloadController.name);

  constructor(private readonly downloadService: DownloadService) {}

  @Post()
  @Throttle({ default: { limit: 5, ttl: 60000 } })
  @HttpCode(HttpStatus.OK)
  @ApiOperation({
    summary: 'Download TikTok video',
    description:
      'Downloads a TikTok video and returns it as a binary stream for local saving',
  })
  @ApiHeader({
    name: 'X-API-Key',
    description: 'API Key for authentication',
    required: true,
  })
  @ApiResponse({
    status: 200,
    description: 'Video file downloaded successfully',
    content: {
      'video/mp4': {
        schema: {
          type: 'string',
          format: 'binary',
        },
      },
    },
  })
  @ApiResponse({
    status: 400,
    description: 'Invalid URL or video not available',
    type: ErrorResponseDto,
  })
  @ApiResponse({
    status: 401,
    description: 'Unauthorized - Invalid or missing API key',
    type: ErrorResponseDto,
  })
  @ApiResponse({
    status: 429,
    description: 'Too many requests - Rate limit exceeded',
    type: ErrorResponseDto,
  })
  @ApiResponse({
    status: 500,
    description: 'Internal server error during download',
    type: ErrorResponseDto,
  })
  @Header('Content-Type', 'video/mp4')
  async downloadVideo(
    @Body() downloadRequest: DownloadRequestDto,
    @Res({ passthrough: true }) res: Response,
  ): Promise<StreamableFile> {
    this.logger.log(`Download requested for URL: ${downloadRequest.url}`);

    try {
      const result = await this.downloadService.downloadVideo(
        downloadRequest.url,
      );

      // Set response headers
      const headers: Record<string, string | number> = {
        'Content-Type': 'video/mp4',
        'Content-Disposition': `attachment; filename=${result.filename}`,
        'Content-Length': result.size,
      };

      // Add comments content as base64 in header if available
      if (result.commentsContent) {
        const commentsBase64 = Buffer.from(result.commentsContent, 'utf-8').toString('base64');
        headers['X-Comments-Available'] = 'true';
        headers['X-Comments-Data'] = commentsBase64;
        const commentsFilename = result.filename.replace('.mp4', '_comments.txt');
        headers['X-Comments-Filename'] = commentsFilename;
        this.logger.log(`Comments attached to response (${result.commentsContent.length} chars)`);
      }

      res.set(headers);

      this.logger.log(`Video downloaded successfully: ${result.filename}`);

      return result.stream;
    } catch (error) {
      this.logger.error(`Download failed: ${error.message}`, error.stack);
      throw error;
    }
  }
}
