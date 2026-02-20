@echo off
echo ======================================
echo 足球数据分析系统统一启动脚本
echo ======================================
echo 1. 数据处理: setup_data.py
echo 2. 模型训练: train_model.py  
echo 3. 命令行预测: predict_cli.py
echo 4. Web应用: start_app.py
echo 5. 退出
echo ======================================

:menu
set /p choice="请选择操作 (1-5): "

if "%choice%"=="1" goto setup_data
if "%choice%"=="2" goto train_model
if "%choice%"=="3" goto predict_cli
if "%choice%"=="4" goto start_app
if "%choice%"=="5" goto exit
goto menu

:setup_data
echo.
echo === 执行数据处理 ===
python scripts\setup_data.py
pause
goto menu

:train_model
echo.
echo === 执行模型训练 ===
python scripts\train_model.py --mode train
pause
goto menu

:predict_cli
echo.
echo === 执行命令行预测 ===
echo 示例: python scripts\predict_cli.py --home-team "上海海港" --away-team "北京国安"
echo 请输入参数:
set /p params=参数:
python scripts\predict_cli.py %params%
pause
goto menu

:start_app
echo.
echo === 启动Web应用 ===
python scripts\start_app.py
goto menu

:exit
echo.
echo 系统已退出
pause