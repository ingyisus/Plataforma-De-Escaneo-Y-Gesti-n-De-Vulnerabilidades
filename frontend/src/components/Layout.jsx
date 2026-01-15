import { Outlet, Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, Server, AlertTriangle, ScanLine, FileText, LogOut, Wrench, Zap } from 'lucide-react'
import './Layout.css'

function Layout({ onLogout }) {
  const location = useLocation()

  const handleLogout = () => {
    localStorage.removeItem('token')
    onLogout()
  }

  const navItems = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/devices', icon: Server, label: 'Dispositivos' },
    { path: '/assets', icon: Server, label: 'Activos' },
    { path: '/vulnerabilities', icon: AlertTriangle, label: 'Vulnerabilidades' },
    { path: '/scans', icon: ScanLine, label: 'Escaneos' },
    { path: '/advanced-scanning', icon: Zap, label: 'Escaneo Avanzado' },
    { path: '/maintenance', icon: Wrench, label: 'Mantenimiento' },
    { path: '/reports', icon: FileText, label: 'Reportes' }
  ]

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1>Goodyear</h1>
          <p>Gestión de Vulnerabilidades</p>
        </div>
        <nav className="sidebar-nav">
          {navItems.map(({ path, icon: Icon, label }) => (
            <Link
              key={path}
              to={path}
              className={location.pathname === path ? 'nav-item active' : 'nav-item'}
            >
              <Icon size={20} />
              <span>{label}</span>
            </Link>
          ))}
        </nav>
        <div className="sidebar-footer">
          <button onClick={handleLogout} className="logout-button">
            <LogOut size={20} />
            <span>Cerrar Sesión</span>
          </button>
        </div>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout
