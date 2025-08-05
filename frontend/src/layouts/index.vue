<template>
  <el-container class="layout-container">
    <el-aside width="210px">
      <div class="logo"><span>智能视频分析平台</span></div>
      <el-menu :router="true" :default-active="$route.path">
        <el-menu-item index="/video/list">
          <el-icon><Tickets /></el-icon><span>视频列表</span>
        </el-menu-item>
        <el-menu-item index="/video/search">
          <el-icon><Search /></el-icon><span>内容检索</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header>
        <div class="header-content">
          <div class="header-title">
            <h2>{{ getPageTitle }}</h2>
          </div>
          <div class="user-info">
            <el-button type="primary" @click="handleUpload">上传视频</el-button>
          </div>
        </div>
      </el-header>
      <el-main>
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>

    <!-- 上传视频对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="上传视频" width="500px">
      <el-upload
        class="upload-video"
        drag
        action=""
        :auto-upload="false"
        :on-change="handleFileChange"
        :limit="1"
        accept="video/*"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将视频拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持MP4、AVI、MOV等常见视频格式
          </div>
        </template>
      </el-upload>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="uploadDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitUpload" :loading="uploading" :disabled="!videoFile">
            上传
          </el-button>
        </span>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Tickets, Search, UploadFilled } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { uploadVideoApi } from '@/api/modules/video';

const route = useRoute();
const router = useRouter();

// 页面标题
const getPageTitle = computed(() => {
  const pathMap: Record<string, string> = {
    '/video/list': '视频列表',
    '/video/search': '内容检索',
    '/video/detail': '视频详情'
  };
  
  // 获取当前路径的前两段
  const path = '/' + route.path.split('/').slice(1, 3).join('/');
  return pathMap[path] || '智能视频分析平台';
});

// 上传视频相关
const uploadDialogVisible = ref(false);
const videoFile = ref<File | null>(null);
const uploading = ref(false);

const handleUpload = () => {
  uploadDialogVisible.value = true;
};

const handleFileChange = (file: any) => {
  videoFile.value = file.raw;
};

const submitUpload = async () => {
  if (!videoFile.value) {
    ElMessage.warning('请先选择要上传的视频文件');
    return;
  }
  
  uploading.value = true;
  try {
    const formData = new FormData();
    formData.append('file', videoFile.value);
    
    const res = await uploadVideoApi(formData);
    ElMessage.success('视频上传成功');
    uploadDialogVisible.value = false;
    videoFile.value = null;
    
    // 上传成功后跳转到视频详情页
    router.push(`/video/detail/${res.data.video_id}`);
  } catch (error) {
    console.error('上传失败:', error);
  } finally {
    uploading.value = false;
  }
};
</script>

<style scoped>
.layout-container {
  height: 100vh;
  width: 100%;
}

.el-aside {
  background-color: #304156;
  color: #fff;
  height: 100%;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  color: #fff;
  background-color: #263445;
}

.el-menu {
  border-right: none;
  background-color: #304156;
}

.el-menu-item {
  color: #bfcbd9;
}

.el-menu-item.is-active {
  background-color: #263445 !important;
  color: #409EFF !important;
}

.el-menu-item:hover {
  background-color: #263445 !important;
}

.el-header {
  background-color: #fff;
  color: #333;
  line-height: 60px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  position: relative;
  z-index: 10;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.header-title h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
  height: calc(100vh - 60px);
  overflow-y: auto;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 上传视频样式 */
.upload-video {
  width: 100%;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>