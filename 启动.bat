@echo off
title 二手平台一键启动器

:: 1. 启动后端
echo 正在启动后端 Django...
start cmd /k "cd /d E:\secondhand_platform\backend && venv\Scripts\activate && python manage.py runserver"

:: 2. 启动前端
echo 正在启动前端 Vue 3...
start cmd /k "cd /d E:\secondhand_platform\frontend && npm run dev"

echo 项目已启动！
pause