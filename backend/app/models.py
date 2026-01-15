from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100), nullable=False)
    ip = db.Column(db.String(50), nullable=False)
    os = db.Column(db.String(100))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scans = db.relationship('Scan', backref='asset', lazy=True, cascade='all, delete-orphan')

class Vulnerability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    cve = db.Column(db.String(50))
    severity = db.Column(db.String(20))
    cvss = db.Column(db.Float)
    description = db.Column(db.Text)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'))
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Scan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    scan_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='pending')
    options = db.Column(db.String(200))
    result = db.Column(db.Text)
    vulnerabilities_found = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    vulnerabilities = db.relationship('Vulnerability', backref='scan', lazy=True)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    report_type = db.Column(db.String(50))
    file_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ip = db.Column(db.String(50), nullable=False)
    device_type = db.Column(db.String(50), nullable=False)
    manufacturer = db.Column(db.String(100))
    model = db.Column(db.String(100))
    serial_number = db.Column(db.String(100))
    firmware_version = db.Column(db.String(100))
    location = db.Column(db.String(200))
    status = db.Column(db.String(20), default='active')
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_scan = db.Column(db.DateTime)
    device_scans = db.relationship('DeviceScan', backref='device', lazy=True, cascade='all, delete-orphan')
    maintenance_records = db.relationship('MaintenanceRecord', backref='device', lazy=True, cascade='all, delete-orphan')

class DeviceScan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    scan_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='pending')
    result = db.Column(db.Text)
    issues_found = db.Column(db.Integer, default=0)
    response_time = db.Column(db.Float)
    cpu_usage = db.Column(db.Float)
    memory_usage = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    device_issues = db.relationship('DeviceIssue', backref='device_scan', lazy=True, cascade='all, delete-orphan')

class DeviceIssue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_scan_id = db.Column(db.Integer, db.ForeignKey('device_scan.id'), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    issue_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20))
    description = db.Column(db.Text)
    recommendation = db.Column(db.Text)
    status = db.Column(db.String(20), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MaintenanceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    maintenance_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='scheduled')
    scheduled_date = db.Column(db.DateTime, nullable=False)
    completed_date = db.Column(db.DateTime)
    technician = db.Column(db.String(100))
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    cost = db.Column(db.Float)
    downtime_minutes = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100))

class ScanTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    scan_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    parameters = db.Column(db.Text)
    enabled = db.Column(db.Boolean, default=True)
    frequency_days = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ScheduledScan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('scan_template.id'), nullable=False)
    next_run = db.Column(db.DateTime)
    last_run = db.Column(db.DateTime)
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    template = db.relationship('ScanTemplate')
