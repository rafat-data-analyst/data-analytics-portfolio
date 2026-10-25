@echo off
REM Runs the ETL pipeline. Schedule this file with Windows Task Scheduler (see README).
cd /d "%~dp0"
if not exist logs mkdir logs
python etl_pipeline.py >> logs\scheduler.log 2>&1
