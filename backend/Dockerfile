# 1. 使用官方的 Python 3.11 镜像作为基础
FROM python:3.11

RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
    rm -f /etc/apt/apt.conf.d/docker-clean && \
    apt-get clean && \
    apt-get update

# 2. 安装系统依赖：FFmpeg 用于视频处理，curl/wget 用于健康检查
RUN apt-get install -y ffmpeg curl wget ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 3. 设置工作目录，容器内所有后续操作都在 /app 目录下进行
WORKDIR /app

# 4. 将 requirements.txt 文件复制到容器的 /app 目录中
COPY ./requirements.txt /app/requirements.txt

# 5. 在容器内运行 pip 命令，安装所有依赖
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# 6. 在构建镜像时，预先下载并缓存所有 AI 模型
COPY ./download_models.py /app/download_models.py
RUN python /app/download_models.py


# 7. 将 backend 目录下的所有文件（我们写的代码）复制到容器的 /app 目录中
COPY . /app

# (这句 CMD 在 docker-compose.yml 中会被覆盖，这里只是个占位)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]