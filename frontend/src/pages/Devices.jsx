import { useState, useEffect } from 'react'
import { Plus, Trash2, Activity, AlertTriangle } from 'lucide-react'
import './Common.css'

function Devices() {
  const [devices, setDevices] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    ip: '',
    device_type: 'server',
    manufacturer: '',
    model: '',
    firmware_version: '',
    location: '',
    description: ''
  })

  const deviceTypes = [
    { value: 'server', label: 'Servidor' },
    { value: 'switch', label: 'Switch' },
    { value: 'router', label: 'Router' },
    { value: 'firewall', label: 'Firewall' },
    { value: 'load_balancer', label: 'Load Balancer' },
    { value: 'nas', label: 'NAS' },
    { value: 'ups', label: 'UPS' },
    { value: 'printer', label: 'Impresora' },
    { value: 'workstation', label: 'Workstation' }
  ]

  useEffect(() => {
    fetchDevices()
  }, [])

  const fetchDevices = async () => {
    try {
      const response = await fetch('/api/devices', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      })
      if (response.ok) {
        const data = await response.json()
        setDevices(data)
      }
    } catch (error) {
      console.error('Error fetching devices:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const response = await fetch('/api/devices', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(formData)
      })
      if (response.ok) {
        fetchDevices()
        setShowModal(false)
        setFormData({
          name: '',
          ip: '',
          device_type: 'server',
          manufacturer: '',
          model: '',
          firmware_version: '',
          location: '',
          description: ''
        })
      }
    } catch (error) {
      console.error('Error creating device:', error)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('¿Está seguro de eliminar este dispositivo?')) return
    try {
      const response = await fetch(`/api/devices/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      })
      if (response.ok) {
        fetchDevices()
      }
    } catch (error) {
      console.error('Error deleting device:', error)
    }
  }

  const getStatusColor = (status) => {
    return status === 'active' ? '#22c55e' : '#ef4444'
  }

  if (loading) return <div className="loading">Cargando dispositivos...</div>

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Dispositivos de Infraestructura</h1>
          <p>Gestión de switches, servidores y dispositivos de red</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-primary">
          <Plus size={20} />
          Agregar Dispositivo
        </button>
      </div>

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>IP</th>
              <th>Tipo</th>
              <th>Fabricante</th>
              <th>Modelo</th>
              <th>Ubicación</th>
              <th>Estado</th>
              <th>Último Escaneo</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {devices.length > 0 ? (
              devices.map(device => (
                <tr key={device.id}>
                  <td><strong>{device.name}</strong></td>
                  <td><code>{device.ip}</code></td>
                  <td>{deviceTypes.find(t => t.value === device.device_type)?.label || device.device_type}</td>
                  <td>{device.manufacturer || '-'}</td>
                  <td>{device.model || '-'}</td>
                  <td>{device.location || '-'}</td>
                  <td>
                    <span
                      className="severity-badge"
                      style={{ backgroundColor: getStatusColor(device.status) }}
                    >
                      {device.status}
                    </span>
                  </td>
                  <td>{device.last_scan ? new Date(device.last_scan).toLocaleString('es') : 'Nunca'}</td>
                  <td>
                    <button
                      className="btn-icon btn-danger"
                      onClick={() => handleDelete(device.id)}
                    >
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="9" className="no-data">No se encontraron dispositivos</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Agregar Dispositivo</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Nombre *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
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
                <label>Tipo de Dispositivo *</label>
                <select
                  value={formData.device_type}
                  onChange={(e) => setFormData({ ...formData, device_type: e.target.value })}
                  required
                >
                  {deviceTypes.map(type => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Fabricante</label>
                <input
                  type="text"
                  value={formData.manufacturer}
                  onChange={(e) => setFormData({ ...formData, manufacturer: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Modelo</label>
                <input
                  type="text"
                  value={formData.model}
                  onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Versión de Firmware</label>
                <input
                  type="text"
                  value={formData.firmware_version}
                  onChange={(e) => setFormData({ ...formData, firmware_version: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Ubicación</label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
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

export default Devices
