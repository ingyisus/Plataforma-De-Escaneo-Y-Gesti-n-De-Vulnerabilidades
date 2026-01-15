#!/bin/bash

if [ -z "$1" ]; then
    echo "Uso: ./restore.sh <archivo_backup.sql>"
    echo "Ejemplo: ./restore.sh /opt/backups/goodyear-vuln/backup_20240101_120000.sql"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: El archivo $BACKUP_FILE no existe"
    exit 1
fi

echo "==================================="
echo "Restauración de Base de Datos"
echo "==================================="
echo ""
echo "ADVERTENCIA: Esto sobrescribirá todos los datos actuales"
echo "Archivo a restaurar: $BACKUP_FILE"
echo ""
read -p "¿Deseas continuar? (si/no): " confirm

if [ "$confirm" != "si" ]; then
    echo "Restauración cancelada"
    exit 0
fi

cd "$(dirname "$0")/../docker"

echo ""
echo "Deteniendo servicios..."
docker-compose stop web frontend nginx

echo "Restaurando base de datos..."
if [[ "$BACKUP_FILE" == *.gz ]]; then
    gunzip -c "$BACKUP_FILE" | docker-compose exec -T db psql -U vulnuser vulndb
else
    cat "$BACKUP_FILE" | docker-compose exec -T db psql -U vulnuser vulndb
fi

if [ $? -eq 0 ]; then
    echo "Restauración completada exitosamente"
    echo ""
    echo "Reiniciando servicios..."
    docker-compose start web frontend nginx
    echo "Servicios reiniciados"
else
    echo "Error durante la restauración"
    exit 1
fi

echo ""
echo "==================================="
