#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app
from app.report_generator import ReportGenerator

def main():
    if len(sys.argv) < 2:
        print("Uso: python generate_report.py [executive|technical|compliance]")
        sys.exit(1)

    report_type = sys.argv[1]

    app = create_app()

    with app.app_context():
        if report_type == 'executive':
            print("Generando reporte ejecutivo...")
            buffer = ReportGenerator.generate_executive_report()
            filename = 'reporte_ejecutivo_goodyear.pdf'
        elif report_type == 'technical':
            print("Generando reporte técnico...")
            buffer = ReportGenerator.generate_technical_report()
            filename = 'reporte_tecnico_goodyear.pdf'
        elif report_type == 'compliance':
            print("Generando reporte de cumplimiento...")
            buffer = ReportGenerator.generate_compliance_report()
            filename = 'reporte_cumplimiento_goodyear.pdf'
        else:
            print(f"Tipo de reporte inválido: {report_type}")
            print("Tipos válidos: executive, technical, compliance")
            sys.exit(1)

        with open(filename, 'wb') as f:
            f.write(buffer.read())

        print(f"Reporte generado exitosamente: {filename}")

if __name__ == '__main__':
    main()
