from datetime import datetime, timedelta
from .models import MaintenanceRecord, Device, ScheduledScan, ScanTemplate
from . import db

class MaintenanceManager:

    MAINTENANCE_TYPES = {
        'preventive': 'Mantenimiento preventivo',
        'corrective': 'Mantenimiento correctivo',
        'firmware_update': 'Actualización de firmware',
        'security_patch': 'Parche de seguridad',
        'hardware_replacement': 'Reemplazo de hardware',
        'inspection': 'Inspección general',
        'cleaning': 'Limpieza y mantenimiento físico'
    }

    @staticmethod
    def schedule_maintenance(device_id, maintenance_type, scheduled_date, description, technician=None, created_by=None):
        """Schedule maintenance for a device"""
        maintenance = MaintenanceRecord(
            device_id=device_id,
            maintenance_type=maintenance_type,
            scheduled_date=scheduled_date,
            description=description,
            technician=technician,
            created_by=created_by,
            status='scheduled'
        )
        db.session.add(maintenance)
        db.session.commit()
        return maintenance

    @staticmethod
    def complete_maintenance(maintenance_id, notes, downtime_minutes=0, cost=0):
        """Mark maintenance as completed"""
        maintenance = MaintenanceRecord.query.get(maintenance_id)
        if maintenance:
            maintenance.status = 'completed'
            maintenance.completed_date = datetime.utcnow()
            maintenance.notes = notes
            maintenance.downtime_minutes = downtime_minutes
            maintenance.cost = cost
            db.session.commit()
        return maintenance

    @staticmethod
    def get_scheduled_maintenance(days_ahead=30):
        """Get scheduled maintenance for next N days"""
        future_date = datetime.utcnow() + timedelta(days=days_ahead)
        records = MaintenanceRecord.query.filter(
            MaintenanceRecord.status == 'scheduled',
            MaintenanceRecord.scheduled_date <= future_date,
            MaintenanceRecord.scheduled_date >= datetime.utcnow()
        ).order_by(MaintenanceRecord.scheduled_date).all()
        return records

    @staticmethod
    def get_overdue_maintenance():
        """Get overdue maintenance records"""
        records = MaintenanceRecord.query.filter(
            MaintenanceRecord.status == 'scheduled',
            MaintenanceRecord.scheduled_date < datetime.utcnow()
        ).all()
        return records

    @staticmethod
    def get_maintenance_history(device_id):
        """Get maintenance history for a device"""
        records = MaintenanceRecord.query.filter_by(device_id=device_id).order_by(
            MaintenanceRecord.created_at.desc()
        ).all()
        return records

    @staticmethod
    def schedule_scan_template(device_id, template_id, frequency_days=None):
        """Schedule a scan template for a device"""
        template = ScanTemplate.query.get(template_id)
        if not template:
            return None

        frequency = frequency_days or template.frequency_days or 7
        next_run = datetime.utcnow() + timedelta(days=frequency)

        scheduled_scan = ScheduledScan(
            device_id=device_id,
            template_id=template_id,
            next_run=next_run,
            enabled=True
        )
        db.session.add(scheduled_scan)
        db.session.commit()
        return scheduled_scan

    @staticmethod
    def get_due_scans():
        """Get scans that are due to run"""
        due_scans = ScheduledScan.query.filter(
            ScheduledScan.enabled == True,
            ScheduledScan.next_run <= datetime.utcnow()
        ).all()
        return due_scans

    @staticmethod
    def update_scan_schedule(scheduled_scan_id):
        """Update next run time after scan execution"""
        scheduled_scan = ScheduledScan.query.get(scheduled_scan_id)
        if scheduled_scan:
            template = scheduled_scan.template
            frequency = template.frequency_days or 7
            scheduled_scan.last_run = datetime.utcnow()
            scheduled_scan.next_run = datetime.utcnow() + timedelta(days=frequency)
            db.session.commit()
        return scheduled_scan

    @staticmethod
    def get_maintenance_statistics(device_id=None):
        """Get maintenance statistics"""
        query = MaintenanceRecord.query

        if device_id:
            query = query.filter_by(device_id=device_id)

        total = query.count()
        completed = query.filter_by(status='completed').count()
        scheduled = query.filter_by(status='scheduled').count()
        overdue = query.filter(
            MaintenanceRecord.status == 'scheduled',
            MaintenanceRecord.scheduled_date < datetime.utcnow()
        ).count()

        total_downtime = db.session.query(db.func.sum(MaintenanceRecord.downtime_minutes)).filter_by(
            status='completed'
        ).scalar() or 0

        total_cost = db.session.query(db.func.sum(MaintenanceRecord.cost)).filter_by(
            status='completed'
        ).scalar() or 0

        return {
            'total': total,
            'completed': completed,
            'scheduled': scheduled,
            'overdue': overdue,
            'total_downtime': total_downtime,
            'total_cost': total_cost
        }

    @staticmethod
    def create_scan_template(name, scan_type, description, parameters, frequency_days=7):
        """Create a new scan template"""
        template = ScanTemplate(
            name=name,
            scan_type=scan_type,
            description=description,
            parameters=parameters,
            frequency_days=frequency_days,
            enabled=True
        )
        db.session.add(template)
        db.session.commit()
        return template

    @staticmethod
    def get_device_health(device_id):
        """Calculate overall device health score"""
        device = Device.query.get(device_id)
        if not device:
            return 0

        from .models import DeviceScan, DeviceIssue

        recent_scans = DeviceScan.query.filter_by(device_id=device_id).order_by(
            DeviceScan.created_at.desc()
        ).limit(10).all()

        if not recent_scans:
            return 50

        total_issues = 0
        critical_issues = 0

        for scan in recent_scans:
            issues = DeviceIssue.query.filter_by(device_scan_id=scan.id).all()
            total_issues += len(issues)
            critical_issues += len([i for i in issues if i.severity == 'critical'])

        health_score = max(0, 100 - (total_issues * 5) - (critical_issues * 20))
        return health_score

    @staticmethod
    def get_maintenance_calendar(month, year):
        """Get maintenance calendar for a specific month"""
        from calendar import monthrange

        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, monthrange(year, month)[1], 23, 59, 59)

        records = MaintenanceRecord.query.filter(
            MaintenanceRecord.scheduled_date >= start_date,
            MaintenanceRecord.scheduled_date <= end_date
        ).all()

        calendar_data = {}
        for record in records:
            day = record.scheduled_date.day
            if day not in calendar_data:
                calendar_data[day] = []
            calendar_data[day].append({
                'id': record.id,
                'type': record.maintenance_type,
                'device': record.device.name,
                'status': record.status,
                'technician': record.technician
            })

        return calendar_data
