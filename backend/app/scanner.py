import subprocess
import json
import re
from .models import Vulnerability, Scan
from . import db
from datetime import datetime

class VulnerabilityScanner:
    @staticmethod
    def run_nmap_scan(asset, options='-sV -sC'):
        try:
            cmd = f"nmap {options} {asset.ip}"
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            return "Scan timeout"
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def parse_nmap_results(scan_result, asset_id, scan_id):
        vulnerabilities = []

        port_pattern = r'(\d+)/tcp\s+open\s+(\S+)'
        ports = re.findall(port_pattern, scan_result)

        for port, service in ports:
            severity = 'low'
            cvss = 3.0

            if 'ssh' in service.lower() and port == '22':
                severity = 'medium'
                cvss = 5.0
            elif 'http' in service.lower():
                severity = 'medium'
                cvss = 5.3
            elif 'ftp' in service.lower():
                severity = 'high'
                cvss = 7.5
            elif 'telnet' in service.lower():
                severity = 'critical'
                cvss = 9.8

            vuln = Vulnerability(
                name=f"Puerto {port}/{service} expuesto",
                cve=f"NMAP-{port}",
                severity=severity,
                cvss=cvss,
                description=f"El puerto {port} con servicio {service} está abierto y accesible",
                asset_id=asset_id,
                scan_id=scan_id
            )
            vulnerabilities.append(vuln)

        return vulnerabilities

    @staticmethod
    def run_trivy_scan(asset):
        try:
            cmd = f"trivy image --format json {asset.hostname}"
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=600
            )
            return result.stdout
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def parse_trivy_results(scan_result, asset_id, scan_id):
        vulnerabilities = []
        try:
            data = json.loads(scan_result)
            for result in data.get('Results', []):
                for vuln_data in result.get('Vulnerabilities', []):
                    severity_map = {
                        'CRITICAL': 'critical',
                        'HIGH': 'high',
                        'MEDIUM': 'medium',
                        'LOW': 'low'
                    }

                    vuln = Vulnerability(
                        name=vuln_data.get('Title', 'Unknown'),
                        cve=vuln_data.get('VulnerabilityID', 'N/A'),
                        severity=severity_map.get(vuln_data.get('Severity', 'UNKNOWN'), 'low'),
                        cvss=float(vuln_data.get('CVSS', {}).get('nvd', {}).get('V3Score', 0)),
                        description=vuln_data.get('Description', 'No description available'),
                        asset_id=asset_id,
                        scan_id=scan_id
                    )
                    vulnerabilities.append(vuln)
        except json.JSONDecodeError:
            pass

        return vulnerabilities

    @staticmethod
    def execute_scan(scan_id):
        scan = Scan.query.get(scan_id)
        if not scan:
            return

        scan.status = 'running'
        db.session.commit()

        try:
            asset = scan.asset
            vulnerabilities = []

            if scan.scan_type == 'nmap':
                result = VulnerabilityScanner.run_nmap_scan(asset, scan.options or '-sV -sC')
                scan.result = result
                vulnerabilities = VulnerabilityScanner.parse_nmap_results(result, asset.id, scan.id)

            elif scan.scan_type == 'trivy':
                result = VulnerabilityScanner.run_trivy_scan(asset)
                scan.result = result
                vulnerabilities = VulnerabilityScanner.parse_trivy_results(result, asset.id, scan.id)

            elif scan.scan_type == 'full':
                nmap_result = VulnerabilityScanner.run_nmap_scan(asset, scan.options or '-sV -sC')
                trivy_result = VulnerabilityScanner.run_trivy_scan(asset)
                scan.result = f"NMAP:\n{nmap_result}\n\nTRIVY:\n{trivy_result}"

                vulnerabilities.extend(VulnerabilityScanner.parse_nmap_results(nmap_result, asset.id, scan.id))
                vulnerabilities.extend(VulnerabilityScanner.parse_trivy_results(trivy_result, asset.id, scan.id))

            for vuln in vulnerabilities:
                db.session.add(vuln)

            scan.vulnerabilities_found = len(vulnerabilities)
            scan.status = 'completed'
            scan.completed_at = datetime.utcnow()

        except Exception as e:
            scan.status = 'failed'
            scan.result = f"Error: {str(e)}"

        db.session.commit()
