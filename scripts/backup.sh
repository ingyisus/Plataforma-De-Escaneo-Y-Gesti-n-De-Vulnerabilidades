#!/bin/bash

BACKUP_DIR="/opt/backups/goodyear-vuln"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_${DATE}.sql"

echo "==================================="
echo "Backup de Base de Datos - Goodyear"
echo "==================================="
echo ""

mkdir -p "$BACKUP_DIR"

cd "$(dirname "$0")/../docker"

echo "Realizando backup de la base de datos..."
docker-compose exec -T db pg_dump -U vulnuser vulndb > "${BACKUP_DIR}/${BACKUP_FILE}"

if [ $? -eq 0 ]; then
    echo "Backup completado exitosamente:"
    echo "Archivo: ${BACKUP_DIR}/${BACKUP_FILE}"
    echo "Tamaño: $(du -h ${BACKUP_DIR}/${BACKUP_FILE} | cut -f1)"

    gzip "${BACKUP_DIR}/${BACKUP_FILE}"
    echo "Archivo comprimido: ${BACKUP_DIR}/${BACKUP_FILE}.gz"

    find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +30 -delete
    echo "Backups antiguos (>30 días) eliminados"
else
    echo "Error al realizar el backup"
    exit 1
fi

echo ""
echo "==================================="
