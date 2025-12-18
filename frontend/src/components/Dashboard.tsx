import React, { useState } from 'react';
import {
  Shield,
  Zap,
  BarChart3,
  FileSearch,
  Settings,
  Activity,
  Globe,
  CheckCircle,
  Copy,
  ExternalLink,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button } from './ui/Button';
import { Card } from './ui/Card';
import { SectionLabel } from './ui/SectionLabel';

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
      label: 'Threats Blocked', 
      value: '2,847', 
      change: '+12%',
      icon: <Shield size={24} />,
      trend: 'up'
    },
    { 
      label: 'Scans Completed', 
      value: '156K', 
      change: '+8%',
      icon: <FileSearch size={24} />,
      trend: 'up'
    },
    { 
      label: 'Rules Active', 
      value: '342', 
      change: '+5%',
      icon: <Settings size={24} />,
      trend: 'up'
    },
    { 
      label: 'System Uptime', 
      value: '99.9%', 
      change: 'Stable',
      icon: <Activity size={24} />,
      trend: 'stable'
    }
  ];

  const features = [
    {
      title: 'AI-Powered Log Analysis',
      description: 'Advanced machine learning algorithms detect anomalies and security threats in real-time across your cloud infrastructure.',
      icon: <BarChart3 size={32} />,
      action: () => navigate('/logs'),
      actionText: 'Analyze Logs',
      highlights: ['Real-time Detection', 'ML Algorithms', 'Cloud Integration'],
    },
    {
      title: 'Infrastructure Security Scanner',
      description: 'Comprehensive Terraform and IaC security scanning with 150+ built-in rules and custom policy enforcement.',
      icon: <Shield size={32} />,
      action: () => navigate('/scanner'),
      actionText: 'Scan Infrastructure',
      highlights: ['150+ Rules', 'Terraform Support', 'Policy Engine'],
    },
    {
      title: 'Intelligent Rule Engine',
      description: 'Automatically generate and manage security rules based on detected patterns and threat intelligence.',
      icon: <Settings size={32} />,
      action: () => navigate('/rules'),
      actionText: 'Manage Rules',
      highlights: ['Auto-Generation', 'Pattern Learning', 'Threat Intel'],
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
    <div className="min-h-screen">
      {/* Hero Section */}
      <section style={{ padding: '3rem 0' }}>
        <div style={{ maxWidth: '64rem', margin: '0 auto', padding: '0 1.5rem', textAlign: 'center' }}>
          <SectionLabel>Enterprise Security Platform</SectionLabel>
          
          <h1 style={{ 
            fontFamily: 'var(--font-display)', 
            fontSize: 'clamp(2.5rem, 5vw, 4rem)', 
            fontWeight: 400, 
            lineHeight: 1.1, 
            letterSpacing: '-0.02em',
            textAlign: 'center', 
            marginBottom: '1.5rem',
            color: 'var(--foreground)'
          }}>
            Secure Your <span style={{ color: 'var(--accent)' }}>Cloud</span> Infrastructure
          </h1>
          
          <p style={{ 
            fontFamily: 'var(--font-body)', 
            fontSize: '1.125rem', 
            lineHeight: 1.75, 
            letterSpacing: '0.01em',
            color: 'var(--muted-foreground)', 
            maxWidth: '48rem', 
            margin: '0 auto 2rem auto' 
          }}>
            Enterprise-grade security platform powered by AI and advanced threat detection. 
            Protect your cloud infrastructure with intelligent monitoring and automated response systems.
          </p>
          
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button 
              variant="primary" 
              size="lg"
              onClick={() => navigate('/logs')}
            >
              <Zap size={20} />
              Start Analysis
            </Button>
            <Button 
              variant="secondary" 
              size="lg"
              onClick={() => navigate('/scanner')}
            >
              <Shield size={20} />
              Scan Infrastructure
            </Button>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section style={{ padding: '2rem 0', backgroundColor: 'var(--muted)' }}>
        <div style={{ maxWidth: '80rem', margin: '0 auto', padding: '0 1.5rem' }}>
          <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <SectionLabel>Platform Status</SectionLabel>
            <h2 style={{ 
              fontFamily: 'var(--font-display)', 
              fontSize: '2rem', 
              fontWeight: 400, 
              lineHeight: 1.2, 
              letterSpacing: '-0.01em',
              marginTop: '1rem'
            }}>
              Security <span style={{ color: 'var(--accent)' }}>Operations</span>
            </h2>
          </div>

          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
            gap: '1.5rem' 
          }}>
            {stats.map((stat, index) => (
              <div 
                key={index} 
                style={{
                  backgroundColor: 'var(--card)',
                  border: '1px solid var(--border)',
                  borderTop: '2px solid var(--accent)',
                  borderRadius: 'var(--radius-lg)',
                  boxShadow: 'var(--shadow-sm)',
                  padding: '1.5rem',
                  textAlign: 'center',
                  transition: 'all 200ms ease-out'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.boxShadow = 'var(--shadow-md)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.boxShadow = 'var(--shadow-sm)';
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1rem' }}>
                  <div 
                    style={{ 
                      width: '3rem',
                      height: '3rem',
                      borderRadius: 'var(--radius-lg)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      backgroundColor: 'rgba(184, 134, 11, 0.1)',
                      border: '1px solid var(--accent)',
                      color: 'var(--accent)'
                    }}
                  >
                    {stat.icon}
                  </div>
                </div>
                
                <h3 style={{ 
                  fontFamily: 'var(--font-display)', 
                  fontSize: '1.5rem', 
                  fontWeight: 600, 
                  lineHeight: 1.3,
                  color: 'var(--accent)', 
                  marginBottom: '0.5rem' 
                }}>
                  {stat.value}
                </h3>
                
                <p style={{ 
                  fontFamily: 'var(--font-mono)', 
                  fontSize: '0.75rem', 
                  fontWeight: 500, 
                  letterSpacing: '0.15em', 
                  textTransform: 'uppercase',
                  color: 'var(--muted-foreground)', 
                  marginBottom: '0.5rem' 
                }}>
                  {stat.label}
                </p>
                
                <span 
                  style={{
                    fontSize: '0.75rem',
                    padding: '0.25rem 0.5rem',
                    borderRadius: '9999px',
                    backgroundColor: stat.trend === 'up' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(59, 130, 246, 0.1)',
                    color: stat.trend === 'up' ? '#10B981' : '#3B82F6',
                    border: `1px solid ${stat.trend === 'up' ? '#10B981' : '#3B82F6'}40`
                  }}
                >
                  {stat.change}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="section-padding">
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
            <SectionLabel>Core Features</SectionLabel>
            <h2 className="text-section font-display">
              Security <span style={{ color: 'var(--accent)' }}>Modules</span>
            </h2>
          </div>
          
          <div className="features-grid">
            {features.map((feature, index) => (
              <Card key={index} style={{ padding: '2rem', height: '100%', display: 'flex', flexDirection: 'column' }}>
                {/* Icon */}
                <div 
                  style={{ 
                    width: '4rem',
                    height: '4rem',
                    borderRadius: 'var(--radius-lg)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: '1.5rem',
                    backgroundColor: 'var(--accent)',
                    boxShadow: 'var(--shadow-accent)'
                  }}
                >
                  <div style={{ color: 'white' }}>
                    {feature.icon}
                  </div>
                </div>
                
                <h3 className="text-card-title font-display" style={{ marginBottom: '1rem' }}>
                  {feature.title}
                </h3>
                
                <p className="text-body text-muted" style={{ flexGrow: 1, lineHeight: 1.625, marginBottom: '1.5rem' }}>
                  {feature.description}
                </p>
                
                {/* Highlights */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1.5rem' }}>
                  {feature.highlights.map((highlight, idx) => (
                    <span 
                      key={idx}
                      className="small-caps"
                      style={{ 
                        padding: '0.25rem 0.75rem',
                        fontSize: '0.75rem',
                        fontWeight: 500,
                        borderRadius: '9999px',
                        backgroundColor: 'rgba(184, 134, 11, 0.1)',
                        color: 'var(--accent)',
                        border: '1px solid var(--accent)'
                      }}
                    >
                      {highlight}
                    </span>
                  ))}
                </div>
                
                <Button 
                  variant="ghost" 
                  onClick={feature.action}
                  style={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                >
                  <span>{feature.actionText}</span>
                  <span>→</span>
                </Button>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Quick Commands Section */}
      <section className="section-padding" style={{ backgroundColor: 'var(--muted)' }}>
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
            <SectionLabel>Quick Deployment</SectionLabel>
            <h2 className="text-section font-display">
              Get <span style={{ color: 'var(--accent)' }}>Started</span>
            </h2>
          </div>
          
          <div className="commands-grid">
            {quickCommands.map((section, index) => (
              <Card key={index} style={{ padding: '2rem' }}>
                {/* Header */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                  <div
                    style={{
                      width: '3rem',
                      height: '3rem',
                      borderRadius: 'var(--radius-lg)',
                      backgroundColor: 'rgba(184, 134, 11, 0.1)',
                      border: '1px solid var(--accent)',
                      color: 'var(--accent)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    {section.icon}
                  </div>
                  <h3 className="text-card-title font-display">
                    {section.title}
                  </h3>
                </div>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {section.commands.map((cmd, idx) => (
                    <div key={idx}>
                      <p className="small-caps text-accent" style={{ marginBottom: '0.5rem' }}>
                        {cmd.label}
                      </p>
                      <div 
                        style={{ 
                          padding: '0.75rem',
                          borderRadius: 'var(--radius-md)',
                          border: '1px solid var(--border)',
                          backgroundColor: 'var(--foreground)',
                          transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.borderColor = 'var(--accent)';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.borderColor = 'var(--border)';
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <code 
                            className="font-mono"
                            style={{ color: 'var(--accent-secondary)', flex: 1, fontSize: '0.875rem' }}
                          >
                            {cmd.command}
                          </code>
                          <button
                            onClick={() => copyToClipboard(cmd.command, cmd.command)}
                            style={{ 
                              marginLeft: '0.5rem',
                              padding: '0.25rem',
                              borderRadius: 'var(--radius-sm)',
                              color: copiedCommand === cmd.command ? '#10B981' : 'var(--muted-foreground)',
                              backgroundColor: 'transparent',
                              border: 'none',
                              cursor: 'pointer',
                              transition: 'color 0.2s'
                            }}
                          >
                            {copiedCommand === cmd.command ? <CheckCircle size={16} /> : <Copy size={16} />}
                          </button>
                        </div>
                      </div>
                      <p style={{ fontSize: '0.875rem', color: 'var(--muted-foreground)', marginTop: '0.25rem' }}>
                        {cmd.description}
                      </p>
                    </div>
                  ))}
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="section-padding">
        <div className="container-narrow" style={{ textAlign: 'center' }}>
          <Card className="p-16" elevated>
            <h2 className="text-section font-display" style={{ marginBottom: '1.5rem' }}>
              Ready to <span style={{ color: 'var(--accent)' }}>Secure</span> Your Infrastructure?
            </h2>
            <p className="text-body text-muted" style={{ maxWidth: '42rem', margin: '0 auto 2rem auto' }}>
              Join organizations worldwide protecting their cloud infrastructure with 
              enterprise-grade security and intelligent threat detection.
            </p>
            
            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
              <Button 
                variant="primary" 
                size="lg"
                onClick={() => navigate('/logs')}
              >
                <Zap size={20} />
                Start Security Scan
              </Button>
              <Button 
                variant="secondary" 
                size="lg"
                onClick={() => navigate('/scanner')}
              >
                <ExternalLink size={20} />
                View Documentation
              </Button>
            </div>
          </Card>
        </div>
      </section>
    </div>
  );
};

export default Dashboard;