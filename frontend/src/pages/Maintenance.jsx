import { useState, useEffect } from 'react'
import { Plus, CheckCircle, AlertCircle, Calendar } from 'lucide-react'
import './Common.css'

function Maintenance() {
  const [records, setRecords] = useState([])
  const [statistics, setStatistics] = useState({})
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [devices, setDevices] = useState([])
  const [formData, setFormData] = useState({
    device_id: '',
    maintenance_type: 'preventive',
    scheduled_date: '',
    technician: '',
    description: ''
  })

  const maintenanceTypes = [
    { value: 'preventive', label: 'Mantenimiento Preventivo' },
    { value: 'corrective', label: 'Mantenimiento Correctivo' },
    { value: 'firmware_update', label: 'Actualización de Firmware' },
    { value: 'security_patch', label: 'Parche de Seguridad' },
    { value: 'hardware_replacement', label: 'Reemplazo de Hardware' },
    { value: 'inspection', label: 'Inspección General' },
    { value: 'cleaning', label: 'Limpieza y Mantenimiento Físico' }
  ]

  useEffect(() => {
    fetchMaintenanceRecords()
    fetchStatistics()
    fetchDevices()
  }, [])

  const fetchMaintenanceRecords = async () => {
    try {
      const response = await fetch('/api/maintenance', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      })
      if (response.ok) {
        const data = await response.json()
        setRecords(data)
      }
    } catch (error) {
      console.error('Error fetching maintenance records:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchStatistics = async () => {
    try {
      const response = await fetch('/api/maintenance/statistics', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      })
      if (response.ok) {
        const data = await response.json()
        setStatistics(data)
      }
    } catch (error) {
      console.error('Error fetching statistics:', error)
    }
  }

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
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const response = await fetch('/api/maintenance', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          ...formData,
          scheduled_date: new Date(formData.scheduled_date).toISOString()
        })
      })
      if (response.ok) {
        fetchMaintenanceRecords()
        fetchStatistics()
        setShowModal(false)
        setFormData({
          device_id: '',
          maintenance_type: 'preventive',
          scheduled_date: '',
          technician: '',
          description: ''
        })
      }
    } catch (error) {
      console.error('Error creating maintenance:', error)
    }
  }

  const getStatusColor = (status) => {
    return status === 'completed' ? '#22c55e' : status === 'scheduled' ? '#3b82f6' : '#ef4444'
  }

  if (loading) return <div className="loading">Cargando mantenimientos...</div>

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Gestión de Mantenimiento</h1>
          <p>Planificación y seguimiento de mantenimientos de infraestructura</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-primary">
          <Plus size={20} />
          Programar Mantenimiento
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#dbeafe' }}>
            <Calendar size={24} color="#2563eb" />
          </div>
          <div className="stat-content">
            <h3>{statistics.total || 0}</h3>
            <p>Total de Registros</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#dcfce7' }}>
            <CheckCircle size={24} color="#16a34a" />
          </div>
          <div className="stat-content">
            <h3>{statistics.completed || 0}</h3>
            <p>Completados</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#dbeafe' }}>
            <AlertCircle size={24} color="#2563eb" />
          </div>
          <div className="stat-content">
            <h3>{statistics.scheduled || 0}</h3>
            <p>Programados</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#fee2e2' }}>
            <AlertCircle size={24} color="#dc2626" />
          </div>
          <div className="stat-content">
            <h3>{statistics.overdue || 0}</h3>
            <p>Vencidos</p>
          </div>
        </div>
      </div>

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Dispositivo</th>
              <th>Tipo de Mantenimiento</th>
              <th>Estado</th>
              <th>Fecha Programada</th>
              <th>Técnico</th>
              <th>Costo</th>
              <th>Tiempo de Inactividad</th>
            </tr>
          </thead>
          <tbody>
            {records.length > 0 ? (
              records.map(record => (
                <tr key={record.id}>
                  <td><strong>{record.device_name}</strong></td>
                  <td>{maintenanceTypes.find(t => t.value === record.maintenance_type)?.label}</td>
                  <td>
                    <span
                      className="severity-badge"
                      style={{ backgroundColor: getStatusColor(record.status) }}
                    >
                      {record.status}
                    </span>
                  </td>
                  <td>{new Date(record.scheduled_date).toLocaleString('es')}</td>
                  <td>{record.technician || '-'}</td>
                  <td>${record.cost || '0.00'}</td>
                  <td>{record.downtime_minutes ? `${record.downtime_minutes} min` : '-'}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="7" className="no-data">No hay registros de mantenimiento</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Programar Mantenimiento</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Dispositivo *</label>
                <select
                  value={formData.device_id}
                  onChange={(e) => setFormData({ ...formData, device_id: e.target.value })}
                  required
                >
                  <option value="">Seleccione un dispositivo</option>
                  {devices.map(device => (
                    <option key={device.id} value={device.id}>
                      {device.name} ({device.ip})
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Tipo de Mantenimiento *</label>
                <select
                  value={formData.maintenance_type}
                  onChange={(e) => setFormData({ ...formData, maintenance_type: e.target.value })}
                  required
                >
                  {maintenanceTypes.map(type => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Fecha Programada *</label>
                <input
                  type="datetime-local"
                  value={formData.scheduled_date}
                  onChange={(e) => setFormData({ ...formData, scheduled_date: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Técnico</label>
                <input
                  type="text"
                  value={formData.technician}
                  onChange={(e) => setFormData({ ...formData, technician: e.target.value })}
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
                  Programar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Maintenance
