import React from 'react';
import {
  Shield,
  Activity,
  BarChart3,
  FileSearch,
  Settings,
  Menu,
} from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: <BarChart3 size={18} /> },
    { label: 'Log Analysis', path: '/logs', icon: <FileSearch size={18} /> },
    { label: 'Code Scanner', path: '/scanner', icon: <Shield size={18} /> },
    { label: 'Rule Engine', path: '/rules', icon: <Settings size={18} /> },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav 
      style={{ 
        position: 'sticky',
        top: 0,
        zIndex: 50,
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(16px)',
        borderBottom: '1px solid var(--border)',
        boxShadow: 'var(--shadow-sm)'
      }}
    >
      <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '0 1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '4rem' }}>
          {/* Logo Section */}
          <div 
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '0.75rem', 
              cursor: 'pointer',
              transition: 'opacity 0.2s'
            }}
            onClick={() => navigate('/dashboard')}
            onMouseEnter={(e) => e.currentTarget.style.opacity = '0.8'}
            onMouseLeave={(e) => e.currentTarget.style.opacity = '1'}
          >
            {/* Logo Icon */}
            <div
              style={{
                width: '2.5rem',
                height: '2.5rem',
                borderRadius: '0.5rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: 'var(--accent)',
                boxShadow: 'var(--shadow-accent)',
              }}
            >
              <Shield size={20} color="white" />
            </div>
            
            {/* Brand Text */}
            <div>
              <h1 style={{ 
                fontFamily: 'var(--font-display)', 
                fontSize: '1.25rem', 
                fontWeight: 600, 
                color: 'var(--foreground)', 
                lineHeight: 1,
                margin: 0
              }}>
                Securon
              </h1>
              <p style={{ 
                fontFamily: 'var(--font-mono)', 
                fontSize: '0.625rem', 
                fontWeight: 500,
                textTransform: 'uppercase',
                letterSpacing: '0.1em',
                color: 'var(--accent)', 
                margin: 0,
                marginTop: '0.125rem'
              }}>
                Security Platform
              </p>
            </div>
          </div>

          {/* Navigation Items - Desktop */}
          <div className="nav-desktop">
            {navItems.map((item) => (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.5rem 0.75rem',
                  borderRadius: '0.375rem',
                  fontSize: '0.875rem',
                  fontWeight: 500,
                  transition: 'all 0.2s',
                  border: 'none',
                  cursor: 'pointer',
                  backgroundColor: isActive(item.path) ? 'var(--accent)' : 'transparent',
                  color: isActive(item.path) ? 'white' : 'var(--muted-foreground)',
                  boxShadow: isActive(item.path) ? 'var(--shadow-sm)' : 'none'
                }}
                onMouseEnter={(e) => {
                  if (!isActive(item.path)) {
                    e.currentTarget.style.backgroundColor = 'var(--muted)';
                    e.currentTarget.style.color = 'var(--foreground)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive(item.path)) {
                    e.currentTarget.style.backgroundColor = 'transparent';
                    e.currentTarget.style.color = 'var(--muted-foreground)';
                  }
                }}
              >
                {item.icon}
                {item.label}
              </button>
            ))}
          </div>

          {/* Status Indicators - Desktop */}
          <div className="status-desktop">
            {/* System Status */}
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '0.5rem', 
              padding: '0.375rem 0.75rem', 
              borderRadius: '9999px', 
              backgroundColor: '#f0fdf4', 
              border: '1px solid #bbf7d0' 
            }}>
              <div 
                style={{
                  width: '0.5rem',
                  height: '0.5rem',
                  borderRadius: '50%',
                  backgroundColor: '#10b981',
                  animation: 'pulse 2s infinite'
                }}
              />
              <span style={{ 
                fontFamily: 'var(--font-mono)', 
                fontSize: '0.625rem', 
                fontWeight: 500,
                textTransform: 'uppercase',
                letterSpacing: '0.1em',
                color: '#15803d' 
              }}>
                Online
              </span>
            </div>

            {/* Activity Indicator */}
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '0.5rem', 
              padding: '0.375rem 0.75rem', 
              borderRadius: '9999px', 
              backgroundColor: 'rgba(184, 134, 11, 0.1)', 
              border: '1px solid var(--accent)' 
            }}>
              <Activity size={12} style={{ color: 'var(--accent)' }} />
              <span style={{ 
                fontFamily: 'var(--font-mono)', 
                fontSize: '0.625rem', 
                fontWeight: 500,
                textTransform: 'uppercase',
                letterSpacing: '0.1em',
                color: 'var(--accent)' 
              }}>
                Active
              </span>
            </div>
          </div>

          {/* Mobile Menu Button */}
          <div className="nav-mobile">
            <button
              style={{
                padding: '0.5rem',
                borderRadius: '0.375rem',
                border: 'none',
                backgroundColor: 'transparent',
                color: 'var(--muted-foreground)',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--muted)';
                e.currentTarget.style.color = 'var(--foreground)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.color = 'var(--muted-foreground)';
              }}
            >
              <Menu size={18} />
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;