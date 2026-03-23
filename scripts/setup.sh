#!/bin/bash

set -e

echo "=== 多模态数据分析可视化 Agent 系统安装脚本 ==="
echo ""

echo "[1/5] 检查 Python 版本..."
python3 --version

echo ""
echo "[2/5] 创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

echo ""
echo "[3/5] 安装后端依赖..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "[4/5] 安装前端依赖..."
cd frontend
npm install

echo ""
echo "[5/5] 创建必要目录..."
cd ..
mkdir -p uploads temp logs

echo ""
echo "=== 安装完成! ==="
echo ""
echo "启动后端服务:"
echo "  source venv/bin/activate"
echo "  cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "启动前端服务 (新终端):"
echo "  cd frontend && npm run dev"
echo ""
echo "访问 http://localhost:3000 开始使用系统"
