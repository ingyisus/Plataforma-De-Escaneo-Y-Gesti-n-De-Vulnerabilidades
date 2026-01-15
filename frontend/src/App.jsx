import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Assets from './pages/Assets'
import Vulnerabilities from './pages/Vulnerabilities'
import Scans from './pages/Scans'
import Reports from './pages/Reports'
import Devices from './pages/Devices'
import Maintenance from './pages/Maintenance'
import AdvancedScanning from './pages/AdvancedScanning'
import Login from './pages/Login'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      setIsAuthenticated(true)
    }
    setLoading(false)
  }, [])

  if (loading) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
      Cargando...
    </div>
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={
          isAuthenticated ? <Navigate to="/" /> : <Login onLogin={() => setIsAuthenticated(true)} />
        } />
        <Route path="/" element={
          isAuthenticated ? <Layout onLogout={() => setIsAuthenticated(false)} /> : <Navigate to="/login" />
        }>
          <Route index element={<Dashboard />} />
          <Route path="assets" element={<Assets />} />
          <Route path="vulnerabilities" element={<Vulnerabilities />} />
          <Route path="scans" element={<Scans />} />
          <Route path="reports" element={<Reports />} />
          <Route path="devices" element={<Devices />} />
          <Route path="maintenance" element={<Maintenance />} />
          <Route path="advanced-scanning" element={<AdvancedScanning />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
