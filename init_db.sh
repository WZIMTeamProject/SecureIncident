#!/bin/bash

echo "[1/3] Uruchamianie bazy danych w srodowisku Docker..."
cd "$(dirname "$0")/docker"
docker-compose up -d

echo "[2/3] Oczekiwanie na poprawne uruchomienie bazy danych (10 sekund)..."
sleep 10

echo "[3/3] Aktualizacja schematu bazy danych (Alembic)..."
cd "$(dirname "$0")/backend"

# Pobranie DATABASE_URL z pliku .env
export $(grep -v '^#' .env | xargs)

# Uzywamy bin dla Linux/Mac lub Scripts dla Windows (git bash)
if [ -f "./.venv/bin/alembic" ]; then
    ./.venv/bin/alembic upgrade head
else
    ./.venv/Scripts/alembic upgrade head
fi

echo ""
echo "=========================================================="
echo "Baza danych jest uruchomiona i w pelni zaktualizowana!"
echo "Mozesz teraz uruchomic aplikacje."
echo "=========================================================="
