
import { Test, TestingModule } from '@nestjs/testing';
import { ConfigModule } from '@nestjs/config';
import { DownloadService } from './download.service';

describe('DownloadService', () => {
  let service: DownloadService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      imports: [ConfigModule.forRoot()],
      providers: [DownloadService],
    }).compile();

    service = module.get<DownloadService>(DownloadService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });
});
