import { useState, useEffect } from 'react'
import { Play, BarChart3, Search } from 'lucide-react'
import './Common.css'

function AdvancedScanning() {
  const [scans, setScans] = useState([])
  const [devices, setDevices] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState({
    device_id: '',
    scan_type: 'ssl_tls'
  })

  const scanTypes = [
    { value: 'ssl_tls', label: 'SSL/TLS Security', icon: '🔒' },
    { value: 'http_security', label: 'HTTP Headers', icon: '🌐' },
    { value: 'network_device', label: 'Red (SNMP)', icon: '📡' },
    { value: 'database', label: 'Base de Datos', icon: '💾' },
    { value: 'dns', label: 'DNS', icon: '🔍' },
    { value: 'smtp', label: 'SMTP', icon: '📧' },
    { value: 'full', label: 'Escaneo Completo', icon: '⚡' }
  ]

  useEffect(() => {
    fetchDeviceScans()
    fetchDevices()
  }, [])

  const fetchDeviceScans = async () => {
    try {
      const response = await fetch('/api/device-scans', {
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
      const response = await fetch('/api/device-scans', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(formData)
      })
      if (response.ok) {
        fetchDeviceScans()
        setShowModal(false)
        setFormData({ device_id: '', scan_type: 'ssl_tls' })
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
          <h1>Escaneo Avanzado</h1>
          <p>Análisis profundo de seguridad SSL/TLS, HTTP, DNS y más</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-primary">
          <Play size={20} />
          Nuevo Escaneo
        </button>
      </div>

      <div className="scan-types-grid">
        {scanTypes.map(type => (
          <div key={type.value} className="scan-type-card">
            <div className="scan-type-icon">{type.icon}</div>
            <h3>{type.label}</h3>
            <p>{getScanDescription(type.value)}</p>
          </div>
        ))}
      </div>

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Dispositivo</th>
              <th>Tipo de Escaneo</th>
              <th>Estado</th>
              <th>Problemas Encontrados</th>
              <th>Tiempo de Respuesta</th>
              <th>CPU</th>
              <th>Memoria</th>
              <th>Fecha</th>
            </tr>
          </thead>
          <tbody>
            {scans.length > 0 ? (
              scans.map(scan => (
                <tr key={scan.id}>
                  <td><strong>{scan.device_name}</strong></td>
                  <td>{scanTypes.find(t => t.value === scan.scan_type)?.label}</td>
                  <td>
                    <span
                      className="severity-badge"
                      style={{ backgroundColor: getStatusColor(scan.status) }}
                    >
                      {scan.status}
                    </span>
                  </td>
                  <td>
                    {scan.issues_found > 0 ? (
                      <span style={{ color: '#dc2626', fontWeight: 'bold' }}>
                        {scan.issues_found} problemas
                      </span>
                    ) : (
                      <span style={{ color: '#22c55e' }}>Sin problemas</span>
                    )}
                  </td>
                  <td>{scan.response_time ? `${scan.response_time.toFixed(2)}ms` : '-'}</td>
                  <td>{scan.cpu_usage ? `${scan.cpu_usage.toFixed(1)}%` : '-'}</td>
                  <td>{scan.memory_usage ? `${scan.memory_usage.toFixed(1)}%` : '-'}</td>
                  <td>{new Date(scan.created_at).toLocaleString('es')}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="8" className="no-data">No hay escaneos avanzados</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Nuevo Escaneo Avanzado</h2>
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
                      {device.name} ({device.ip}) - {device.device_type}
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
                  {scanTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.icon} {type.label}
                    </option>
                  ))}
                </select>
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

      <style>{`
        .scan-types-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 16px;
          margin-bottom: 32px;
        }

        .scan-type-card {
          background: white;
          padding: 20px;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
          text-align: center;
          transition: transform 0.2s;
        }

        .scan-type-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        }

        .scan-type-icon {
          font-size: 32px;
          margin-bottom: 12px;
        }

        .scan-type-card h3 {
          font-size: 16px;
          font-weight: 600;
          margin-bottom: 8px;
          color: #1a1a2e;
        }

        .scan-type-card p {
          font-size: 13px;
          color: #6b7280;
        }
      `}</style>
    </div>
  )
}

function getScanDescription(scanType) {
  const descriptions = {
    ssl_tls: 'Valida certificados y configuración SSL/TLS',
    http_security: 'Verifica headers de seguridad HTTP',
    network_device: 'Escaneo SNMP de dispositivos de red',
    database: 'Prueba conectividad a bases de datos',
    dns: 'Análisis de configuración DNS',
    smtp: 'Escaneo de servidores SMTP',
    full: 'Escaneo completo de todos los aspectos'
  }
  return descriptions[scanType] || 'Escaneo de seguridad'
}

export default AdvancedScanning
