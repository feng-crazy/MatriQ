# MatriQ 部署文档

本文档介绍如何部署 MatriQ 物料标签识别助手系统。

## 📋 目录

- [Docker 部署](#docker-部署)
- [传统部署](#传统部署)
- [CI/CD 配置](#cicd-配置)
- [生产环境配置](#生产环境配置)
- [监控与维护](#监控与维护)

## 🐳 Docker 部署

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 2GB 可用内存

### 快速启动

1. **克隆项目**

```bash
git clone <repository-url>
cd MatriQ
```

2. **配置环境变量**

```bash
cp backend/.env.example backend/.env
# 编辑 backend/.env，至少配置 PADDLEOCR_TOKEN
```

3. **启动服务**

```bash
docker-compose up -d
```

4. **验证部署**

```bash
curl http://localhost:8000/
# 应该返回: {"status":"ok","app":"MatriQ OCR Service"}
```

### 使用生产环境配置

```bash
docker-compose --profile production up -d
```

这将同时启动 Nginx 反向代理。

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看后端日志
docker-compose logs -f backend
```

### 停止服务

```bash
docker-compose down
```

### 更新服务

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build
```

## 🖥️ 传统部署

### 后端部署

#### 1. 服务器要求

- Ubuntu 20.04+ / CentOS 7+
- Python 3.11+
- 至少 2GB RAM
- 10GB+ 磁盘空间

#### 2. 安装依赖

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 和 pip
sudo apt install python3.11 python3.11-venv python3-pip -y

# 安装系统依赖
sudo apt install gcc g++ -y
```

#### 3. 部署应用

```bash
# 创建应用目录
sudo mkdir -p /opt/matriq
sudo chown $USER:$USER /opt/matriq

# 克隆项目
cd /opt/matriq
git clone <repository-url> .

# 创建虚拟环境
cd backend
python3.11 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
nano .env  # 编辑配置文件
```

#### 4. 配置系统服务

创建 systemd 服务文件 `/etc/systemd/system/matriq.service`:

```ini
[Unit]
Description=MatriQ OCR Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/matriq/backend
Environment="PATH=/opt/matriq/backend/.venv/bin"
ExecStart=/opt/matriq/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable matriq
sudo systemctl start matriq
sudo systemctl status matriq
```

#### 5. 配置 Nginx 反向代理

安装 Nginx：

```bash
sudo apt install nginx -y
```

创建配置文件 `/etc/nginx/sites-available/matriq`:

```nginx
server {
    listen 80;
    server_name matriq.example.com;

    client_max_body_size 15M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/matriq /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 6. 配置 SSL（可选）

使用 Let's Encrypt：

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d matriq.example.com
```

### 前端部署

#### 1. 构建生产版本

```bash
cd frontend
npm install
npm run build
```

#### 2. 部署到 Nginx

将 `dist` 目录内容复制到 Nginx 静态文件目录：

```bash
sudo cp -r dist/* /var/www/matriq/
```

更新 Nginx 配置：

```nginx
server {
    listen 80;
    server_name matriq.example.com;
    root /var/www/matriq;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 🔄 CI/CD 配置

### GitHub Actions

项目已配置 GitHub Actions 工作流：

1. **CI Pipeline** (`.github/workflows/ci.yml`)
   - 后端测试
   - 前端代码检查
   - 小程序构建验证
   - Docker 镜像构建（仅 main 分支）

2. **Deploy Pipeline** (`.github/workflows/deploy.yml`)
   - 自动部署到生产服务器（仅 main 分支）

### 配置 Secrets

在 GitHub 仓库设置中添加以下 Secrets：

- `DOCKER_USERNAME` - Docker Hub 用户名
- `DOCKER_PASSWORD` - Docker Hub 密码
- `DEPLOY_HOST` - 部署服务器地址
- `DEPLOY_USER` - 部署服务器用户名
- `DEPLOY_SSH_KEY` - 部署服务器 SSH 私钥
- `DEPLOY_PORT` - SSH 端口（可选，默认 22）

### 手动触发部署

```bash
# 创建标签触发部署
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## ⚙️ 生产环境配置

### 环境变量

生产环境 `.env` 配置示例：

```bash
# 应用配置
APP_NAME=MatriQ OCR Service
API_PREFIX=/api/v1

# 数据存储
SQLITE_PATH=/app/data/matriq.db
PIPELINES_ROOT=/app/data/pipelines

# PaddleOCR API（必填）
PADDLEOCR_API_URL=https://gfc197xb35lb0274.aistudio-app.com/layout-parsing
PADDLEOCR_TOKEN=your-production-token

# 文件上传限制
MAX_UPLOAD_MB=15
ALLOWED_EXTENSIONS=.jpg,.jpeg,.png
```

### 数据备份

#### 自动备份脚本

创建 `scripts/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/matriq"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
cp /opt/matriq/backend/data/matriq.db $BACKUP_DIR/matriq_$DATE.db

# 备份 Excel 文件
tar -czf $BACKUP_DIR/pipelines_$DATE.tar.gz /opt/matriq/backend/data/pipelines

# 删除 30 天前的备份
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

添加到 crontab：

```bash
# 每天凌晨 2 点备份
0 2 * * * /opt/matriq/scripts/backup.sh
```

### 日志管理

#### 配置日志轮转

创建 `/etc/logrotate.d/matriq`:

```
/opt/matriq/backend/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload matriq > /dev/null 2>&1 || true
    endscript
}
```

## 📊 监控与维护

### 健康检查

```bash
# 检查服务状态
curl http://localhost:8000/

# 检查 API 端点
curl http://localhost:8000/api/v1/pipelines
```

### 性能监控

推荐使用以下工具：

- **Prometheus + Grafana** - 指标监控
- **Sentry** - 错误追踪
- **ELK Stack** - 日志分析

### 常见问题排查

#### 1. 服务无法启动

```bash
# 查看日志
journalctl -u matriq -n 50

# 检查端口占用
sudo netstat -tlnp | grep 8000

# 检查环境变量
systemctl show matriq | grep Environment
```

#### 2. OCR 识别失败

```bash
# 检查 PaddleOCR API 连接
curl -X POST https://gfc197xb35lb0274.aistudio-app.com/layout-parsing \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"file":"base64_encoded_image","fileType":1}'

# 检查网络连接
ping gfc197xb35lb0274.aistudio-app.com
```

#### 3. 数据库问题

```bash
# 检查数据库文件权限
ls -la /opt/matriq/backend/data/matriq.db

# 修复数据库（SQLite）
sqlite3 /opt/matriq/backend/data/matriq.db "PRAGMA integrity_check;"
```

### 更新流程

1. **备份数据**
```bash
./scripts/backup.sh
```

2. **拉取最新代码**
```bash
cd /opt/matriq
git pull origin main
```

3. **更新依赖**
```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt --upgrade
```

4. **重启服务**
```bash
sudo systemctl restart matriq
# 或
docker-compose restart backend
```

5. **验证部署**
```bash
curl http://localhost:8000/
```

## 🔒 安全建议

1. **使用 HTTPS** - 配置 SSL 证书
2. **防火墙配置** - 只开放必要端口
3. **定期更新** - 保持系统和依赖更新
4. **访问控制** - 使用 Nginx 限制访问
5. **数据加密** - 敏感数据加密存储
6. **API 限流** - 防止 API 滥用

## 📞 支持

如遇问题，请查看：
- [README.md](./README.md)
- [API_CHECK.md](./API_CHECK.md)
- [QUICK_START.md](./QUICK_START.md)

