import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Container,
} from '@mui/material';
import {
  Shield,
  Zap,
  Lock,
  BarChart3,
  FileSearch,
  Settings,
} from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { label: 'DASHBOARD', path: '/dashboard', icon: <BarChart3 size={18} /> },
    { label: 'LOG ANALYSIS', path: '/logs', icon: <FileSearch size={18} /> },
    { label: 'CODE SCANNER', path: '/scanner', icon: <Shield size={18} /> },
    { label: 'RULE ENGINE', path: '/rules', icon: <Settings size={18} /> },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <AppBar 
      position="sticky" 
      elevation={0}
      sx={{ 
        backgroundColor: 'rgba(15, 17, 21, 0.8)',
        backdropFilter: 'blur(16px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
      }}
    >
      <Container maxWidth="xl">
        <Toolbar sx={{ py: 2 }}>
          {/* Logo Section */}
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 2,
              cursor: 'pointer',
            }}
            onClick={() => navigate('/dashboard')}
          >
            {/* Glowing Logo Icon */}
            <Box
              sx={{
                width: 48,
                height: 48,
                background: 'linear-gradient(135deg, #EA580C, #F7931A)',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 0 20px -5px rgba(247, 147, 26, 0.6)',
                position: 'relative',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  inset: 0,
                  borderRadius: '12px',
                  padding: '2px',
                  background: 'linear-gradient(135deg, #F7931A, #FFD600)',
                  mask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
                  maskComposite: 'xor',
                },
              }}
            >
              <Lock size={24} color="#FFFFFF" />
            </Box>
            
            {/* Brand Text */}
            <Box>
              <Typography 
                variant="h5" 
                sx={{ 
                  fontFamily: '"Space Grotesk", sans-serif',
                  fontWeight: 700,
                  color: '#FFFFFF',
                  lineHeight: 1,
                }}
              >
                SECURON
              </Typography>
              <Typography 
                variant="caption" 
                sx={{ 
                  fontFamily: '"JetBrains Mono", monospace',
                  color: '#F7931A',
                  letterSpacing: '0.2em',
                  fontSize: '0.7rem',
                }}
              >
                DEFI SECURITY
              </Typography>
            </Box>
          </Box>

          {/* Spacer */}
          <Box sx={{ flexGrow: 1 }} />

          {/* Navigation Items */}
          <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 1 }}>
            {navItems.map((item) => (
              <Button
                key={item.path}
                onClick={() => navigate(item.path)}
                startIcon={item.icon}
                sx={{
                  color: isActive(item.path) ? '#F7931A' : '#94A3B8',
                  fontFamily: '"JetBrains Mono", monospace',
                  fontSize: '0.75rem',
                  fontWeight: 500,
                  letterSpacing: '0.1em',
                  px: 3,
                  py: 1.5,
                  borderRadius: '8px',
                  textTransform: 'uppercase',
                  position: 'relative',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    color: '#F7931A',
                    backgroundColor: 'rgba(247, 147, 26, 0.1)',
                    transform: 'translateY(-2px)',
                  },
                  ...(isActive(item.path) && {
                    backgroundColor: 'rgba(247, 147, 26, 0.2)',
                    border: '1px solid rgba(247, 147, 26, 0.5)',
                    boxShadow: '0 0 15px -5px rgba(247, 147, 26, 0.4)',
                    '&::after': {
                      content: '""',
                      position: 'absolute',
                      bottom: -2,
                      left: '50%',
                      transform: 'translateX(-50%)',
                      width: 4,
                      height: 4,
                      backgroundColor: '#F7931A',
                      borderRadius: '50%',
                      boxShadow: '0 0 8px rgba(247, 147, 26, 0.8)',
                    },
                  }),
                }}
              >
                {item.label}
              </Button>
            ))}
          </Box>

          {/* Status Indicator */}
          <Box sx={{ ml: 4, display: { xs: 'none', lg: 'flex' }, alignItems: 'center', gap: 2 }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                px: 2,
                py: 1,
                backgroundColor: 'rgba(16, 185, 129, 0.2)',
                border: '1px solid rgba(16, 185, 129, 0.5)',
                borderRadius: '20px',
              }}
            >
              <Box
                sx={{
                  width: 8,
                  height: 8,
                  backgroundColor: '#10B981',
                  borderRadius: '50%',
                  animation: 'pulse 2s infinite',
                  '@keyframes pulse': {
                    '0%, 100%': { opacity: 1 },
                    '50%': { opacity: 0.5 },
                  },
                }}
              />
              <Typography
                variant="caption"
                sx={{
                  fontFamily: '"JetBrains Mono", monospace',
                  color: '#10B981',
                  fontSize: '0.7rem',
                  letterSpacing: '0.05em',
                }}
              >
                SYSTEM ONLINE
              </Typography>
            </Box>

            {/* Network Activity Indicator */}
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 0.5,
                px: 2,
                py: 1,
                backgroundColor: 'rgba(247, 147, 26, 0.2)',
                border: '1px solid rgba(247, 147, 26, 0.5)',
                borderRadius: '20px',
              }}
            >
              <Zap size={12} color="#F7931A" />
              <Typography
                variant="caption"
                sx={{
                  fontFamily: '"JetBrains Mono", monospace',
                  color: '#F7931A',
                  fontSize: '0.7rem',
                  letterSpacing: '0.05em',
                }}
              >
                SCANNING
              </Typography>
            </Box>
          </Box>

          {/* Mobile Menu Button */}
          <Box sx={{ display: { xs: 'flex', md: 'none' }, ml: 2 }}>
            <Button
              variant="outlined"
              size="small"
              sx={{
                minWidth: 'auto',
                width: 40,
                height: 40,
                borderRadius: '8px',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                color: '#FFFFFF',
                '&:hover': {
                  border: '1px solid #F7931A',
                  backgroundColor: 'rgba(247, 147, 26, 0.1)',
                },
              }}
            >
              <Settings size={18} />
            </Button>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Navbar;