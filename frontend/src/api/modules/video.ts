import http from '@/api/index';
import type { Video, Subtitle, VideoDetail, SearchResult } from '@/api/interface/video';

// 获取视频列表
export const getVideoListApi = () => {
  return http.get<Video[]>(`/api/videos/`);
};

// 获取视频详情
export const getVideoDetailApi = (id: string | number) => {
  return http.get<VideoDetail>(`/api/videos/${id}`);
};

// 文本搜索
export const searchTextApi = (query: string) => {
  return http.get<SearchResult>(`/api/search/text`, { params: { q: query } });
};

// 以文搜图
export const searchImageByTextApi = (query: string) => {
  return http.get<SearchResult>(`/api/search/image-by-text`, { params: { q: query } });
};

// 上传视频
export const uploadVideoApi = (formData: FormData) => {
  return http.post<{message: string; video_id: number}>(`/api/videos/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};