from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
from .models import Asset, Vulnerability, Scan
import io

class ReportGenerator:
    @staticmethod
    def generate_executive_report():
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a2e'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        story.append(Paragraph("Goodyear Air Springs", title_style))
        story.append(Paragraph("Reporte Ejecutivo de Vulnerabilidades", styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 0.5*inch))

        story.append(Paragraph("Resumen Ejecutivo", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))

        total_assets = Asset.query.count()
        total_vulns = Vulnerability.query.count()
        critical_vulns = Vulnerability.query.filter_by(severity='critical').count()
        high_vulns = Vulnerability.query.filter_by(severity='high').count()
        medium_vulns = Vulnerability.query.filter_by(severity='medium').count()
        low_vulns = Vulnerability.query.filter_by(severity='low').count()

        summary_data = [
            ['Métrica', 'Cantidad'],
            ['Activos Totales', str(total_assets)],
            ['Vulnerabilidades Totales', str(total_vulns)],
            ['Vulnerabilidades Críticas', str(critical_vulns)],
            ['Vulnerabilidades Altas', str(high_vulns)],
            ['Vulnerabilidades Medias', str(medium_vulns)],
            ['Vulnerabilidades Bajas', str(low_vulns)],
        ]

        summary_table = Table(summary_data, colWidths=[4*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(summary_table)
        story.append(Spacer(1, 0.5*inch))

        story.append(Paragraph("Análisis de Riesgo", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))

        risk_text = f"""
        Se han identificado {total_vulns} vulnerabilidades en {total_assets} activos de la infraestructura.
        De estas, {critical_vulns} son de severidad crítica y requieren atención inmediata.
        Se recomienda priorizar la remediación de las vulnerabilidades críticas y altas en un plazo no mayor a 30 días.
        """

        story.append(Paragraph(risk_text, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))

        story.append(Paragraph("Recomendaciones", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))

        recommendations = [
            "Implementar parches de seguridad para todas las vulnerabilidades críticas",
            "Realizar escaneos de vulnerabilidades de forma periódica (mensual)",
            "Establecer un proceso de gestión de vulnerabilidades formal",
            "Capacitar al personal en buenas prácticas de seguridad",
            "Implementar un sistema de monitoreo continuo de la infraestructura"
        ]

        for i, rec in enumerate(recommendations, 1):
            story.append(Paragraph(f"{i}. {rec}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))

        doc.build(story)
        buffer.seek(0)
        return buffer

    @staticmethod
    def generate_technical_report():
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("Reporte Técnico de Vulnerabilidades", styles['Title']))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 0.5*inch))

        vulnerabilities = Vulnerability.query.join(Asset).order_by(
            Vulnerability.cvss.desc()
        ).all()

        if vulnerabilities:
            story.append(Paragraph("Vulnerabilidades Detectadas", styles['Heading2']))
            story.append(Spacer(1, 0.2*inch))

            for vuln in vulnerabilities[:20]:
                vuln_data = [
                    ['CVE', vuln.cve or 'N/A'],
                    ['Nombre', vuln.name],
                    ['Severidad', vuln.severity.upper()],
                    ['CVSS', str(vuln.cvss)],
                    ['Activo', vuln.asset.hostname if vuln.asset else 'N/A'],
                    ['Descripción', vuln.description or 'Sin descripción']
                ]

                vuln_table = Table(vuln_data, colWidths=[1.5*inch, 4.5*inch])

                severity_color = {
                    'critical': colors.red,
                    'high': colors.orange,
                    'medium': colors.yellow,
                    'low': colors.lightgreen
                }.get(vuln.severity, colors.grey)

                vuln_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('TEXTCOLOR', (0, 2), (1, 2), severity_color),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                ]))

                story.append(vuln_table)
                story.append(Spacer(1, 0.3*inch))

        else:
            story.append(Paragraph("No se encontraron vulnerabilidades", styles['Normal']))

        doc.build(story)
        buffer.seek(0)
        return buffer

    @staticmethod
    def generate_compliance_report():
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("Reporte de Cumplimiento Normativo", styles['Title']))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
        story.append(Spacer(1, 0.5*inch))

        story.append(Paragraph("Marco Normativo", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))

        frameworks = [
            "ISO 27001 - Sistema de Gestión de Seguridad de la Información",
            "NIST Cybersecurity Framework",
            "PCI DSS - Payment Card Industry Data Security Standard",
            "SOC 2 - Service Organization Control 2"
        ]

        for framework in frameworks:
            story.append(Paragraph(f"• {framework}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))

        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("Estado de Cumplimiento", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))

        critical_vulns = Vulnerability.query.filter_by(severity='critical').count()
        compliance_score = max(0, 100 - (critical_vulns * 10))

        compliance_data = [
            ['Control', 'Estado', 'Score'],
            ['Gestión de Vulnerabilidades', 'Implementado', '85%'],
            ['Gestión de Activos', 'Implementado', '90%'],
            ['Control de Acceso', 'Parcial', '70%'],
            ['Monitoreo de Seguridad', 'Implementado', '80%'],
            ['SCORE GENERAL', 'CUMPLIMIENTO', f'{compliance_score}%']
        ]

        compliance_table = Table(compliance_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        compliance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#fbbf24')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(compliance_table)
        story.append(Spacer(1, 0.5*inch))

        story.append(Paragraph("Áreas de Mejora", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))

        improvements = [
            "Fortalecer controles de acceso y autenticación",
            "Implementar sistema de respuesta a incidentes",
            "Mejorar la documentación de políticas de seguridad",
            "Realizar auditorías de seguridad periódicas"
        ]

        for improvement in improvements:
            story.append(Paragraph(f"• {improvement}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))

        doc.build(story)
        buffer.seek(0)
        return buffer
