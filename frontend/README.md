# Securon Frontend

A React-based web interface for the Securon security platform, implementing Task 8 requirements.

## Features

### 1. **Log Upload Interface** (Requirement 2.5, 7.2)
- Drag & drop file upload with progress tracking
- Support for VPC Flow Logs, CloudTrail, and IAM logs
- Real-time upload progress indicators
- Automatic log processing and anomaly detection

### 2. **ML Findings & Explanations** (Requirement 7.3)
- View machine learning detected anomalies
- Detailed explanations for each finding
- Severity and confidence scoring
- Affected resources tracking
- Time window analysis

### 3. **Rule Management Interface** (Requirement 7.4)
- Approve/reject candidate security rules
- View active and candidate rules
- Rule details with patterns and remediation
- Severity-based categorization

### 4. **IaC Scanning Interface** (Requirement 7.5)
- Upload Terraform files for scanning
- Paste code directly for analysis
- Real-time security issue detection
- Detailed remediation guidance

### 5. **Dashboard Overview**
- System status monitoring
- Quick action buttons
- Security metrics visualization
- Recent activity tracking

## Tech Stack

- **React 18** with TypeScript
- **Material-UI (MUI)** for components
- **React Router** for navigation
- **React Dropzone** for file uploads
- **Axios** for API communication

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

3. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

## API Integration

The frontend is configured to proxy API requests to `http://localhost:8000` where the Python backend should be running.

### API Endpoints Used:
- `POST /api/logs/upload` - Log file upload and processing
- `GET /api/ml/findings` - Retrieve ML anomaly findings
- `GET /api/rules` - Get active and candidate rules
- `POST /api/rules/{id}/approve` - Approve candidate rules
- `POST /api/rules/{id}/reject` - Reject candidate rules
- `POST /api/iac/scan` - Scan uploaded Terraform files
- `POST /api/iac/scan-text` - Scan pasted Terraform code

## Components

### Core Components:
- **Dashboard** - Main overview and quick actions
- **LogUpload** - File upload with progress tracking
- **MLFindings** - ML anomaly results and explanations
- **RuleManagement** - Rule approval/rejection interface
- **IaCScanner** - Infrastructure scanning interface
- **Navbar** - Navigation between sections

### Features:
- **File Upload**: Drag & drop with progress bars
- **Real-time Updates**: Live status updates during processing
- **Responsive Design**: Works on desktop and mobile
- **Error Handling**: User-friendly error messages
- **Loading States**: Progress indicators for all operations

## Interface Synchronization (Requirement 7.4, 7.5)

The web interface maintains synchronization with the backend through:
- Real-time API calls for data updates
- Automatic refresh after rule actions
- Progress tracking for long-running operations
- Error handling and retry mechanisms

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)