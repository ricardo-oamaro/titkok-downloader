
import { ApiProperty } from '@nestjs/swagger';
import { IsString, IsUrl, Matches } from 'class-validator';

export class DownloadRequestDto {
  @ApiProperty({
    description: 'TikTok video URL to download',
    example: 'https://www.tiktok.com/@username/video/1234567890123456789',
  })
  @IsString()
  @IsUrl({}, { message: 'Invalid URL format' })
  @Matches(/tiktok\.com/, {
    message: 'URL must be from tiktok.com domain',
  })
  url: string;
}
