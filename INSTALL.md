# Guía de Instalación Rápida - Plataforma Goodyear

## Prerrequisitos

Asegúrate de tener instalado en tu sistema Rocky Linux:

1. Docker
2. Docker Compose
3. Git

## Instalación en Rocky Linux

### Paso 1: Instalar Docker

```bash
sudo dnf install -y docker docker-compose
sudo systemctl start docker
sudo systemctl enable docker
```

### Paso 2: Clonar el proyecto

```bash
cd /opt
sudo git clone <repository-url> vuln-platform-goodyear
cd vuln-platform-goodyear
```

### Paso 3: Configurar permisos

```bash
sudo chmod +x scripts/setup.sh start.sh
```

### Paso 4: Ejecutar instalación

```bash
sudo ./scripts/setup.sh
```

Este proceso tomará varios minutos mientras:
- Descarga las imágenes de Docker
- Construye los contenedores
- Configura la base de datos
- Inicializa los datos de ejemplo

### Paso 5: Verificar instalación

```bash
cd docker
sudo docker-compose ps
```

Deberías ver todos los servicios en estado "Up":
- frontend
- web
- db
- redis
- nginx

### Paso 6: Acceder a la plataforma

Abre tu navegador en: **http://192.168.253.129:8080**

Credenciales:
- Usuario: `admin`
- Contraseña: `goodyear123`

## Instalación con Ansible

Si prefieres usar Ansible:

```bash
cd ansible
ansible-playbook -i inventory/hosts.ini playbooks/deploy.yml
```

## Configurar Firewall

Si tienes firewalld activo:

```bash
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

## Verificar Logs

```bash
cd docker
sudo docker-compose logs -f
```

Para ver logs de un servicio específico:

```bash
sudo docker-compose logs -f web
sudo docker-compose logs -f frontend
```

## Solución de Problemas

### Error: Puerto 8080 ya en uso

```bash
sudo netstat -tulpn | grep 8080
# Detén el proceso que usa el puerto o cambia el puerto en docker-compose.yml
```

### Error: No se puede conectar a Docker

```bash
sudo systemctl status docker
sudo systemctl start docker
sudo usermod -aG docker $USER
# Luego cierra sesión y vuelve a iniciar
```

### Error: Contenedor web no inicia

```bash
cd docker
sudo docker-compose logs web
sudo docker-compose restart web
```

### Reinstalar desde cero

```bash
cd docker
sudo docker-compose down -v
sudo docker volume prune -f
cd ..
sudo ./scripts/setup.sh
```

## Comandos Útiles

### Detener todos los servicios
```bash
cd docker
sudo docker-compose down
```

### Reiniciar servicios
```bash
cd docker
sudo docker-compose restart
```

### Backup de base de datos
```bash
cd docker
sudo docker-compose exec db pg_dump -U vulnuser vulndb > backup_$(date +%Y%m%d).sql
```

### Restaurar base de datos
```bash
cd docker
cat backup_20240101.sql | sudo docker-compose exec -T db psql -U vulnuser vulndb
```

### Ver uso de recursos
```bash
sudo docker stats
```

### Actualizar la aplicación
```bash
cd /opt/vuln-platform-goodyear
sudo git pull
cd docker
sudo docker-compose down
sudo docker-compose build
sudo docker-compose up -d
```

## Configuración de Producción

Para un entorno de producción, considera:

1. **Cambiar contraseñas**:
   - Edita `docker/docker-compose.yml`
   - Cambia las credenciales de PostgreSQL
   - Actualiza `SECRET_KEY` en variables de entorno

2. **Configurar HTTPS**:
   - Obtén certificados SSL
   - Configura Nginx para HTTPS
   - Redirige HTTP a HTTPS

3. **Configurar backups automáticos**:
   - Crea un cron job para backups diarios
   - Almacena backups en ubicación segura

4. **Monitoreo**:
   - Configura alertas de sistema
   - Monitorea uso de recursos
   - Revisa logs regularmente

## Soporte

Para más información, consulta el README.md principal o contacta al equipo de desarrollo.
