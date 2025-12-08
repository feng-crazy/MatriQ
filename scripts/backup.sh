#!/bin/bash
# MatriQ 数据备份脚本

set -e

# 配置
BACKUP_DIR="${BACKUP_DIR:-/opt/backups/matriq}"
DATA_DIR="${DATA_DIR:-./backend/data}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 生成时间戳
DATE=$(date +%Y%m%d_%H%M%S)

echo "开始备份 MatriQ 数据: $DATE"

# 备份数据库
if [ -f "$DATA_DIR/matriq.db" ]; then
    cp "$DATA_DIR/matriq.db" "$BACKUP_DIR/matriq_$DATE.db"
    echo "✓ 数据库备份完成: matriq_$DATE.db"
else
    echo "⚠ 数据库文件不存在，跳过备份"
fi

# 备份 Excel 文件
if [ -d "$DATA_DIR/pipelines" ]; then
    tar -czf "$BACKUP_DIR/pipelines_$DATE.tar.gz" -C "$DATA_DIR" pipelines/
    echo "✓ Excel 文件备份完成: pipelines_$DATE.tar.gz"
else
    echo "⚠ Excel 目录不存在，跳过备份"
fi

# 删除过期备份
find "$BACKUP_DIR" -type f -mtime +$RETENTION_DAYS -delete
echo "✓ 已清理 $RETENTION_DAYS 天前的备份文件"

echo "备份完成！"
echo "备份位置: $BACKUP_DIR"

