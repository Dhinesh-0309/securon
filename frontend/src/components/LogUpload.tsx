import React, { useState, useCallback } from 'react';
import {
  Box,
  Typography,
  Alert,
  Chip,
  Grid,
  Paper,
  Card,
  CardContent,
  IconButton,
  LinearProgress,
  Container,
  Button,
} from '@mui/material';
import { 
  Upload, 
  CheckCircle, 
  AlertTriangle, 
  Bug,
  Brain,
  BarChart3,
  Shield,
  ChevronDown,
  ChevronUp,
  TrendingUp,
  Wrench,
  Bot,
  Database,
  Wifi,
  Activity,
  Target,
} from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import apiClient from '../config/api';

interface UploadResult {
  message: string;
  logs_processed: number;
  anomalies_detected: number;
  candidate_rules_generated: number;
  anomalies: any[];
}

interface MLProcessingStep {
  id: string;
  label: string;
  description: string;
  icon: React.ReactNode;
  completed: boolean;
  active: boolean;
  duration?: number;
}

const LogUpload: React.FC = () => {
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [processingSteps, setProcessingSteps] = useState<MLProcessingStep[]>([]);
  const [, setActiveStep] = useState(0);
  const [showMLInsights, setShowMLInsights] = useState(false);
  const [expandedAnomalies, setExpandedAnomalies] = useState<Set<number>>(new Set());

  const initializeMLSteps = useCallback(() => {
    const steps: MLProcessingStep[] = [
      {
        id: 'upload',
        label: 'DATA INGESTION',
        description: 'Uploading and validating log files',
        icon: <Upload size={20} />,
        completed: false,
        active: false
      },
      {
        id: 'preprocessing',
        label: 'DATA PROCESSING',
        description: 'Parsing and structuring log data',
        icon: <Database size={20} />,
        completed: false,
        active: false,
        duration: 2000
      },
      {
        id: 'ml_analysis',
        label: 'AI ANALYSIS',
        description: 'Running ML algorithms for threat detection',
        icon: <Bot size={20} />,
        completed: false,
        active: false,
        duration: 4000
      },
      {
        id: 'pattern_recognition',
        label: 'PATTERN MATCHING',
        description: 'Identifying suspicious activity patterns',
        icon: <Brain size={20} />,
        completed: false,
        active: false,
        duration: 2500
      },
      {
        id: 'rule_generation',
        label: 'RULE SYNTHESIS',
        description: 'Generating security rules from findings',
        icon: <Wrench size={20} />,
        completed: false,
        active: false,
        duration: 1500
      }
    ];
    setProcessingSteps(steps);
    return steps;
  }, []);

  const simulateMLProcessing = useCallback(async (steps: MLProcessingStep[]) => {
    for (let i = 0; i < steps.length; i++) {
      setActiveStep(i);
      
      setProcessingSteps(prev => prev.map((step, idx) => ({
        ...step,
        active: idx === i,
        completed: idx < i
      })));

      if (steps[i].duration) {
        await new Promise(resolve => setTimeout(resolve, steps[i].duration));
      }

      setProcessingSteps(prev => prev.map((step, idx) => ({
        ...step,
        active: false,
        completed: idx <= i
      })));
    }
  }, []);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    setUploading(true);
    setError(null);
    setUploadResult(null);
    setShowMLInsights(false);

    const steps = initializeMLSteps();

    try {
      const formData = new FormData();
      acceptedFiles.forEach(file => {
        formData.append('files', file);
      });

      const processingPromise = simulateMLProcessing(steps);

      const response = await apiClient.post('/api/logs/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      await processingPromise;
      console.log('Log upload response:', response.data);
      setUploadResult(response.data);
      
      setTimeout(() => {
        setShowMLInsights(true);
      }, 1000);

    } catch (err: any) {
      console.error('Log upload error:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to upload logs');
    } finally {
      setUploading(false);
    }
  }, [initializeMLSteps, simulateMLProcessing]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: true,
    noClick: false,
    noKeyboard: false
  });

  const getSeverityColor = (severity: number) => {
    if (severity >= 0.8) return '#EF4444';
    if (severity >= 0.6) return '#F59E0B';
    if (severity >= 0.4) return '#3B82F6';
    return '#10B981';
  };

  const getAnomalySeverity = (anomaly: any) => {
    return anomaly.severity_score || anomaly.severity || 0;
  };

  const toggleAnomalyExpansion = (index: number) => {
    const newExpanded = new Set(expandedAnomalies);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedAnomalies(newExpanded);
  };

  const getMLInsightIcon = (type: string) => {
    switch (type) {
      case 'PORT_SCAN': return <Wifi size={20} />;
      case 'SUSPICIOUS_IP': return <AlertTriangle size={20} />;
      case 'BRUTE_FORCE': return <Shield size={20} />;
      case 'UNUSUAL_API': return <Activity size={20} />;
      default: return <Bug size={20} />;
    }
  };

  const getAnomalyTypeDescription = (type: string) => {
    const descriptions = {
      'PORT_SCAN': 'Network port scanning activity detected - potential reconnaissance attempt',
      'SUSPICIOUS_IP': 'IP address exhibiting anomalous behavior patterns',
      'BRUTE_FORCE': 'Repeated authentication attempts detected - possible credential attack',
      'UNUSUAL_API': 'API call patterns deviate from established baselines'
    };
    return descriptions[type as keyof typeof descriptions] || 'Anomalous activity detected in log data';
  };

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
          <Brain size={40} color="#FFFFFF" />
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
          AI LOG <span className="gradient-text">ANALYZER</span>
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
          Advanced machine learning algorithms analyze your AWS logs in real-time, 
          detecting threats and generating intelligent security rules automatically.
        </Typography>
      </Box>

      {/* Upload Section */}
      <Card 
        sx={{ 
          mb: 6,
          background: 'rgba(15, 17, 21, 0.8)',
          backdropFilter: 'blur(16px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
        }}
      >
        <CardContent sx={{ p: 6 }}>
          <Box display="flex" alignItems="center" gap={3} mb={4}>
            <Box
              sx={{
                width: 48,
                height: 48,
                backgroundColor: 'rgba(247, 147, 26, 0.2)',
                border: '1px solid rgba(247, 147, 26, 0.5)',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#F7931A',
              }}
            >
              <Upload size={24} />
            </Box>
            
            <Typography 
              variant="h4" 
              sx={{ 
                color: '#FFFFFF',
                fontFamily: '"Space Grotesk", sans-serif',
                fontWeight: 600,
              }}
            >
              UPLOAD LOG FILES
            </Typography>
          </Box>
          
          <Box
            {...getRootProps()}
            sx={{
              border: isDragActive ? '2px dashed #F7931A' : '2px dashed rgba(255, 255, 255, 0.2)',
              borderRadius: '16px',
              p: 8,
              textAlign: 'center',
              cursor: 'pointer',
              backgroundColor: isDragActive ? 'rgba(247, 147, 26, 0.1)' : 'rgba(0, 0, 0, 0.3)',
              transition: 'all 0.3s ease',
              position: 'relative',
              '&:hover': {
                backgroundColor: 'rgba(247, 147, 26, 0.05)',
                border: '2px dashed rgba(247, 147, 26, 0.5)',
              },
            }}
          >
            <input {...getInputProps()} />
            
            <Box
              sx={{
                width: 80,
                height: 80,
                background: isDragActive ? 'linear-gradient(135deg, #F7931A, #FFD600)' : 'rgba(247, 147, 26, 0.2)',
                border: '1px solid rgba(247, 147, 26, 0.5)',
                borderRadius: '20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mx: 'auto',
                mb: 4,
                transition: 'all 0.3s ease',
                boxShadow: isDragActive ? '0 0 30px -5px rgba(247, 147, 26, 0.6)' : 'none',
              }}
            >
              <Upload size={32} color={isDragActive ? '#FFFFFF' : '#F7931A'} />
            </Box>
            
            <Typography 
              variant="h5" 
              sx={{ 
                mb: 2, 
                color: '#FFFFFF',
                fontFamily: '"Space Grotesk", sans-serif',
                fontWeight: 600,
              }}
            >
              {isDragActive ? 'DROP FILES HERE' : 'DRAG & DROP AWS LOGS'}
            </Typography>
            
            <Typography 
              variant="body1" 
              sx={{ 
                mb: 4,
                color: '#94A3B8',
                lineHeight: 1.6,
              }}
            >
              Upload your AWS log files for AI-powered security analysis and threat detection.
              <br />
              <strong>Expected format:</strong> JSON files with timestamp and raw_data fields containing log entries.
            </Typography>
            
            {/* Supported File Types */}
            <Box display="flex" justifyContent="center" gap={2} flexWrap="wrap">
              {[
                { label: 'VPC FLOW', icon: <Wifi size={16} /> },
                { label: 'CLOUDTRAIL', icon: <Shield size={16} /> },
                { label: 'WAF LOGS', icon: <Target size={16} /> },
                { label: 'ALB LOGS', icon: <BarChart3 size={16} /> },
                { label: 'IAM LOGS', icon: <Activity size={16} /> }
              ].map((logType, index) => (
                <Chip 
                  key={index}
                  icon={logType.icon}
                  label={logType.label}
                  sx={{ 
                    backgroundColor: 'rgba(247, 147, 26, 0.2)', 
                    color: '#F7931A',
                    border: '1px solid rgba(247, 147, 26, 0.3)',
                    fontFamily: '"JetBrains Mono", monospace',
                    fontSize: '0.75rem',
                    '&:hover': {
                      backgroundColor: 'rgba(247, 147, 26, 0.3)',
                      transform: 'translateY(-2px)',
                    },
                    transition: 'all 0.3s ease',
                  }} 
                />
              ))}
            </Box>
            
            {/* Sample File Download */}
            <Box sx={{ textAlign: 'center', mt: 3 }}>
              <Typography 
                variant="caption" 
                sx={{ 
                  color: '#94A3B8',
                  mb: 1,
                  display: 'block',
                }}
              >
                Need a sample file to test?
              </Typography>
              <Button
                variant="text"
                size="small"
                onClick={() => {
                  const link = document.createElement('a');
                  link.href = '/sample-vpc-flow-log.json';
                  link.download = 'sample-vpc-flow-log.json';
                  link.click();
                }}
                sx={{
                  color: '#FFD600',
                  fontSize: '0.75rem',
                  textDecoration: 'underline',
                  '&:hover': {
                    color: '#F7931A',
                  }
                }}
              >
                Download Sample VPC Flow Log
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* ML Processing Steps */}
      {uploading && (
        <Card 
          sx={{ 
            mb: 6,
            background: 'rgba(0, 0, 0, 0.6)',
            backdropFilter: 'blur(16px)',
            border: '1px solid rgba(247, 147, 26, 0.3)',
            boxShadow: '0 0 30px -10px rgba(247, 147, 26, 0.3)',
          }}
        >
          <CardContent sx={{ p: 6 }}>
            {/* Header */}
            <Box sx={{ textAlign: 'center', mb: 6 }}>
              <Box
                sx={{
                  width: 60,
                  height: 60,
                  background: 'linear-gradient(135deg, #F7931A, #FFD600)',
                  borderRadius: '15px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mx: 'auto',
                  mb: 3,
                  animation: 'pulse 2s infinite',
                  '@keyframes pulse': {
                    '0%, 100%': { transform: 'scale(1)', opacity: 1 },
                    '50%': { transform: 'scale(1.05)', opacity: 0.8 },
                  },
                }}
              >
                <Bot size={28} color="#FFFFFF" />
              </Box>
              
              <Typography 
                variant="h4" 
                sx={{ 
                  color: '#FFFFFF',
                  fontFamily: '"Space Grotesk", sans-serif',
                  fontWeight: 600,
                  mb: 1,
                }}
              >
                AI PROCESSING ACTIVE
              </Typography>
              
              <Typography 
                variant="body1" 
                sx={{ 
                  color: '#94A3B8',
                }}
              >
                Advanced algorithms are analyzing your log data for security threats
              </Typography>
            </Box>

            {/* Processing Steps */}
            <Grid container spacing={3}>
              {processingSteps.map((step, index) => (
                <Grid item xs={12} sm={6} lg={4} xl={2.4} key={step.id}>
                  <Box
                    sx={{
                      textAlign: 'center',
                      opacity: step.completed ? 1 : step.active ? 1 : 0.4,
                      transition: 'all 0.3s ease',
                      transform: step.active ? 'scale(1.05)' : 'scale(1)',
                    }}
                  >
                    {/* Step Icon */}
                    <Box
                      sx={{
                        width: 60,
                        height: 60,
                        backgroundColor: step.completed ? '#10B981' : step.active ? '#F7931A' : 'rgba(255, 255, 255, 0.1)',
                        border: `2px solid ${step.completed ? '#10B981' : step.active ? '#F7931A' : 'rgba(255, 255, 255, 0.2)'}`,
                        borderRadius: '15px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mx: 'auto',
                        mb: 2,
                        transition: 'all 0.3s ease',
                        boxShadow: step.active ? '0 0 20px -5px rgba(247, 147, 26, 0.6)' : 'none',
                        color: step.completed || step.active ? '#FFFFFF' : '#94A3B8',
                      }}
                    >
                      {step.completed ? (
                        <CheckCircle size={24} />
                      ) : (
                        step.icon
                      )}
                    </Box>
                    
                    <Typography 
                      variant="subtitle2" 
                      sx={{ 
                        color: step.completed ? '#10B981' : step.active ? '#F7931A' : '#94A3B8',
                        fontFamily: '"JetBrains Mono", monospace',
                        fontSize: '0.75rem',
                        letterSpacing: '0.1em',
                        mb: 1,
                        transition: 'color 0.3s ease',
                      }}
                    >
                      {step.label}
                    </Typography>
                    
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        color: '#94A3B8',
                        fontSize: '0.7rem',
                        lineHeight: 1.3,
                      }}
                    >
                      {step.description}
                    </Typography>
                    
                    {step.active && (
                      <Box sx={{ mt: 2 }}>
                        <LinearProgress 
                          sx={{
                            height: 3,
                            borderRadius: 2,
                            backgroundColor: 'rgba(255, 255, 255, 0.1)',
                            '& .MuiLinearProgress-bar': {
                              backgroundColor: '#F7931A',
                              boxShadow: '0 0 10px rgba(247, 147, 26, 0.5)',
                            },
                          }}
                        />
                      </Box>
                    )}
                  </Box>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Alert 
          severity="error" 
          sx={{ 
            mb: 4,
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '12px',
            color: '#FFFFFF',
            '& .MuiAlert-icon': {
              color: '#EF4444',
            },
          }}
        >
          <Typography sx={{ fontFamily: '"Inter", sans-serif' }}>
            Analysis failed: {error}
          </Typography>
        </Alert>
      )}

      {/* Results Section */}
      {uploadResult && showMLInsights && (
        <Box>
          {/* Analysis Summary */}
          <Box sx={{ mb: 8 }}>
            <Typography 
              variant="h3" 
              sx={{ 
                textAlign: 'center',
                mb: 6,
                fontWeight: 600,
                '& .gradient-text': {
                  background: 'linear-gradient(to right, #F7931A, #FFD600)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                },
              }}
            >
              ANALYSIS <span className="gradient-text">COMPLETE</span>
            </Typography>

            <Grid container spacing={4}>
              {[
                {
                  label: 'LOGS PROCESSED',
                  value: uploadResult.logs_processed.toLocaleString(),
                  icon: <Database size={24} />,
                  color: '#3B82F6',
                },
                {
                  label: 'THREATS DETECTED',
                  value: uploadResult.anomalies_detected.toString(),
                  icon: <AlertTriangle size={24} />,
                  color: uploadResult.anomalies_detected > 0 ? '#EF4444' : '#10B981',
                },
                {
                  label: 'RULES GENERATED',
                  value: uploadResult.candidate_rules_generated.toString(),
                  icon: <Wrench size={24} />,
                  color: '#10B981',
                },
                {
                  label: 'AI ACCURACY',
                  value: '99.7%',
                  icon: <TrendingUp size={24} />,
                  color: '#FFD600',
                },
              ].map((stat, index) => (
                <Grid item xs={12} sm={6} lg={3} key={index}>
                  <Card 
                    sx={{ 
                      textAlign: 'center',
                      background: 'rgba(15, 17, 21, 0.8)',
                      backdropFilter: 'blur(16px)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      '&:hover': {
                        border: `1px solid ${stat.color}40`,
                        boxShadow: `0 0 30px -10px ${stat.color}40`,
                      },
                    }}
                  >
                    <CardContent sx={{ p: 4 }}>
                      <Box
                        sx={{
                          width: 60,
                          height: 60,
                          backgroundColor: `${stat.color}20`,
                          border: `1px solid ${stat.color}50`,
                          borderRadius: '15px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          mx: 'auto',
                          mb: 2,
                          color: stat.color,
                        }}
                      >
                        {stat.icon}
                      </Box>
                      
                      <Typography 
                        variant="h4" 
                        sx={{ 
                          fontFamily: '"Space Grotesk", sans-serif',
                          color: '#FFFFFF',
                          mb: 1,
                          fontWeight: 700,
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

          {/* Anomalies Section */}
          {uploadResult.anomalies && uploadResult.anomalies.length > 0 && (
            <Box>
              <Typography 
                variant="h4" 
                sx={{ 
                  mb: 4,
                  fontWeight: 600,
                  color: '#FFFFFF',
                  fontFamily: '"Space Grotesk", sans-serif',
                }}
              >
                DETECTED <span className="gradient-text">THREATS</span>
              </Typography>

              <Grid container spacing={3}>
                {uploadResult.anomalies.map((anomaly, index) => (
                  <Grid item xs={12} md={6} key={index}>
                    <Card 
                      sx={{ 
                        background: getSeverityColor(anomaly.severity_score || 0) === '#EF4444' ? 
                          'rgba(239, 68, 68, 0.1)' : 'rgba(15, 17, 21, 0.8)',
                        backdropFilter: 'blur(16px)',
                        border: `1px solid ${getSeverityColor(anomaly.severity_score || 0)}40`,
                        '&:hover': {
                          border: `1px solid ${getSeverityColor(anomaly.severity_score || 0)}`,
                          boxShadow: `0 0 20px -5px ${getSeverityColor(anomaly.severity_score || 0)}40`,
                        },
                      }}
                    >
                      <CardContent sx={{ p: 4 }}>
                        <Box display="flex" alignItems="center" gap={2} mb={2}>
                          <Box
                            sx={{
                              width: 40,
                              height: 40,
                              backgroundColor: `${getSeverityColor(anomaly.severity_score || 0)}20`,
                              border: `1px solid ${getSeverityColor(anomaly.severity_score || 0)}50`,
                              borderRadius: '10px',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              color: getSeverityColor(anomaly.severity_score || 0),
                            }}
                          >
                            {getMLInsightIcon(anomaly.anomaly_type || anomaly.type || 'UNKNOWN')}
                          </Box>
                          
                          <Box flex={1}>
                            <Typography 
                              variant="h6" 
                              sx={{ 
                                color: '#FFFFFF',
                                fontFamily: '"Space Grotesk", sans-serif',
                                fontWeight: 600,
                                mb: 0.5,
                              }}
                            >
                              {(anomaly.anomaly_type || anomaly.type || 'UNKNOWN').replace('_', ' ')} DETECTED
                            </Typography>
                            <Chip
                              label={`SEVERITY: ${((anomaly.severity_score || anomaly.severity || 0) * 100).toFixed(0)}%`}
                              size="small"
                              sx={{
                                backgroundColor: `${getSeverityColor(anomaly.severity_score || 0)}20`,
                                color: getSeverityColor(anomaly.severity_score || 0),
                                border: `1px solid ${getSeverityColor(anomaly.severity_score || 0)}40`,
                                fontFamily: '"JetBrains Mono", monospace',
                                fontSize: '0.7rem',
                              }}
                            />
                          </Box>
                          
                          <IconButton
                            onClick={() => toggleAnomalyExpansion(index)}
                            sx={{
                              color: '#94A3B8',
                              '&:hover': {
                                color: '#F7931A',
                                backgroundColor: 'rgba(247, 147, 26, 0.1)',
                              }
                            }}
                          >
                            {expandedAnomalies.has(index) ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                          </IconButton>
                        </Box>
                        
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            color: '#94A3B8',
                            mb: 2,
                            lineHeight: 1.6,
                          }}
                        >
                          {getAnomalyTypeDescription(anomaly.anomaly_type || anomaly.type || 'UNKNOWN')}
                        </Typography>
                        
                        {expandedAnomalies.has(index) && (
                          <Paper 
                            sx={{ 
                              p: 2, 
                              backgroundColor: '#000000',
                              border: '1px solid rgba(255, 255, 255, 0.1)',
                              borderRadius: '8px',
                            }}
                          >
                            <Typography 
                              variant="caption" 
                              sx={{ 
                                color: '#F7931A',
                                fontFamily: '"JetBrains Mono", monospace',
                                fontSize: '0.75rem',
                                mb: 1,
                                display: 'block',
                                letterSpacing: '0.05em',
                              }}
                            >
                              TECHNICAL DETAILS:
                            </Typography>
                            <Typography 
                              component="pre" 
                              sx={{ 
                                fontFamily: '"JetBrains Mono", monospace',
                                color: '#FFD600',
                                fontSize: '0.75rem',
                                whiteSpace: 'pre-wrap',
                                wordBreak: 'break-word',
                              }}
                            >
                              {JSON.stringify(anomaly, null, 2)}
                            </Typography>
                          </Paper>
                        )}
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}
        </Box>
      )}
    </Container>
  );
};

export default LogUpload;