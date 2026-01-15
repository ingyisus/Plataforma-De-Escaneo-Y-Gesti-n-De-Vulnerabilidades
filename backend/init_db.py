from app import create_app, db
from app.models import (User, Asset, Vulnerability, Scan, Device, DeviceScan,
                       DeviceIssue, MaintenanceRecord, ScanTemplate, ScheduledScan)
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    print("Creando tablas...")
    db.create_all()

    print("Verificando usuario admin...")
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        print("Creando usuario admin...")
        admin = User(username='admin', email='admin@goodyear.com')
        admin.set_password('goodyear123')
        db.session.add(admin)
        db.session.commit()
        print("Usuario admin creado: admin / goodyear123")
    else:
        print("Usuario admin ya existe")

    if Asset.query.count() == 0:
        print("Creando activos de ejemplo...")
        assets_data = [
            {
                'hostname': 'web-server-01',
                'ip': '192.168.253.10',
                'os': 'Ubuntu 22.04 LTS',
                'description': 'Servidor web principal de producción'
            },
            {
                'hostname': 'db-server-01',
                'ip': '192.168.253.20',
                'os': 'Rocky Linux 8',
                'description': 'Servidor de base de datos PostgreSQL'
            },
            {
                'hostname': 'app-server-01',
                'ip': '192.168.253.30',
                'os': 'CentOS 7',
                'description': 'Servidor de aplicaciones'
            },
            {
                'hostname': 'backup-server',
                'ip': '192.168.253.40',
                'os': 'Ubuntu 20.04 LTS',
                'description': 'Servidor de respaldos'
            }
        ]

        assets = []
        for asset_data in assets_data:
            asset = Asset(**asset_data)
            db.session.add(asset)
            assets.append(asset)

        db.session.commit()
        print(f"{len(assets)} activos creados")

        print("Creando vulnerabilidades de ejemplo...")
        vulnerabilities_data = [
            {
                'name': 'OpenSSH Version Disclosure',
                'cve': 'CVE-2023-38408',
                'severity': 'medium',
                'cvss': 5.3,
                'description': 'La versión de OpenSSH permite la divulgación de información del sistema',
                'asset_id': assets[0].id
            },
            {
                'name': 'Apache HTTP Server DoS Vulnerability',
                'cve': 'CVE-2023-25690',
                'severity': 'high',
                'cvss': 7.5,
                'description': 'Vulnerabilidad de denegación de servicio en Apache HTTP Server',
                'asset_id': assets[0].id
            },
            {
                'name': 'PostgreSQL Privilege Escalation',
                'cve': 'CVE-2023-5869',
                'severity': 'critical',
                'cvss': 9.8,
                'description': 'Escalada de privilegios en PostgreSQL permite ejecución de código arbitrario',
                'asset_id': assets[1].id
            },
            {
                'name': 'Linux Kernel Use-After-Free',
                'cve': 'CVE-2023-52340',
                'severity': 'high',
                'cvss': 7.8,
                'description': 'Vulnerabilidad use-after-free en el kernel de Linux',
                'asset_id': assets[1].id
            },
            {
                'name': 'Sudo Privilege Escalation',
                'cve': 'CVE-2023-42465',
                'severity': 'critical',
                'cvss': 9.1,
                'description': 'Escalada de privilegios en sudo permite obtener acceso root',
                'asset_id': assets[2].id
            },
            {
                'name': 'OpenSSL Denial of Service',
                'cve': 'CVE-2023-6129',
                'severity': 'medium',
                'cvss': 5.9,
                'description': 'Vulnerabilidad de denegación de servicio en OpenSSL',
                'asset_id': assets[2].id
            },
            {
                'name': 'rsync Path Traversal',
                'cve': 'CVE-2022-37434',
                'severity': 'high',
                'cvss': 8.1,
                'description': 'Vulnerabilidad de path traversal en rsync',
                'asset_id': assets[3].id
            },
            {
                'name': 'Weak SSH Configuration',
                'cve': 'CUSTOM-001',
                'severity': 'low',
                'cvss': 3.7,
                'description': 'Configuración débil de SSH permite algoritmos de cifrado obsoletos',
                'asset_id': assets[3].id
            }
        ]

        for vuln_data in vulnerabilities_data:
            vuln = Vulnerability(**vuln_data)
            db.session.add(vuln)

        db.session.commit()
        print(f"{len(vulnerabilities_data)} vulnerabilidades creadas")

        print("Creando escaneos de ejemplo...")
        scans_data = [
            {
                'asset_id': assets[0].id,
                'scan_type': 'nmap',
                'status': 'completed',
                'vulnerabilities_found': 2,
                'completed_at': datetime.utcnow()
            },
            {
                'asset_id': assets[1].id,
                'scan_type': 'full',
                'status': 'completed',
                'vulnerabilities_found': 2,
                'completed_at': datetime.utcnow()
            },
            {
                'asset_id': assets[2].id,
                'scan_type': 'trivy',
                'status': 'completed',
                'vulnerabilities_found': 2,
                'completed_at': datetime.utcnow()
            }
        ]

        for scan_data in scans_data:
            scan = Scan(**scan_data)
            db.session.add(scan)

        db.session.commit()
        print(f"{len(scans_data)} escaneos creados")

    if Device.query.count() == 0:
        print("Creando dispositivos de infraestructura...")
        devices_data = [
            {
                'name': 'switch-core-01',
                'ip': '192.168.253.50',
                'device_type': 'switch',
                'manufacturer': 'Cisco',
                'model': 'Catalyst 9300',
                'firmware_version': '17.3.4',
                'location': 'Data Center Principal',
                'description': 'Switch core de la red principal'
            },
            {
                'name': 'firewall-01',
                'ip': '192.168.253.51',
                'device_type': 'firewall',
                'manufacturer': 'Fortinet',
                'model': 'FortiGate 3100D',
                'firmware_version': '7.2.1',
                'location': 'Data Center Principal',
                'description': 'Firewall de perimetro'
            },
            {
                'name': 'router-edge-01',
                'ip': '192.168.253.52',
                'device_type': 'router',
                'manufacturer': 'Juniper',
                'model': 'MX480',
                'firmware_version': '21.2R2',
                'location': 'Data Center Principal',
                'description': 'Router de borde'
            },
            {
                'name': 'load-balancer-01',
                'ip': '192.168.253.53',
                'device_type': 'load_balancer',
                'manufacturer': 'F5',
                'model': 'BIG-IP 5000',
                'firmware_version': '16.1.0',
                'location': 'Data Center Principal',
                'description': 'Load balancer principal'
            },
            {
                'name': 'nas-storage-01',
                'ip': '192.168.253.54',
                'device_type': 'nas',
                'manufacturer': 'NetApp',
                'model': 'FAS2820',
                'firmware_version': '9.10.1',
                'location': 'Data Center Principal',
                'description': 'Storage NAS para backups'
            },
            {
                'name': 'ups-primary',
                'ip': '192.168.253.55',
                'device_type': 'ups',
                'manufacturer': 'Eaton',
                'model': '9PXEBM300',
                'firmware_version': '3.12.2',
                'location': 'Data Center Principal',
                'description': 'UPS sistema de potencia ininterrumpible'
            }
        ]

        devices = []
        for device_data in devices_data:
            device = Device(**device_data)
            db.session.add(device)
            devices.append(device)

        db.session.commit()
        print(f"{len(devices)} dispositivos creados")

        print("Creando plantillas de escaneo...")
        templates_data = [
            {
                'name': 'SSL/TLS Weekly',
                'scan_type': 'ssl_tls',
                'description': 'Escaneo semanal de SSL/TLS',
                'frequency_days': 7
            },
            {
                'name': 'HTTP Security Daily',
                'scan_type': 'http_security',
                'description': 'Verificación diaria de headers HTTP',
                'frequency_days': 1
            },
            {
                'name': 'Network Health Weekly',
                'scan_type': 'network_device',
                'description': 'Escaneo semanal de salud de red',
                'frequency_days': 7
            },
            {
                'name': 'Database Monthly',
                'scan_type': 'database',
                'description': 'Escaneo mensual de bases de datos',
                'frequency_days': 30
            },
            {
                'name': 'Full Security Monthly',
                'scan_type': 'full',
                'description': 'Escaneo completo mensual',
                'frequency_days': 30
            }
        ]

        for template_data in templates_data:
            template = ScanTemplate(**template_data)
            db.session.add(template)

        db.session.commit()
        print(f"{len(templates_data)} plantillas de escaneo creadas")

        print("Creando registros de mantenimiento...")
        maintenance_data = [
            {
                'device_id': devices[0].id,
                'maintenance_type': 'preventive',
                'scheduled_date': datetime.utcnow() + timedelta(days=7),
                'description': 'Mantenimiento preventivo trimestral del switch',
                'technician': 'Juan García',
                'created_by': 'admin'
            },
            {
                'device_id': devices[1].id,
                'maintenance_type': 'security_patch',
                'scheduled_date': datetime.utcnow() + timedelta(days=3),
                'description': 'Parche de seguridad crítica',
                'technician': 'María López',
                'created_by': 'admin'
            },
            {
                'device_id': devices[2].id,
                'maintenance_type': 'firmware_update',
                'scheduled_date': datetime.utcnow() + timedelta(days=14),
                'description': 'Actualización de firmware de router',
                'technician': 'Carlos Rodríguez',
                'created_by': 'admin'
            },
            {
                'device_id': devices[4].id,
                'maintenance_type': 'inspection',
                'scheduled_date': datetime.utcnow() + timedelta(days=21),
                'description': 'Inspección general del NAS',
                'technician': 'Ana Martínez',
                'created_by': 'admin'
            }
        ]

        for maint_data in maintenance_data:
            maintenance = MaintenanceRecord(**maint_data)
            db.session.add(maintenance)

        db.session.commit()
        print(f"{len(maintenance_data)} registros de mantenimiento creados")

    print("\nBase de datos inicializada correctamente!")
    print("\nCredenciales de acceso:")
    print("  Usuario: admin")
    print("  Contraseña: goodyear123")
    print(f"\nAccede a la plataforma en: http://192.168.253.129:8080")
    print("\nNuevas funcionalidades:")
    print("  - Gestión de dispositivos (switches, routers, firewalls)")
    print("  - Escaneo avanzado (SSL/TLS, HTTP, DNS, SMTP)")
    print("  - Sistema de mantenimiento y programación")
    print("  - Análisis de salud de dispositivos")
