import { useState, useEffect } from 'react'
import { FileText, Download } from 'lucide-react'
import './Common.css'

function Reports() {
  const [generating, setGenerating] = useState(false)
  const [reports, setReports] = useState([])

  useEffect(() => {
    fetchReports()
  }, [])

  const fetchReports = async () => {
    try {
      const response = await fetch('/api/reports', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      })
      if (response.ok) {
        const data = await response.json()
        setReports(data)
      }
    } catch (error) {
      console.error('Error fetching reports:', error)
    }
  }

  const generateReport = async (type) => {
    setGenerating(true)
    try {
      const response = await fetch('/api/reports/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ report_type: type })
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `reporte_${type}_${new Date().getTime()}.pdf`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        fetchReports()
      }
    } catch (error) {
      console.error('Error generating report:', error)
      alert('Error al generar el reporte')
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Reportes</h1>
          <p>Generación de reportes ejecutivos</p>
        </div>
      </div>

      <div className="reports-grid">
        <div className="report-card">
          <div className="report-icon">
            <FileText size={32} />
          </div>
          <h3>Reporte Ejecutivo</h3>
          <p>Resumen general de vulnerabilidades y activos para la alta dirección</p>
          <button
            onClick={() => generateReport('executive')}
            disabled={generating}
            className="btn-primary"
          >
            <Download size={16} />
            {generating ? 'Generando...' : 'Generar Reporte'}
          </button>
        </div>

        <div className="report-card">
          <div className="report-icon">
            <FileText size={32} />
          </div>
          <h3>Reporte Técnico</h3>
          <p>Detalles técnicos completos de todas las vulnerabilidades detectadas</p>
          <button
            onClick={() => generateReport('technical')}
            disabled={generating}
            className="btn-primary"
          >
            <Download size={16} />
            {generating ? 'Generando...' : 'Generar Reporte'}
          </button>
        </div>

        <div className="report-card">
          <div className="report-icon">
            <FileText size={32} />
          </div>
          <h3>Reporte de Cumplimiento</h3>
          <p>Análisis de cumplimiento normativo y mejores prácticas</p>
          <button
            onClick={() => generateReport('compliance')}
            disabled={generating}
            className="btn-primary"
          >
            <Download size={16} />
            {generating ? 'Generando...' : 'Generar Reporte'}
          </button>
        </div>
      </div>

      <div className="recent-reports">
        <h2>Reportes Recientes</h2>
        <div className="reports-list">
          {reports.length > 0 ? (
            reports.map((report, index) => (
              <div key={index} className="report-item">
                <FileText size={24} />
                <div className="report-info">
                  <strong>{report.name}</strong>
                  <span>{new Date(report.created_at).toLocaleString('es')}</span>
                </div>
                <button className="btn-icon">
                  <Download size={16} />
                </button>
              </div>
            ))
          ) : (
            <p className="no-data">No hay reportes generados</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default Reports
