#!/bin/bash

echo "==================================="
echo "Estado de la Plataforma Goodyear"
echo "==================================="
echo ""

cd "$(dirname "$0")/../docker"

echo "Servicios Docker:"
echo "---------------------------------"
docker-compose ps
echo ""

echo "Uso de recursos:"
echo "---------------------------------"
docker stats --no-stream
echo ""

echo "Estado de la base de datos:"
echo "---------------------------------"
docker-compose exec -T db psql -U vulnuser vulndb -c "SELECT
    (SELECT COUNT(*) FROM asset) as activos,
    (SELECT COUNT(*) FROM vulnerability) as vulnerabilidades,
    (SELECT COUNT(*) FROM scan) as escaneos,
    (SELECT COUNT(*) FROM vulnerability WHERE severity='critical') as criticas;"
echo ""

echo "==================================="
echo "Para acceder: http://192.168.253.129:8080"
echo "==================================="
