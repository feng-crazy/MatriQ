#!/bin/bash
# MatriQ 部署脚本

set -e

echo "=========================================="
echo "MatriQ 部署脚本"
echo "=========================================="

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "错误: 未安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "错误: 未安装 Docker Compose"
    exit 1
fi

# 备份数据
if [ -f "./scripts/backup.sh" ]; then
    echo "执行数据备份..."
    bash ./scripts/backup.sh
fi

# 拉取最新代码（如果使用 Git）
if [ -d ".git" ]; then
    echo "拉取最新代码..."
    git pull
fi

# 构建并启动服务
echo "构建 Docker 镜像..."
docker-compose build

echo "启动服务..."
docker-compose up -d

# 等待服务启动
echo "等待服务启动..."
sleep 5

# 健康检查
echo "执行健康检查..."
for i in {1..10}; do
    if curl -f http://localhost:8000/ > /dev/null 2>&1; then
        echo "✓ 服务启动成功！"
        exit 0
    fi
    echo "等待服务启动... ($i/10)"
    sleep 2
done

echo "✗ 服务启动失败，请检查日志"
docker-compose logs --tail=50
exit 1

