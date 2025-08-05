# 1. 使用官方的 Python 3.11 标准镜像
FROM python:3.11

# 2. 更换 Debian 的 apt 软件源为国内镜像源 (阿里云源)
#    并增加重试和容错机制
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    rm -f /etc/apt/apt.conf.d/docker-clean && \
    apt-get clean && \
    # 增加重试配置，遇到网络问题时自动重试3次
    echo "APT::Acquire::Retries \"3\";" > /etc/apt/apt.conf.d/80-retries && \
    apt-get update

# 3. 安装所有系统依赖，并增加 -q 参数减少不必要的输出
RUN apt-get install -y -q ffmpeg curl wget ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 4. 设置工作目录
WORKDIR /app

# 5. 复制并安装 Python 依赖 (使用国内 pip 源)
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 6.  在构建镜像时，预先下载并缓存所有 AI 模型
COPY ./download_models.py /app/download_models.py
RUN python /app/download_models.py

# 7. 将所有后端代码复制到容器中
COPY . /app

# 8. (占位命令)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]