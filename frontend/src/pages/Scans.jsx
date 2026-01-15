import { useState, useEffect } from 'react'
import { Plus, Play, Search } from 'lucide-react'
import './Common.css'

function Scans() {
  const [scans, setScans] = useState([])
  const [assets, setAssets] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState({
    asset_id: '',
    scan_type: 'nmap',
    options: '-sV -sC'
  })

  useEffect(() => {
    fetchScans()
    fetchAssets()
  }, [])

  const fetchScans = async () => {
    try {
      const response = await fetch('/api/scans', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      })
      if (response.ok) {
        const data = await response.json()
        setScans(data)
      }
    } catch (error) {
      console.error('Error fetching scans:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchAssets = async () => {
    try {
      const response = await fetch('/api/assets', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      })
      if (response.ok) {
        const data = await response.json()
        setAssets(data)
      }
    } catch (error) {
      console.error('Error fetching assets:', error)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const response = await fetch('/api/scans', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(formData)
      })
      if (response.ok) {
        fetchScans()
        setShowModal(false)
        setFormData({ asset_id: '', scan_type: 'nmap', options: '-sV -sC' })
      }
    } catch (error) {
      console.error('Error creating scan:', error)
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      'completed': '#22c55e',
      'running': '#3b82f6',
      'failed': '#ef4444',
      'pending': '#eab308'
    }
    return colors[status] || '#6b7280'
  }

  if (loading) return <div className="loading">Cargando escaneos...</div>

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Escaneos</h1>
          <p>Gestión de escaneos de vulnerabilidades</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-primary">
          <Plus size={20} />
          Nuevo Escaneo
        </button>
      </div>

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Activo</th>
              <th>Tipo</th>
              <th>Estado</th>
              <th>Vulnerabilidades</th>
              <th>Fecha</th>
            </tr>
          </thead>
          <tbody>
            {scans.length > 0 ? (
              scans.map(scan => (
                <tr key={scan.id}>
                  <td><code>#{scan.id}</code></td>
                  <td><strong>{scan.asset_hostname}</strong></td>
                  <td><span className="type-badge">{scan.scan_type}</span></td>
                  <td>
                    <span
                      className="status-badge"
                      style={{ backgroundColor: getStatusColor(scan.status) }}
                    >
                      {scan.status}
                    </span>
                  </td>
                  <td>{scan.vulnerabilities_found || 0}</td>
                  <td>{new Date(scan.created_at).toLocaleString('es')}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" className="no-data">No hay escaneos registrados</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Nuevo Escaneo</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Activo *</label>
                <select
                  value={formData.asset_id}
                  onChange={(e) => setFormData({ ...formData, asset_id: e.target.value })}
                  required
                >
                  <option value="">Seleccione un activo</option>
                  {assets.map(asset => (
                    <option key={asset.id} value={asset.id}>
                      {asset.hostname} ({asset.ip})
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Tipo de Escaneo *</label>
                <select
                  value={formData.scan_type}
                  onChange={(e) => setFormData({ ...formData, scan_type: e.target.value })}
                  required
                >
                  <option value="nmap">Nmap - Escaneo de puertos</option>
                  <option value="trivy">Trivy - Análisis de vulnerabilidades</option>
                  <option value="full">Completo - Nmap + Trivy</option>
                </select>
              </div>
              <div className="form-group">
                <label>Opciones</label>
                <input
                  type="text"
                  value={formData.options}
                  onChange={(e) => setFormData({ ...formData, options: e.target.value })}
                  placeholder="-sV -sC"
                />
              </div>
              <div className="modal-actions">
                <button type="button" onClick={() => setShowModal(false)} className="btn-secondary">
                  Cancelar
                </button>
                <button type="submit" className="btn-primary">
                  <Play size={16} />
                  Iniciar Escaneo
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Scans
