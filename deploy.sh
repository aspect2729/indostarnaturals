#!/bin/bash

# IndoStar Naturals Deployment Script
# This script helps deploy the application to different environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if environment is provided
if [ -z "$1" ]; then
    print_error "Usage: ./deploy.sh [development|staging|production]"
    exit 1
fi

ENVIRONMENT=$1

print_info "Deploying to $ENVIRONMENT environment..."

case $ENVIRONMENT in
    development)
        print_info "Starting development environment with docker-compose..."
        docker-compose up -d
        print_info "Development environment started!"
        print_info "Backend: http://localhost:8000"
        print_info "Frontend: http://localhost:5173"
        ;;
    
    staging|production)
        print_info "Building Docker images..."
        
        # Build backend image
        print_info "Building backend image..."
        docker build -t indostar-naturals/backend:latest -f backend/Dockerfile.prod backend/
        
        # Build frontend image
        print_info "Building frontend image..."
        docker build -t indostar-naturals/frontend:latest -f frontend/Dockerfile.prod frontend/
        
        if [ "$ENVIRONMENT" = "production" ]; then
            print_warning "Deploying to PRODUCTION environment!"
            read -p "Are you sure you want to continue? (yes/no): " confirm
            if [ "$confirm" != "yes" ]; then
                print_error "Deployment cancelled."
                exit 1
            fi
            
            # Check if .env.prod exists
            if [ ! -f "backend/.env.prod" ]; then
                print_error "backend/.env.prod file not found!"
                print_info "Please create it from backend/.env.prod.example"
                exit 1
            fi
            
            print_info "Starting production environment..."
            docker-compose -f docker-compose.prod.yml up -d
            
            print_info "Waiting for services to be healthy..."
            sleep 10
            
            print_info "Running database migrations..."
            docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head
            
            print_info "Production deployment complete!"
            print_info "Application: https://indostarnaturals.com"
            print_info "API: https://api.indostarnaturals.com"
        else
            print_info "Deploying to staging environment..."
            # Add staging-specific deployment logic here
            print_info "Staging deployment complete!"
        fi
        ;;
    
    *)
        print_error "Invalid environment: $ENVIRONMENT"
        print_error "Valid options: development, staging, production"
        exit 1
        ;;
esac

print_info "Deployment completed successfully!"
