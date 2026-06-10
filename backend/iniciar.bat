@echo off
REM Coloque sua chave do Gemini na linha abaixo (entre as aspas)
set GEMINI_API_KEY=COLE_SUA_CHAVE_AQUI
python -m uvicorn main:app --port 8000
