<template>
  <div class="search-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>内容检索</span>
        </div>
      </template>

      <!-- 搜索输入区域 -->
      <div class="search-form-container">
        <el-radio-group v-model="searchMode" style="margin-bottom: 20px;">
          <el-radio-button label="text">按字幕搜索</el-radio-button>
          <el-radio-button label="image">按画面搜索</el-radio-button>
        </el-radio-group>

        <el-input
          v-model="searchQuery"
          :placeholder="searchMode === 'text' ? '输入关键词搜索视频字幕' : '输入英文描述，搜索视频中的相关画面'"
          size="large"
          clearable
          @keyup.enter="handleSearch"
          class="search-input"
        >
          <template #prepend>
            <el-icon><Search v-if="searchMode === 'text'" /><Picture v-if="searchMode === 'image'" /></el-icon>
          </template>
          <template #append>
            <el-button @click="handleSearch" :loading="isLoading">搜索</el-button>
          </template>
        </el-input>
      </div>

      <el-divider />

      <!-- 结果展示区域 -->
      <div class="search-results" v-loading="isLoading">
        <el-empty v-if="!hasSearched" description="输入关键词或描述开始搜索吧" />
        
        <el-empty v-else-if="!isLoading && textResults.length === 0 && imageResults.length === 0" description="未找到匹配的内容" />
        
        <!-- 文本搜索结果 -->
        <div v-if="searchMode === 'text' && textResults.length > 0">
          <div class="result-summary">找到 {{ textResults.length }} 条相关字幕</div>
          <el-card v-for="item in textResults" :key="item.id" class="result-item-card" shadow="hover">
            <p @click="goToVideoDetail(item.video_id, item.start_time)" v-html="highlightKeyword(item.text, searchQuery)"></p>
            <div class="item-footer">
              <span class="footer-link" @click="goToVideoDetail(item.video_id)">来自 Video ID: {{ item.video_id }}</span>
              <span>{{ formatTime(item.start_time) }}</span>
            </div>
          </el-card>
        </div>

        <!-- 图像搜索结果 -->
        <div v-if="searchMode === 'image' && imageResults.length > 0">
          <div class="result-summary">找到 {{ imageResults.length }} 个相似画面</div>
          <el-row :gutter="20">
            <el-col :xs="12" :sm="8" :md="6" :lg="4" v-for="item in imageResults" :key="item.id">
              <el-card :body-style="{ padding: '0px' }" class="image-item-card" shadow="hover" @click="goToVideoDetail(item.videoId, item.timestamp)">
                <el-image :src="item.imageUrl" fit="cover" lazy class="result-image">
                   <template #placeholder><div class="image-slot">加载中...</div></template>
                   <template #error><div class="image-slot">图片加载失败</div></template>
                </el-image>
                <div class="image-info">
                  <span class="footer-link" @click.stop="goToVideoDetail(item.videoId)">Video ID: {{ item.videoId }}</span>
                  <el-tag size="small" type="info">相似度: {{ item.distance }}</el-tag>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { Search, Picture } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { searchTextApi, searchImageByTextApi } from '@/api/modules/video';

const router = useRouter();
const API_BASE_URL = 'http://127.0.0.1:8000';

// --- 响应式状态 ---
const searchMode = ref('text');
const searchQuery = ref('');
const isLoading = ref(false);
const hasSearched = ref(false);

interface TextResult { id: number; video_id: number; start_time: number; text: string; }
interface ImageResult { id: string; imageUrl: string; videoId: number; distance: number; timestamp: number; }

const textResults = ref<TextResult[]>([]);
const imageResults = ref<ImageResult[]>([]);

const handleSearch = () => {
  if (!searchQuery.value.trim()) {
    return ElMessage.warning(searchMode.value === 'text' ? '请输入搜索关键词' : '请输入图像描述');
  }
  if (searchMode.value === 'text') {
    handleTextSearch();
  } else {
    handleImageSearch();
  }
};

const handleTextSearch = async () => {
  isLoading.value = true;
  hasSearched.value = true;
  textResults.value = [];

  try {
    const res = await searchTextApi(searchQuery.value);
    textResults.value = res.data.results;
  } finally {
    isLoading.value = false;
  }
};

const handleImageSearch = async () => {
  isLoading.value = true;
  hasSearched.value = true;
  imageResults.value = [];
  
  try {
    const res = await searchImageByTextApi(searchQuery.value);
    const backendResults = res.data.results;
    
    if (backendResults && backendResults.metadatas && backendResults.metadatas[0]) {
      const metadatas = backendResults.metadatas[0];
      const ids = backendResults.ids[0];
      const distances = backendResults.distances[0];

      imageResults.value = metadatas.map((meta, index) => {
        const videoFilename = meta.video_filename || '';
        const videoFilenameWithoutExt = videoFilename.split('.').slice(0, -1).join('.');
        return {
          id: ids[index],
          videoId: meta.video_id,
          timestamp: meta.timestamp_approx,
          imageUrl: `${API_BASE_URL}/media/${encodeURIComponent(videoFilenameWithoutExt)}/${meta.frame_filename}`,
          distance: parseFloat(distances[index].toFixed(2))
        };
      });
    }
  } finally {
    isLoading.value = false;
  }
};

const goToVideoDetail = (videoId: number, timestamp?: number) => {
  const query = timestamp ? { time: timestamp.toString() } : {};
  router.push({ name: 'VideoDetail', params: { id: videoId }, query });
};

const formatTime = (seconds: number) => {
  if (isNaN(seconds)) return '00:00';
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
};

const highlightKeyword = (text: string, keyword: string) => {
  if (!keyword.trim()) return text;
  const regex = new RegExp(keyword, 'gi');
  return text.replace(regex, (match) => `<span class="highlight">${match}</span>`);
};
</script>

<style>
/* 将高亮样式设为全局，以便 v-html 可以应用 */
.highlight {
  background-color: #f5d349;
  color: #303133;
  padding: 2px 4px;
  border-radius: 3px;
}
</style>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.search-form-container { display: flex; flex-direction: column; align-items: center; padding: 20px 0; }
.search-input { width: 100%; max-width: 800px; }
.search-results { min-height: 300px; margin-top: 20px; }
.result-summary { margin-bottom: 16px; color: var(--el-text-color-secondary); font-size: 14px; }
.result-item-card { margin-bottom: 16px; }
.result-item-card p { margin: 0; cursor: pointer; line-height: 1.6; }
.item-footer { display: flex; justify-content: space-between; color: var(--el-text-color-secondary); font-size: 12px; margin-top: 10px; }
.footer-link { cursor: pointer; color: var(--el-color-primary); }
.footer-link:hover { text-decoration: underline; }
.image-item-card { cursor: pointer; }
.result-image { width: 100%; height: 160px; background-color: #f5f7fa; }
.image-slot { display: flex; justify-content: center; align-items: center; width: 100%; height: 100%; color: var(--el-text-color-secondary); font-size: 14px; }
.image-info { padding: 12px; display: flex; justify-content: space-between; align-items: center; }
.image-info span { font-size: 13px; }
</style>