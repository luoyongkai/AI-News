@echo off
chcp 65001
echo ====================================
echo     Twitter AI 监控系统
echo ====================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7或更高版本
    pause
    exit /b 1
)

REM 安装依赖
echo 正在安装依赖包...
pip install -r requirements.txt

REM 启动应用
echo.
echo 启动应用...
echo 访问地址: http://localhost:5000
echo 按 Ctrl+C 停止服务
echo.
python app.py

pause 