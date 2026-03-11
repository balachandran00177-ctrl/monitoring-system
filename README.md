# Cloud-Based Electricity Energy Consumption Monitoring System

A comprehensive web-based platform for monitoring, analyzing, and managing electricity consumption with AI-powered predictions and anomaly detection.

## Features

### Core Features
- **Real-time Monitoring**: Track electricity consumption in real-time
- **Historical Data Analysis**: View consumption trends over days, weeks, and months
- **Cost Analysis**: Calculate and visualize energy costs
- **Multi-device Support**: Track consumption from different devices and locations
- **Data Export**: Export consumption data in CSV and JSON formats

### AI-Powered Features (NEW!)
- **Consumption Prediction**: AI-powered predictions for future energy usage using exponential smoothing
- **Anomaly Detection**: Automatic detection of unusual consumption patterns using statistical analysis
- **Smart Alerts**: Real-time notifications for abnormal consumption
- **Health Score**: Overall consumption health score based on usage patterns
- **AI Recommendations**: Personalized energy-saving recommendations

### Dashboard Features
- Interactive charts and visualizations
- Daily, monthly, and yearly statistics
- Consumption health scoring
- Alert management
- Settings customization

## Technology Stack

### Backend
- **Python 3.11+**
- **Flask** - Web framework
- **SQLite** - Database
- **NumPy** - Numerical computations for AI
- **SciPy** - Statistical analysis

### Frontend
- **HTML5, CSS3, JavaScript**
- **Chart.js** - Data visualization
- **Responsive Design** - Mobile-friendly interface

### Cloud Deployment
- **AWS / Google Cloud / Azure** support
- **Docker** containerization
- **Docker Compose** for easy deployment

## Installation

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd energy-monitoring-system
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
cd backend
python app.py
```

The application will start on `http://localhost:5000`

## Docker Deployment

### Using Docker Compose (Recommended)
```bash
docker-compose up -d
```

### Using Docker
```bash
# Build the image
docker build -t energy-monitor .

# Run the container
docker run -p 5000:5000 -v $(pwd)/database:/app/database energy-monitor
```

## Cloud Deployment

### AWS Deployment

1. Install AWS CLI
2. Configure AWS credentials:
```bash
aws configure
```

3. Run deployment script:
```bash
chmod +x deploy_aws.sh
./deploy_aws.sh
```

### Manual Deployment Steps

1. **Create EC2 Instance** (t2.micro or higher)
2. **Install Python 3.11+**
3. **Upload application files**
4. **Install dependencies**:
```bash
pip3 install -r requirements.txt
```
5. **Run the application**:
```bash
python3 backend/app.py
```

## Usage Guide

### 1. Registration and Login
- Navigate to `http://localhost:5000`
- Create a new account or login with existing credentials

### 2. Adding Energy Readings
- Click "Add Reading" button in the dashboard
- Enter consumption (kWh), cost, device name, and location
- Submit the form

### 3. Viewing Analytics
- **Overview**: See daily, monthly, and average consumption
- **Consumption**: View detailed consumption history
- **AI Predictions**: Generate future consumption predictions
- **Alerts**: Check for anomalies and unusual patterns
- **Recommendations**: View AI-generated energy-saving tips

### 4. AI Features

#### Consumption Predictions
1. Navigate to "AI Predictions" section
2. Select prediction period (7, 14, or 30 days)
3. Click "Generate Predictions"
4. View predicted consumption with confidence ranges

#### Anomaly Detection
- Automatic detection runs when new data is added
- Alerts appear in the "Alerts" section
- Severity levels: Low, Medium, High, Critical

#### Health Score
- Displayed on the overview page
- Scores from 0-100 based on:
  - Consumption consistency
  - Trend analysis
  - Pattern stability

## API Documentation

### Authentication Endpoints

#### Register User
```
POST /api/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password"
}
```

#### Login User
```
POST /api/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "secure_password"
}
```

### Consumption Endpoints

#### Add Consumption
```
POST /api/consumption/add
Content-Type: application/json

{
  "user_id": 1,
  "consumption_kwh": 45.5,
  "cost": 5.46,
  "device_name": "Main Meter",
  "location": "Home"
}
```

#### Get Consumption Data
```
GET /api/consumption/{user_id}?period=week
```

#### Get Statistics
```
GET /api/stats/{user_id}
```

### AI Endpoints

#### Generate Predictions
```
GET /api/predict/{user_id}?days=7
```

#### Get Alerts
```
GET /api/alerts/{user_id}
```

#### Get Recommendations
```
GET /api/recommendations/{user_id}
```

### Export Endpoint
```
GET /api/export/{user_id}?format=csv
```

## Project Structure

```
energy-monitoring-system/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── ai_predictor.py        # AI prediction engine
│   └── anomaly_detector.py    # Anomaly detection system
├── frontend/
│   ├── index.html             # Login page
│   ├── dashboard.html         # Main dashboard
│   ├── css/
│   │   └── style.css          # Styles
│   └── js/
│       ├── auth.js            # Authentication logic
│       └── dashboard.js       # Dashboard functionality
├── database/
│   └── energy.db              # SQLite database (auto-created)
├── config/
│   └── config.py              # Configuration settings
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose configuration
├── deploy_aws.sh              # AWS deployment script
└── README.md                  # This file
```

## AI Models Explained

### 1. Energy Consumption Predictor
- **Algorithm**: Exponential Smoothing
- **Features**:
  - Level and trend smoothing
  - Confidence score calculation
  - Range estimation
  - Adaptive to consumption patterns

### 2. Anomaly Detector
- **Algorithm**: Statistical Z-score Analysis
- **Features**:
  - Real-time anomaly detection
  - Pattern-based analysis
  - Severity classification
  - Consecutive increase detection
  - Sudden spike detection

### 3. Health Score Calculator
- **Metrics**:
  - Consumption variability
  - Trend analysis
  - Anomaly frequency
  - Pattern consistency

## Configuration

Edit `config/config.py` to customize:

- Database path
- API host and port
- AI model parameters
- Electricity rates
- Alert thresholds
- Cloud provider settings

## Security Considerations

- Change default SECRET_KEY in production
- Use HTTPS for production deployment
- Implement proper password hashing (bcrypt recommended)
- Set up environment variables for sensitive data
- Configure CORS properly for production
- Regular database backups
- Use AWS RDS or Cloud SQL for production databases

## Future Enhancements

1. **Machine Learning Integration**
   - Deep learning models for better predictions
   - Pattern recognition using neural networks
   - Weather-based consumption forecasting

2. **IoT Integration**
   - Smart meter integration
   - Real-time sensor data collection
   - MQTT protocol support

3. **Advanced Features**
   - Mobile application
   - Bill payment integration
   - Energy-saving challenges
   - Community comparison
   - Carbon footprint calculation

4. **Enhanced AI**
   - Natural language reports
   - Voice assistant integration
   - Automated scheduling recommendations

## Troubleshooting

### Database Issues
If database errors occur, delete `database/energy.db` and restart the application.

### Port Already in Use
Change the port in `backend/app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8000)
```

### CORS Errors
Check that Flask-CORS is installed and configured properly.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is open-source and available under the MIT License.

## Support

For issues and questions, please create an issue in the repository.

## Acknowledgments

- Chart.js for data visualization
- Flask framework
- NumPy and SciPy for AI computations

---

**Developed as a Final Year Project**
Cloud-Based Electricity Energy Consumption Monitoring System with AI Features
