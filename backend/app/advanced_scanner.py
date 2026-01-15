import subprocess
import json
import re
from datetime import datetime
from .models import DeviceIssue, DeviceScan
from . import db

class AdvancedScanner:

    @staticmethod
    def scan_ssl_tls(device, port=443):
        """Scan SSL/TLS certificate and security"""
        try:
            cmd = f"openssl s_client -connect {device.ip}:{port} -servername {device.name}"
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def scan_http_headers(device, port=80):
        """Analyze HTTP security headers"""
        try:
            cmd = f"curl -i http://{device.ip}:{port}/"
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=15
            )
            return result.stdout
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def scan_network_device(device):
        """Scan network switches and routers"""
        try:
            cmd = f"snmp-walk -v2c -c public {device.ip} 1.3.6.1.2.1.1"
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def scan_database(device, port=5432, db_type='postgresql'):
        """Scan database servers"""
        try:
            if db_type == 'postgresql':
                cmd = f"pg_isready -h {device.ip} -p {port}"
            elif db_type == 'mysql':
                cmd = f"mysql -h {device.ip} -P {port} -u root -e 'SELECT VERSION();'"
            else:
                return "Unsupported database type"

            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=15
            )
            return result.stdout
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def scan_dns(device):
        """Scan DNS configuration"""
        try:
            cmd = f"nslookup {device.ip}"
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def scan_smtp(device, port=25):
        """Scan SMTP server"""
        try:
            cmd = f"nmap -p {port} -sC {device.ip}"
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.stdout
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def parse_ssl_results(result, device_id, scan_id):
        """Parse SSL/TLS scan results"""
        issues = []

        if "error" in result.lower() or "unable" in result.lower():
            issue = DeviceIssue(
                device_scan_id=scan_id,
                device_id=device_id,
                issue_type='ssl_error',
                severity='high',
                description='SSL/TLS error detected',
                recommendation='Check SSL certificate and configuration'
            )
            issues.append(issue)

        if "SSLv2" in result or "SSLv3" in result:
            issue = DeviceIssue(
                device_scan_id=scan_id,
                device_id=device_id,
                issue_type='weak_ssl',
                severity='critical',
                description='Weak SSL protocol version detected',
                recommendation='Disable SSLv2/SSLv3 and use TLS 1.2+'
            )
            issues.append(issue)

        if "no shared cipher" in result.lower():
            issue = DeviceIssue(
                device_scan_id=scan_id,
                device_id=device_id,
                issue_type='cipher_weakness',
                severity='high',
                description='Weak cipher configuration',
                recommendation='Update cipher suite to secure options'
            )
            issues.append(issue)

        return issues

    @staticmethod
    def parse_http_headers(result, device_id, scan_id):
        """Parse HTTP header security"""
        issues = []

        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'Strict-Transport-Security': 'https',
            'X-XSS-Protection': '1; mode=block'
        }

        for header, required_value in security_headers.items():
            if header.lower() not in result.lower():
                issue = DeviceIssue(
                    device_scan_id=scan_id,
                    device_id=device_id,
                    issue_type='missing_header',
                    severity='medium',
                    description=f'Missing security header: {header}',
                    recommendation=f'Add {header} header to HTTP responses'
                )
                issues.append(issue)

        if "HTTP/1.0" in result:
            issue = DeviceIssue(
                device_scan_id=scan_id,
                device_id=device_id,
                issue_type='old_http',
                severity='medium',
                description='Old HTTP protocol version detected',
                recommendation='Upgrade to HTTP/1.1 or HTTP/2'
            )
            issues.append(issue)

        return issues

    @staticmethod
    def parse_network_device(result, device_id, scan_id):
        """Parse network device scan"""
        issues = []

        if "Authentication failed" in result or "Timeout" in result:
            issue = DeviceIssue(
                device_scan_id=scan_id,
                device_id=device_id,
                issue_type='snmp_auth',
                severity='high',
                description='SNMP authentication failed or unreachable',
                recommendation='Verify SNMP credentials and connectivity'
            )
            issues.append(issue)

        return issues

    @staticmethod
    def execute_device_scan(device_scan_id):
        """Execute comprehensive device scan"""
        device_scan = DeviceScan.query.get(device_scan_id)
        if not device_scan:
            return

        device = device_scan.device
        device_scan.status = 'running'
        db.session.commit()

        try:
            issues = []

            if device_scan.scan_type == 'ssl_tls':
                result = AdvancedScanner.scan_ssl_tls(device)
                device_scan.result = result
                issues = AdvancedScanner.parse_ssl_results(result, device.id, device_scan_id)

            elif device_scan.scan_type == 'http_security':
                result = AdvancedScanner.scan_http_headers(device)
                device_scan.result = result
                issues = AdvancedScanner.parse_http_headers(result, device.id, device_scan_id)

            elif device_scan.scan_type == 'network_device':
                result = AdvancedScanner.scan_network_device(device)
                device_scan.result = result
                issues = AdvancedScanner.parse_network_device(result, device.id, device_scan_id)

            elif device_scan.scan_type == 'database':
                result = AdvancedScanner.scan_database(device)
                device_scan.result = result

            elif device_scan.scan_type == 'dns':
                result = AdvancedScanner.scan_dns(device)
                device_scan.result = result

            elif device_scan.scan_type == 'smtp':
                result = AdvancedScanner.scan_smtp(device)
                device_scan.result = result

            elif device_scan.scan_type == 'full':
                results = {}
                results['ssl'] = AdvancedScanner.scan_ssl_tls(device)
                results['http'] = AdvancedScanner.scan_http_headers(device)
                results['network'] = AdvancedScanner.scan_network_device(device)
                device_scan.result = json.dumps(results)

                issues.extend(AdvancedScanner.parse_ssl_results(results['ssl'], device.id, device_scan_id))
                issues.extend(AdvancedScanner.parse_http_headers(results['http'], device.id, device_scan_id))

            for issue in issues:
                db.session.add(issue)

            device_scan.issues_found = len(issues)
            device_scan.status = 'completed'
            device_scan.completed_at = datetime.utcnow()
            device.last_scan = datetime.utcnow()

        except Exception as e:
            device_scan.status = 'failed'
            device_scan.result = f"Error: {str(e)}"

        db.session.commit()
