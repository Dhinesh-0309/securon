import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Box,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Grid,
  IconButton,
  Collapse,
} from '@mui/material';
import {
  Visibility,
  ExpandMore,
  ExpandLess,
  TrendingUp,
  Security,
  Warning,
  Info,
  Refresh,
} from '@mui/icons-material';
import apiClient from '../config/api';
import { AnomalyResult } from '../types';

interface MLFinding {
  id: string;
  timestamp: string;
  type: string;
  severity: number;
  confidence: number;
  description: string;
  explanation: string;
  affected_resources: string[];
  time_window: {
    start: string;
    end: string;
  };
  status: 'new' | 'reviewed' | 'resolved';
}

const MLFindings: React.FC = () => {
  const [findings, setFindings] = useState<MLFinding[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedFinding, setSelectedFinding] = useState<MLFinding | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchFindings();
  }, []);

  const fetchFindings = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/api/ml/findings');
      setFindings(response.data.findings || []);
    } catch (error) {
      console.error('Failed to fetch ML findings:', error);
      // Mock data for demonstration
      setFindings([
        {
          id: '1',
          timestamp: '2024-01-15T14:30:00Z',
          type: 'suspicious_ip_activity',
          severity: 0.85,
          confidence: 0.92,
          description: 'Multiple failed login attempts from suspicious IP addresses',
          explanation: 'The ML model detected an unusual pattern of failed authentication attempts from IP addresses not previously seen in your environment. This could indicate a brute force attack or credential stuffing attempt.',
          affected_resources: ['vpc-12345', 'sg-67890'],
          time_window: {
            start: '2024-01-15T14:00:00Z',
            end: '2024-01-15T14:30:00Z'
          },
          status: 'new'
        },
        {
          id: '2',
          timestamp: '2024-01-15T13:45:00Z',
          type: 'unusual_api_calls',
          severity: 0.65,
          confidence: 0.78,
          description: 'Unusual API call patterns detected during off-hours',
          explanation: 'Administrative API calls were made outside of normal business hours from an unfamiliar location. While this could be legitimate remote work, it deviates from established patterns.',
          affected_resources: ['iam-role-admin', 'ec2-instances'],
          time_window: {
            start: '2024-01-15T02:00:00Z',
            end: '2024-01-15T03:00:00Z'
          },
          status: 'reviewed'
        },
        {
          id: '3',
          timestamp: '2024-01-15T12:15:00Z',
          type: 'data_exfiltration',
          severity: 0.45,
          confidence: 0.68,
          description: 'Potential data exfiltration pattern detected',
          explanation: 'Large amounts of data were transferred to external endpoints. The pattern suggests possible data exfiltration, though it could also be legitimate backup or sync operations.',
          affected_resources: ['s3-bucket-data', 'cloudfront-dist'],
          time_window: {
            start: '2024-01-15T11:00:00Z',
            end: '2024-01-15T12:00:00Z'
          },
          status: 'resolved'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: number) => {
    if (severity >= 0.8) return 'error';
    if (severity >= 0.6) return 'warning';
    if (severity >= 0.4) return 'info';
    return 'success';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'new': return 'error';
      case 'reviewed': return 'warning';
      case 'resolved': return 'success';
      default: return 'default';
    }
  };

  const handleViewDetails = (finding: MLFinding) => {
    setSelectedFinding(finding);
    setDialogOpen(true);
  };

  const handleRowExpand = (id: string) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedRows(newExpanded);
  };

  const stats = [
    {
      title: 'Total Findings',
      value: findings.length.toString(),
      icon: <TrendingUp sx={{ fontSize: 40, color: 'primary.main' }} />,
    },
    {
      title: 'High Severity',
      value: findings.filter(f => f.severity >= 0.8).length.toString(),
      icon: <Warning sx={{ fontSize: 40, color: 'error.main' }} />,
    },
    {
      title: 'New Findings',
      value: findings.filter(f => f.status === 'new').length.toString(),
      icon: <Security sx={{ fontSize: 40, color: 'warning.main' }} />,
    },
    {
      title: 'Resolved',
      value: findings.filter(f => f.status === 'resolved').length.toString(),
      icon: <Info sx={{ fontSize: 40, color: 'success.main' }} />,
    },
  ];

  return (
    <Container maxWidth="xl">
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            ML Findings & Explanations
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Review machine learning detected anomalies and security insights
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={fetchFindings}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {/* Stats Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card elevation={2}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  {stat.icon}
                  <Box sx={{ ml: 2 }}>
                    <Typography variant="h4" component="div">
                      {stat.value}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {stat.title}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Findings Table */}
      <Card elevation={2}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Findings
          </Typography>
          
          {loading ? (
            <Typography>Loading findings...</Typography>
          ) : findings.length === 0 ? (
            <Alert severity="info">
              No ML findings available. Upload logs to generate security insights.
            </Alert>
          ) : (
            <TableContainer component={Paper} elevation={0}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Timestamp</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Severity</TableCell>
                    <TableCell>Confidence</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {findings.map((finding) => (
                    <React.Fragment key={finding.id}>
                      <TableRow hover>
                        <TableCell>
                          <Typography variant="body2">
                            {new Date(finding.timestamp).toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                            {finding.type.replace(/_/g, ' ').toUpperCase()}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={`${Math.round(finding.severity * 100)}%`}
                            color={getSeverityColor(finding.severity)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={`${Math.round(finding.confidence * 100)}%`}
                            variant="outlined"
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={finding.status.toUpperCase()}
                            color={getStatusColor(finding.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <IconButton
                              size="small"
                              onClick={() => handleViewDetails(finding)}
                            >
                              <Visibility fontSize="small" />
                            </IconButton>
                            <IconButton
                              size="small"
                              onClick={() => handleRowExpand(finding.id)}
                            >
                              {expandedRows.has(finding.id) ? <ExpandLess /> : <ExpandMore />}
                            </IconButton>
                          </Box>
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
                          <Collapse in={expandedRows.has(finding.id)} timeout="auto" unmountOnExit>
                            <Box sx={{ py: 2 }}>
                              <Typography variant="subtitle2" gutterBottom>
                                Description:
                              </Typography>
                              <Typography variant="body2" paragraph>
                                {finding.description}
                              </Typography>
                              <Typography variant="subtitle2" gutterBottom>
                                Affected Resources:
                              </Typography>
                              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                                {finding.affected_resources.map((resource, idx) => (
                                  <Chip key={idx} label={resource} size="small" variant="outlined" />
                                ))}
                              </Box>
                              <Typography variant="subtitle2" gutterBottom>
                                Time Window:
                              </Typography>
                              <Typography variant="body2">
                                {new Date(finding.time_window.start).toLocaleString()} - {new Date(finding.time_window.end).toLocaleString()}
                              </Typography>
                            </Box>
                          </Collapse>
                        </TableCell>
                      </TableRow>
                    </React.Fragment>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Details Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          ML Finding Details
        </DialogTitle>
        <DialogContent>
          {selectedFinding && (
            <Box>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Type
                  </Typography>
                  <Typography variant="body1">
                    {selectedFinding.type.replace(/_/g, ' ').toUpperCase()}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Timestamp
                  </Typography>
                  <Typography variant="body1">
                    {new Date(selectedFinding.timestamp).toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Severity
                  </Typography>
                  <Chip
                    label={`${Math.round(selectedFinding.severity * 100)}%`}
                    color={getSeverityColor(selectedFinding.severity)}
                    size="small"
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Confidence
                  </Typography>
                  <Chip
                    label={`${Math.round(selectedFinding.confidence * 100)}%`}
                    variant="outlined"
                    size="small"
                  />
                </Grid>
              </Grid>

              <Typography variant="subtitle1" gutterBottom>
                Description
              </Typography>
              <Typography variant="body2" paragraph>
                {selectedFinding.description}
              </Typography>

              <Typography variant="subtitle1" gutterBottom>
                ML Explanation
              </Typography>
              <Alert severity="info" sx={{ mb: 2 }}>
                {selectedFinding.explanation}
              </Alert>

              <Typography variant="subtitle1" gutterBottom>
                Affected Resources
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                {selectedFinding.affected_resources.map((resource, idx) => (
                  <Chip key={idx} label={resource} size="small" variant="outlined" />
                ))}
              </Box>

              <Typography variant="subtitle1" gutterBottom>
                Time Window
              </Typography>
              <Typography variant="body2">
                From: {new Date(selectedFinding.time_window.start).toLocaleString()}
              </Typography>
              <Typography variant="body2">
                To: {new Date(selectedFinding.time_window.end).toLocaleString()}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Close</Button>
          <Button variant="contained" color="primary">
            Mark as Reviewed
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default MLFindings;