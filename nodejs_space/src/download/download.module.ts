
import { Module } from '@nestjs/common';
import { DownloadController } from './download.controller';
import { DownloadService } from './download.service';
import { ApiKeyGuard } from './guards/api-key.guard';

@Module({
  controllers: [DownloadController],
  providers: [DownloadService, ApiKeyGuard],
})
export class DownloadModule {}
