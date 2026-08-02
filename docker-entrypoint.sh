#!/bin/bash
set -e

export PYTHONPATH=/app:$PYTHONPATH

# Docker/Swarm secrets: cada arquivo em /run/secrets/<nome> vira a env var
# <NOME EM MAIÚSCULO>, lida normalmente pelo settings via os.getenv/decouple.
# Secret vazio não é exportado — deixamos a var indefinida de propósito,
# para que config('X', default=...) caia no default em vez de receber "".
if [ -d /run/secrets ]; then
  for secret_file in /run/secrets/*; do
    [ -f "$secret_file" ] || continue
    var_name=$(basename "$secret_file" | tr '[:lower:]' '[:upper:]')
    secret_value="$(cat "$secret_file")"
    if [ -n "$secret_value" ]; then
      export "$var_name"="$secret_value"
    fi
  done
fi

echo "=========================================="
echo "🚀 INICIANDO KOINONIA API"
echo "=========================================="

echo "⏳ Aguardando banco de dados..."
while ! nc -z "${DB_HOST}" "${DB_PORT:-5432}"; do
  echo "   Tentando conectar ao banco..."
  sleep 2
done
echo "✓ Banco de dados disponível!"

cd /app
echo ""
echo "📦 Aplicando migrations..."
python manage.py migrate --noinput
echo "✓ Migrations aplicadas!"

echo ""
echo "=========================================="
echo "✅ SETUP CONCLUÍDO"
echo "=========================================="

exec "$@"
