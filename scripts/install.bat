@echo off
REM ===========================================
REM BUKO AI - SCRIPT DE INSTALACIÓN WINDOWS
REM ===========================================

echo 🚀 Instalando Buko AI...

REM Verificar si está corriendo en el directorio correcto
if not exist "README.md" (
    echo ❌ Por favor ejecuta este script desde el directorio raíz del proyecto
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ❌ Por favor ejecuta este script desde el directorio raíz del proyecto
    pause
    exit /b 1
)

REM Verificar Python
echo ℹ️  Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no está instalado o no está en PATH
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% encontrado

REM Verificar Python 3.12+
python -c "import sys; assert sys.version_info >= (3, 12)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 3.12+ es requerido. Versión actual: %PYTHON_VERSION%
    pause
    exit /b 1
)

REM Crear entorno virtual
echo ℹ️  Creando entorno virtual...
if exist "venv" (
    echo ⚠️  Entorno virtual ya existe. Eliminando...
    rmdir /s /q venv
)

python -m venv venv
echo ✅ Entorno virtual creado

REM Activar entorno virtual
echo ℹ️  Activando entorno virtual...
call venv\Scripts\activate.bat

REM Actualizar pip
echo ℹ️  Actualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias
echo ℹ️  Instalando dependencias...
pip install -r requirements.txt
echo ✅ Dependencias instaladas

REM Instalar dependencias de desarrollo
echo ℹ️  Instalando dependencias de desarrollo...
pip install -e .[dev]
echo ✅ Dependencias de desarrollo instaladas

REM Configurar archivos de entorno
echo ℹ️  Configurando archivos de entorno...
if not exist ".env" (
    copy .env.example .env
    echo ✅ Archivo .env creado desde .env.example
    echo ⚠️  Por favor configura las variables de entorno en .env
) else (
    echo ℹ️  Archivo .env ya existe
)

REM Crear directorios necesarios
echo ℹ️  Creando directorios necesarios...
mkdir logs 2>nul
mkdir storage\uploads 2>nul
mkdir storage\books 2>nul
mkdir storage\covers 2>nul
echo ✅ Directorios creados

REM Configurar pre-commit hooks
echo ℹ️  Configurando pre-commit hooks...
pre-commit install
echo ✅ Pre-commit hooks configurados

REM Verificar instalación
echo ℹ️  Verificando instalación...

REM Verificar Flask
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error al instalar Flask
    pause
    exit /b 1
)
echo ✅ Flask instalado correctamente

REM Verificar otras dependencias críticas
python -c "import sqlalchemy" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error al instalar sqlalchemy
    pause
    exit /b 1
)
echo ✅ sqlalchemy instalado correctamente

python -c "import celery" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error al instalar celery
    pause
    exit /b 1
)
echo ✅ celery instalado correctamente

python -c "import redis" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error al instalar redis
    pause
    exit /b 1
)
echo ✅ redis instalado correctamente

python -c "import anthropic" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error al instalar anthropic
    pause
    exit /b 1
)
echo ✅ anthropic instalado correctamente

python -c "import reportlab" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error al instalar reportlab
    pause
    exit /b 1
)
echo ✅ reportlab instalado correctamente

REM Crear archivo de configuración inicial
echo ℹ️  Creando configuración inicial...
(
echo from flask import Flask
echo from config import get_config
echo.
echo def create_app^(config_name='development'^):
echo     app = Flask^(__name__^)
echo     config_class = get_config^(config_name^)
echo     app.config.from_object^(config_class^)
echo     config_class.init_app^(app^)
echo     
echo     @app.route^('/'^)
echo     def index^(^):
echo         return {
echo             'message': 'Buko AI API',
echo             'version': '0.1.0',
echo             'status': 'healthy'
echo         }
echo     
echo     return app
echo.
echo if __name__ == '__main__':
echo     app = create_app^(^)
echo     app.run^(debug=True^)
) > app.py

echo ✅ Archivo app.py creado

REM Mostrar información final
echo.
echo 🎉 ¡Instalación completada exitosamente!
echo.
echo Para comenzar a desarrollar:
echo 1. Configura las variables de entorno en .env
echo 2. Ejecuta: venv\Scripts\activate.bat
echo 3. Ejecuta: python app.py
echo.
echo Para usar Docker:
echo 1. Ejecuta: docker-compose up --build
echo.
echo Documentación disponible en: https://docs.buko-ai.com
echo.
echo ✅ ¡Listo para comenzar a desarrollar!
pause