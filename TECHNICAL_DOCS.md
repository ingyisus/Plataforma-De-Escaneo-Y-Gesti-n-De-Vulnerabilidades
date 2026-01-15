# Documentación Técnica - Plataforma Goodyear

## Arquitectura del Sistema

### Stack Tecnológico

**Frontend:**
- React 18.3
- Vite 5.1 (Build tool)
- React Router 6.22 (Routing)
- Recharts 2.12 (Gráficos)
- Lucide React (Iconos)

**Backend:**
- Python 3.11
- Flask 3.x (Framework web)
- SQLAlchemy (ORM)
- PostgreSQL 15 (Base de datos)
- Redis 7 (Cache)
- JWT (Autenticación)
- ReportLab (Generación de PDFs)

**Infraestructura:**
- Docker & Docker Compose
- Nginx (Reverse proxy)
- Nmap (Escaneo de puertos)
- Trivy (Escaneo de vulnerabilidades)

## Estructura de Base de Datos

### Tabla: users
```sql
- id (INTEGER, PK)
- username (VARCHAR(80), UNIQUE)
- password_hash (VARCHAR(255))
- email (VARCHAR(120))
- created_at (TIMESTAMP)
```

### Tabla: asset
```sql
- id (INTEGER, PK)
- hostname (VARCHAR(100))
- ip (VARCHAR(50))
- os (VARCHAR(100))
- description (TEXT)
- created_at (TIMESTAMP)
```

### Tabla: vulnerability
```sql
- id (INTEGER, PK)
- name (VARCHAR(200))
- cve (VARCHAR(50))
- severity (VARCHAR(20))
- cvss (FLOAT)
- description (TEXT)
- asset_id (INTEGER, FK -> asset.id)
- scan_id (INTEGER, FK -> scan.id)
- created_at (TIMESTAMP)
```

### Tabla: scan
```sql
- id (INTEGER, PK)
- asset_id (INTEGER, FK -> asset.id)
- scan_type (VARCHAR(50))
- status (VARCHAR(20))
- options (VARCHAR(200))
- result (TEXT)
- vulnerabilities_found (INTEGER)
- created_at (TIMESTAMP)
- completed_at (TIMESTAMP)
```

### Tabla: report
```sql
- id (INTEGER, PK)
- name (VARCHAR(200))
- report_type (VARCHAR(50))
- file_path (VARCHAR(500))
- created_at (TIMESTAMP)
```

## API Endpoints

### Autenticación

**POST /api/auth/login**
```json
Request:
{
  "username": "admin",
  "password": "goodyear123"
}

Response:
{
  "token": "jwt_token_here",
  "username": "admin"
}
```

### Activos

**GET /api/assets**
- Headers: Authorization: Bearer {token}
- Response: Array de activos

**POST /api/assets**
```json
Request:
{
  "hostname": "server-01",
  "ip": "192.168.1.10",
  "os": "Ubuntu 22.04",
  "description": "Servidor web"
}
```

**DELETE /api/assets/{id}**
- Headers: Authorization: Bearer {token}

### Vulnerabilidades

**GET /api/vulnerabilities**
- Headers: Authorization: Bearer {token}
- Response: Array de vulnerabilidades con información del activo

### Escaneos

**GET /api/scans**
- Headers: Authorization: Bearer {token}

**POST /api/scans**
```json
Request:
{
  "asset_id": 1,
  "scan_type": "nmap",
  "options": "-sV -sC"
}
```

### Dashboard

**GET /api/dashboard/stats**
- Headers: Authorization: Bearer {token}
- Response: Estadísticas generales del sistema

### Reportes

**GET /api/reports**
- Headers: Authorization: Bearer {token}

**POST /api/reports/generate**
```json
Request:
{
  "report_type": "executive"
}

Response: PDF file download
```

## Módulos del Sistema

### Scanner (backend/app/scanner.py)

Gestiona el escaneo de vulnerabilidades:

**Métodos principales:**
- `run_nmap_scan(asset, options)`: Ejecuta escaneo Nmap
- `parse_nmap_results(result, asset_id, scan_id)`: Procesa resultados Nmap
- `run_trivy_scan(asset)`: Ejecuta escaneo Trivy
- `parse_trivy_results(result, asset_id, scan_id)`: Procesa resultados Trivy
- `execute_scan(scan_id)`: Ejecuta escaneo completo

### Report Generator (backend/app/report_generator.py)

Genera reportes en PDF:

**Métodos principales:**
- `generate_executive_report()`: Reporte ejecutivo
- `generate_technical_report()`: Reporte técnico detallado
- `generate_compliance_report()`: Reporte de cumplimiento normativo

## Configuración de Red

### Puertos Expuestos

- **80**: Frontend (solo internamente)
- **5000**: API Backend (192.168.253.129:5000)
- **8080**: Nginx (192.168.253.129:8080) - Punto de entrada principal
- **5432**: PostgreSQL (solo red Docker)
- **6379**: Redis (solo red Docker)

### Red Docker

Network: `goodyear-net` (bridge)

Servicios en la red:
- frontend
- web (backend)
- db (PostgreSQL)
- redis
- nginx

## Seguridad

### Autenticación
- JWT tokens con expiración de 24 horas
- Contraseñas hasheadas con Werkzeug (pbkdf2:sha256)
- Middleware de verificación de token en todas las rutas protegidas

### CORS
- Configurado para permitir requests desde el frontend
- Headers personalizados permitidos

### Base de Datos
- Credenciales configurables vía variables de entorno
- PostgreSQL no expuesto externamente
- Backups automáticos recomendados

### Docker
- Red aislada para servicios internos
- Capacidades NET_ADMIN y NET_RAW solo para escaneo
- Volúmenes persistentes para datos

## Variables de Entorno

```bash
SECRET_KEY=goodyear-secure-key-2024
DATABASE_URL=postgresql://vulnuser:vulnpass@db:5432/vulndb
REDIS_HOST=redis
REDIS_PORT=6379
SERVER_IP=192.168.253.129
```

## Flujo de Datos

### Escaneo de Vulnerabilidades

1. Usuario crea nuevo escaneo desde frontend
2. POST /api/scans crea registro con status='pending'
3. Scanner.execute_scan() se ejecuta:
   - Cambia status a 'running'
   - Ejecuta Nmap/Trivy según tipo
   - Parsea resultados
   - Crea registros de vulnerabilidades
   - Cambia status a 'completed'
4. Frontend muestra resultados actualizados

### Generación de Reportes

1. Usuario solicita reporte desde frontend
2. POST /api/reports/generate con tipo de reporte
3. ReportGenerator consulta base de datos
4. Genera PDF con ReportLab
5. Crea registro en tabla report
6. Envía PDF como respuesta
7. Frontend descarga archivo

## Monitoreo y Logs

### Ver logs de servicios

```bash
# Todos los servicios
docker-compose logs -f

# Servicio específico
docker-compose logs -f web
docker-compose logs -f db

# Últimas 100 líneas
docker-compose logs --tail=100 web
```

### Métricas del sistema

```bash
# Uso de recursos por contenedor
docker stats

# Estado de servicios
docker-compose ps

# Health check
curl http://192.168.253.129:5000/api/health
```

## Desarrollo Local

### Configurar entorno de desarrollo

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
npm run dev
```

### Estructura de archivos de desarrollo

```
frontend/src/
├── components/      # Componentes reutilizables
│   └── Layout.jsx
├── pages/          # Páginas principales
│   ├── Dashboard.jsx
│   ├── Assets.jsx
│   ├── Vulnerabilities.jsx
│   ├── Scans.jsx
│   └── Reports.jsx
├── App.jsx         # Router principal
└── main.jsx        # Entry point

backend/app/
├── __init__.py     # Factory de aplicación
├── models.py       # Modelos SQLAlchemy
├── routes.py       # Endpoints API
├── scanner.py      # Lógica de escaneo
└── report_generator.py  # Generación de reportes
```

## Testing

### Test de API

```bash
# Health check
curl http://192.168.253.129:5000/api/health

# Login
curl -X POST http://192.168.253.129:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"goodyear123"}'

# Obtener activos (con token)
curl http://192.168.253.129:5000/api/assets \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Performance

### Optimizaciones implementadas

- Índices en tablas de base de datos
- Queries optimizadas con joins
- Compresión gzip en Nginx
- Cache de archivos estáticos
- Lazy loading de componentes React

### Recomendaciones de producción

- Configurar Redis para cache de API
- Implementar rate limiting
- Usar CDN para assets estáticos
- Configurar auto-scaling de contenedores
- Implementar health checks automáticos

## Mantenimiento

### Tareas periódicas recomendadas

**Diario:**
- Verificar estado de servicios
- Revisar logs de errores

**Semanal:**
- Backup de base de datos
- Verificar uso de disco
- Revisar vulnerabilidades nuevas

**Mensual:**
- Actualizar dependencias
- Revisar y limpiar logs antiguos
- Auditoría de seguridad

## Troubleshooting

### Problema: Frontend no carga

```bash
# Verificar logs
docker-compose logs frontend

# Reconstruir contenedor
docker-compose build frontend
docker-compose up -d frontend
```

### Problema: API no responde

```bash
# Verificar estado
docker-compose ps web

# Reiniciar servicio
docker-compose restart web

# Ver logs detallados
docker-compose logs --tail=50 web
```

### Problema: Base de datos no accesible

```bash
# Verificar PostgreSQL
docker-compose exec db psql -U vulnuser vulndb -c "\dt"

# Verificar conexión
docker-compose exec web python -c "from app import db; print(db.engine.url)"
```

## Contribución al Código

### Estándares de código

**Python:**
- PEP 8 style guide
- Docstrings para funciones públicas
- Type hints cuando sea posible

**JavaScript/React:**
- ESLint configurado
- Componentes funcionales con hooks
- Props validation con PropTypes

### Workflow de desarrollo

1. Crear branch feature/nombre
2. Desarrollar y testear localmente
3. Commit con mensajes descriptivos
4. Push y crear Pull Request
5. Code review
6. Merge a main

## Licencia y Soporte

Este software es propiedad de Goodyear. Para soporte técnico, contactar al equipo de desarrollo interno.
