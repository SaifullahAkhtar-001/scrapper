@echo off
echo ========================================
echo    COMBINED SCRAPER RUNNER
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then: venv\Scripts\activate.bat
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if we're in the right directory
if not exist "services\combined_scraper_service.py" (
    echo Error: Please run this script from the backend directory!
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo.
echo Starting combined scraper...
echo.

REM Run the combined scraper
python run_combined_scraper.py %*

echo.
echo ========================================
echo    SCRAPING COMPLETED
echo ========================================
pause
