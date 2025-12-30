@echo off
chcp 65001 >nul
setlocal

REM ==========================================
REM WorkKit PyInstaller 构建脚本
REM ==========================================

REM 设置项目根目录
set "BASE_DIR=%~dp0"
REM 去掉末尾的反斜杠
if "%BASE_DIR:~-1%"=="\" set "BASE_DIR=%BASE_DIR:~0,-1%"

REM 设置虚拟环境路径
set "VENV_PATH=%BASE_DIR%\.venv"

REM 检查虚拟环境
if not exist "%VENV_PATH%\Scripts\activate.bat" (
    echo [错误] 找不到虚拟环境: %VENV_PATH%
    echo 请确保已运行 ''uv sync' 创建了虚拟环境。
    pause
    exit /b 1
)

REM 激活虚拟环境
call "%VENV_PATH%\Scripts\activate.bat"

REM 设置构建参数
set "APP_NAME=WorkKit"
set "SRC_DIR=%BASE_DIR%\src"
set "MAIN_SCRIPT=main.py"
set "ICON_PATH=resources\app_icon.ico"
set "DIST_DIR=%BASE_DIR%\dist"
set "BUILD_DIR=%BASE_DIR%\build_temp"

echo [信息] 正在构建项目: %APP_NAME%
echo [信息] 源代码路径: %SRC_DIR%
echo [信息] 输出目录: %DIST_DIR%

REM 切换到 src 目录 (确保相对导入和资源路径正确)
pushd "%SRC_DIR%"

REM 检查入口文件
if not exist "%MAIN_SCRIPT%" (
    echo [错误] 找不到入口文件: %SRC_DIR%\%MAIN_SCRIPT%
    popd
    exit /b 1
)

REM 执行 PyInstaller
REM 注意: 已移除特定用户的硬编码 DLL 路径。
REM 如果遇到 DLL 缺失错误，请确保虚拟环境完整，或手动添加 --add-binary 参数。
echo [信息] 开始打包...

pyinstaller ^
    --noconfirm ^
    --onedir ^
    --windowed ^
    --name "%APP_NAME%" ^
    --icon "%ICON_PATH%" ^
    --paths "%SRC_DIR%" ^
    --add-data "resources;resources" ^
    --add-data "alembic;alembic" ^
    --add-data "alembic.ini;." ^
    --hidden-import "ipaddress" ^
    --hidden-import "shiboken6" ^
    --hidden-import "PySide6.QtCore" ^
    --hidden-import "PySide6.QtGui" ^
    --hidden-import "PySide6.QtWidgets" ^
    --distpath "%DIST_DIR%" ^
    --workpath "%BUILD_DIR%" ^
    --clean ^
    --noupx ^
    "%MAIN_SCRIPT%"

if errorlevel 1 (
    echo [错误] PyInstaller 构建失败。
    popd
    exit /b 1
)

popd

echo.
echo [成功] 构建完成!
echo 可执行文件位于: %DIST_DIR%\%APP_NAME%\%APP_NAME%.exe
echo.
pause
