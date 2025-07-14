#!/bin/bash
# Production Start Script for Minoru Packing Tools v3.0.0

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root. Consider using a non-root user for security."
fi

# Check environment
if [ -f ".env" ]; then
    print_status "Loading environment variables from .env file..."
    export $(cat .env | xargs)
else
    print_warning "No .env file found. Using default environment variables."
fi

# Set default environment if not specified
export ENVIRONMENT=${ENVIRONMENT:-production}
export APP_VERSION=${APP_VERSION:-3.0.0}
export LOG_LEVEL=${LOG_LEVEL:-WARNING}

print_status "Starting Minoru Packing Tools v${APP_VERSION} in ${ENVIRONMENT} mode..."

# Create necessary directories
mkdir -p logs/production
mkdir -p data/cache
mkdir -p data/uploads

# Set appropriate permissions
chmod 755 logs/production
chmod 755 data/cache
chmod 755 data/uploads

# Health check function
health_check() {
    local max_attempts=30
    local attempt=1
    
    print_status "Performing health check..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
            print_status "Health check passed!"
            return 0
        fi
        
        print_status "Health check attempt $attempt/$max_attempts failed. Retrying in 2 seconds..."
        sleep 2
        ((attempt++))
    done
    
    print_error "Health check failed after $max_attempts attempts"
    return 1
}

# Signal handlers for graceful shutdown
cleanup() {
    print_status "Shutting down gracefully..."
    if [ ! -z "$STREAMLIT_PID" ]; then
        kill -TERM "$STREAMLIT_PID" 2>/dev/null || true
        wait "$STREAMLIT_PID" 2>/dev/null || true
    fi
    print_status "Shutdown complete"
    exit 0
}

trap cleanup SIGTERM SIGINT

# Pre-flight checks
print_status "Performing pre-flight checks..."

# Check Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.10"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

# Check required environment variables
if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your-super-secret-key-here-change-this-in-production" ]; then
    print_error "SECRET_KEY environment variable must be set and changed from default"
    exit 1
fi

# Check if port is available
if netstat -ln | grep :8501 > /dev/null 2>&1; then
    print_warning "Port 8501 is already in use. Application may fail to start."
fi

# Install/update dependencies if needed
if [ "$ENVIRONMENT" != "development" ]; then
    print_status "Installing production dependencies..."
    pip install --no-cache-dir -r deploy/requirements.txt
fi

# Create Streamlit config directory
mkdir -p ~/.streamlit

# Copy production config
if [ -f "deploy/production.toml" ]; then
    cp deploy/production.toml ~/.streamlit/config.toml
    print_status "Production configuration loaded"
else
    print_warning "Production config not found. Using default Streamlit configuration."
fi

# Start the application
print_status "Starting Streamlit application..."
print_status "Application will be available at: http://localhost:8501"
print_status "Press Ctrl+C to stop the application"

# Start Streamlit in background for health check
streamlit run src/main_production.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=true \
    --logger.level=${LOG_LEVEL} \
    --global.developmentMode=false &

STREAMLIT_PID=$!

# Wait a bit for the application to start
sleep 5

# Perform health check
if health_check; then
    print_status "Application started successfully!"
    print_status "Monitoring application... (PID: $STREAMLIT_PID)"
    
    # Wait for the background process
    wait "$STREAMLIT_PID"
else
    print_error "Application failed to start properly"
    cleanup
    exit 1
fi