#!/bin/bash
set -e
echo "📥 拉取最新内容..."
git pull origin main

echo "🔨 构建静态站点..."
docker run --rm -v "$(pwd)":/docs squidfunk/mkdocs-material build --clean

echo "♻️  重启 Nginx..."
docker compose restart docs 2>/dev/null || docker compose up -d

echo "✅ 完成！访问 http://119.91.152.183"
