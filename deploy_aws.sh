#!/bin/bash

# AWS Deployment Script for Energy Monitoring System

echo "========================================="
echo "AWS Deployment Script"
echo "Cloud-Based Energy Monitoring System"
echo "========================================="

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Variables
APP_NAME="energy-monitoring-system"
REGION="us-east-1"
EC2_INSTANCE_TYPE="t2.micro"
KEY_NAME="energy-monitor-key"

echo ""
echo "Step 1: Creating EC2 Key Pair..."
aws ec2 create-key-pair --key-name $KEY_NAME --query 'KeyMaterial' --output text > ${KEY_NAME}.pem
chmod 400 ${KEY_NAME}.pem
echo "Key pair created: ${KEY_NAME}.pem"

echo ""
echo "Step 2: Creating Security Group..."
SECURITY_GROUP_ID=$(aws ec2 create-security-group \
    --group-name ${APP_NAME}-sg \
    --description "Security group for Energy Monitoring System" \
    --query 'GroupId' --output text)

echo "Security group created: $SECURITY_GROUP_ID"

echo ""
echo "Step 3: Configuring Security Group Rules..."
# Allow SSH
aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0

# Allow HTTP
aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

# Allow HTTPS
aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

# Allow Flask app port
aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 5000 \
    --cidr 0.0.0.0/0

echo "Security group rules configured"

echo ""
echo "Step 4: Launching EC2 Instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type $EC2_INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-group-ids $SECURITY_GROUP_ID \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "EC2 instance launched: $INSTANCE_ID"

echo ""
echo "Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo "Instance is running!"
echo "Public IP: $PUBLIC_IP"

echo ""
echo "========================================="
echo "Deployment Information"
echo "========================================="
echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"
echo "Key File: ${KEY_NAME}.pem"
echo ""
echo "To connect to your instance:"
echo "ssh -i ${KEY_NAME}.pem ec2-user@${PUBLIC_IP}"
echo ""
echo "After connecting, run:"
echo "1. sudo yum update -y"
echo "2. sudo yum install python3 -y"
echo "3. Upload your application files"
echo "4. pip3 install -r requirements.txt"
echo "5. python3 backend/app.py"
echo "========================================="
