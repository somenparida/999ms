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
import {
  MOCK_VIDEOS,
  MOCK_TRACKS,
  MOCK_BEHAVIOURS,
  MOCK_EVENTS,
  MOCK_TIMELINE,
  MOCK_ANALYTICS,
  MOCK_ANALYSIS_STATUS,
  MOCK_ZONES,
  MOCK_EVIDENCE,
} from '@/mock/mockData';

// Simulated delay helper
const delay = (ms: number = 200) => new Promise((resolve) => setTimeout(resolve, ms));

export class MockApiService {
  private videos: Video[] = [...MOCK_VIDEOS];
  private tracks: Track[] = [...MOCK_TRACKS];
  private behaviours: Behaviour[] = [...MOCK_BEHAVIOURS];
  private zones: Zone[] = [...MOCK_ZONES];
  private evidence: EvidenceRecord[] = [...MOCK_EVIDENCE];
  private analysisStatuses: Map<string, AnalysisStatus> = new Map([
    ['vid-autovision-001', { ...MOCK_ANALYSIS_STATUS }],
  ]);
  private analysisStartTimes: Map<string, number> = new Map();

  async getVideos(): Promise<Video[]> {
    await delay(150);
    return [...this.videos];
  }

  async getVideo(videoId: string): Promise<Video | null> {
    await delay(100);
    return this.videos.find((v) => v.video_id === videoId) || null;
  }

  async uploadVideo(file: File): Promise<Video> {
    await delay(500);
    const newVideo: Video = {
      video_id: `vid-${Date.now()}`,
      title: file.name.replace(/\.[^/.]+$/, ''),
      filename: file.name,
      duration_seconds: 151,
      fps: 30,
      resolution: '1920x1080',
      uploaded_at: new Date().toISOString(),
      url: URL.createObjectURL(file),
      status: 'unprocessed',
    };
    this.videos.unshift(newVideo);
    return newVideo;
  }

  async startAnalysis(videoId: string): Promise<AnalysisStatus> {
    await delay(200);
    this.analysisStartTimes.set(videoId, Date.now());
    const status: AnalysisStatus = {
      video_id: videoId,
      status: 'processing',
      progress: 25,
      current_step: 'Initializing YOLOv8 inference & DeepSORT tracker...',
      started_at: new Date().toISOString(),
    };
    this.analysisStatuses.set(videoId, status);
    return status;
  }

  async getAnalysisStatus(videoId: string): Promise<AnalysisStatus> {
    await delay(100);
    const startTime = this.analysisStartTimes.get(videoId);
    if (startTime) {
      const elapsed = Date.now() - startTime;
      if (elapsed > 4000) {
        const completed: AnalysisStatus = {
          video_id: videoId,
          status: 'completed',
          progress: 100,
          current_step: 'Analysis completed successfully. Abnormal events generated.',
          completed_at: new Date().toISOString(),
        };
        this.analysisStatuses.set(videoId, completed);
        return completed;
      } else if (elapsed > 2500) {
        return {
          video_id: videoId,
          status: 'processing',
          progress: 75,
          current_step: 'Evaluating spatial boundary violations & fall heuristics...',
        };
      } else if (elapsed > 1000) {
        return {
          video_id: videoId,
          status: 'processing',
          progress: 45,
          current_step: 'Assigning track IDs and trajectory vectors...',
        };
      }
    }
    const existing = this.analysisStatuses.get(videoId);
    if (!existing) {
      return {
        video_id: videoId,
        status: 'completed',
        progress: 100,
        current_step: 'Ready',
      };
    }
    return existing;
  }

  async getTracks(_videoId: string): Promise<Track[]> {
    await delay(150);
    return [...this.tracks];
  }

  async getBehaviours(_videoId: string): Promise<Behaviour[]> {
    await delay(150);
    return [...this.behaviours];
  }

  async getEvents(_videoId: string): Promise<Event[]> {
    await delay(150);
    return [...MOCK_EVENTS];
  }

  async getTimeline(_videoId: string): Promise<TimelineEntry[]> {
    await delay(150);
    return [...MOCK_TIMELINE];
  }

  async getAnalytics(_videoId?: string): Promise<SystemAnalytics> {
    await delay(150);
    return { ...MOCK_ANALYTICS };
  }

  // Member 3 Backend Additions: Zones, Evidence, Imports
  async getZones(_videoId: string): Promise<Zone[]> {
    await delay(100);
    return [...this.zones];
  }

  async createZone(zoneData: Partial<Zone>): Promise<Zone> {
    await delay(200);
    const newZone: Zone = {
      zone_id: `ZONE-${Date.now()}`,
      video_id: zoneData.video_id || 'vid-autovision-001',
      name: zoneData.name || 'Custom Safety Boundary',
      zone_type: zoneData.zone_type || 'restricted',
      coordinates: zoneData.coordinates || [
        [30, 30],
        [70, 30],
        [70, 70],
        [30, 70],
      ],
      color: zoneData.color || '#f43f5e',
      enabled: zoneData.enabled !== false,
    };
    this.zones.push(newZone);
    return newZone;
  }

  async getEvidence(_videoId: string): Promise<EvidenceRecord[]> {
    await delay(100);
    return [...this.evidence];
  }

  async importTracks(_videoId: string, importedTracks: Track[]): Promise<{ imported: number }> {
    await delay(250);
    this.tracks.push(...importedTracks);
    return { imported: importedTracks.length };
  }

  async importBehaviours(_videoId: string, importedBehaviours: Behaviour[]): Promise<{ imported: number }> {
    await delay(250);
    this.behaviours.push(...importedBehaviours);
    return { imported: importedBehaviours.length };
  }
}

export const mockApi = new MockApiService();
