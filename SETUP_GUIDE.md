# Setup Guide - Energy Monitoring System

Complete step-by-step guide to set up and run the Cloud-Based Electricity Energy Consumption Monitoring System.

## Table of Contents
1. [Local Development Setup](#local-development-setup)
2. [Running the Application](#running-the-application)
3. [Testing the System](#testing-the-system)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [Common Issues](#common-issues)

---

## Local Development Setup

### Step 1: Install Python
Make sure Python 3.11 or higher is installed:
```bash
python --version
# or
python3 --version
```

If not installed, download from [python.org](https://www.python.org/downloads/)

### Step 2: Download the Project
```bash
# Extract the project files to a folder
cd path/to/energy-monitoring-system
```

### Step 3: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

Expected output:
```
Successfully installed Flask-3.0.0 Flask-CORS-4.0.0 numpy-1.26.3 scipy-1.11.4 ...
```

---

## Running the Application

### Method 1: Direct Python Execution

1. Navigate to the backend folder:
```bash
cd backend
```

2. Run the Flask application:
```bash
python app.py
```

Expected output:
```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://0.0.0.0:5000
Press CTRL+C to quit
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

### Method 2: Using Flask Command

```bash
# Set environment variables
export FLASK_APP=backend/app.py
export FLASK_ENV=development

# Run Flask
flask run
```

---

## Testing the System

### Step 1: Create an Account
1. Open `http://localhost:5000` in your browser
2. Click on "Register" tab
3. Fill in:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `password123`
4. Click "Register"

### Step 2: Login
1. Click on "Login" tab
2. Enter credentials
3. Click "Login"

You should be redirected to the dashboard.

### Step 3: Add Sample Data
1. Click "Add Reading" button
2. Enter sample data:
   - Consumption: `45.5` kWh
   - Cost: `$5.46`
   - Device: `Main Meter`
   - Location: `Home`
3. Click "Add Reading"

### Step 4: Add Multiple Readings
To test AI features, add at least 10 readings with varying consumption values:

```
Day 1: 42.3 kWh, $5.08
Day 2: 45.1 kWh, $5.41
Day 3: 43.8 kWh, $5.26
Day 4: 46.2 kWh, $5.54
Day 5: 44.5 kWh, $5.34
Day 6: 47.0 kWh, $5.64
Day 7: 85.0 kWh, $10.20 (Anomaly - will trigger alert!)
Day 8: 44.8 kWh, $5.38
Day 9: 43.2 kWh, $5.18
Day 10: 45.9 kWh, $5.51
```

### Step 5: Test AI Features

#### Generate Predictions
1. Navigate to "AI Predictions" section
2. Select "Next 7 Days"
3. Click "Generate Predictions"
4. View predicted consumption with confidence ranges

#### Check Anomaly Alerts
1. Navigate to "Alerts" section
2. You should see an alert for Day 7 (85.0 kWh) as it's significantly higher

#### View Recommendations
1. Navigate to "Recommendations" section
2. View AI-generated energy-saving tips

#### Check Health Score
1. Go back to "Overview" section
2. View your consumption health score

---

## Docker Deployment

### Prerequisites
- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed

### Step 1: Build and Run with Docker Compose

```bash
# Build and start containers
docker-compose up -d
```

### Step 2: Check Container Status
```bash
docker-compose ps
```

### Step 3: View Logs
```bash
docker-compose logs -f
```

### Step 4: Access Application
Open browser: `http://localhost:5000`

### Step 5: Stop Containers
```bash
docker-compose down
```

---

## Cloud Deployment

### AWS Deployment

#### Prerequisites
- AWS Account
- AWS CLI installed and configured
- EC2 key pair created

#### Step 1: Install AWS CLI
```bash
# On Windows (using installer from AWS website)
# On macOS
brew install awscli

# On Linux
sudo apt-get install awscli
```

#### Step 2: Configure AWS
```bash
aws configure
```
Enter:
- AWS Access Key ID
- AWS Secret Access Key
- Default region: `us-east-1`
- Default output format: `json`

#### Step 3: Run Deployment Script
```bash
chmod +x deploy_aws.sh
./deploy_aws.sh
```

#### Step 4: Manual Setup (Alternative)

1. **Launch EC2 Instance**
   - Login to AWS Console
   - Navigate to EC2
   - Click "Launch Instance"
   - Select: Amazon Linux 2 AMI
   - Instance type: t2.micro (free tier)
   - Configure security group: Allow ports 22, 80, 443, 5000
   - Launch instance

2. **Connect to Instance**
```bash
ssh -i your-key.pem ec2-user@your-instance-ip
```

3. **Install Dependencies**
```bash
sudo yum update -y
sudo yum install python3 git -y
```

4. **Upload Project Files**
```bash
# On your local machine
scp -i your-key.pem -r energy-monitoring-system ec2-user@your-instance-ip:~/
```

5. **Run Application on EC2**
```bash
cd energy-monitoring-system
pip3 install -r requirements.txt
python3 backend/app.py
```

6. **Access Application**
```
http://your-instance-ip:5000
```

### Google Cloud Deployment

1. **Create GCP Project**
2. **Enable Compute Engine API**
3. **Create VM Instance**
4. **SSH into instance and follow similar steps as AWS**

### Microsoft Azure Deployment

1. **Create Azure Account**
2. **Create Virtual Machine**
3. **Configure Network Security Group**
4. **SSH and deploy application**

---

## Common Issues

### Issue 1: Port 5000 Already in Use
**Solution**: Change port in `backend/app.py`
```python
app.run(debug=True, host='0.0.0.0', port=8000)
```

### Issue 2: Module Not Found Error
**Solution**: Install missing dependencies
```bash
pip install -r requirements.txt
```

### Issue 3: Database Connection Error
**Solution**: Delete existing database and restart
```bash
rm database/energy.db
python backend/app.py
```

### Issue 4: CORS Error in Browser
**Solution**: Make sure Flask-CORS is installed
```bash
pip install flask-cors
```

### Issue 5: Charts Not Displaying
**Solution**: Check internet connection (Chart.js loads from CDN)

### Issue 6: Login Not Working
**Solution**:
1. Check browser console for errors
2. Verify backend is running
3. Clear browser cache

### Issue 7: AI Predictions Fail
**Solution**: Add at least 7 consumption records before generating predictions

---

## Production Deployment Checklist

- [ ] Change SECRET_KEY in config
- [ ] Disable DEBUG mode
- [ ] Use production database (PostgreSQL/MySQL)
- [ ] Set up HTTPS with SSL certificate
- [ ] Configure proper CORS origins
- [ ] Implement password hashing (bcrypt)
- [ ] Set up database backups
- [ ] Configure logging
- [ ] Use environment variables for secrets
- [ ] Set up monitoring and alerts
- [ ] Configure firewall rules
- [ ] Use process manager (PM2, Supervisor, Gunicorn)

### Production Server Setup (Gunicorn)

1. Install Gunicorn:
```bash
pip install gunicorn
```

2. Run with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

3. Use with Nginx (Recommended):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Testing Checklist

- [ ] User registration works
- [ ] User login works
- [ ] Add consumption data works
- [ ] Dashboard displays data
- [ ] Charts render correctly
- [ ] AI predictions generate
- [ ] Anomaly detection triggers alerts
- [ ] Health score calculates
- [ ] Recommendations display
- [ ] Data export works
- [ ] Settings save properly

---

## Next Steps

1. Customize electricity rates in Settings
2. Add real consumption data
3. Set up alert thresholds
4. Generate weekly reports
5. Explore AI predictions
6. Implement additional features

---

## Support

If you encounter any issues not covered in this guide, please:
1. Check the error messages in terminal/console
2. Review the application logs
3. Verify all dependencies are installed
4. Check the README.md for additional information

---

**Happy Monitoring!**
