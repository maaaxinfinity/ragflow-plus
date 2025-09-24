@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM RAGFlow Plus 重新构建所有镜像并启动服务脚本 (Windows 版本)
REM 作者: AI Assistant
REM 用途: 重新构建所有 Docker 镜像并启动完整的 RAGFlow Plus 服务栈
REM 
REM 使用方法:
REM   rebuild_and_up.bat           # 使用缓存构建
REM   rebuild_and_up.bat --no-cache # 不使用缓存构建

REM 解析命令行参数
set NO_CACHE=false
if "%1"=="--no-cache" set NO_CACHE=true

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
    docker-compose down --remove-orphans
)

REM 停止管理系统服务
cd ..\management
docker-compose ps -q >nul 2>&1
if not errorlevel 1 (
    echo [INFO] 停止管理系统服务...
    docker-compose down --remove-orphans
)

cd ..

REM 强制删除可能存在的容器
echo [INFO] 清理残留容器...
docker rm -f ragflowplus-server 2>nul
docker rm -f ragflowplus-management-frontend 2>nul
docker rm -f ragflowplus-management-backend 2>nul
docker rm -f ragflow-mysql 2>nul
docker rm -f ragflow-es-01 2>nul
docker rm -f ragflow-redis 2>nul
docker rm -f ragflow-minio 2>nul

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
if "%NO_CACHE%"=="true" (
    echo [INFO] 使用 --no-cache 构建主镜像...
    docker build --no-cache -t zstar1003/ragflowplus:v0.5.0 .
) else (
    echo [INFO] 使用缓存构建主镜像...
    docker build -t zstar1003/ragflowplus:v0.5.0 .
)
if errorlevel 1 (
    echo [ERROR] 主镜像构建失败
    pause
    exit /b 1
)
echo [SUCCESS] 主 RAGFlow 镜像构建完成

REM 构建管理系统镜像
echo [INFO] 构建管理系统镜像...
cd management
if "%NO_CACHE%"=="true" (
    echo [INFO] 使用 --no-cache 构建管理系统镜像...
    docker-compose build --no-cache management-backend management-frontend
) else (
    echo [INFO] 使用缓存构建管理系统镜像...
    docker-compose build management-backend management-frontend
)
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
timeout /t 15 /nobreak >nul

REM 启动管理系统 - 分别启动避免冲突
cd ..\management
echo [INFO] 启动管理系统后端...
docker-compose up -d management-backend
if errorlevel 1 (
    echo [ERROR] 管理系统后端启动失败
    pause
    exit /b 1
)

REM 等待后端启动
timeout /t 5 /nobreak >nul

echo [INFO] 启动管理系统前端...
docker-compose up -d management-frontend
if errorlevel 1 (
    echo [ERROR] 管理系统前端启动失败
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