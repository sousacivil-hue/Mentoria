@echo off
cd /d "%~dp0"
REM Coloque sua chave do Gemini na linha abaixo
set GEMINI_API_KEY=COLE_SUA_CHAVE_AQUI
echo Iniciando servidor DiarioAuto...
python -m uvicorn main:app --port 8000
echo.
echo O servidor parou. Veja a mensagem de erro acima.
pause
