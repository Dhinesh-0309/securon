import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Chip,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  Grid,
  Container,
  Card,
  CardContent,
  Paper,
} from '@mui/material';
import {
  CheckCircle,
  X,
  Shield,
  Settings,
  AlertTriangle,
  Info,
  Eye,
  ThumbsUp,
  ThumbsDown,
  Wrench,
  Activity,
  Clock,
  Target,
} from 'lucide-react';
import apiClient from '../config/api';
import { SecurityRule, Severity } from '../types';

interface RulesData {
  active_rules: SecurityRule[];
  candidate_rules: SecurityRule[];
}

const RuleManagement: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [rulesData, setRulesData] = useState<RulesData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRule, setSelectedRule] = useState<SecurityRule | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/api/rules');
      setRulesData(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch rules');
    } finally {
      setLoading(false);
    }
  };

  const handleApproveRule = async (ruleId: string) => {
    try {
      await apiClient.post(`/api/rules/${ruleId}/approve`);
      await fetchRules();
      setDialogOpen(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to approve rule');
    }
  };

  const handleRejectRule = async (ruleId: string) => {
    try {
      await apiClient.post(`/api/rules/${ruleId}/reject`);
      await fetchRules();
      setDialogOpen(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to reject rule');
    }
  };

  const getSeverityIcon = (severity: Severity) => {
    switch (severity) {
      case Severity.CRITICAL:
        return <AlertTriangle size={20} color="#EF4444" />;
      case Severity.HIGH:
        return <AlertTriangle size={20} color="#F59E0B" />;
      case Severity.MEDIUM:
        return <Info size={20} color="#3B82F6" />;
      case Severity.LOW:
        return <Info size={20} color="#10B981" />;
      default:
        return <Info size={20} />;
    }
  };

  const getSeverityColor = (severity: Severity) => {
    switch (severity) {
      case Severity.CRITICAL:
        return '#EF4444';
      case Severity.HIGH:
        return '#F59E0B';
      case Severity.MEDIUM:
        return '#3B82F6';
      case Severity.LOW:
        return '#10B981';
      default:
        return '#94A3B8';
    }
  };

  const openRuleDialog = (rule: SecurityRule) => {
    setSelectedRule(rule);
    setDialogOpen(true);
  };

  const RuleList: React.FC<{ rules: SecurityRule[]; showActions?: boolean }> = ({ 
    rules, 
    showActions = false 
  }) => (
    <Box>
      {rules.map((rule, index) => (
        <Card 
          key={rule.id} 
          sx={{ 
            mb: 3,
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
              background: `linear-gradient(to right, ${getSeverityColor(rule.severity)}, transparent)`,
            },
            '&:hover': {
              border: `1px solid ${getSeverityColor(rule.severity)}40`,
              boxShadow: `0 0 20px -5px ${getSeverityColor(rule.severity)}40`,
            },
          }}
        >
          <CardContent sx={{ p: 4 }}>
            <Box display="flex" alignItems="flex-start" gap={3}>
              {/* Rule Icon */}
              <Box
                sx={{
                  width: 48,
                  height: 48,
                  backgroundColor: `${getSeverityColor(rule.severity)}20`,
                  border: `1px solid ${getSeverityColor(rule.severity)}50`,
                  borderRadius: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}
              >
                {getSeverityIcon(rule.severity)}
              </Box>
              
              <Box flex={1}>
                {/* Rule Header */}
                <Box display="flex" alignItems="center" gap={2} mb={2}>
                  <Typography 
                    variant="h6" 
                    sx={{ 
                      color: '#FFFFFF',
                      fontFamily: '"Space Grotesk", sans-serif',
                      fontWeight: 600,
                    }}
                  >
                    {rule.name}
                  </Typography>
                  
                  <Chip
                    label={`#${index + 1}`}
                    size="small"
                    sx={{
                      backgroundColor: 'rgba(247, 147, 26, 0.2)',
                      color: '#F7931A',
                      border: '1px solid rgba(247, 147, 26, 0.3)',
                      fontFamily: '"JetBrains Mono", monospace',
                      fontSize: '0.7rem',
                    }}
                  />
                </Box>
                
                {/* Rule Metadata */}
                <Box display="flex" gap={1} flexWrap="wrap" mb={2}>
                  <Chip
                    label={rule.severity}
                    size="small"
                    sx={{
                      backgroundColor: `${getSeverityColor(rule.severity)}20`,
                      color: getSeverityColor(rule.severity),
                      border: `1px solid ${getSeverityColor(rule.severity)}40`,
                      fontFamily: '"JetBrains Mono", monospace',
                      fontSize: '0.7rem',
                    }}
                  />
                  <Chip
                    label={rule.source}
                    size="small"
                    sx={{
                      backgroundColor: 'rgba(59, 130, 246, 0.2)',
                      color: '#3B82F6',
                      border: '1px solid rgba(59, 130, 246, 0.3)',
                      fontFamily: '"JetBrains Mono", monospace',
                      fontSize: '0.7rem',
                    }}
                  />
                  <Chip
                    label={rule.status}
                    size="small"
                    sx={{
                      backgroundColor: rule.status === 'ACTIVE' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(156, 163, 175, 0.2)',
                      color: rule.status === 'ACTIVE' ? '#10B981' : '#9CA3AF',
                      border: `1px solid ${rule.status === 'ACTIVE' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(156, 163, 175, 0.3)'}`,
                      fontFamily: '"JetBrains Mono", monospace',
                      fontSize: '0.7rem',
                    }}
                  />
                </Box>
                
                {/* Rule Description */}
                <Typography 
                  variant="body2" 
                  sx={{ 
                    color: '#94A3B8',
                    mb: 2,
                    lineHeight: 1.6,
                  }}
                >
                  {rule.description}
                </Typography>
                
                {/* Rule Timestamp */}
                <Box display="flex" alignItems="center" gap={1} mb={3}>
                  <Clock size={14} color="#94A3B8" />
                  <Typography 
                    variant="caption" 
                    sx={{ 
                      color: '#94A3B8',
                      fontFamily: '"JetBrains Mono", monospace',
                      fontSize: '0.75rem',
                    }}
                  >
                    CREATED: {new Date(rule.created_at).toLocaleDateString()}
                  </Typography>
                </Box>
                
                {/* Actions */}
                <Box display="flex" gap={2} alignItems="center" flexWrap="wrap">
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => openRuleDialog(rule)}
                    startIcon={<Eye size={16} />}
                    sx={{
                      fontSize: '0.75rem',
                      py: 1,
                      px: 2,
                    }}
                  >
                    VIEW DETAILS
                  </Button>
                  
                  {showActions && (
                    <>
                      <Button
                        variant="contained"
                        size="small"
                        startIcon={<ThumbsUp size={16} />}
                        onClick={() => handleApproveRule(rule.id)}
                        sx={{
                          background: 'linear-gradient(135deg, #10B981, #059669)',
                          fontSize: '0.75rem',
                          py: 1,
                          px: 2,
                          '&:hover': {
                            background: 'linear-gradient(135deg, #059669, #047857)',
                          },
                        }}
                      >
                        APPROVE
                      </Button>
                      <Button
                        variant="contained"
                        size="small"
                        startIcon={<ThumbsDown size={16} />}
                        onClick={() => handleRejectRule(rule.id)}
                        sx={{
                          background: 'linear-gradient(135deg, #EF4444, #DC2626)',
                          fontSize: '0.75rem',
                          py: 1,
                          px: 2,
                          '&:hover': {
                            background: 'linear-gradient(135deg, #DC2626, #B91C1C)',
                          },
                        }}
                      >
                        REJECT
                      </Button>
                    </>
                  )}
                </Box>
              </Box>
            </Box>
          </CardContent>
        </Card>
      ))}
    </Box>
  );

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 8 }}>
        <Box 
          sx={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center',
            minHeight: '60vh',
            flexDirection: 'column',
            gap: 4,
          }}
        >
          <Box
            sx={{
              width: 80,
              height: 80,
              background: 'linear-gradient(135deg, #F7931A, #FFD600)',
              borderRadius: '20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              animation: 'pulse 2s infinite',
              '@keyframes pulse': {
                '0%, 100%': { transform: 'scale(1)', opacity: 1 },
                '50%': { transform: 'scale(1.05)', opacity: 0.8 },
              },
            }}
          >
            <Wrench size={40} color="#FFFFFF" />
          </Box>
          <Typography 
            variant="h5" 
            sx={{ 
              color: '#FFFFFF',
              fontFamily: '"Space Grotesk", sans-serif',
              fontWeight: 600,
            }}
          >
            LOADING SECURITY RULES...
          </Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 8 }}>
      {/* Header Section */}
      <Box sx={{ textAlign: 'center', mb: 8 }}>
        <Box
          sx={{
            width: 80,
            height: 80,
            background: 'linear-gradient(135deg, #F7931A, #FFD600)',
            borderRadius: '20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            mx: 'auto',
            mb: 4,
            boxShadow: '0 0 30px -5px rgba(247, 147, 26, 0.6)',
          }}
        >
          <Settings size={40} color="#FFFFFF" />
        </Box>

        <Typography 
          variant="h2" 
          sx={{ 
            mb: 2,
            fontWeight: 700,
            '& .gradient-text': {
              background: 'linear-gradient(to right, #F7931A, #FFD600)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            },
          }}
        >
          RULE <span className="gradient-text">ENGINE</span>
        </Typography>
        
        <Typography 
          variant="body1" 
          sx={{ 
            color: '#94A3B8',
            maxWidth: 600,
            mx: 'auto',
            fontSize: '1.125rem',
            lineHeight: 1.6,
          }}
        >
          Manage and approve AI-generated security rules. Review candidate rules and activate them 
          to strengthen your infrastructure protection.
        </Typography>
      </Box>

      {/* Error Display */}
      {error && (
        <Card 
          sx={{ 
            mb: 6,
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            backdropFilter: 'blur(16px)',
          }}
        >
          <CardContent sx={{ p: 4 }}>
            <Box display="flex" alignItems="center" gap={2}>
              <AlertTriangle size={24} color="#EF4444" />
              <Box>
                <Typography 
                  variant="h6" 
                  sx={{ 
                    color: '#EF4444',
                    fontFamily: '"Space Grotesk", sans-serif',
                    fontWeight: 600,
                    mb: 1,
                  }}
                >
                  SYSTEM ERROR
                </Typography>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    color: '#FFFFFF',
                  }}
                >
                  {error}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Main Content Card */}
      <Card 
        sx={{ 
          background: 'rgba(15, 17, 21, 0.8)',
          backdropFilter: 'blur(16px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
        }}
      >
        {/* Tabs Header */}
        <Box sx={{ 
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          p: 2,
        }}>
          <Tabs 
            value={tabValue} 
            onChange={(_, newValue) => setTabValue(newValue)}
            sx={{
              '& .MuiTab-root': {
                minHeight: 60,
                fontSize: '0.875rem',
                fontWeight: 500,
                fontFamily: '"JetBrains Mono", monospace',
                letterSpacing: '0.1em',
                color: '#94A3B8',
                '&.Mui-selected': {
                  color: '#F7931A',
                },
              },
              '& .MuiTabs-indicator': {
                backgroundColor: '#F7931A',
                height: 3,
                borderRadius: '2px',
              }
            }}
          >
            <Tab
              icon={
                <Box
                  sx={{
                    width: 32,
                    height: 32,
                    backgroundColor: tabValue === 0 ? 'rgba(16, 185, 129, 0.2)' : 'rgba(255, 255, 255, 0.1)',
                    border: `1px solid ${tabValue === 0 ? 'rgba(16, 185, 129, 0.5)' : 'rgba(255, 255, 255, 0.2)'}`,
                    borderRadius: '8px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    transition: 'all 0.3s ease',
                  }}
                >
                  <Shield size={16} color={tabValue === 0 ? '#10B981' : '#94A3B8'} />
                </Box>
              }
              label={`ACTIVE RULES (${rulesData?.active_rules.length || 0})`}
              iconPosition="start"
            />
            <Tab
              icon={
                <Box
                  sx={{
                    width: 32,
                    height: 32,
                    backgroundColor: tabValue === 1 ? 'rgba(247, 147, 26, 0.2)' : 'rgba(255, 255, 255, 0.1)',
                    border: `1px solid ${tabValue === 1 ? 'rgba(247, 147, 26, 0.5)' : 'rgba(255, 255, 255, 0.2)'}`,
                    borderRadius: '8px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    transition: 'all 0.3s ease',
                  }}
                >
                  <Target size={16} color={tabValue === 1 ? '#F7931A' : '#94A3B8'} />
                </Box>
              }
              label={`CANDIDATE RULES (${rulesData?.candidate_rules.length || 0})`}
              iconPosition="start"
            />
          </Tabs>
        </Box>

        <Box sx={{ p: 6 }}>
          {tabValue === 0 && rulesData && (
            <Box>
              {rulesData.active_rules.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 12 }}>
                  <Box
                    sx={{
                      width: 80,
                      height: 80,
                      backgroundColor: 'rgba(255, 255, 255, 0.05)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      borderRadius: '20px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mx: 'auto',
                      mb: 4,
                    }}
                  >
                    <Shield size={32} color="#94A3B8" />
                  </Box>
                  <Typography 
                    variant="h4" 
                    sx={{ 
                      color: '#FFFFFF',
                      fontFamily: '"Space Grotesk", sans-serif',
                      fontWeight: 600,
                      mb: 2,
                    }}
                  >
                    NO ACTIVE RULES
                  </Typography>
                  <Typography 
                    variant="body1" 
                    sx={{ 
                      color: '#94A3B8',
                      maxWidth: 400,
                      mx: 'auto',
                    }}
                  >
                    Approve candidate rules to activate security protection for your infrastructure.
                  </Typography>
                </Box>
              ) : (
                <RuleList rules={rulesData.active_rules} />
              )}
            </Box>
          )}

          {tabValue === 1 && rulesData && (
            <Box>
              {rulesData.candidate_rules.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 12 }}>
                  <Box
                    sx={{
                      width: 80,
                      height: 80,
                      backgroundColor: 'rgba(255, 255, 255, 0.05)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      borderRadius: '20px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mx: 'auto',
                      mb: 4,
                    }}
                  >
                    <Target size={32} color="#94A3B8" />
                  </Box>
                  <Typography 
                    variant="h4" 
                    sx={{ 
                      color: '#FFFFFF',
                      fontFamily: '"Space Grotesk", sans-serif',
                      fontWeight: 600,
                      mb: 2,
                    }}
                  >
                    NO CANDIDATE RULES
                  </Typography>
                  <Typography 
                    variant="body1" 
                    sx={{ 
                      color: '#94A3B8',
                      maxWidth: 400,
                      mx: 'auto',
                    }}
                  >
                    Upload log files to generate new security rules automatically using AI analysis.
                  </Typography>
                </Box>
              ) : (
                <RuleList rules={rulesData.candidate_rules} showActions />
              )}
            </Box>
          )}
        </Box>
      </Card>

      {/* Rule Details Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            background: 'rgba(15, 17, 21, 0.95)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '16px',
          }
        }}
      >
        <DialogTitle sx={{ 
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          p: 4,
        }}>
          <Box display="flex" alignItems="center" gap={2}>
            <Box
              sx={{
                width: 40,
                height: 40,
                backgroundColor: selectedRule ? `${getSeverityColor(selectedRule.severity)}20` : 'rgba(255, 255, 255, 0.1)',
                border: selectedRule ? `1px solid ${getSeverityColor(selectedRule.severity)}50` : '1px solid rgba(255, 255, 255, 0.2)',
                borderRadius: '10px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              {selectedRule && getSeverityIcon(selectedRule.severity)}
            </Box>
            <Typography 
              variant="h5" 
              sx={{ 
                fontFamily: '"Space Grotesk", sans-serif',
                fontWeight: 600,
                color: '#FFFFFF',
              }}
            >
              RULE DETAILS
            </Typography>
          </Box>
        </DialogTitle>
        
        <DialogContent sx={{ p: 4 }}>
          {selectedRule && (
            <Box>
              <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12}>
                  <Typography 
                    variant="subtitle2" 
                    sx={{ 
                      color: '#F7931A',
                      fontFamily: '"JetBrains Mono", monospace',
                      fontSize: '0.75rem',
                      letterSpacing: '0.1em',
                      mb: 1,
                    }}
                  >
                    RULE NAME
                  </Typography>
                  <Typography 
                    variant="h6" 
                    sx={{ 
                      color: '#FFFFFF',
                      fontFamily: '"Space Grotesk", sans-serif',
                      fontWeight: 600,
                    }}
                  >
                    {selectedRule.name}
                  </Typography>
                </Grid>
                
                <Grid item xs={12} sm={4}>
                  <Typography 
                    variant="subtitle2" 
                    sx={{ 
                      color: '#F7931A',
                      fontFamily: '"JetBrains Mono", monospace',
                      fontSize: '0.75rem',
                      letterSpacing: '0.1em',
                      mb: 1,
                    }}
                  >
                    SEVERITY
                  </Typography>
                  <Chip
                    label={selectedRule.severity}
                    sx={{
                      backgroundColor: `${getSeverityColor(selectedRule.severity)}20`,
                      color: getSeverityColor(selectedRule.severity),
                      border: `1px solid ${getSeverityColor(selectedRule.severity)}40`,
                      fontFamily: '"JetBrains Mono", monospace',
                    }}
                  />
                </Grid>
                
                <Grid item xs={12} sm={4}>
                  <Typography 
                    variant="subtitle2" 
                    sx={{ 
                      color: '#F7931A',
                      fontFamily: '"JetBrains Mono", monospace',
                      fontSize: '0.75rem',
                      letterSpacing: '0.1em',
                      mb: 1,
                    }}
                  >
                    SOURCE
                  </Typography>
                  <Chip
                    label={selectedRule.source}
                    sx={{
                      backgroundColor: 'rgba(59, 130, 246, 0.2)',
                      color: '#3B82F6',
                      border: '1px solid rgba(59, 130, 246, 0.3)',
                      fontFamily: '"JetBrains Mono", monospace',
                    }}
                  />
                </Grid>
                
                <Grid item xs={12} sm={4}>
                  <Typography 
                    variant="subtitle2" 
                    sx={{ 
                      color: '#F7931A',
                      fontFamily: '"JetBrains Mono", monospace',
                      fontSize: '0.75rem',
                      letterSpacing: '0.1em',
                      mb: 1,
                    }}
                  >
                    STATUS
                  </Typography>
                  <Chip
                    label={selectedRule.status}
                    sx={{
                      backgroundColor: selectedRule.status === 'ACTIVE' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(156, 163, 175, 0.2)',
                      color: selectedRule.status === 'ACTIVE' ? '#10B981' : '#9CA3AF',
                      border: `1px solid ${selectedRule.status === 'ACTIVE' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(156, 163, 175, 0.3)'}`,
                      fontFamily: '"JetBrains Mono", monospace',
                    }}
                  />
                </Grid>
              </Grid>

              <Divider sx={{ 
                my: 3, 
                borderColor: 'rgba(255, 255, 255, 0.1)',
              }} />

              <Typography 
                variant="subtitle2" 
                sx={{ 
                  color: '#F7931A',
                  fontFamily: '"JetBrains Mono", monospace',
                  fontSize: '0.75rem',
                  letterSpacing: '0.1em',
                  mb: 2,
                }}
              >
                DESCRIPTION
              </Typography>
              <Typography 
                variant="body1" 
                sx={{ 
                  color: '#FFFFFF',
                  mb: 4,
                  lineHeight: 1.6,
                }}
              >
                {selectedRule.description}
              </Typography>

              <Typography 
                variant="subtitle2" 
                sx={{ 
                  color: '#F7931A',
                  fontFamily: '"JetBrains Mono", monospace',
                  fontSize: '0.75rem',
                  letterSpacing: '0.1em',
                  mb: 2,
                }}
              >
                DETECTION PATTERN
              </Typography>
              <Paper
                sx={{
                  backgroundColor: '#000000',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '8px',
                  p: 3,
                  mb: 4,
                }}
              >
                <Typography 
                  component="pre"
                  sx={{ 
                    fontFamily: '"JetBrains Mono", monospace',
                    color: '#FFD600',
                    fontSize: '0.85rem',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                  }}
                >
                  {selectedRule.pattern}
                </Typography>
              </Paper>

              <Typography 
                variant="subtitle2" 
                sx={{ 
                  color: '#F7931A',
                  fontFamily: '"JetBrains Mono", monospace',
                  fontSize: '0.75rem',
                  letterSpacing: '0.1em',
                  mb: 2,
                }}
              >
                REMEDIATION STEPS
              </Typography>
              <Typography 
                variant="body1" 
                sx={{ 
                  color: '#94A3B8',
                  lineHeight: 1.6,
                }}
              >
                {selectedRule.remediation}
              </Typography>
            </Box>
          )}
        </DialogContent>
        
        <DialogActions sx={{ 
          p: 4, 
          borderTop: '1px solid rgba(255, 255, 255, 0.1)',
          gap: 2,
        }}>
          {selectedRule?.status === 'CANDIDATE' && (
            <>
              <Button
                variant="contained"
                startIcon={<ThumbsUp size={16} />}
                onClick={() => selectedRule && handleApproveRule(selectedRule.id)}
                sx={{
                  background: 'linear-gradient(135deg, #10B981, #059669)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #059669, #047857)',
                  },
                }}
              >
                APPROVE RULE
              </Button>
              <Button
                variant="contained"
                startIcon={<ThumbsDown size={16} />}
                onClick={() => selectedRule && handleRejectRule(selectedRule.id)}
                sx={{
                  background: 'linear-gradient(135deg, #EF4444, #DC2626)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #DC2626, #B91C1C)',
                  },
                }}
              >
                REJECT RULE
              </Button>
            </>
          )}
          <Button 
            variant="outlined"
            onClick={() => setDialogOpen(false)}
          >
            CLOSE
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default RuleManagement;