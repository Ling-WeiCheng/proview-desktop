#!/bin/bash
# 启动后端服务 - 使用 conda 环境 3.13_langchia

echo "正在激活 conda 环境: 3.13_langchia"
source ~/miniforge3/etc/profile.d/conda.sh 2>/dev/null || source ~/anaconda3/etc/profile.d/conda.sh 2>/dev/null || true
conda activate 3.13_langchia

echo ""
echo "检查 Python 版本:"
python --version

echo ""
echo "检查 Flask 是否已安装:"
if ! python -c "import flask" 2>/dev/null; then
    echo "[错误] Flask 未安装，正在安装依赖..."
    pip install -r requirements.txt
fi

echo ""
echo "启动 Flask 服务器..."
python app.py
