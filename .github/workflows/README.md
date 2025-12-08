# GitHub Actions CI/CD 工作流

## 工作流说明

### 1. CI Pipeline (`ci.yml`)

在每次 push 或 pull request 时自动运行：

- **后端测试**: 运行 pytest 测试套件，生成覆盖率报告
- **前端代码检查**: 运行 ESLint 检查
- **小程序构建**: 验证小程序代码可以正常构建
- **Docker 构建**: 仅在 main 分支 push 时构建并推送 Docker 镜像

### 2. Deploy Pipeline (`deploy.yml`)

在 main 分支 push 或创建版本标签时自动部署：

- **SSH 部署**: 通过 SSH 连接到服务器并执行部署命令
- **健康检查**: 部署后验证服务是否正常运行

## 配置要求

### GitHub Secrets

在仓库设置中添加以下 Secrets：

#### Docker Hub
- `DOCKER_USERNAME`: Docker Hub 用户名
- `DOCKER_PASSWORD`: Docker Hub 密码或访问令牌

#### 部署服务器
- `DEPLOY_HOST`: 服务器 IP 或域名
- `DEPLOY_USER`: SSH 用户名
- `DEPLOY_SSH_KEY`: SSH 私钥（完整内容，包括 -----BEGIN 和 -----END）
- `DEPLOY_PORT`: SSH 端口（可选，默认 22）

### 服务器要求

部署服务器需要：

1. 安装 Docker 和 Docker Compose
2. 配置 SSH 密钥认证
3. 创建部署目录：`/opt/matriq`
4. 在部署目录中创建 `docker-compose.yml` 文件

### 部署目录结构

```
/opt/matriq/
├── docker-compose.yml
├── backend/
│   ├── .env
│   └── data/
└── nginx/
    └── nginx.conf
```

## 手动触发

### 创建版本标签

```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

这将触发部署流程。

## 故障排查

### 查看工作流日志

1. 进入 GitHub 仓库
2. 点击 "Actions" 标签
3. 选择失败的工作流
4. 查看详细日志

### 常见问题

1. **Docker 构建失败**
   - 检查 Docker Hub 凭据是否正确
   - 检查 Dockerfile 语法

2. **部署失败**
   - 检查 SSH 密钥是否正确
   - 检查服务器是否可访问
   - 检查部署目录是否存在

3. **测试失败**
   - 检查测试代码是否有错误
   - 检查依赖是否正确安装

