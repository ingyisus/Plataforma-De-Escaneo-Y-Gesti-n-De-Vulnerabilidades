import { useState, useEffect } from 'react'
import { Search, AlertCircle } from 'lucide-react'
import './Common.css'

function Vulnerabilities() {
  const [vulnerabilities, setVulnerabilities] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterSeverity, setFilterSeverity] = useState('all')

  useEffect(() => {
    fetchVulnerabilities()
  }, [])

  const fetchVulnerabilities = async () => {
    try {
      const response = await fetch('/api/vulnerabilities', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      })
      if (response.ok) {
        const data = await response.json()
        setVulnerabilities(data)
      }
    } catch (error) {
      console.error('Error fetching vulnerabilities:', error)
    } finally {
      setLoading(false)
    }
  }

  const getSeverityColor = (severity) => {
    const colors = {
      'critical': '#ef4444',
      'high': '#f97316',
      'medium': '#eab308',
      'low': '#22c55e'
    }
    return colors[severity?.toLowerCase()] || '#6b7280'
  }

  const filteredVulnerabilities = vulnerabilities.filter(vuln => {
    const matchesSearch = vuln.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         vuln.cve?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesSeverity = filterSeverity === 'all' || vuln.severity?.toLowerCase() === filterSeverity
    return matchesSearch && matchesSeverity
  })

  if (loading) return <div className="loading">Cargando vulnerabilidades...</div>

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Vulnerabilidades</h1>
          <p>Gestión de vulnerabilidades detectadas</p>
        </div>
      </div>

      <div className="filters">
        <div className="search-bar">
          <Search size={20} />
          <input
            type="text"
            placeholder="Buscar por nombre o CVE..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <select
          value={filterSeverity}
          onChange={(e) => setFilterSeverity(e.target.value)}
          className="filter-select"
        >
          <option value="all">Todas las severidades</option>
          <option value="critical">Crítica</option>
          <option value="high">Alta</option>
          <option value="medium">Media</option>
          <option value="low">Baja</option>
        </select>
      </div>

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>CVE</th>
              <th>Nombre</th>
              <th>Severidad</th>
              <th>CVSS</th>
              <th>Activo</th>
              <th>Descripción</th>
            </tr>
          </thead>
          <tbody>
            {filteredVulnerabilities.length > 0 ? (
              filteredVulnerabilities.map(vuln => (
                <tr key={vuln.id}>
                  <td><code>{vuln.cve || 'N/A'}</code></td>
                  <td><strong>{vuln.name}</strong></td>
                  <td>
                    <span
                      className="severity-badge"
                      style={{ backgroundColor: getSeverityColor(vuln.severity) }}
                    >
                      {vuln.severity}
                    </span>
                  </td>
                  <td><strong>{vuln.cvss?.toFixed(1) || 'N/A'}</strong></td>
                  <td>{vuln.asset_hostname || 'N/A'}</td>
                  <td className="description-cell">{vuln.description || '-'}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" className="no-data">
                  <AlertCircle size={48} />
                  <p>No se encontraron vulnerabilidades</p>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Vulnerabilities
