# **智能视频分析与检索平台**

## **1. 项目概述 (Abstract)**

本项目实现了一个全栈的智能视频内容分析与检索系统。该系统基于一个异步、微服务化的后端架构，能够对用户上传的视频进行自动化的多模态内容提取，并将分析结果持久化至一个混合数据库集群。最终，通过一组RESTful API，平台对外提供高效的文本及跨模态（文搜图）内容检索能力。所有服务均通过Docker容器化进行部署与管理，确保了环境的一致性与可移植性。

## **2. 核心功能 (Core Functionalities)**

- **异步处理管道**: 采用Celery与Redis构建任务队列，解耦API网关与耗时的后台处理，保证系统的高可用性与快速响应。
- **媒体预处理**: 集成FFmpeg，实现视频流的自动化分解，提取音频（WAV, 16kHz, 单声道）与关键视频帧（JPEG序列）。
- **多模态AI分析**:
    - **语音内容提取**: 应用OpenAI Whisper模型 (`base` version) 进行语音到文本的转换，生成带时间戳的字幕数据。
    - **视觉内容理解**: 应用OpenAI CLIP模型 (`openai/clip-vit-base-patch32`) 对视频帧进行编码，生成512维的语义向量。
- **混合数据持久化架构**:
    - **PostgreSQL**: 存储视频元数据、任务状态及结构化的字幕文本。
    - **ChromaDB**: 存储图像内容的语义向量，用于高效的近似最近邻（ANN）搜索。
    - **Elasticsearch**: 为字幕文本建立全文倒排索引，支持复杂的关键词与短语检索。
- **混合检索API**:
    - **文本检索**: 基于Elasticsearch实现字幕内容的全文搜索。
    - **跨模态检索**: 基于ChromaDB和CLIP嵌入，实现“以文搜图”的语义检索功能。

## **3. 系统架构 (System Architecture)**

本系统采用Docker Compose进行服务编排，各服务在隔离的容器中运行，并通过自定义的桥接网络进行通信。服务间的启动顺序与可用性通过健康检查（Healthcheck）机制进行严格保证。

**服务组件:**

- `api_server`: 基于FastAPI的Web服务，作为系统入口，负责接收请求和任务分发。
- `celery_worker`: 后台任务执行单元，负责所有CPU/GPU密集型的媒体处理与AI推理任务。
- `postgres_db`: 主关系型数据库。
- `redis_broker`: Celery的消息代理与结果后端。
- `vector_db`: ChromaDB向量数据库服务。
- `search_engine`: Elasticsearch全文搜索引擎服务。

## **4. 技术栈 (Technology Stack)**

- **后端框架**: Python 3.11, FastAPI
- **异步任务队列**: Celery 5.x
- **数据库集群**:
    - PostgreSQL 15
    - ChromaDB (latest)
    - Elasticsearch 8.11.3
- **AI / ML**:
    - `openai-whisper`
    - `transformers` (Hugging Face)
    - `torch` (PyTorch)
- **媒体处理**: FFmpeg
- **容器化**: Docker, Docker Compose

## **5. 本地部署与运行 (Deployment & Execution)**

### **5.1. 前提条件**

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 必须已安装并处于运行状态。

### **5.2. 启动流程**

1. **克隆仓库**
    
    Bash
    
    ```
    git clone https://github.com/Byoushinwo/Intelligent-video.git
    cd my-video-platform
    ```
    
2. **构建并启动服务**
    
    Bash
    
    ```
    docker-compose up --build
    ```
    
    **注意**: 首次执行此命令将触发一个长时间的构建过程（预计20-40分钟），期间会下载所有基础镜像、安装系统与Python依赖，并预先下载和缓存所需的AI模型。此过程为一次性操作。当所有服务的健康检查通过且日志稳定后，系统即启动完成。
    

### **5.3. 停止服务**

在项目根目录终端中，按下 `Ctrl + C`，然后执行：

Bash

```
docker-compose down
```

## **6. API 端点**

- `POST /api/videos/upload`: 上传视频文件以启动分析流程。
- `GET /api/videos/`: 获取所有视频的元数据列表。
- `GET /api/videos/{video_id}`: 获取指定视频的元数据及其全文字幕。
- `GET /api/search/text`: 文本检索接口，参数: `q` (string)。
- `GET /api/search/image-by-text`: 跨模态检索接口，参数: `q` (string, English)。
- `GET /health`: 应用健康检查端点。
