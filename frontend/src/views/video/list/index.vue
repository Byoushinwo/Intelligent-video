<template>
  <div class="video-list-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>视频列表</span>
        </div>
      </template>

      <!-- 数据加载成功后，显示视频卡片列表 -->
      <el-row :gutter="20" v-if="videoList.length > 0">
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="video in videoList" :key="video.id">
          <el-card :body-style="{ padding: '0px' }" shadow="hover" class="video-card">
            <div class="video-card-image">
              <el-image :src="video.cover_url" fit="cover" lazy>
                <template #error><div class="image-slot">封面生成中...</div></template>
              </el-image>
              <el-tag class="status-tag" :type="getStatusType(video.status)" effect="dark">
                <el-icon v-if="video.status === 'PROCESSING'" class="is-loading"><Loading /></el-icon>
                <span style="margin-left: 4px;">{{ video.status }}</span>
              </el-tag>
            </div>
            <div style="padding: 14px;">
              <div class="video-filename" :title="video.filename">{{ video.filename }}</div>
              <div class="bottom">
                <time class="time">{{ formatTime(video.created_at) }}</time>
                <el-button type="primary" link @click="goToDetail(video.id)">查看详情</el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 加载中或无数据时，显示相应状态 -->
      <el-empty v-if="!loading && videoList.length === 0" description="暂无视频数据，快去上传一个吧！" />

      <div v-if="loading" v-loading="loading" style="height: 200px;"></div>

    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import dayjs from 'dayjs';
import type { UploadProps } from 'element-plus'
import { Loading } from '@element-plus/icons-vue';

// --- 类型定义 ---
enum TaskStatus {
  PENDING = "PENDING",
  PROCESSING = "PROCESSING",
  COMPLETED = "COMPLETED",
  FAILED = "FAILED"
}

interface Video {
  id: number;
  filename: string;
  status: TaskStatus;
  created_at: string;
  cover_url?: string; // 封面URL是可选的
}

// --- API (实际项目中应封装到 api/modules/video.ts) ---
const API_BASE_URL = 'http://127.0.0.1:8000';

async function getVideoListApi(): Promise<Video[]> {
  const response = await fetch(`${API_BASE_URL}/api/videos/`);
  if (!response.ok) {
    throw new Error('Failed to fetch video list');
  }
  return response.json();
}

// --- 响应式数据 ---
const videoList = ref<Video[]>([]);
const loading = ref(true); // 初始为 true，进入页面立即加载
const router = useRouter();
let pollingTimer: number | null = null;
const uploadUrl = `${API_BASE_URL}/api/videos/upload`;

// --- 方法 ---

const fetchVideoList = async (isPolling = false) => {
  if (!isPolling) {
    loading.value = true;
  }
  try {
    videoList.value = await getVideoListApi();
  } catch (error) {
    if (!isPolling) ElMessage.error('获取视频列表失败');
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const getStatusType = (status: TaskStatus) => {
  switch (status) {
    case TaskStatus.PENDING: return 'info';
    case TaskStatus.PROCESSING: return 'primary';
    case TaskStatus.COMPLETED: return 'success';
    case TaskStatus.FAILED: return 'danger';
    default: return '';
  }
};

const formatTime = (timeStr: string) => {
  return dayjs(timeStr).format('YYYY-MM-DD HH:mm:ss');
};

const goToDetail = (id: number) => {
  router.push(`/video/detail/${id}`);
};

const handleUploadSuccess: UploadProps['onSuccess'] = (response) => {
  ElMessage.success(`视频 (ID: ${response.video_id}) 上传成功，已开始处理！`);
  fetchVideoList();
};

const handleUploadError: UploadProps['onError'] = (error) => {
  ElMessage.error('视频上传失败');
  console.error("Upload Error:", error);
};

const handleBeforeUpload: UploadProps['beforeUpload'] = (rawFile) => {
  if (!rawFile.type.startsWith('video/')) {
    ElMessage.error('请上传视频文件!');
    return false;
  }
  return true;
};

onMounted(() => {
  fetchVideoList();
  pollingTimer = window.setInterval(() => {
    fetchVideoList(true); // 轮询时，传入标记以避免显示 loading
  }, 5000);
});

onUnmounted(() => {
  if (pollingTimer) {
    clearInterval(pollingTimer);
  }
});
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.video-card {
  margin-bottom: 20px;
}
.video-card-image {
  position: relative;
  width: 100%;
  height: 160px; /* 或者使用 aspect-ratio: 16 / 9; */
}
.el-image {
  width: 100%;
  height: 100%;
  display: block;
}
.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  color: var(--el-text-color-secondary);
}
.status-tag {
  position: absolute;
  top: 10px;
  right: 10px;
}
.video-filename {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.bottom {
  margin-top: 13px;
  line-height: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.time {
  font-size: 12px;
  color: #999;
}
</style>