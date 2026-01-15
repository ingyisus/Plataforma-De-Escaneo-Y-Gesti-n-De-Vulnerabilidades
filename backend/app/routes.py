from flask import Blueprint, jsonify, request
from . import db
from .models import User, Asset, Vulnerability, Scan, Report
from datetime import datetime, timedelta
import jwt
import os
from functools import wraps

main = Blueprint("main", __name__)

SECRET_KEY = os.environ.get('SECRET_KEY', 'goodyear-secure-key')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            token = token.split(' ')[1] if ' ' in token else token
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(*args, **kwargs)
    return decorated

@main.route("/api/health")
def health():
    return jsonify({"status": "OK"})

@main.route("/api/auth/login", methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=1)
        }, SECRET_KEY, algorithm="HS256")
        return jsonify({'token': token, 'username': user.username})

    return jsonify({'message': 'Invalid credentials'}), 401

@main.route("/api/assets", methods=['GET', 'POST'])
@token_required
def assets():
    if request.method == 'GET':
        assets = Asset.query.order_by(Asset.created_at.desc()).all()
        return jsonify([{
            'id': a.id,
            'hostname': a.hostname,
            'ip': a.ip,
            'os': a.os,
            'description': a.description,
            'created_at': a.created_at.isoformat()
        } for a in assets])

    elif request.method == 'POST':
        data = request.get_json()
        asset = Asset(
            hostname=data['hostname'],
            ip=data['ip'],
            os=data.get('os'),
            description=data.get('description')
        )
        db.session.add(asset)
        db.session.commit()
        return jsonify({'id': asset.id, 'message': 'Asset created'}), 201

@main.route("/api/assets/<int:id>", methods=['DELETE'])
@token_required
def delete_asset(id):
    asset = Asset.query.get_or_404(id)
    db.session.delete(asset)
    db.session.commit()
    return jsonify({'message': 'Asset deleted'})

@main.route("/api/vulnerabilities", methods=['GET'])
@token_required
def vulnerabilities():
    vulns = Vulnerability.query.join(Asset).order_by(Vulnerability.created_at.desc()).all()
    return jsonify([{
        'id': v.id,
        'name': v.name,
        'cve': v.cve,
        'severity': v.severity,
        'cvss': v.cvss,
        'description': v.description,
        'asset_hostname': v.asset.hostname if v.asset else None,
        'created_at': v.created_at.isoformat()
    } for v in vulns])

@main.route("/api/scans", methods=['GET', 'POST'])
@token_required
def scans():
    if request.method == 'GET':
        scans = Scan.query.join(Asset).order_by(Scan.created_at.desc()).all()
        return jsonify([{
            'id': s.id,
            'asset_hostname': s.asset.hostname,
            'scan_type': s.scan_type,
            'status': s.status,
            'vulnerabilities_found': s.vulnerabilities_found,
            'created_at': s.created_at.isoformat()
        } for s in scans])

    elif request.method == 'POST':
        data = request.get_json()
        scan = Scan(
            asset_id=data['asset_id'],
            scan_type=data['scan_type'],
            options=data.get('options'),
            status='pending'
        )
        db.session.add(scan)
        db.session.commit()
        return jsonify({'id': scan.id, 'message': 'Scan created'}), 201

@main.route("/api/dashboard/stats", methods=['GET'])
@token_required
def dashboard_stats():
    total_assets = Asset.query.count()
    total_vulns = Vulnerability.query.count()

    critical = Vulnerability.query.filter_by(severity='critical').count()
    high = Vulnerability.query.filter_by(severity='high').count()
    medium = Vulnerability.query.filter_by(severity='medium').count()
    low = Vulnerability.query.filter_by(severity='low').count()

    recent_scans = Scan.query.join(Asset).order_by(Scan.created_at.desc()).limit(5).all()

    return jsonify({
        'total_assets': total_assets,
        'total_vulnerabilities': total_vulns,
        'critical_vulns': critical,
        'high_vulns': high,
        'medium_vulns': medium,
        'low_vulns': low,
        'recent_scans': [{
            'target': s.asset.hostname,
            'status': s.status,
            'created_at': s.created_at.isoformat()
        } for s in recent_scans]
    })

@main.route("/api/reports", methods=['GET'])
@token_required
def reports():
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return jsonify([{
        'id': r.id,
        'name': r.name,
        'report_type': r.report_type,
        'created_at': r.created_at.isoformat()
    } for r in reports])

@main.route("/api/reports/generate", methods=['POST'])
@token_required
def generate_report():
    from flask import send_file
    from .report_generator import ReportGenerator

    data = request.get_json()
    report_type = data.get('report_type', 'executive')

    if report_type == 'executive':
        buffer = ReportGenerator.generate_executive_report()
        filename = f'reporte_ejecutivo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    elif report_type == 'technical':
        buffer = ReportGenerator.generate_technical_report()
        filename = f'reporte_tecnico_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    elif report_type == 'compliance':
        buffer = ReportGenerator.generate_compliance_report()
        filename = f'reporte_cumplimiento_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    else:
        return jsonify({'message': 'Invalid report type'}), 400

    report = Report(
        name=filename,
        report_type=report_type,
        file_path=f'/reports/{filename}'
    )
    db.session.add(report)
    db.session.commit()

    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

@main.route("/api/devices", methods=['GET', 'POST'])
@token_required
def devices():
    if request.method == 'GET':
        devices = Device.query.order_by(Device.created_at.desc()).all()
        return jsonify([{
            'id': d.id,
            'name': d.name,
            'ip': d.ip,
            'device_type': d.device_type,
            'manufacturer': d.manufacturer,
            'model': d.model,
            'firmware_version': d.firmware_version,
            'location': d.location,
            'status': d.status,
            'last_scan': d.last_scan.isoformat() if d.last_scan else None,
            'created_at': d.created_at.isoformat()
        } for d in devices])

    elif request.method == 'POST':
        data = request.get_json()
        device = Device(
            name=data['name'],
            ip=data['ip'],
            device_type=data['device_type'],
            manufacturer=data.get('manufacturer'),
            model=data.get('model'),
            serial_number=data.get('serial_number'),
            firmware_version=data.get('firmware_version'),
            location=data.get('location'),
            description=data.get('description')
        )
        db.session.add(device)
        db.session.commit()
        return jsonify({'id': device.id, 'message': 'Device created'}), 201

@main.route("/api/devices/<int:id>", methods=['GET', 'PUT', 'DELETE'])
@token_required
def device_detail(id):
    device = Device.query.get_or_404(id)

    if request.method == 'GET':
        return jsonify({
            'id': device.id,
            'name': device.name,
            'ip': device.ip,
            'device_type': device.device_type,
            'manufacturer': device.manufacturer,
            'model': device.model,
            'serial_number': device.serial_number,
            'firmware_version': device.firmware_version,
            'location': device.location,
            'status': device.status,
            'description': device.description,
            'last_scan': device.last_scan.isoformat() if device.last_scan else None,
            'created_at': device.created_at.isoformat()
        })

    elif request.method == 'PUT':
        data = request.get_json()
        device.name = data.get('name', device.name)
        device.device_type = data.get('device_type', device.device_type)
        device.manufacturer = data.get('manufacturer', device.manufacturer)
        device.model = data.get('model', device.model)
        device.firmware_version = data.get('firmware_version', device.firmware_version)
        device.location = data.get('location', device.location)
        device.status = data.get('status', device.status)
        device.description = data.get('description', device.description)
        db.session.commit()
        return jsonify({'message': 'Device updated'})

    elif request.method == 'DELETE':
        db.session.delete(device)
        db.session.commit()
        return jsonify({'message': 'Device deleted'})

@main.route("/api/device-scans", methods=['GET', 'POST'])
@token_required
def device_scans():
    if request.method == 'GET':
        scans = DeviceScan.query.join(Device).order_by(DeviceScan.created_at.desc()).all()
        return jsonify([{
            'id': s.id,
            'device_name': s.device.name,
            'device_id': s.device_id,
            'scan_type': s.scan_type,
            'status': s.status,
            'issues_found': s.issues_found,
            'response_time': s.response_time,
            'cpu_usage': s.cpu_usage,
            'memory_usage': s.memory_usage,
            'created_at': s.created_at.isoformat()
        } for s in scans])

    elif request.method == 'POST':
        from .advanced_scanner import AdvancedScanner
        data = request.get_json()
        scan = DeviceScan(
            device_id=data['device_id'],
            scan_type=data['scan_type'],
            status='pending'
        )
        db.session.add(scan)
        db.session.commit()

        AdvancedScanner.execute_device_scan(scan.id)

        return jsonify({'id': scan.id, 'message': 'Device scan created'}), 201

@main.route("/api/device-issues", methods=['GET'])
@token_required
def device_issues():
    issues = DeviceIssue.query.join(Device).order_by(DeviceIssue.created_at.desc()).all()
    return jsonify([{
        'id': i.id,
        'device_name': i.device.name,
        'device_id': i.device_id,
        'issue_type': i.issue_type,
        'severity': i.severity,
        'description': i.description,
        'recommendation': i.recommendation,
        'status': i.status,
        'created_at': i.created_at.isoformat()
    } for i in issues])

@main.route("/api/maintenance", methods=['GET', 'POST'])
@token_required
def maintenance():
    from .maintenance_manager import MaintenanceManager

    if request.method == 'GET':
        records = MaintenanceRecord.query.order_by(MaintenanceRecord.scheduled_date).all()
        return jsonify([{
            'id': r.id,
            'device_name': r.device.name,
            'device_id': r.device_id,
            'maintenance_type': r.maintenance_type,
            'status': r.status,
            'scheduled_date': r.scheduled_date.isoformat(),
            'completed_date': r.completed_date.isoformat() if r.completed_date else None,
            'technician': r.technician,
            'cost': r.cost,
            'downtime_minutes': r.downtime_minutes,
            'created_at': r.created_at.isoformat()
        } for r in records])

    elif request.method == 'POST':
        data = request.get_json()
        maintenance_record = MaintenanceManager.schedule_maintenance(
            device_id=data['device_id'],
            maintenance_type=data['maintenance_type'],
            scheduled_date=datetime.fromisoformat(data['scheduled_date']),
            description=data.get('description'),
            technician=data.get('technician'),
            created_by=request.headers.get('X-User-ID')
        )
        return jsonify({'id': maintenance_record.id, 'message': 'Maintenance scheduled'}), 201

@main.route("/api/maintenance/<int:id>", methods=['PUT'])
@token_required
def update_maintenance(id):
    from .maintenance_manager import MaintenanceManager
    data = request.get_json()
    maintenance_record = MaintenanceManager.complete_maintenance(
        maintenance_id=id,
        notes=data.get('notes'),
        downtime_minutes=data.get('downtime_minutes', 0),
        cost=data.get('cost', 0)
    )
    return jsonify({'message': 'Maintenance updated'})

@main.route("/api/maintenance/statistics", methods=['GET'])
@token_required
def maintenance_statistics():
    from .maintenance_manager import MaintenanceManager
    device_id = request.args.get('device_id')
    stats = MaintenanceManager.get_maintenance_statistics(device_id=device_id)
    return jsonify(stats)

@main.route("/api/maintenance/scheduled", methods=['GET'])
@token_required
def scheduled_maintenance():
    from .maintenance_manager import MaintenanceManager
    days = request.args.get('days', 30, type=int)
    records = MaintenanceManager.get_scheduled_maintenance(days_ahead=days)
    return jsonify([{
        'id': r.id,
        'device_name': r.device.name,
        'maintenance_type': r.maintenance_type,
        'scheduled_date': r.scheduled_date.isoformat(),
        'technician': r.technician
    } for r in records])

@main.route("/api/scan-templates", methods=['GET', 'POST'])
@token_required
def scan_templates():
    if request.method == 'GET':
        templates = ScanTemplate.query.all()
        return jsonify([{
            'id': t.id,
            'name': t.name,
            'scan_type': t.scan_type,
            'description': t.description,
            'frequency_days': t.frequency_days,
            'enabled': t.enabled
        } for t in templates])

    elif request.method == 'POST':
        from .maintenance_manager import MaintenanceManager
        data = request.get_json()
        template = MaintenanceManager.create_scan_template(
            name=data['name'],
            scan_type=data['scan_type'],
            description=data.get('description'),
            parameters=data.get('parameters'),
            frequency_days=data.get('frequency_days', 7)
        )
        return jsonify({'id': template.id, 'message': 'Template created'}), 201

@main.route("/api/device/<int:device_id>/health", methods=['GET'])
@token_required
def device_health(device_id):
    from .maintenance_manager import MaintenanceManager
    health_score = MaintenanceManager.get_device_health(device_id)
    return jsonify({'device_id': device_id, 'health_score': health_score})
