#!/bin/bash

echo "==================================="
echo "Goodyear - Plataforma de Gestión de Vulnerabilidades"
echo "==================================="
echo ""

cd "$(dirname "$0")/.."

echo "1. Construyendo contenedores Docker..."
cd docker
docker-compose build

echo ""
echo "2. Iniciando servicios..."
docker-compose up -d db redis

echo ""
echo "3. Esperando a que PostgreSQL esté listo..."
sleep 10

echo ""
echo "4. Iniciando servicio web..."
docker-compose up -d web

echo ""
echo "5. Inicializando base de datos..."
sleep 5
docker-compose exec web python init_db.py

echo ""
echo "6. Iniciando frontend y nginx..."
docker-compose up -d frontend nginx

echo ""
echo "==================================="
echo "¡Instalación completada!"
echo "==================================="
echo ""
echo "Accede a la plataforma en: http://192.168.253.129:8080"
echo ""
echo "Credenciales de acceso:"
echo "  Usuario: admin"
echo "  Contraseña: goodyear123"
echo ""
echo "Para ver los logs: docker-compose logs -f"
echo "Para detener: docker-compose down"
echo "==================================="
