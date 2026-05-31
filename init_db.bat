@echo off
echo [1/3] Uruchamianie bazy danych w srodowisku Docker...
cd "%~dp0docker"
docker-compose up -d

echo [2/3] Oczekiwanie na poprawne uruchomienie bazy danych (10 sekund)...
timeout /t 10 /nobreak

echo [3/3] Aktualizacja schematu bazy danych (Alembic)...
cd "%~dp0backend"
:: Pobranie DATABASE_URL z pliku .env
FOR /F "tokens=*" %%i IN ('findstr DATABASE_URL .env') DO SET %%i

.venv\Scripts\alembic.exe upgrade head

echo.
echo ==========================================================
echo Baza danych jest uruchomiona i w pelni zaktualizowana!
echo Mozesz teraz uruchomic aplikacje.
echo ==========================================================
pause
