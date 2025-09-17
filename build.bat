@echo off
REM PyInstaller 打包脚本

REM 设置基础路径
set BASEPATH=%cd%
set PYTHONPATH=%BASEPATH%
set PYTHONENVNAME=WorkKit

REM 激活虚拟环境
@REM call activate %PYTHONENVNAME%
call C:\Users\wt\AppData\Local\pypoetry\Cache\virtualenvs\workkit-0NqmBcOK-py3.10\Scripts\activate.bat
if errorlevel 1 (
    echo 错误: 无法激活虚拟环境 %PYTHONENVNAME%
    exit /b 1
)

REM 设置变量
set SOURCE_FILE=main.py
set ICON_FILE=resources/app_icon.ico
set DIST_PATH=C:\dist\app
set WORK_PATH=C:\dist\build
set NAME=工作工具包

cd src/

REM 检查源文件和图标文件是否存在
if not exist "%SOURCE_FILE%" (
    echo 错误: 源文件 %SOURCE_FILE% 不存在
    exit /b 1
)
if not exist "%ICON_FILE%" (
    echo 警告: 图标文件 %ICON_FILE% 不存在，将使用默认图标
    set ICON_FILE=
)

REM 执行 PyInstaller
echo 正在打包，请稍候...
pyinstaller ^
    -w ^
    -n "%NAME%"^
    -i "%ICON_FILE%" ^
    %SOURCE_FILE% ^
    -p ./ ^
    --add-binary "C:/Users/wt/.conda/envs/py310/Library/bin/libexpat.dll;." ^
    --add-binary "C:/Users/wt/.conda/envs/py310/Library/bin/ffi.dll;." ^
    --add-data resources;resources ^
    --add-data alembic;alembic ^
    --add-data alembic.ini;. ^
    --hidden-import ipaddress ^
    --hidden-import=shiboken6 ^
    --hidden-import=PySide6.QtCore ^
    --hidden-import=PySide6.QtGui ^
    --hidden-import=PySide6.QtWidgets ^
    --distpath "%DIST_PATH%" ^
    --workpath "%WORK_PATH%" ^
    --clean ^
    --noconfirm ^
    --noupx

REM 检查 PyInstaller 是否成功
if errorlevel 1 (
    echo 错误: PyInstaller 打包失败
    exit /b 1
)

cd ../
REM 打包完成提示
echo 打包完成，输出目录: %DIST_PATH%
exit /b 0