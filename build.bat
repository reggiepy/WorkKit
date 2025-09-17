@echo off
REM PyInstaller ����ű�

REM ���û���·��
set BASEPATH=%cd%
set PYTHONPATH=%BASEPATH%
set PYTHONENVNAME=WorkKit

REM �������⻷��
@REM call activate %PYTHONENVNAME%
call C:\Users\wt\AppData\Local\pypoetry\Cache\virtualenvs\workkit-0NqmBcOK-py3.10\Scripts\activate.bat
if errorlevel 1 (
    echo ����: �޷��������⻷�� %PYTHONENVNAME%
    exit /b 1
)

REM ���ñ���
set SOURCE_FILE=main.py
set ICON_FILE=resources/app_icon.ico
set DIST_PATH=C:\dist\app
set WORK_PATH=C:\dist\build
set NAME=�������߰�

cd src/

REM ���Դ�ļ���ͼ���ļ��Ƿ����
if not exist "%SOURCE_FILE%" (
    echo ����: Դ�ļ� %SOURCE_FILE% ������
    exit /b 1
)
if not exist "%ICON_FILE%" (
    echo ����: ͼ���ļ� %ICON_FILE% �����ڣ���ʹ��Ĭ��ͼ��
    set ICON_FILE=
)

REM ִ�� PyInstaller
echo ���ڴ�������Ժ�...
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

REM ��� PyInstaller �Ƿ�ɹ�
if errorlevel 1 (
    echo ����: PyInstaller ���ʧ��
    exit /b 1
)

cd ../
REM ��������ʾ
echo �����ɣ����Ŀ¼: %DIST_PATH%
exit /b 0