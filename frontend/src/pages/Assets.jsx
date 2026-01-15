import { useState, useEffect } from 'react'
import { Plus, Trash2, Edit2, Search } from 'lucide-react'
import './Common.css'

function Assets() {
  const [assets, setAssets] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [formData, setFormData] = useState({
    hostname: '',
    ip: '',
    os: '',
    description: ''
  })

  useEffect(() => {
    fetchAssets()
  }, [])

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
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const response = await fetch('/api/assets', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(formData)
      })
      if (response.ok) {
        fetchAssets()
        setShowModal(false)
        setFormData({ hostname: '', ip: '', os: '', description: '' })
      }
    } catch (error) {
      console.error('Error creating asset:', error)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('¿Está seguro de eliminar este activo?')) return
    try {
      const response = await fetch(`/api/assets/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      })
      if (response.ok) {
        fetchAssets()
      }
    } catch (error) {
      console.error('Error deleting asset:', error)
    }
  }

  const filteredAssets = assets.filter(asset =>
    asset.hostname?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    asset.ip?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading) return <div className="loading">Cargando activos...</div>

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Activos</h1>
          <p>Gestión de servidores y dispositivos</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-primary">
          <Plus size={20} />
          Agregar Activo
        </button>
      </div>

      <div className="search-bar">
        <Search size={20} />
        <input
          type="text"
          placeholder="Buscar por hostname o IP..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Hostname</th>
              <th>IP</th>
              <th>Sistema Operativo</th>
              <th>Descripción</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filteredAssets.length > 0 ? (
              filteredAssets.map(asset => (
                <tr key={asset.id}>
                  <td><strong>{asset.hostname}</strong></td>
                  <td><code>{asset.ip}</code></td>
                  <td>{asset.os || 'N/A'}</td>
                  <td>{asset.description || '-'}</td>
                  <td>
                    <div className="action-buttons">
                      <button className="btn-icon btn-danger" onClick={() => handleDelete(asset.id)}>
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="5" className="no-data">No se encontraron activos</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Agregar Activo</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Hostname *</label>
                <input
                  type="text"
                  value={formData.hostname}
                  onChange={(e) => setFormData({ ...formData, hostname: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Dirección IP *</label>
                <input
                  type="text"
                  value={formData.ip}
                  onChange={(e) => setFormData({ ...formData, ip: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Sistema Operativo</label>
                <input
                  type="text"
                  value={formData.os}
                  onChange={(e) => setFormData({ ...formData, os: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Descripción</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows="3"
                />
              </div>
              <div className="modal-actions">
                <button type="button" onClick={() => setShowModal(false)} className="btn-secondary">
                  Cancelar
                </button>
                <button type="submit" className="btn-primary">
                  Guardar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Assets
