#!/bin/bash

cd docker
docker-compose up -d

echo ""
echo "==================================="
echo "Plataforma Goodyear iniciada"
echo "==================================="
echo ""
echo "Accede en: http://192.168.253.129:8080"
echo ""
echo "Usuario: admin"
echo "Contraseña: goodyear123"
echo ""
echo "Para ver logs: cd docker && docker-compose logs -f"
echo "==================================="
