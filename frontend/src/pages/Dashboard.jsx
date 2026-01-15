import { useState, useEffect } from 'react'
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Server, AlertTriangle, CheckCircle, XCircle } from 'lucide-react'
import './Dashboard.css'

function Dashboard() {
  const [stats, setStats] = useState({
    total_assets: 0,
    total_vulnerabilities: 0,
    critical_vulns: 0,
    high_vulns: 0,
    medium_vulns: 0,
    low_vulns: 0,
    recent_scans: []
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/dashboard/stats', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      })
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Error fetching stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const severityData = [
    { name: 'Crítica', value: stats.critical_vulns, color: '#ef4444' },
    { name: 'Alta', value: stats.high_vulns, color: '#f97316' },
    { name: 'Media', value: stats.medium_vulns, color: '#eab308' },
    { name: 'Baja', value: stats.low_vulns, color: '#22c55e' }
  ]

  if (loading) {
    return <div className="loading">Cargando estadísticas...</div>
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p>Resumen de la plataforma de gestión de vulnerabilidades</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#dbeafe' }}>
            <Server size={24} color="#2563eb" />
          </div>
          <div className="stat-content">
            <h3>{stats.total_assets}</h3>
            <p>Activos Totales</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#fee2e2' }}>
            <AlertTriangle size={24} color="#dc2626" />
          </div>
          <div className="stat-content">
            <h3>{stats.total_vulnerabilities}</h3>
            <p>Vulnerabilidades</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#fef3c7' }}>
            <XCircle size={24} color="#ca8a04" />
          </div>
          <div className="stat-content">
            <h3>{stats.critical_vulns}</h3>
            <p>Críticas</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#dcfce7' }}>
            <CheckCircle size={24} color="#16a34a" />
          </div>
          <div className="stat-content">
            <h3>{stats.low_vulns}</h3>
            <p>Baja Severidad</p>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h2>Distribución por Severidad</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={severityData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {severityData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h2>Vulnerabilidades por Severidad</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={severityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#fbbf24" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="recent-scans">
        <h2>Escaneos Recientes</h2>
        <div className="scans-list">
          {stats.recent_scans.length > 0 ? (
            stats.recent_scans.map((scan, index) => (
              <div key={index} className="scan-item">
                <div className="scan-info">
                  <strong>{scan.target}</strong>
                  <span className="scan-date">{new Date(scan.created_at).toLocaleString('es')}</span>
                </div>
                <span className={`scan-status status-${scan.status}`}>{scan.status}</span>
              </div>
            ))
          ) : (
            <p className="no-data">No hay escaneos recientes</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
