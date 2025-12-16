import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import LogUpload from './components/LogUpload';
import RuleManagement from './components/RuleManagement';
import IaCScanner from './components/IaCScanner';

// Bitcoin DeFi Design System Theme
const bitcoinDefiTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#F7931A', // Bitcoin Orange
      dark: '#EA580C', // Burnt Orange
      light: '#FFD600', // Digital Gold
    },
    secondary: {
      main: '#FFD600', // Digital Gold
      dark: '#F7931A', // Bitcoin Orange
    },
    background: {
      default: '#030304', // True Void
      paper: '#0F1115', // Dark Matter
    },
    text: {
      primary: '#FFFFFF', // Pure Light
      secondary: '#94A3B8', // Stardust
    },
    divider: '#1E293B', // Dim Boundary
    error: {
      main: '#EF4444',
    },
    warning: {
      main: '#F59E0B',
    },
    success: {
      main: '#10B981',
    },
    info: {
      main: '#3B82F6',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontFamily: '"Space Grotesk", sans-serif',
      fontWeight: 700,
      fontSize: '3rem',
      lineHeight: 1.2,
      letterSpacing: '-0.02em',
      '@media (min-width:768px)': {
        fontSize: '4.5rem',
      },
    },
    h2: {
      fontFamily: '"Space Grotesk", sans-serif',
      fontWeight: 600,
      fontSize: '2.25rem',
      lineHeight: 1.3,
      letterSpacing: '-0.02em',
      '@media (min-width:768px)': {
        fontSize: '3rem',
      },
    },
    h3: {
      fontFamily: '"Space Grotesk", sans-serif',
      fontWeight: 600,
      fontSize: '1.875rem',
      lineHeight: 1.3,
      '@media (min-width:768px)': {
        fontSize: '2.25rem',
      },
    },
    h4: {
      fontFamily: '"Space Grotesk", sans-serif',
      fontWeight: 600,
      fontSize: '1.5rem',
      lineHeight: 1.4,
    },
    h5: {
      fontFamily: '"Space Grotesk", sans-serif',
      fontWeight: 600,
      fontSize: '1.25rem',
      lineHeight: 1.4,
    },
    h6: {
      fontFamily: '"Space Grotesk", sans-serif',
      fontWeight: 600,
      fontSize: '1.125rem',
      lineHeight: 1.4,
    },
    body1: {
      fontFamily: '"Inter", sans-serif',
      fontSize: '1rem',
      lineHeight: 1.6,
      '@media (min-width:768px)': {
        fontSize: '1.125rem',
      },
    },
    body2: {
      fontFamily: '"Inter", sans-serif',
      fontSize: '0.875rem',
      lineHeight: 1.6,
    },
    button: {
      fontFamily: '"JetBrains Mono", monospace',
      fontSize: '0.875rem',
      fontWeight: 500,
      textTransform: 'uppercase',
      letterSpacing: '0.1em',
    },
    caption: {
      fontFamily: '"JetBrains Mono", monospace',
      fontSize: '0.75rem',
      fontWeight: 400,
      letterSpacing: '0.05em',
    },
  },
  shape: {
    borderRadius: 16,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: `
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
        
        body {
          background: #030304;
          background-image: 
            linear-gradient(to right, rgba(30, 41, 59, 0.5) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(30, 41, 59, 0.5) 1px, transparent 1px);
          background-size: 50px 50px;
          mask-image: radial-gradient(circle at center, black 40%, transparent 100%);
        }
        
        .gradient-text {
          background: linear-gradient(to right, #F7931A, #FFD600);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        
        .bitcoin-glow {
          box-shadow: 0 0 20px -5px rgba(247, 147, 26, 0.5);
        }
        
        .gold-glow {
          box-shadow: 0 0 20px rgba(255, 214, 0, 0.3);
        }
        
        .glass-morphism {
          backdrop-filter: blur(16px);
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .holographic-gradient {
          background: linear-gradient(135deg, rgba(247, 147, 26, 0.1) 0%, rgba(255, 214, 0, 0.1) 100%);
        }
        
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-20px); }
        }
        
        .animate-float {
          animation: float 8s ease-in-out infinite;
        }
        
        @keyframes pulse-glow {
          0%, 100% { box-shadow: 0 0 20px -5px rgba(247, 147, 26, 0.5); }
          50% { box-shadow: 0 0 30px -5px rgba(247, 147, 26, 0.8); }
        }
        
        .animate-pulse-glow {
          animation: pulse-glow 2s ease-in-out infinite;
        }
      `,
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '9999px', // Full rounded
          minHeight: '44px',
          fontFamily: '"JetBrains Mono", monospace',
          fontSize: '0.875rem',
          fontWeight: 500,
          textTransform: 'uppercase',
          letterSpacing: '0.1em',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'scale(1.05)',
          },
        },
        contained: {
          background: 'linear-gradient(to right, #EA580C, #F7931A)',
          color: '#FFFFFF',
          boxShadow: '0 0 20px -5px rgba(234, 88, 12, 0.5)',
          border: 'none',
          '&:hover': {
            background: 'linear-gradient(to right, #EA580C, #F7931A)',
            boxShadow: '0 0 30px -5px rgba(247, 147, 26, 0.6)',
            transform: 'scale(1.05)',
          },
        },
        outlined: {
          background: 'transparent',
          color: '#FFFFFF',
          border: '2px solid rgba(255, 255, 255, 0.2)',
          '&:hover': {
            background: 'rgba(255, 255, 255, 0.1)',
            border: '2px solid #FFFFFF',
            transform: 'scale(1.05)',
          },
        },
        text: {
          color: '#F7931A',
          '&:hover': {
            background: 'rgba(255, 255, 255, 0.1)',
            color: '#FFD600',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: '#0F1115',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: '16px',
          padding: '32px',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-4px)',
            border: '1px solid rgba(247, 147, 26, 0.5)',
            boxShadow: '0 0 30px -10px rgba(247, 147, 26, 0.2)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            borderRadius: '8px',
            fontFamily: '"Inter", sans-serif',
            '& fieldset': {
              border: 'none',
              borderBottom: '2px solid rgba(255, 255, 255, 0.2)',
              borderRadius: 0,
            },
            '&:hover fieldset': {
              borderBottom: '2px solid rgba(247, 147, 26, 0.5)',
            },
            '&.Mui-focused fieldset': {
              borderBottom: '2px solid #F7931A',
              boxShadow: '0 10px 20px -10px rgba(247, 147, 26, 0.3)',
            },
          },
          '& .MuiInputLabel-root': {
            color: 'rgba(255, 255, 255, 0.7)',
            fontFamily: '"Inter", sans-serif',
            '&.Mui-focused': {
              color: '#F7931A',
            },
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          backgroundColor: 'rgba(247, 147, 26, 0.2)',
          border: '1px solid rgba(247, 147, 26, 0.5)',
          color: '#F7931A',
          fontFamily: '"JetBrains Mono", monospace',
          fontSize: '0.75rem',
          fontWeight: 500,
          letterSpacing: '0.05em',
          borderRadius: '8px',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: '#0F1115',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: '16px',
        },
      },
    },
    MuiTabs: {
      styleOverrides: {
        root: {
          '& .MuiTab-root': {
            fontFamily: '"JetBrains Mono", monospace',
            fontSize: '0.875rem',
            fontWeight: 500,
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
            color: '#94A3B8',
            '&.Mui-selected': {
              color: '#F7931A',
            },
          },
          '& .MuiTabs-indicator': {
            backgroundColor: '#F7931A',
            height: '3px',
            borderRadius: '2px',
          },
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={bitcoinDefiTheme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: '100vh',
          backgroundColor: '#030304',
          position: 'relative',
          '&::before': {
            content: '""',
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: `
              radial-gradient(circle at 20% 50%, rgba(247, 147, 26, 0.1) 0%, transparent 50%),
              radial-gradient(circle at 80% 20%, rgba(255, 214, 0, 0.05) 0%, transparent 50%),
              radial-gradient(circle at 40% 80%, rgba(234, 88, 12, 0.08) 0%, transparent 50%)
            `,
            pointerEvents: 'none',
            zIndex: 0,
          }
        }}
      >
        <Router>
          <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', position: 'relative', zIndex: 1 }}>
            <Navbar />
            <Box component="main" sx={{ flexGrow: 1 }}>
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/logs" element={<LogUpload />} />
                <Route path="/rules" element={<RuleManagement />} />
                <Route path="/scanner" element={<IaCScanner />} />
              </Routes>
            </Box>
          </Box>
        </Router>
      </Box>
    </ThemeProvider>
  );
}

export default App;