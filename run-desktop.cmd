@echo off
rem Launch PULU from source on Windows.
rem
rem The npm "start" script uses `env -u ELECTRON_RUN_AS_NODE`, which only exists
rem on macOS and Linux. Inheriting ELECTRON_RUN_AS_NODE=1 from a parent process
rem makes Electron run as plain Node and the main process fails with
rem "app is not defined", so clear it here before launching.
cd /d "%~dp0"
set "ELECTRON_RUN_AS_NODE="
if not exist "dist\index.html" (
  node scripts\build.mjs || exit /b 1
)
"node_modules\electron\dist\electron.exe" . %*
