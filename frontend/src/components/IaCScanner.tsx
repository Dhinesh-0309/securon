import React, { useState, useCallback } from 'react';
import {
  Box,
  Typography,
  Button,
  Alert,
  Chip,
  Grid,
  Paper,
  Card,
  CardContent,
  LinearProgress,
  Container,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  FileText,
  Shield,
  AlertTriangle,
  CheckCircle,
  Info,
  ChevronDown,
  Code,
  Zap,
  Settings,
  Layers,
} from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import apiClient from '../config/api';

interface ScanResult {
  message: string;
  total_files: number;
  total_violations: number;
  violations_by_severity: {
    CRITICAL: number;
    HIGH: number;
    MEDIUM: number;
    LOW: number;
  };
  violations: Array<{
    file: string;
    rule: string;
    severity: string;
    message: string;
    line: number;
    resource: string;
  }>;
}

const IaCScanner: React.FC = () => {
  const [scanning, setScanning] = useState(false);
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    setScanning(true);
    setError(null);
    setScanResult(null);
    setProgress(0);

    // Simulate progress
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + Math.random() * 15;
      });
    }, 200);

    try {
      const formData = new FormData();
      acceptedFiles.forEach(file => {
        formData.append('files', file);
      });

      const response = await apiClient.post('/api/iac/scan', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      clearInterval(progressInterval);
      setProgress(100);
      // Transform backend response to match expected format
      const backendData = response.data;
      const transformedData = {
        message: backendData.message,
        total_files: backendData.files_scanned || 0,
        total_violations: backendData.issues_found || 0,
        violations_by_severity: {
          CRITICAL: 0,
          HIGH: 0,
          MEDIUM: 0,
          LOW: 0
        },
        violations: (backendData.results || []).map((result: any) => ({
          file: result.file_path || 'unknown',
          rule: result.rule_id || 'unknown',
          severity: result.severity || 'MEDIUM',
          message: result.description || 'No description',
          line: result.line_number || 0,
          resource: result.file_path || 'unknown'
        }))
      };
      
      // Count violations by severity
      if (backendData.results) {
        backendData.results.forEach((result: any) => {
          const severity = result.severity || 'MEDIUM';
          if (transformedData.violations_by_severity[severity as keyof typeof transformedData.violations_by_severity] !== undefined) {
            transformedData.violations_by_severity[severity as keyof typeof transformedData.violations_by_severity]++;
          }
        });
      }
      
      console.log('IaC scan response:', backendData);
      console.log('Transformed data:', transformedData);
      setScanResult(transformedData);
    } catch (err: any) {
      console.error('IaC scan error:', err);
      clearInterval(progressInterval);
      setError(err.response?.data?.detail || err.message || 'Failed to scan files');
    } finally {
      setScanning(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: true,
    accept: {
      'text/plain': ['.tf', '.tfvars'],
      'application/json': ['.json'],
      'text/yaml': ['.yml', '.yaml'],
    },
  });

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return '#EF4444';
      case 'HIGH': return '#F59E0B';
      case 'MEDIUM': return '#3B82F6';
      case 'LOW': return '#10B981';
      default: return '#94A3B8';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return <AlertTriangle size={20} />;
      case 'HIGH': return <AlertTriangle size={20} />;
      case 'MEDIUM': return <Info size={20} />;
      case 'LOW': return <CheckCircle size={20} />;
      default: return <Info size={20} />;
    }
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
          <Shield size={40} color="#FFFFFF" />
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
          IAC <span className="gradient-text">SCANNER</span>
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
          Advanced Infrastructure as Code security scanner with 150+ built-in rules. 
          Detect misconfigurations and security vulnerabilities in your Terraform files.
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
              <Code size={24} />
            </Box>
            
            <Typography 
              variant="h4" 
              sx={{ 
                color: '#FFFFFF',
                fontFamily: '"Space Grotesk", sans-serif',
                fontWeight: 600,
              }}
            >
              UPLOAD TERRAFORM FILES
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
              <FileText size={32} color={isDragActive ? '#FFFFFF' : '#F7931A'} />
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
              {isDragActive ? 'DROP FILES HERE' : 'DRAG & DROP IAC FILES'}
            </Typography>
            
            <Typography 
              variant="body1" 
              sx={{ 
                mb: 4,
                color: '#94A3B8',
                lineHeight: 1.6,
              }}
            >
              Upload your Terraform, CloudFormation, or Kubernetes files for security analysis.
              <br />
              <strong>Supported:</strong> .tf, .tfvars, .json, .yml files with infrastructure code.
            </Typography>
            
            {/* Supported File Types */}
            <Box display="flex" justifyContent="center" gap={2} flexWrap="wrap">
              {[
                { label: 'TERRAFORM', ext: '.tf', icon: <Layers size={16} /> },
                { label: 'VARIABLES', ext: '.tfvars', icon: <Settings size={16} /> },
                { label: 'JSON', ext: '.json', icon: <Code size={16} /> },
                { label: 'YAML', ext: '.yml', icon: <FileText size={16} /> },
              ].map((fileType, index) => (
                <Chip 
                  key={index}
                  icon={fileType.icon}
                  label={`${fileType.label} ${fileType.ext}`}
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
                  link.href = '/sample-terraform.tf';
                  link.download = 'sample-terraform.tf';
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
                Download Sample Terraform File
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Scanning Progress */}
      {scanning && (
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
            <Box sx={{ textAlign: 'center', mb: 4 }}>
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
                <Zap size={28} color="#FFFFFF" />
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
                SCANNING IN PROGRESS
              </Typography>
              
              <Typography 
                variant="body1" 
                sx={{ 
                  color: '#94A3B8',
                  mb: 4,
                }}
              >
                Analyzing your infrastructure code for security vulnerabilities...
              </Typography>

              <Box sx={{ width: '100%', maxWidth: 400, mx: 'auto' }}>
                <LinearProgress 
                  variant="determinate" 
                  value={progress}
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: '#F7931A',
                      boxShadow: '0 0 10px rgba(247, 147, 26, 0.5)',
                      borderRadius: 4,
                    },
                  }}
                />
                <Typography 
                  variant="caption" 
                  sx={{ 
                    color: '#F7931A',
                    fontFamily: '"JetBrains Mono", monospace',
                    fontSize: '0.8rem',
                    mt: 1,
                    display: 'block',
                  }}
                >
                  {Math.round(progress)}% COMPLETE
                </Typography>
              </Box>
            </Box>
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
            Scan failed: {error}
          </Typography>
        </Alert>
      )}

      {/* Scan Results */}
      {scanResult && (
        <Box>
          {/* Results Summary */}
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
              SCAN <span className="gradient-text">RESULTS</span>
            </Typography>

            <Grid container spacing={4}>
              <Grid item xs={12} sm={6} lg={3}>
                <Card 
                  sx={{ 
                    textAlign: 'center',
                    background: 'rgba(15, 17, 21, 0.8)',
                    backdropFilter: 'blur(16px)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    '&:hover': {
                      border: '1px solid rgba(59, 130, 246, 0.4)',
                      boxShadow: '0 0 30px -10px rgba(59, 130, 246, 0.4)',
                    },
                  }}
                >
                  <CardContent sx={{ p: 4 }}>
                    <Box
                      sx={{
                        width: 60,
                        height: 60,
                        backgroundColor: 'rgba(59, 130, 246, 0.2)',
                        border: '1px solid rgba(59, 130, 246, 0.5)',
                        borderRadius: '15px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mx: 'auto',
                        mb: 2,
                        color: '#3B82F6',
                      }}
                    >
                      <FileText size={24} />
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
                      {scanResult.total_files}
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
                      FILES SCANNED
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} lg={3}>
                <Card 
                  sx={{ 
                    textAlign: 'center',
                    background: 'rgba(15, 17, 21, 0.8)',
                    backdropFilter: 'blur(16px)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    '&:hover': {
                      border: scanResult.total_violations > 0 ? '1px solid rgba(239, 68, 68, 0.4)' : '1px solid rgba(16, 185, 129, 0.4)',
                      boxShadow: scanResult.total_violations > 0 ? '0 0 30px -10px rgba(239, 68, 68, 0.4)' : '0 0 30px -10px rgba(16, 185, 129, 0.4)',
                    },
                  }}
                >
                  <CardContent sx={{ p: 4 }}>
                    <Box
                      sx={{
                        width: 60,
                        height: 60,
                        backgroundColor: scanResult.total_violations > 0 ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.2)',
                        border: scanResult.total_violations > 0 ? '1px solid rgba(239, 68, 68, 0.5)' : '1px solid rgba(16, 185, 129, 0.5)',
                        borderRadius: '15px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mx: 'auto',
                        mb: 2,
                        color: scanResult.total_violations > 0 ? '#EF4444' : '#10B981',
                      }}
                    >
                      {scanResult.total_violations > 0 ? <AlertTriangle size={24} /> : <CheckCircle size={24} />}
                    </Box>
                    
                    <Typography 
                      variant="h4" 
                      sx={{ 
                        fontFamily: '"Space Grotesk", sans-serif',
                        color: scanResult.total_violations > 0 ? '#EF4444' : '#10B981',
                        mb: 1,
                        fontWeight: 700,
                      }}
                    >
                      {scanResult.total_violations}
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
                      VIOLATIONS FOUND
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              {/* Severity Breakdown */}
              {Object.entries(scanResult.violations_by_severity).map(([severity, count]) => (
                <Grid item xs={6} lg={1.5} key={severity}>
                  <Card 
                    sx={{ 
                      textAlign: 'center',
                      background: 'rgba(15, 17, 21, 0.8)',
                      backdropFilter: 'blur(16px)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      '&:hover': {
                        border: `1px solid ${getSeverityColor(severity)}40`,
                        boxShadow: `0 0 20px -5px ${getSeverityColor(severity)}40`,
                      },
                    }}
                  >
                    <CardContent sx={{ p: 3 }}>
                      <Box
                        sx={{
                          width: 40,
                          height: 40,
                          backgroundColor: `${getSeverityColor(severity)}20`,
                          border: `1px solid ${getSeverityColor(severity)}50`,
                          borderRadius: '10px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          mx: 'auto',
                          mb: 1,
                          color: getSeverityColor(severity),
                        }}
                      >
                        {getSeverityIcon(severity)}
                      </Box>
                      
                      <Typography 
                        variant="h6" 
                        sx={{ 
                          fontFamily: '"Space Grotesk", sans-serif',
                          color: getSeverityColor(severity),
                          mb: 0.5,
                          fontWeight: 700,
                        }}
                      >
                        {count}
                      </Typography>
                      
                      <Typography 
                        variant="caption" 
                        sx={{ 
                          color: '#94A3B8',
                          fontFamily: '"JetBrains Mono", monospace',
                          fontSize: '0.7rem',
                        }}
                      >
                        {severity}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>

          {/* Violations List */}
          {scanResult.violations.length > 0 && (
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
                SECURITY <span className="gradient-text">VIOLATIONS</span>
              </Typography>

              <Box>
                {scanResult.violations.map((violation, index) => (
                  <Accordion 
                    key={index}
                    sx={{
                      mb: 2,
                      background: 'rgba(15, 17, 21, 0.8)',
                      backdropFilter: 'blur(16px)',
                      border: `1px solid ${getSeverityColor(violation.severity)}40`,
                      borderRadius: '12px !important',
                      '&:before': {
                        display: 'none',
                      },
                      '&.Mui-expanded': {
                        margin: '0 0 16px 0',
                      },
                    }}
                  >
                    <AccordionSummary
                      expandIcon={<ChevronDown size={20} color="#94A3B8" />}
                      sx={{
                        '& .MuiAccordionSummary-content': {
                          alignItems: 'center',
                        },
                      }}
                    >
                      <Box display="flex" alignItems="center" gap={2} width="100%">
                        <Box
                          sx={{
                            width: 32,
                            height: 32,
                            backgroundColor: `${getSeverityColor(violation.severity)}20`,
                            border: `1px solid ${getSeverityColor(violation.severity)}50`,
                            borderRadius: '8px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: getSeverityColor(violation.severity),
                          }}
                        >
                          {getSeverityIcon(violation.severity)}
                        </Box>
                        
                        <Box flex={1}>
                          <Typography 
                            variant="subtitle1" 
                            sx={{ 
                              color: '#FFFFFF',
                              fontFamily: '"Space Grotesk", sans-serif',
                              fontWeight: 600,
                            }}
                          >
                            {violation.rule}
                          </Typography>
                          <Typography 
                            variant="caption" 
                            sx={{ 
                              color: '#94A3B8',
                              fontFamily: '"JetBrains Mono", monospace',
                              fontSize: '0.75rem',
                            }}
                          >
                            {violation.file}:{violation.line} • {violation.resource}
                          </Typography>
                        </Box>
                        
                        <Chip
                          label={violation.severity}
                          size="small"
                          sx={{
                            backgroundColor: `${getSeverityColor(violation.severity)}20`,
                            color: getSeverityColor(violation.severity),
                            border: `1px solid ${getSeverityColor(violation.severity)}40`,
                            fontFamily: '"JetBrains Mono", monospace',
                            fontSize: '0.7rem',
                          }}
                        />
                      </Box>
                    </AccordionSummary>
                    
                    <AccordionDetails sx={{ pt: 0 }}>
                      <Box sx={{ pl: 6 }}>
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            color: '#94A3B8',
                            lineHeight: 1.6,
                            mb: 2,
                          }}
                        >
                          {violation.message}
                        </Typography>
                        
                        <Paper
                          sx={{
                            backgroundColor: '#000000',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            borderRadius: '8px',
                            p: 2,
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
                            }}
                          >
                            RESOURCE: {violation.resource}
                          </Typography>
                          <Typography 
                            variant="caption" 
                            sx={{ 
                              color: '#FFD600',
                              fontFamily: '"JetBrains Mono", monospace',
                              fontSize: '0.75rem',
                            }}
                          >
                            FILE: {violation.file} (Line {violation.line})
                          </Typography>
                        </Paper>
                      </Box>
                    </AccordionDetails>
                  </Accordion>
                ))}
              </Box>
            </Box>
          )}

          {/* No Violations Found */}
          {scanResult.total_violations === 0 && (
            <Card 
              sx={{ 
                textAlign: 'center',
                py: 8,
                background: 'rgba(16, 185, 129, 0.1)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                backdropFilter: 'blur(16px)',
              }}
            >
              <CardContent>
                <Box
                  sx={{
                    width: 80,
                    height: 80,
                    backgroundColor: 'rgba(16, 185, 129, 0.2)',
                    border: '1px solid rgba(16, 185, 129, 0.5)',
                    borderRadius: '20px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mx: 'auto',
                    mb: 4,
                  }}
                >
                  <CheckCircle size={40} color="#10B981" />
                </Box>
                
                <Typography 
                  variant="h4" 
                  sx={{ 
                    color: '#10B981',
                    fontFamily: '"Space Grotesk", sans-serif',
                    fontWeight: 600,
                    mb: 2,
                  }}
                >
                  SECURITY SCAN PASSED
                </Typography>
                
                <Typography 
                  variant="body1" 
                  sx={{ 
                    color: '#FFFFFF',
                    maxWidth: 400,
                    mx: 'auto',
                  }}
                >
                  No security violations detected in your infrastructure code. 
                  Your configuration follows security best practices.
                </Typography>
              </CardContent>
            </Card>
          )}
        </Box>
      )}
    </Container>
  );
};

export default IaCScanner;