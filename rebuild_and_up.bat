@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM RAGFlow Plus 重新构建所有镜像并启动服务脚本 (Windows 版本)
REM 作者: AI Assistant
REM 用途: 重新构建所有 Docker 镜像并启动完整的 RAGFlow Plus 服务栈

echo ==========================================
echo RAGFlow Plus 重新构建和启动脚本 (Windows)
echo ==========================================

REM 检查 Docker 是否运行
echo [INFO] 检查 Docker 服务状态...
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker 未运行或无法访问，请启动 Docker Desktop
    pause
    exit /b 1
)
echo [SUCCESS] Docker 服务正常运行

REM 停止现有服务
echo [INFO] 停止现有服务...

REM 停止主服务
cd docker
docker-compose ps -q >nul 2>&1
if not errorlevel 1 (
    echo [INFO] 停止主 RAGFlow 服务...
    docker-compose down
)

REM 停止管理系统服务
cd ..\management
docker-compose ps -q >nul 2>&1
if not errorlevel 1 (
    echo [INFO] 停止管理系统服务...
    docker-compose down
)

cd ..
echo [SUCCESS] 所有服务已停止

REM 清理旧镜像
echo [INFO] 清理旧镜像...
docker rmi -f zstar1003/ragflowplus:v0.5.0 2>nul
docker rmi -f zstar1003/ragflowplus-management-web:v0.5.0 2>nul
docker rmi -f zstar1003/ragflowplus-management-server:v0.5.0 2>nul
docker image prune -f >nul
echo [SUCCESS] 镜像清理完成

REM 构建主 RAGFlow 镜像
echo [INFO] 构建主 RAGFlow 镜像...
docker build -t zstar1003/ragflowplus:v0.5.0 .
if errorlevel 1 (
    echo [ERROR] 主镜像构建失败
    pause
    exit /b 1
)
echo [SUCCESS] 主 RAGFlow 镜像构建完成

REM 构建管理系统镜像
echo [INFO] 构建管理系统镜像...
cd management
docker-compose build --no-cache management-backend management-frontend
if errorlevel 1 (
    echo [ERROR] 管理系统镜像构建失败
    pause
    exit /b 1
)
cd ..
echo [SUCCESS] 管理系统镜像构建完成

REM 启动所有服务
echo [INFO] 启动所有服务...

REM 启动主服务
cd docker
echo [INFO] 启动主 RAGFlow 服务...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] 主服务启动失败
    pause
    exit /b 1
)

REM 等待主服务启动
echo [INFO] 等待主服务启动...
timeout /t 10 /nobreak >nul

REM 启动管理系统
cd ..\management
echo [INFO] 启动管理系统服务...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] 管理系统启动失败
    pause
    exit /b 1
)

cd ..
echo [SUCCESS] 所有服务启动完成

REM 显示服务状态
echo [INFO] 服务状态检查...
echo.
echo ==========================================
echo 服务状态
echo ==========================================

cd docker
echo 主 RAGFlow 服务:
docker-compose ps

echo.
cd ..\management
echo 管理系统服务:
docker-compose ps

cd ..

echo.
echo ==========================================
echo 访问地址
echo ==========================================
echo 主 RAGFlow 服务: http://localhost:80
echo 管理系统前端: http://localhost:8888
echo 管理系统后端: http://localhost:5000
echo MySQL: localhost:5455
echo Elasticsearch: http://localhost:1200
echo ==========================================

echo [SUCCESS] RAGFlow Plus 重新构建和部署完成！
echo.
echo 按任意键退出...
pause >nul