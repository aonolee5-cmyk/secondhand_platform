@echo off
title 二手平台全栈一键启动器
color 0b

:: ==================================================
:: 1. 启动 Redis (路径：E:\redis)
:: ==================================================
echo [1/3] 正在启动 Redis 消息中间件...
:: /d 参数确保能正确跨盘符切换（如果脚本在C盘运行也能切到E盘）
start "Redis-Server" cmd /k "cd /d E:\redis && redis-server.exe"

:: 给 Redis 2 秒钟初始化时间
timeout /t 2 /nobreak > nul


:: ==================================================
:: 2. 启动后端 Django (ASGI 服务)
:: ==================================================
echo [2/3] 正在启动后端 Django ASGI 服务...
start "Django-Backend" cmd /k "cd /d E:\secondhand_platform\backend && venv\Scripts\activate && python manage.py runserver"

:: 给后端 3 秒钟启动时间
timeout /t 2 /nobreak > nul


:: ==================================================
:: 3. 启动前端 Vue 3 (npm 模式)
:: ==================================================
echo [3/3] 正在启动前端 Vue 3 渲染引擎...
start "Vue-Frontend" cmd /k "cd /d E:\secondhand_platform\frontend && npm run dev"


echo.
echo ==================================================
echo 🚀 所有服务已指令化拉起！
echo --------------------------------------------------
echo - Redis  已就绪 (E:\redis)
echo - Backend 已运行 (Django 4.2)
echo - Frontend 已启动 (Vite + Vue 3)
echo ==================================================
echo.
pause