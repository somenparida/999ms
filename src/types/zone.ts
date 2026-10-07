export interface Zone {
  zone_id: string;
  video_id: string;
  name: string;
  zone_type: 'restricted' | 'caution' | 'safe';
  coordinates: [number, number][]; // percentage coordinates [[x, y], ...]
  color?: string;
  enabled: boolean;
}
