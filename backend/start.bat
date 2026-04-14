@echo off
REM 启动后端服务 - 使用 conda 环境 3.13_langchia

echo 正在激活 conda 环境: 3.13_langchia
call conda activate 3.13_langchia

echo.
echo 检查 Python 版本:
python --version

echo.
echo 检查 Flask 是否已安装:
python -c "import flask; print('Flask 版本:', flask.__version__)" 2>nul
if errorlevel 1 (
    echo [错误] Flask 未安装，正在安装依赖...
    pip install -r requirements.txt
)

echo.
echo 启动 Flask 服务器...
python app.py
