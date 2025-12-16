import React, { useState } from 'react';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Box,
  Button,
  Chip,
  Paper,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Shield,
  Zap,
  Lock,
  BarChart3,
  FileSearch,
  Settings,
  TrendingUp,
  Activity,
  Globe,
  Layers,
  CheckCircle,
  AlertTriangle,
  Copy,
  ExternalLink,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [copiedCommand, setCopiedCommand] = useState('');

  const copyToClipboard = (text: string, command: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCommand(command);
    setTimeout(() => setCopiedCommand(''), 2000);
  };

  const stats = [
    { 
      label: 'THREATS BLOCKED', 
      value: '2,847', 
      change: '+12%',
      icon: <Shield size={24} />,
      color: '#10B981',
      trend: 'up'
    },
    { 
      label: 'SCANS COMPLETED', 
      value: '156K', 
      change: '+8%',
      icon: <FileSearch size={24} />,
      color: '#F7931A',
      trend: 'up'
    },
    { 
      label: 'RULES ACTIVE', 
      value: '342', 
      change: '+5%',
      icon: <Settings size={24} />,
      color: '#FFD600',
      trend: 'up'
    },
    { 
      label: 'UPTIME', 
      value: '99.9%', 
      change: 'STABLE',
      icon: <Activity size={24} />,
      color: '#3B82F6',
      trend: 'stable'
    }
  ];

  const features = [
    {
      title: 'AI-Powered Log Analysis',
      description: 'Advanced machine learning algorithms detect anomalies and security threats in real-time across your AWS infrastructure.',
      icon: <BarChart3 size={32} />,
      action: () => navigate('/logs'),
      actionText: 'ANALYZE LOGS',
      highlights: ['Real-time Detection', 'ML Algorithms', 'AWS Integration'],
      gradient: 'linear-gradient(135deg, #F7931A, #FFD600)',
    },
    {
      title: 'Infrastructure Security Scanner',
      description: 'Comprehensive Terraform and IaC security scanning with 150+ built-in rules and custom policy enforcement.',
      icon: <Shield size={32} />,
      action: () => navigate('/scanner'),
      actionText: 'SCAN CODE',
      highlights: ['150+ Rules', 'Terraform Support', 'Policy Engine'],
      gradient: 'linear-gradient(135deg, #EA580C, #F7931A)',
    },
    {
      title: 'Intelligent Rule Engine',
      description: 'Automatically generate and manage security rules based on detected patterns and threat intelligence.',
      icon: <Settings size={32} />,
      action: () => navigate('/rules'),
      actionText: 'MANAGE RULES',
      highlights: ['Auto-Generation', 'Pattern Learning', 'Threat Intel'],
      gradient: 'linear-gradient(135deg, #FFD600, #F7931A)',
    }
  ];

  const quickCommands = [
    {
      title: 'CLI Installation',
      commands: [
        { label: 'Install CLI', command: 'pip install securon-cli', description: 'Install the Securon CLI tool' },
        { label: 'Scan Infrastructure', command: 'securon scan --path ./terraform', description: 'Scan Terraform files' },
        { label: 'Analyze Logs', command: 'securon logs --file vpc-flow.json', description: 'Process log files' }
      ],
      icon: <FileSearch size={24} />,
    },
    {
      title: 'Docker Deployment',
      commands: [
        { label: 'Pull Image', command: 'docker pull securon/platform:latest', description: 'Get the latest image' },
        { label: 'Run Scanner', command: 'docker run -v $(pwd):/workspace securon/platform scan', description: 'Run in container' }
      ],
      icon: <Globe size={24} />,
    }
  ];

  return (
    <Box sx={{ minHeight: '100vh', position: 'relative' }}>
      <Container maxWidth="xl" sx={{ py: 8 }}>
        {/* Hero Section with Floating Orb */}
        <Box sx={{ 
          textAlign: 'center', 
          py: { xs: 8, md: 16 },
          position: 'relative',
          mb: 12,
        }}>
          {/* Floating 3D Orb */}
          <Box
            sx={{
              position: 'absolute',
              top: '50%',
              right: { xs: '50%', lg: '10%' },
              transform: { xs: 'translate(50%, -50%)', lg: 'translateY(-50%)' },
              width: { xs: 200, md: 300 },
              height: { xs: 200, md: 300 },
              zIndex: 0,
              opacity: { xs: 0.3, lg: 1 },
            }}
            className="animate-float"
          >
            {/* Outer Ring */}
            <Box
              sx={{
                position: 'absolute',
                inset: 0,
                border: '2px solid rgba(247, 147, 26, 0.3)',
                borderRadius: '50%',
                animation: 'spin 20s linear infinite',
                '@keyframes spin': {
                  '0%': { transform: 'rotate(0deg)' },
                  '100%': { transform: 'rotate(360deg)' },
                },
              }}
            />
            {/* Inner Ring */}
            <Box
              sx={{
                position: 'absolute',
                inset: 20,
                border: '1px solid rgba(255, 214, 0, 0.4)',
                borderRadius: '50%',
                animation: 'spin 15s linear infinite reverse',
              }}
            />
            {/* Core */}
            <Box
              sx={{
                position: 'absolute',
                inset: 60,
                background: 'radial-gradient(circle, rgba(247, 147, 26, 0.8), rgba(234, 88, 12, 0.4))',
                borderRadius: '50%',
                boxShadow: '0 0 60px rgba(247, 147, 26, 0.6)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Lock size={48} color="#FFFFFF" />
            </Box>
          </Box>

          {/* Hero Content */}
          <Box sx={{ position: 'relative', zIndex: 1, maxWidth: 800, mx: 'auto' }}>
            <Typography 
              variant="h1" 
              sx={{ 
                mb: 4,
                fontWeight: 700,
                '& .gradient-text': {
                  background: 'linear-gradient(to right, #F7931A, #FFD600)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                },
              }}
            >
              SECURE YOUR <span className="gradient-text">DEFI</span> INFRASTRUCTURE
            </Typography>
            
            <Typography 
              variant="body1" 
              sx={{ 
                mb: 6, 
                color: '#94A3B8',
                maxWidth: 600, 
                mx: 'auto',
                fontSize: { xs: '1.125rem', md: '1.25rem' },
                lineHeight: 1.7,
              }}
            >
              Enterprise-grade security platform powered by AI and blockchain technology. 
              Protect your digital assets with military-grade encryption and real-time threat detection.
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 3, justifyContent: 'center', flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                size="large"
                onClick={() => navigate('/logs')}
                startIcon={<Zap size={20} />}
                sx={{ 
                  px: 4, 
                  py: 2,
                  fontSize: '0.875rem',
                  minWidth: 180,
                }}
                className="bitcoin-glow"
              >
                START ANALYSIS
              </Button>
              <Button
                variant="outlined"
                size="large"
                onClick={() => navigate('/scanner')}
                startIcon={<Shield size={20} />}
                sx={{ 
                  px: 4, 
                  py: 2,
                  fontSize: '0.875rem',
                  minWidth: 180,
                }}
              >
                SCAN INFRASTRUCTURE
              </Button>
            </Box>
          </Box>
        </Box>

        {/* Stats Grid */}
        <Box sx={{ mb: 16 }}>
          <Typography 
            variant="h3" 
            sx={{ 
              textAlign: 'center',
              mb: 8,
              fontWeight: 600,
              '& .gradient-text': {
                background: 'linear-gradient(to right, #F7931A, #FFD600)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              },
            }}
          >
            NETWORK <span className="gradient-text">STATUS</span>
          </Typography>

          <Grid container spacing={4}>
            {stats.map((stat, index) => (
              <Grid item xs={12} sm={6} lg={3} key={index}>
                <Card 
                  sx={{ 
                    height: '100%',
                    background: 'rgba(15, 17, 21, 0.8)',
                    backdropFilter: 'blur(16px)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    position: 'relative',
                    overflow: 'hidden',
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: 3,
                      background: `linear-gradient(to right, ${stat.color}, transparent)`,
                    },
                    '&:hover': {
                      border: `1px solid ${stat.color}40`,
                      boxShadow: `0 0 30px -10px ${stat.color}40`,
                    },
                  }}
                >
                  <CardContent sx={{ p: 4 }}>
                    <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                      <Box
                        sx={{
                          width: 48,
                          height: 48,
                          backgroundColor: `${stat.color}20`,
                          border: `1px solid ${stat.color}50`,
                          borderRadius: '12px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: stat.color,
                        }}
                      >
                        {stat.icon}
                      </Box>
                      <Chip
                        label={stat.change}
                        size="small"
                        sx={{
                          backgroundColor: stat.trend === 'up' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(59, 130, 246, 0.2)',
                          color: stat.trend === 'up' ? '#10B981' : '#3B82F6',
                          border: `1px solid ${stat.trend === 'up' ? '#10B981' : '#3B82F6'}40`,
                          fontFamily: '"JetBrains Mono", monospace',
                          fontSize: '0.7rem',
                        }}
                      />
                    </Box>
                    
                    <Typography 
                      variant="h4" 
                      sx={{ 
                        color: '#FFFFFF',
                        fontFamily: '"Space Grotesk", sans-serif',
                        fontWeight: 700,
                        mb: 1,
                      }}
                    >
                      {stat.value}
                    </Typography>
                    
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        color: '#94A3B8',
                        fontFamily: '"JetBrains Mono", monospace',
                        letterSpacing: '0.1em',
                        fontSize: '0.75rem',
                      }}
                    >
                      {stat.label}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* Features Section */}
        <Box sx={{ mb: 16 }}>
          <Typography 
            variant="h3" 
            sx={{ 
              textAlign: 'center',
              mb: 8,
              fontWeight: 600,
            }}
          >
            SECURITY <span className="gradient-text">MODULES</span>
          </Typography>
          
          <Grid container spacing={4}>
            {features.map((feature, index) => (
              <Grid item xs={12} md={4} key={index}>
                <Card 
                  sx={{ 
                    height: '100%', 
                    display: 'flex', 
                    flexDirection: 'column',
                    background: 'rgba(15, 17, 21, 0.6)',
                    backdropFilter: 'blur(16px)',
                    position: 'relative',
                    overflow: 'hidden',
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      background: feature.gradient,
                      opacity: 0.05,
                      zIndex: 0,
                    },
                    '&:hover': {
                      '&::before': {
                        opacity: 0.1,
                      },
                    },
                  }}
                >
                  <CardContent sx={{ flexGrow: 1, p: 4, position: 'relative', zIndex: 1 }}>
                    {/* Icon Container */}
                    <Box
                      sx={{
                        width: 64,
                        height: 64,
                        background: feature.gradient,
                        borderRadius: '16px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mb: 3,
                        boxShadow: '0 0 20px -5px rgba(247, 147, 26, 0.5)',
                      }}
                    >
                      {React.cloneElement(feature.icon, { color: '#FFFFFF' })}
                    </Box>
                    
                    <Typography 
                      variant="h5" 
                      sx={{ 
                        color: '#FFFFFF',
                        fontFamily: '"Space Grotesk", sans-serif',
                        fontWeight: 600,
                        mb: 2,
                      }}
                    >
                      {feature.title}
                    </Typography>
                    
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        mb: 3, 
                        lineHeight: 1.6,
                        color: '#94A3B8',
                      }}
                    >
                      {feature.description}
                    </Typography>
                    
                    <Box sx={{ mb: 3 }}>
                      {feature.highlights.map((highlight, idx) => (
                        <Chip 
                          key={idx}
                          label={highlight} 
                          size="small" 
                          sx={{ 
                            m: 0.5,
                            backgroundColor: 'rgba(247, 147, 26, 0.2)',
                            border: '1px solid rgba(247, 147, 26, 0.3)',
                            color: '#F7931A',
                            fontFamily: '"JetBrains Mono", monospace',
                            fontSize: '0.7rem',
                          }}
                        />
                      ))}
                    </Box>
                    
                    <Button
                      variant="contained"
                      fullWidth
                      onClick={feature.action}
                      sx={{ 
                        mt: 'auto',
                        py: 1.5,
                        fontSize: '0.875rem',
                      }}
                    >
                      {feature.actionText}
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* Quick Commands Section */}
        <Box sx={{ mb: 16 }}>
          <Typography 
            variant="h3" 
            sx={{ 
              textAlign: 'center',
              mb: 8,
              fontWeight: 600,
            }}
          >
            QUICK <span className="gradient-text">DEPLOYMENT</span>
          </Typography>
          
          <Grid container spacing={4}>
            {quickCommands.map((section, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Card 
                  sx={{ 
                    height: '100%',
                    background: 'rgba(0, 0, 0, 0.4)',
                    backdropFilter: 'blur(16px)',
                  }}
                >
                  <CardContent sx={{ p: 4 }}>
                    {/* Header */}
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 4, gap: 2 }}>
                      <Box
                        sx={{
                          width: 40,
                          height: 40,
                          backgroundColor: 'rgba(247, 147, 26, 0.2)',
                          border: '1px solid rgba(247, 147, 26, 0.5)',
                          borderRadius: '8px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: '#F7931A',
                        }}
                      >
                        {section.icon}
                      </Box>
                      <Typography 
                        variant="h6" 
                        sx={{ 
                          color: '#FFFFFF',
                          fontFamily: '"Space Grotesk", sans-serif',
                          fontWeight: 600,
                        }}
                      >
                        {section.title}
                      </Typography>
                    </Box>
                    
                    <Box>
                      {section.commands.map((cmd, idx) => (
                        <Box key={idx} sx={{ mb: 3 }}>
                          <Typography 
                            variant="subtitle2" 
                            sx={{ 
                              color: '#F7931A', 
                              fontFamily: '"JetBrains Mono", monospace',
                              fontSize: '0.8rem',
                              mb: 1,
                              letterSpacing: '0.05em',
                            }}
                          >
                            {cmd.label}
                          </Typography>
                          <Paper 
                            sx={{ 
                              p: 2, 
                              backgroundColor: '#000000',
                              border: '1px solid rgba(255, 255, 255, 0.1)',
                              borderRadius: '8px',
                              position: 'relative',
                              '&:hover': { 
                                border: '1px solid rgba(247, 147, 26, 0.3)',
                              },
                            }}
                          >
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Typography 
                                component="code" 
                                sx={{ 
                                  color: '#FFD600', 
                                  fontFamily: '"JetBrains Mono", monospace',
                                  fontSize: '0.85rem', 
                                  flex: 1,
                                }}
                              >
                                {cmd.command}
                              </Typography>
                              <Tooltip title={copiedCommand === cmd.command ? 'Copied!' : 'Copy Command'}>
                                <IconButton
                                  size="small"
                                  onClick={() => copyToClipboard(cmd.command, cmd.command)}
                                  sx={{ 
                                    color: copiedCommand === cmd.command ? '#10B981' : '#94A3B8', 
                                    ml: 1,
                                    '&:hover': {
                                      color: '#F7931A',
                                    }
                                  }}
                                >
                                  {copiedCommand === cmd.command ? <CheckCircle size={16} /> : <Copy size={16} />}
                                </IconButton>
                              </Tooltip>
                            </Box>
                          </Paper>
                          <Typography 
                            variant="caption" 
                            sx={{ 
                              mt: 1, 
                              color: '#94A3B8',
                              display: 'block',
                              fontSize: '0.75rem',
                            }}
                          >
                            {cmd.description}
                          </Typography>
                        </Box>
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* Call to Action */}
        <Box 
          sx={{ 
            textAlign: 'center', 
            py: 12,
            background: 'rgba(15, 17, 21, 0.8)',
            backdropFilter: 'blur(16px)',
            borderRadius: '24px',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            position: 'relative',
            overflow: 'hidden',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'linear-gradient(135deg, rgba(247, 147, 26, 0.1), rgba(255, 214, 0, 0.05))',
            },
          }}
        >
          <Box sx={{ position: 'relative', zIndex: 1 }}>
            <Typography 
              variant="h2" 
              sx={{ 
                mb: 3,
                fontWeight: 700,
              }}
            >
              READY TO <span className="gradient-text">SECURE</span> YOUR ASSETS?
            </Typography>
            <Typography 
              variant="body1" 
              sx={{ 
                mb: 6, 
                maxWidth: 600, 
                mx: 'auto',
                color: '#94A3B8',
                fontSize: '1.125rem',
                lineHeight: 1.6,
              }}
            >
              Join thousands of organizations protecting their DeFi infrastructure with enterprise-grade security.
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 3, justifyContent: 'center', flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                size="large"
                onClick={() => navigate('/logs')}
                startIcon={<Zap size={20} />}
                sx={{ 
                  px: 6, 
                  py: 2,
                  fontSize: '0.875rem',
                  minWidth: 200,
                }}
                className="bitcoin-glow"
              >
                START SCANNING
              </Button>
              <Button
                variant="outlined"
                size="large"
                onClick={() => navigate('/scanner')}
                startIcon={<ExternalLink size={20} />}
                sx={{ 
                  px: 6, 
                  py: 2,
                  fontSize: '0.875rem',
                  minWidth: 200,
                }}
              >
                VIEW DOCUMENTATION
              </Button>
            </Box>
          </Box>
        </Box>
      </Container>
    </Box>
  );
};

export default Dashboard;