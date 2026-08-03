@echo off
echo ============================================================
echo         BACKING UP N8N DATA
echo ============================================================

set BACKUP_DIR=C:\Users\khett\Desktop\insurance-rag-backend\backups
set DATE=%date:~10,4%%date:~4,2%%date:~7,2%

if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

echo [1/4] Backing up workflows...
docker exec insurance-rag-n8n tar -czf /tmp/workflows_backup.tar.gz /home/node/.n8n/workflows
docker cp insurance-rag-n8n:/tmp/workflows_backup.tar.gz "%BACKUP_DIR%\workflows_%DATE%.tar.gz"

echo [2/4] Backing up database...
docker exec insurance-rag-postgres pg_dump -U admin -d n8n > "%BACKUP_DIR%\n8n_db_%DATE%.sql"

echo [3/4] Backing up local workflows...
if exist ".\n8n\workflows" (
    xcopy /E /Y ".\n8n\workflows" "%BACKUP_DIR%\workflows_local_%DATE%\"
)

echo [4/4] Backup complete!
echo Backups saved to: %BACKUP_DIR%
echo.
pause