
import {
  Injectable,
  BadRequestException,
  InternalServerErrorException,
  Logger,
} from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { StreamableFile } from '@nestjs/common';
import { spawn } from 'child_process';
import { promises as fs } from 'fs';
import { join } from 'path';
import { randomUUID } from 'crypto';
import * as fsSync from 'fs';

interface DownloadResult {
  stream: StreamableFile;
  filename: string;
  size: number;
  commentsFile?: string;
  commentsContent?: string;
}

interface Comment {
  author: string;
  text: string;
  like_count?: number;
}

@Injectable()
export class DownloadService {
  private readonly logger = new Logger(DownloadService.name);
  private readonly downloadsDir: string;

  constructor(private configService: ConfigService) {
    this.downloadsDir =
      this.configService.get<string>('DOWNLOADS_DIR') || './tmp/downloads';
    this.ensureDownloadsDirExists();
  }

  private async ensureDownloadsDirExists(): Promise<void> {
    try {
      await fs.mkdir(this.downloadsDir, { recursive: true });
      this.logger.log(`Downloads directory ready: ${this.downloadsDir}`);
    } catch (error) {
      this.logger.error(
        `Failed to create downloads directory: ${error.message}`,
      );
    }
  }

  async downloadVideo(url: string): Promise<DownloadResult> {
    const videoId = randomUUID();
    const outputPath = join(this.downloadsDir, `${videoId}.mp4`);

    this.logger.log(`Starting download for video ID: ${videoId}`);

    try {
      // Download video using yt-dlp
      await this.executeYtDlp(url, outputPath);

      // Check if file exists and get size
      const stats = await fs.stat(outputPath);
      if (!stats.isFile() || stats.size === 0) {
        throw new BadRequestException('Downloaded file is invalid or empty');
      }

      // Extract comments (non-blocking, continues even if it fails)
      let commentsFilePath: string | null = null;
      let commentsContent: string | undefined = undefined;
      try {
        commentsFilePath = await this.extractComments(url, videoId);
        if (commentsFilePath) {
          commentsContent = await fs.readFile(commentsFilePath, 'utf-8');
        }
      } catch (error) {
        this.logger.warn(`Comments extraction failed but continuing: ${error.message}`);
      }

      // Create readable stream
      const fileStream = fsSync.createReadStream(outputPath);

      // Clean up files after streaming completes
      fileStream.on('close', async () => {
        try {
          await fs.unlink(outputPath);
          this.logger.log(`Cleaned up temporary file: ${outputPath}`);
          
          // Cleanup comments file if exists
          if (commentsFilePath) {
            await fs.unlink(commentsFilePath).catch(() => {});
            this.logger.log(`Cleaned up comments file: ${commentsFilePath}`);
          }
        } catch (error) {
          this.logger.error(`Failed to cleanup file: ${error.message}`);
        }
      });

      // Handle stream errors
      fileStream.on('error', async (error) => {
        this.logger.error(`Stream error: ${error.message}`);
        try {
          await fs.unlink(outputPath);
          if (commentsFilePath) {
            await fs.unlink(commentsFilePath).catch(() => {});
          }
        } catch {}
      });

      const filename = `tiktok_${videoId}.mp4`;

      return {
        stream: new StreamableFile(fileStream),
        filename,
        size: stats.size,
        commentsFile: commentsFilePath || undefined,
        commentsContent,
      };
    } catch (error) {
      // Cleanup on error
      try {
        await fs.unlink(outputPath);
      } catch {}

      if (error instanceof BadRequestException) {
        throw error;
      }

      this.logger.error(`Download error: ${error.message}`, error.stack);
      throw new InternalServerErrorException(
        `Failed to download video: ${error.message}`,
      );
    }
  }

  private executeYtDlp(url: string, outputPath: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const args = [
        url,
        '-o',
        outputPath,
        '--no-playlist',
        '--no-warnings',
        '-f',
        'best[ext=mp4]/best',
        '--merge-output-format',
        'mp4',
      ];

      // Add cookies from browser if configured (for TikTok authentication)
      const cookiesBrowser = this.configService.get<string>('YTDLP_COOKIES_BROWSER');
      if (cookiesBrowser) {
        args.push('--cookies-from-browser', cookiesBrowser);
        this.logger.log(`Using cookies from browser: ${cookiesBrowser}`);
      }

      // Add user-agent to improve compatibility
      args.push(
        '--user-agent',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      );

      this.logger.debug(`Executing yt-dlp with args: ${args.join(' ')}`);

      const ytDlp = spawn('yt-dlp', args);

      let stderr = '';

      ytDlp.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      ytDlp.on('error', (error) => {
        this.logger.error(`yt-dlp process error: ${error.message}`);
        reject(
          new InternalServerErrorException(
            'Failed to execute yt-dlp: ' + error.message,
          ),
        );
      });

      ytDlp.on('close', (code) => {
        if (code === 0) {
          this.logger.log('yt-dlp download completed successfully');
          resolve();
        } else {
          this.logger.error(`yt-dlp exited with code ${code}: ${stderr}`);
          
          // Parse common errors
          if (stderr.includes('Video unavailable')) {
            reject(new BadRequestException('Video is unavailable or private'));
          } else if (stderr.includes('Unsupported URL')) {
            reject(new BadRequestException('Unsupported or invalid TikTok URL'));
          } else if (stderr.includes('HTTP Error 404')) {
            reject(new BadRequestException('Video not found'));
          } else if (stderr.includes('requiring login') || stderr.includes('Use --cookies')) {
            reject(
              new BadRequestException(
                'TikTok requires authentication. Please configure YTDLP_COOKIES_BROWSER in .env (e.g., chrome, firefox, edge, safari)',
              ),
            );
          } else {
            reject(
              new InternalServerErrorException(
                `Download failed: ${stderr || 'Unknown error'}`,
              ),
            );
          }
        }
      });
    });
  }

  private async extractComments(
    url: string,
    videoId: string,
  ): Promise<string | null> {
    const commentsJsonPath = join(
      this.downloadsDir,
      `${videoId}.info.json`,
    );
    const commentsTxtPath = join(this.downloadsDir, `${videoId}_comments.txt`);

    try {
      this.logger.log(`Extracting comments for video ID: ${videoId}`);

      // Extract video info with comments using yt-dlp
      await this.executeYtDlpComments(url, videoId);

      // Check if info file was created
      const fileExists = await fs
        .access(commentsJsonPath)
        .then(() => true)
        .catch(() => false);

      if (!fileExists) {
        this.logger.warn('Comments info file not created');
        return null;
      }

      // Read and parse JSON
      const jsonContent = await fs.readFile(commentsJsonPath, 'utf-8');
      const videoInfo = JSON.parse(jsonContent);

      const comments = videoInfo.comments || [];

      if (comments.length === 0) {
        this.logger.warn('No comments found for this video');
        await fs.unlink(commentsJsonPath).catch(() => {});
        return null;
      }

      // Sort by like_count and get top 15
      const topComments = comments
        .sort((a: Comment, b: Comment) => (b.like_count || 0) - (a.like_count || 0))
        .slice(0, 15);

      // Create formatted text file
      const textContent = topComments
        .map((comment: Comment, index: number) => {
          // Limit each comment to 200 characters to avoid huge headers
          const commentText = comment.text.length > 200 
            ? comment.text.substring(0, 200) + '...'
            : comment.text;
          return `${index + 1}. ${comment.author}: ${commentText}`;
        })
        .join('\n\n');

      // Limit total size to prevent header size issues (max ~5KB of text before base64)
      const maxSize = 5000;
      const finalContent = textContent.length > maxSize 
        ? textContent.substring(0, maxSize) + '\n\n[... comentários truncados devido ao tamanho]'
        : textContent;

      await fs.writeFile(commentsTxtPath, finalContent, 'utf-8');

      // Cleanup JSON file
      await fs.unlink(commentsJsonPath).catch(() => {});

      this.logger.log(
        `Comments extracted successfully: ${topComments.length} comments`,
      );

      return commentsTxtPath;
    } catch (error) {
      this.logger.error(`Failed to extract comments: ${error.message}`);
      // Cleanup on error
      await fs.unlink(commentsJsonPath).catch(() => {});
      await fs.unlink(commentsTxtPath).catch(() => {});
      return null;
    }
  }

  private executeYtDlpComments(url: string, videoId: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const outputTemplate = join(this.downloadsDir, `${videoId}`);

      const args = [
        url,
        '-o',
        outputTemplate,
        '--write-info-json',
        '--skip-download',
        '--no-warnings',
      ];

      // Add cookies from browser if configured
      const cookiesBrowser =
        this.configService.get<string>('YTDLP_COOKIES_BROWSER');
      if (cookiesBrowser) {
        args.push('--cookies-from-browser', cookiesBrowser);
      }

      // Add user-agent
      args.push(
        '--user-agent',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      );

      this.logger.debug(
        `Executing yt-dlp for comments with args: ${args.join(' ')}`,
      );

      const ytDlp = spawn('yt-dlp', args);

      let stderr = '';

      ytDlp.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      ytDlp.on('error', (error) => {
        this.logger.error(`yt-dlp comments process error: ${error.message}`);
        reject(error);
      });

      ytDlp.on('close', (code) => {
        if (code === 0) {
          this.logger.log('yt-dlp comments extraction completed');
          resolve();
        } else {
          this.logger.warn(
            `yt-dlp comments extraction failed with code ${code}: ${stderr}`,
          );
          // Don't reject, just warn - comments extraction is optional
          resolve();
        }
      });
    });
  }
}
