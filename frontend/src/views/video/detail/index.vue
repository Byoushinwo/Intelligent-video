<template>
  <div class="page-container video-detail-container" v-loading="loading">
    <div class="page-title flex-between">
      <div class="title-with-back">
        <el-button type="text" @click="goBack" class="back-button">
          <el-icon><ArrowLeft /></el-icon> 返回
        </el-button>
        <span>{{ video?.filename || '视频详情' }}</span>
      </div>
      <div class="video-status" v-if="video" :class="getStatusClass(video.status)">
        {{ getStatusText(video.status) }}
      </div>
    </div>

    <el-row :gutter="20" v-if="video">
      <el-col :span="16">
        <div class="video-player-container">
          <div v-if="video.status === TaskStatus.COMPLETED" class="video-player">
            <video
              controls
              class="player"
              :src="getVideoUrl(video.filepath)"
            ></video>
          </div>
          <div v-else class="video-processing">
            <el-icon class="processing-icon"><VideoPlay /></el-icon>
            <p>{{ getStatusDescription(video.status) }}</p>
          </div>
        </div>

        <div class="video-info-card">
          <h3>视频信息</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="文件名">
              {{ video.filename }}
            </el-descriptions-item>
            <el-descriptions-item label="上传时间">
              {{ formatDate(video.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="处理状态">
              <el-tag :type="getStatusTagType(video.status)">
                {{ getStatusText(video.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="文件路径">
              <el-tooltip :content="video.filepath" placement="top">
                <span class="text-ellipsis filepath">{{ video.filepath }}</span>
              </el-tooltip>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-col>

      <el-col :span="8">
        <div class="subtitles-container">
          <div class="subtitles-header">
            <h3>视频字幕</h3>
            <el-input
              v-model="subtitleSearchKeyword"
              placeholder="搜索字幕内容"
              clearable
              @clear="handleSubtitleSearch"
              @input="handleSubtitleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>

          <div v-if="video.status !== TaskStatus.COMPLETED" class="subtitles-processing">
            <p>视频处理完成后将显示字幕</p>
          </div>

          <el-empty v-else-if="filteredSubtitles.length === 0" description="暂无字幕数据" />

          <div v-else class="subtitles-list">
            <div
              v-for="subtitle in filteredSubtitles"
              :key="subtitle.id"
              class="subtitle-item"
              @click="jumpToTime(subtitle.start_time)"
            >
              <div class="subtitle-time">
                {{ formatTime(subtitle.start_time) }} - {{ formatTime(subtitle.end_time) }}
              </div>
              <div class="subtitle-text">
                {{ subtitle.text }}
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-empty v-else-if="!loading" description="未找到视频数据" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ArrowLeft, Search, VideoPlay } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import dayjs from 'dayjs';
import { getVideoDetailApi } from '@/api/modules/video';
import type { Video, Subtitle } from '@/api/interface/video';
import { TaskStatus } from '@/api/interface/video';

const route = useRoute();
const router = useRouter();
const videoId = computed(() => route.params.id as string);

const video = ref<Video | null>(null);
const subtitles = ref<Subtitle[]>([]);
const loading = ref(true);
const subtitleSearchKeyword = ref('');

// 根据关键词过滤字幕
const filteredSubtitles = computed(() => {
  if (!subtitleSearchKeyword.value) return subtitles.value;
  return subtitles.value.filter(subtitle => 
    subtitle.text.toLowerCase().includes(subtitleSearchKeyword.value.toLowerCase())
  );
});

// 获取视频详情数据
const fetchVideoDetail = async () => {
  loading.value = true;
  try {
    const res = await getVideoDetailApi(videoId.value);
    video.value = res.data.video;
    subtitles.value = res.data.subtitles;
  } catch (error) {
    console.error('获取视频详情失败:', error);
    ElMessage.error('获取视频详情失败');
  } finally {
    loading.value = false;
  }
};

// 格式化日期
const formatDate = (dateStr: string) => {
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm:ss');
};

// 格式化时间（秒转为 MM:SS 格式）
const formatTime = (seconds: number) => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
};

// 获取状态文本
const getStatusText = (status: TaskStatus) => {
  const statusMap: Record<TaskStatus, string> = {
    [TaskStatus.PENDING]: '等待处理',
    [TaskStatus.PROCESSING]: '处理中',
    [TaskStatus.COMPLETED]: '已完成',
    [TaskStatus.FAILED]: '处理失败'
  };
  return statusMap[status];
};

// 获取状态描述
const getStatusDescription = (status: TaskStatus) => {
  const statusMap: Record<TaskStatus, string> = {
    [TaskStatus.PENDING]: '视频正在等待处理，请稍后再查看',
    [TaskStatus.PROCESSING]: '视频正在处理中，请稍后再查看',
    [TaskStatus.COMPLETED]: '视频处理已完成',
    [TaskStatus.FAILED]: '视频处理失败，请联系管理员'
  };
  return statusMap[status];
};

// 获取状态样式类
const getStatusClass = (status: TaskStatus) => {
  const statusClassMap: Record<TaskStatus, string> = {
    [TaskStatus.PENDING]: 'status-pending',
    [TaskStatus.PROCESSING]: 'status-processing',
    [TaskStatus.COMPLETED]: 'status-completed',
    [TaskStatus.FAILED]: 'status-failed'
  };
  return statusClassMap[status];
};

// 获取状态标签类型
const getStatusTagType = (status: TaskStatus) => {
  const statusTagMap: Record<TaskStatus, string> = {
    [TaskStatus.PENDING]: 'info',
    [TaskStatus.PROCESSING]: 'warning',
    [TaskStatus.COMPLETED]: 'success',
    [TaskStatus.FAILED]: 'danger'
  };
  return statusTagMap[status];
};

// 获取视频URL
const getVideoUrl = (filepath: string) => {
  // 从文件路径中提取文件名
  const filename = filepath.split('/').pop();
  return `http://127.0.0.1:8000/media/${filename}`;
};

// 跳转到指定时间点
const jumpToTime = (time: number) => {
  const videoElement = document.querySelector('video');
  if (videoElement) {
    videoElement.currentTime = time;
    videoElement.play();
  }
};

// 返回上一页
const goBack = () => {
  router.back();
};

// 字幕搜索处理
const handleSubtitleSearch = () => {
  // 这里可以添加防抖逻辑
};

onMounted(() => {
  fetchVideoDetail();
});
</script>

<style scoped>
.video-detail-container {
  min-height: 100%;
}

.title-with-back {
  display: flex;
  align-items: center;
}

.back-button {
  margin-right: 10px;
  font-size: 14px;
}

.video-status {
  padding: 4px 12px;
  border-radius: 15px;
  font-size: 14px;
  color: white;
}

.status-pending {
  background-color: var(--info-color);
}

.status-processing {
  background-color: var(--warning-color);
}

.status-completed {
  background-color: var(--success-color);
}

.status-failed {
  background-color: var(--danger-color);
}

.video-player-container {
  margin-bottom: 20px;
  background-color: #000;
  border-radius: 4px;
  overflow: hidden;
}

.video-player {
  width: 100%;
  height: 100%;
}

.player {
  width: 100%;
  height: 100%;
  max-height: 450px;
}

.video-processing {
  height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.processing-icon {
  font-size: 60px;
  margin-bottom: 20px;
}

.video-info-card {
  background-color: #fff;
  border-radius: 4px;
  padding: 20px;
  margin-bottom: 20px;
}

.video-info-card h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 18px;
  font-weight: 600;
}

.filepath {
  display: inline-block;
  max-width: 250px;
}

.subtitles-container {
  background-color: #fff;
  border-radius: 4px;
  padding: 20px;
  height: 100%;
}

.subtitles-header {
  margin-bottom: 20px;
}

.subtitles-header h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 18px;
  font-weight: 600;
}

.subtitles-list {
  max-height: 500px;
  overflow-y: auto;
}

.subtitle-item {
  padding: 10px;
  border-bottom: 1px solid var(--border-light);
  cursor: pointer;
  transition: background-color 0.2s;
}

.subtitle-item:hover {
  background-color: #f5f7fa;
}

.subtitle-time {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 5px;
}

.subtitle-text {
  font-size: 14px;
  line-height: 1.5;
}

.subtitles-processing {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}
</style>