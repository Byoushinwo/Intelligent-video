export enum TaskStatus {
  PENDING = "PENDING",
  PROCESSING = "PROCESSING",
  COMPLETED = "COMPLETED",
  FAILED = "FAILED"
}

export interface Video {
  id: number;
  filename: string;
  filepath: string;
  status: TaskStatus;
  created_at: string;
}

export interface Subtitle {
  id: number;
  video_id: number;
  start_time: number;
  end_time: number;
  text: string;
}

export interface SearchResult {
  query: string;
  results: any[];
}

export interface VideoDetail {
  video: Video;
  subtitles: Subtitle[];
}