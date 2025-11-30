#!/bin/bash

# ===========================================
# DEVORA SAAS V2 - Deployment Script
# ===========================================
# Usage: ./deploy.sh [command]
#
# Commands:
#   start     - Start all services (default)
#   stop      - Stop all services
#   restart   - Restart all services
#   logs      - View logs
#   status    - Check status
#   build     - Rebuild containers
#   clean     - Remove all data (DESTRUCTIVE)
#   setup     - First-time setup
# ===========================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env exists
check_env() {
    if [ ! -f .env ]; then
        log_error ".env file not found!"
        log_info "Run: cp .env.example .env"
        log_info "Then edit .env with your configuration"
        exit 1
    fi
}

# First-time setup
setup() {
    log_info "Starting first-time setup..."
    
    # Check if .env exists
    if [ ! -f .env ]; then
        log_info "Creating .env from template..."
        cp .env.example .env
        
        # Generate random passwords
        MONGO_PASS=$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 24)
        POSTGRES_PASS=$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 24)
        SECRET=$(openssl rand -hex 32)
        
        # Replace placeholders (works on both Linux and macOS)
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/CHANGE_ME_SECURE_PASSWORD_123/$MONGO_PASS/g" .env
            sed -i '' "s/CHANGE_ME_SECURE_PASSWORD_456/$POSTGRES_PASS/g" .env
            sed -i '' "s/CHANGE_ME_GENERATE_WITH_OPENSSL_RAND_HEX_32/$SECRET/g" .env
        else
            sed -i "s/CHANGE_ME_SECURE_PASSWORD_123/$MONGO_PASS/g" .env
            sed -i "s/CHANGE_ME_SECURE_PASSWORD_456/$POSTGRES_PASS/g" .env
            sed -i "s/CHANGE_ME_GENERATE_WITH_OPENSSL_RAND_HEX_32/$SECRET/g" .env
        fi
        
        log_success ".env created with secure random passwords"
        log_warning "Edit .env to add your API keys (OpenRouter, Stripe, etc.)"
    else
        log_info ".env already exists, skipping..."
    fi
    
    # Create necessary directories
    mkdir -p data/mongodb data/postgres
    
    log_success "Setup complete!"
    log_info "Next steps:"
    echo "  1. Edit .env and add your API keys"
    echo "  2. Run: ./deploy.sh start"
}

# Start services
start() {
    check_env
    log_info "Starting Devora services..."
    docker compose up -d
    
    log_info "Waiting for services to be healthy..."
    sleep 10
    
    # Check health
    if docker compose ps | grep -q "unhealthy\|Exit"; then
        log_warning "Some services may not be healthy yet. Check with: ./deploy.sh status"
    else
        log_success "All services started!"
    fi
    
    echo ""
    log_info "Access your application:"
    echo "  Frontend: http://localhost:${FRONTEND_PORT:-4522}"
    echo "  Backend:  http://localhost:${BACKEND_PORT:-4521}/api/"
}

# Stop services
stop() {
    log_info "Stopping Devora services..."
    docker compose down
    log_success "All services stopped"
}

# Restart services
restart() {
    stop
    start
}

# View logs
logs() {
    docker compose logs -f "$@"
}

# Check status
status() {
    log_info "Service Status:"
    docker compose ps
    echo ""
    log_info "Health Check:"
    
    # Check backend
    if curl -s http://localhost:${BACKEND_PORT:-4521}/api/ > /dev/null 2>&1; then
        log_success "Backend: Healthy"
    else
        log_error "Backend: Not responding"
    fi
    
    # Check frontend
    if curl -s http://localhost:${FRONTEND_PORT:-4522} > /dev/null 2>&1; then
        log_success "Frontend: Healthy"
    else
        log_error "Frontend: Not responding"
    fi
}

# Rebuild containers
build() {
    check_env
    log_info "Rebuilding containers..."
    docker compose build --no-cache
    log_success "Build complete"
}

# Clean everything (DESTRUCTIVE)
clean() {
    log_warning "This will delete ALL data including databases!"
    read -p "Are you sure? (type 'yes' to confirm): " confirm
    
    if [ "$confirm" = "yes" ]; then
        log_info "Stopping and removing all containers, volumes, and networks..."
        docker compose down -v --remove-orphans
        log_success "Cleanup complete"
    else
        log_info "Cancelled"
    fi
}

# Update from git and rebuild
update() {
    log_info "Pulling latest changes..."
    git pull
    
    log_info "Rebuilding containers..."
    docker compose build
    
    log_info "Restarting services..."
    docker compose up -d
    
    log_success "Update complete!"
}

# Main
case "${1:-start}" in
    setup)
        setup
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        shift
        logs "$@"
        ;;
    status)
        status
        ;;
    build)
        build
        ;;
    clean)
        clean
        ;;
    update)
        update
        ;;
    *)
        echo "Usage: $0 {setup|start|stop|restart|logs|status|build|clean|update}"
        exit 1
        ;;
esac
