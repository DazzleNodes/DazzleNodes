@echo off
REM Fix Python file association to use C:\Python313 instead of Windows Store stub
REM Run this as Administrator

echo Current Python file association:
assoc .py
ftype Python.File

echo.
echo Fixing Python file association to use C:\Python312...
echo.

REM Associate .py files with Python.File type
assoc .py=Python.File

REM Set Python.File to use C:\Python313
ftype Python.File="C:\Python312\python.exe" "%%1" %%*

echo.
echo New Python file association:
assoc .py
ftype Python.File

echo.
echo Done! Now .py files will use C:\Python312\python.exe
echo.
echo You may also want to disable Windows Store Python stubs:
echo 1. Open Windows Settings
echo 2. Go to Apps ^> Apps ^& features ^> App execution aliases
echo 3. Turn OFF both "python.exe" and "python3.exe" toggles
echo.
pause
