@echo off
REM Performance Test Script Converter (PTSC) - Build Script
REM Builds the application into a standalone executable

echo ================================================================================
echo Performance Test Script Converter (PTSC) - Build Script
echo ================================================================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found at .venv
    echo Please run: python -m venv .venv
    echo Then: .venv\Scripts\activate.bat
    echo And: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install PyInstaller if not installed
echo.
echo [INFO] Checking PyInstaller installation...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [INFO] Installing PyInstaller...
    pip install pyinstaller
) else (
    echo [OK] PyInstaller is already installed
)

REM Clean previous build
echo.
echo [INFO] Cleaning previous build...
if exist "dist\PTSC" rmdir /s /q "dist\PTSC"
if exist "build" rmdir /s /q "build"

REM Build with PyInstaller
echo.
echo [INFO] Building executable with PyInstaller...
echo.
pyinstaller --clean PTSC.spec

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

REM Check if build was successful
if not exist "dist\PTSC\PTSC.exe" (
    echo.
    echo [ERROR] PTSC.exe not found in dist\PTSC\
    pause
    exit /b 1
)

REM Copy additional files
echo.
echo [INFO] Copying additional files...
if not exist "dist\PTSC\.streamlit" mkdir "dist\PTSC\.streamlit"
copy ".streamlit\config.toml" "dist\PTSC\.streamlit\" >nul 2>&1

REM Create README in dist folder
echo.
echo [INFO] Creating README...
(
echo Performance Test Script Converter ^(PTSC^)
echo =========================================
echo.
echo To run the application:
echo   1. Double-click PTSC.exe
echo   2. Wait for the browser to open automatically
echo   3. If browser doesn't open, navigate to: http://localhost:8501
echo.
echo To stop the application:
echo   - Close the console window
echo.
echo Note: The first launch may take a few seconds.
) > "dist\PTSC\README.txt"

echo.
echo ================================================================================
echo [SUCCESS] Build completed successfully!
echo ================================================================================
echo.
echo Output directory: dist\PTSC\
echo Executable: dist\PTSC\PTSC.exe
echo.
echo You can now distribute the entire 'dist\PTSC' folder.
echo.
pause
