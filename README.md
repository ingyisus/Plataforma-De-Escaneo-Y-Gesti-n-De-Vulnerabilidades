# Plataforma de Gestión de Vulnerabilidades - Goodyear

Sistema completo de gestión y análisis de vulnerabilidades para la infraestructura de Goodyear Air Springs.

## Características

- **Dashboard Ejecutivo**: Visualización en tiempo real de métricas de seguridad
- **Gestión de Activos**: Administración centralizada de servidores y dispositivos
- **Escaneo de Vulnerabilidades**: Integración con Nmap y Trivy para detección automatizada
- **Reportes Profesionales**: Generación de reportes en PDF (Ejecutivo, Técnico y Cumplimiento)
- **Sistema de Autenticación**: Control de acceso seguro con JWT
- **Arquitectura Moderna**: Frontend React + Backend Flask + PostgreSQL

## Requisitos del Sistema

- Rocky Linux 8 o superior
- Docker y Docker Compose
- 4GB RAM mínimo
- 20GB espacio en disco

## Instalación

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd vuln-platform-goodyear
```

### 2. Configurar permisos

```bash
chmod +x scripts/setup.sh
chmod +x start.sh
```

### 3. Ejecutar instalación

```bash
./scripts/setup.sh
```

Este script realizará:
- Construcción de contenedores Docker
- Configuración de base de datos PostgreSQL
- Inicialización de datos de ejemplo
- Despliegue de frontend y backend
- Configuración de Nginx

### 4. Acceder a la plataforma

Abre tu navegador en: **http://192.168.253.129:8080**

**Credenciales de acceso:**
- Usuario: `admin`
- Contraseña: `goodyear123`

## Arquitectura

```
┌─────────────────┐
│   Frontend      │
│   React + Vite  │ :80
└────────┬────────┘
         │
┌────────▼────────┐
│   Nginx         │ :8080
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌─────────┐
│ Flask  │ │ Postgres│
│ API    │ │   DB    │
│ :5000  │ │  :5432  │
└────┬───┘ └─────────┘
     │
┌────▼────┐
│  Redis  │
└─────────┘
```

## Estructura del Proyecto

```
vuln-platform-goodyear/
├── frontend/               # Aplicación React
│   ├── src/
│   │   ├── components/    # Componentes reutilizables
│   │   ├── pages/         # Páginas principales
│   │   └── App.jsx        # Componente raíz
│   └── package.json
├── backend/               # API Flask
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models.py      # Modelos de base de datos
│   │   ├── routes.py      # Endpoints API
│   │   ├── scanner.py     # Lógica de escaneo
│   │   └── report_generator.py  # Generación de reportes
│   ├── init_db.py         # Inicialización DB
│   └── requirements.txt
├── docker/                # Configuración Docker
│   ├── docker-compose.yml
│   ├── Dockerfile.flask
│   └── Dockerfile.frontend
├── nginx/                 # Configuración Nginx
│   ├── nginx.conf
│   └── frontend.conf
└── scripts/
    └── setup.sh           # Script de instalación
```

## Uso de la Plataforma

### Gestión de Activos

1. Navega a **Activos** en el menú lateral
2. Click en **Agregar Activo**
3. Completa el formulario con:
   - Hostname
   - Dirección IP
   - Sistema Operativo
   - Descripción

### Ejecutar Escaneos

1. Ve a la sección **Escaneos**
2. Click en **Nuevo Escaneo**
3. Selecciona:
   - Activo a escanear
   - Tipo de escaneo (Nmap, Trivy o Completo)
   - Opciones adicionales
4. Click en **Iniciar Escaneo**

### Generar Reportes

1. Accede a **Reportes**
2. Selecciona el tipo de reporte:
   - **Ejecutivo**: Para alta dirección
   - **Técnico**: Detalles técnicos completos
   - **Cumplimiento**: Análisis normativo
3. Click en **Generar Reporte**
4. El PDF se descargará automáticamente

## Comandos Útiles

### Ver logs de todos los servicios

```bash
cd docker
docker-compose logs -f
```

### Ver logs de un servicio específico

```bash
docker-compose logs -f web
docker-compose logs -f frontend
```

### Reiniciar servicios

```bash
docker-compose restart
```

### Detener la plataforma

```bash
docker-compose down
```

### Detener y eliminar volúmenes

```bash
docker-compose down -v
```

### Reiniciar base de datos

```bash
docker-compose down
docker volume rm docker_postgres_data
./scripts/setup.sh
```

## Configuración de Red

La plataforma está configurada para escuchar en la IP **192.168.253.129**:

- **Frontend/Nginx**: Puerto 8080
- **API Backend**: Puerto 5000
- **PostgreSQL**: Puerto 5432 (solo red interna)
- **Redis**: Puerto 6379 (solo red interna)

## Escaneo de Vulnerabilidades

### Nmap

Escanea puertos y servicios expuestos:

```bash
Opciones predeterminadas: -sV -sC
```

### Trivy

Analiza vulnerabilidades conocidas en imágenes y sistemas:

```bash
Compatible con contenedores Docker y sistemas operativos
```

### Escaneo Completo

Combina Nmap + Trivy para análisis exhaustivo

## Seguridad

- ✅ Autenticación JWT con tokens de 24 horas
- ✅ CORS configurado para dominios permitidos
- ✅ Contraseñas hasheadas con Werkzeug
- ✅ Validación de entrada en todos los endpoints
- ✅ Red Docker aislada
- ✅ PostgreSQL no expuesto públicamente

## Resolución de Problemas

### El frontend no carga

```bash
docker-compose logs frontend
docker-compose restart frontend nginx
```

### Error de conexión a base de datos

```bash
docker-compose logs db
docker-compose restart db web
```

### Escaneos fallan

Verifica que el contenedor tenga permisos NET_ADMIN:

```bash
docker-compose down
docker-compose up -d
```

### Puerto 8080 ya en uso

Edita `docker/docker-compose.yml` y cambia el puerto:

```yaml
nginx:
  ports:
    - "192.168.253.129:8081:80"
```

## Mantenimiento

### Backup de Base de Datos

```bash
docker-compose exec db pg_dump -U vulnuser vulndb > backup.sql
```

### Restaurar Base de Datos

```bash
cat backup.sql | docker-compose exec -T db psql -U vulnuser vulndb
```

## Soporte

Para reportar problemas o solicitar características, contacta al equipo de desarrollo.

## Licencia

Propiedad de Goodyear - Todos los derechos reservados
