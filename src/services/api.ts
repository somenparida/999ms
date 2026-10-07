import axios, { AxiosInstance } from 'axios';
import {
  Video,
  Track,
  Behaviour,
  Event,
  AnalysisStatus,
  TimelineEntry,
  SystemAnalytics,
  Zone,
  EvidenceRecord,
} from '@/types';
import { mockApi } from './mockApi';

export interface IApiService {
  getVideos(): Promise<Video[]>;
  getVideo(videoId: string): Promise<Video | null>;
  uploadVideo(file: File): Promise<Video>;
  startAnalysis(videoId: string): Promise<AnalysisStatus>;
  getAnalysisStatus(videoId: string): Promise<AnalysisStatus>;
  getTracks(videoId: string): Promise<Track[]>;
  getBehaviours(videoId: string): Promise<Behaviour[]>;
  getEvents(videoId: string): Promise<Event[]>;
  getTimeline(videoId: string): Promise<TimelineEntry[]>;
  getAnalytics(videoId?: string): Promise<SystemAnalytics>;

  // Member 3 Backend Additions: Zones, Evidence, Imports
  getZones(videoId: string): Promise<Zone[]>;
  createZone(zone: Partial<Zone>): Promise<Zone>;
  getEvidence(videoId: string): Promise<EvidenceRecord[]>;
  importTracks(videoId: string, tracks: Track[]): Promise<{ imported: number }>;
  importBehaviours(videoId: string, behaviours: Behaviour[]): Promise<{ imported: number }>;

  // Multi-laptop networking & health controls
  isMockMode(): boolean;
  setMockMode(enabled: boolean): void;
  getBackendUrl(): string;
  setBackendUrl(url: string): void;
  checkHealth(): Promise<{ status: string; online: boolean; latencyMs?: number }>;
}

const STORAGE_API_URL_KEY = 'autovision_backend_url';
const STORAGE_MOCK_KEY = 'autovision_use_mock';

const getInitialBackendUrl = () => {
  return (
    localStorage.getItem(STORAGE_API_URL_KEY) ||
    import.meta.env.VITE_API_BASE_URL ||
    'http://localhost:8000'
  );
};

const getInitialMockMode = () => {
  const saved = localStorage.getItem(STORAGE_MOCK_KEY);
  if (saved !== null) return saved === 'true';
  return import.meta.env.VITE_USE_MOCK !== 'false';
};

class RealApiService {
  private client: AxiosInstance;
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.client = axios.create({
      baseURL: baseUrl,
      timeout: 8000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  updateBaseUrl(newUrl: string) {
    this.baseUrl = newUrl;
    this.client = axios.create({
      baseURL: newUrl,
      timeout: 8000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  getBaseUrl(): string {
    return this.baseUrl;
  }

  async checkHealth(): Promise<{ status: string; online: boolean; latencyMs?: number }> {
    const start = performance.now();
    try {
      const response = await this.client.get('/health');
      const latency = Math.round(performance.now() - start);
      return { status: response.data?.status || 'online', online: true, latencyMs: latency };
    } catch {
      return { status: 'offline', online: false };
    }
  }

  async getVideos(): Promise<Video[]> {
    const response = await this.client.get<Video[]>('/api/videos');
    return response.data;
  }

  async getVideo(videoId: string): Promise<Video | null> {
    const response = await this.client.get<Video>(`/api/videos/${videoId}`);
    return response.data;
  }

  async uploadVideo(file: File): Promise<Video> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.client.post<Video>('/api/videos/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async startAnalysis(videoId: string): Promise<AnalysisStatus> {
    const response = await this.client.post<AnalysisStatus>(`/api/videos/${videoId}/analyze`);
    return response.data;
  }

  async getAnalysisStatus(videoId: string): Promise<AnalysisStatus> {
    const response = await this.client.get<AnalysisStatus>(`/api/videos/${videoId}/status`);
    return response.data;
  }

  async getTracks(videoId: string): Promise<Track[]> {
    const response = await this.client.get<Track[]>(`/api/videos/${videoId}/tracks`);
    return response.data;
  }

  async getBehaviours(videoId: string): Promise<Behaviour[]> {
    const response = await this.client.get<Behaviour[]>(`/api/videos/${videoId}/behaviours`);
    return response.data;
  }

  async getEvents(videoId: string): Promise<Event[]> {
    const response = await this.client.get<Event[]>(`/api/videos/${videoId}/events`);
    return response.data;
  }

  async getTimeline(videoId: string): Promise<TimelineEntry[]> {
    const response = await this.client.get<TimelineEntry[]>(`/api/videos/${videoId}/timeline`);
    return response.data;
  }

  async getAnalytics(videoId?: string): Promise<SystemAnalytics> {
    const url = videoId ? `/api/analytics?video_id=${videoId}` : '/api/analytics';
    const response = await this.client.get<SystemAnalytics>(url);
    return response.data;
  }

  async getZones(videoId: string): Promise<Zone[]> {
    const response = await this.client.get<Zone[]>(`/api/videos/${videoId}/zones`);
    return response.data;
  }

  async createZone(zone: Partial<Zone>): Promise<Zone> {
    const response = await this.client.post<Zone>(`/api/videos/${zone.video_id}/zones`, zone);
    return response.data;
  }

  async getEvidence(videoId: string): Promise<EvidenceRecord[]> {
    const response = await this.client.get<EvidenceRecord[]>(`/api/videos/${videoId}/evidence`);
    return response.data;
  }

  async importTracks(videoId: string, tracks: Track[]): Promise<{ imported: number }> {
    const response = await this.client.post<{ imported: number }>(
      `/api/videos/${videoId}/tracks/import`,
      tracks
    );
    return response.data;
  }

  async importBehaviours(
    videoId: string,
    behaviours: Behaviour[]
  ): Promise<{ imported: number }> {
    const response = await this.client.post<{ imported: number }>(
      `/api/videos/${videoId}/behaviours/import`,
      behaviours
    );
    return response.data;
  }
}

class DelegatingApiService implements IApiService {
  private backendUrl: string;
  private mockMode: boolean;
  private realService: RealApiService;

  constructor() {
    this.backendUrl = getInitialBackendUrl();
    this.mockMode = getInitialMockMode();
    this.realService = new RealApiService(this.backendUrl);
  }

  isMockMode(): boolean {
    return this.mockMode;
  }

  setMockMode(enabled: boolean): void {
    this.mockMode = enabled;
    localStorage.setItem(STORAGE_MOCK_KEY, String(enabled));
  }

  getBackendUrl(): string {
    return this.backendUrl;
  }

  setBackendUrl(url: string): void {
    this.backendUrl = url;
    localStorage.setItem(STORAGE_API_URL_KEY, url);
    this.realService.updateBaseUrl(url);
  }

  async checkHealth(): Promise<{ status: string; online: boolean; latencyMs?: number }> {
    if (this.isMockMode()) {
      return { status: 'online (mock standalone)', online: true, latencyMs: 1 };
    }
    return this.realService.checkHealth();
  }

  async getVideos(): Promise<Video[]> {
    if (this.isMockMode()) return mockApi.getVideos();
    try {
      return await this.realService.getVideos();
    } catch {
      return mockApi.getVideos();
    }
  }

  async getVideo(videoId: string): Promise<Video | null> {
    if (this.isMockMode()) return mockApi.getVideo(videoId);
    try {
      return await this.realService.getVideo(videoId);
    } catch {
      return mockApi.getVideo(videoId);
    }
  }

  async uploadVideo(file: File): Promise<Video> {
    if (this.isMockMode()) return mockApi.uploadVideo(file);
    try {
      return await this.realService.uploadVideo(file);
    } catch {
      return mockApi.uploadVideo(file);
    }
  }

  async startAnalysis(videoId: string): Promise<AnalysisStatus> {
    if (this.isMockMode()) return mockApi.startAnalysis(videoId);
    try {
      return await this.realService.startAnalysis(videoId);
    } catch {
      return mockApi.startAnalysis(videoId);
    }
  }

  async getAnalysisStatus(videoId: string): Promise<AnalysisStatus> {
    if (this.isMockMode()) return mockApi.getAnalysisStatus(videoId);
    try {
      return await this.realService.getAnalysisStatus(videoId);
    } catch {
      return mockApi.getAnalysisStatus(videoId);
    }
  }

  async getTracks(videoId: string): Promise<Track[]> {
    if (this.isMockMode()) return mockApi.getTracks(videoId);
    try {
      return await this.realService.getTracks(videoId);
    } catch {
      return mockApi.getTracks(videoId);
    }
  }

  async getBehaviours(videoId: string): Promise<Behaviour[]> {
    if (this.isMockMode()) return mockApi.getBehaviours(videoId);
    try {
      return await this.realService.getBehaviours(videoId);
    } catch {
      return mockApi.getBehaviours(videoId);
    }
  }

  async getEvents(videoId: string): Promise<Event[]> {
    if (this.isMockMode()) return mockApi.getEvents(videoId);
    try {
      return await this.realService.getEvents(videoId);
    } catch {
      return mockApi.getEvents(videoId);
    }
  }

  async getTimeline(videoId: string): Promise<TimelineEntry[]> {
    if (this.isMockMode()) return mockApi.getTimeline(videoId);
    try {
      return await this.realService.getTimeline(videoId);
    } catch {
      return mockApi.getTimeline(videoId);
    }
  }

  async getAnalytics(videoId?: string): Promise<SystemAnalytics> {
    if (this.isMockMode()) return mockApi.getAnalytics(videoId);
    try {
      return await this.realService.getAnalytics(videoId);
    } catch {
      return mockApi.getAnalytics(videoId);
    }
  }

  async getZones(videoId: string): Promise<Zone[]> {
    if (this.isMockMode()) return mockApi.getZones(videoId);
    try {
      return await this.realService.getZones(videoId);
    } catch {
      return mockApi.getZones(videoId);
    }
  }

  async createZone(zone: Partial<Zone>): Promise<Zone> {
    if (this.isMockMode()) return mockApi.createZone(zone);
    try {
      return await this.realService.createZone(zone);
    } catch {
      return mockApi.createZone(zone);
    }
  }

  async getEvidence(videoId: string): Promise<EvidenceRecord[]> {
    if (this.isMockMode()) return mockApi.getEvidence(videoId);
    try {
      return await this.realService.getEvidence(videoId);
    } catch {
      return mockApi.getEvidence(videoId);
    }
  }

  async importTracks(videoId: string, tracks: Track[]): Promise<{ imported: number }> {
    if (this.isMockMode()) return mockApi.importTracks(videoId, tracks);
    try {
      return await this.realService.importTracks(videoId, tracks);
    } catch {
      return mockApi.importTracks(videoId, tracks);
    }
  }

  async importBehaviours(
    videoId: string,
    behaviours: Behaviour[]
  ): Promise<{ imported: number }> {
    if (this.isMockMode()) return mockApi.importBehaviours(videoId, behaviours);
    try {
      return await this.realService.importBehaviours(videoId, behaviours);
    } catch {
      return mockApi.importBehaviours(videoId, behaviours);
    }
  }
}

export const api: IApiService = new DelegatingApiService();
