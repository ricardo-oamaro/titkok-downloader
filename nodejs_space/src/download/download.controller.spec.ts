
import { Test, TestingModule } from '@nestjs/testing';
import { ConfigModule } from '@nestjs/config';
import { DownloadController } from './download.controller';
import { DownloadService } from './download.service';
import { ApiKeyGuard } from './guards/api-key.guard';

describe('DownloadController', () => {
  let controller: DownloadController;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      imports: [ConfigModule.forRoot()],
      controllers: [DownloadController],
      providers: [DownloadService, ApiKeyGuard],
    }).compile();

    controller = module.get<DownloadController>(DownloadController);
  });

  it('should be defined', () => {
    expect(controller).toBeDefined();
  });
});
