#!/bin/bash

# Redis Cluster Local Deployment Script
# Deploys Redis master-replica-sentinel setup locally on Ubuntu
# Based on: https://github.com/Hatef-Rostamkhani/test-docker

set -e  # Exit on any error

# Configuration
PROJECT_DIR="/opt/redis-cluster"
GITHUB_REPO="https://github.com/Hatef-Rostamkhani/test-docker.git"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root (use sudo)"
        exit 1
    fi
    success "Running as root - OK"
}

# Check if required tools are installed
check_requirements() {
    log "Checking system requirements..."
    
    # Check Ubuntu version
    if ! grep -q "Ubuntu" /etc/os-release; then
        warning "This script is designed for Ubuntu. Proceeding anyway..."
    fi
    
    # Check if git is installed
    if ! command -v git &> /dev/null; then
        log "Installing git..."
        apt-get update
        apt-get install -y git
    fi
    
    # Check if curl is installed
    if ! command -v curl &> /dev/null; then
        log "Installing curl..."
        apt-get install -y curl
    fi
    
    success "System requirements check passed"
}

# Install Docker and Docker Compose
install_docker() {
    log "Installing Docker and Docker Compose..."
    
    # Update package index
    apt-get update
    
    # Install prerequisites
    apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io
    
    # Install Docker Compose
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    
    # Create docker group and add current user
    groupadd docker 2>/dev/null || true
    usermod -aG docker $SUDO_USER 2>/dev/null || true
    
    success "Docker and Docker Compose installed successfully"
}

# Clone the repository
clone_repository() {
    log "Cloning Redis cluster repository..."
    
    # Remove existing directory if it exists
    if [ -d "$PROJECT_DIR" ]; then
        log "Removing existing directory..."
        rm -rf "$PROJECT_DIR"
    fi
    
    # Clone the repository
    git clone "$GITHUB_REPO" "$PROJECT_DIR"
    
    # Navigate to project directory
    cd "$PROJECT_DIR"
    
    success "Repository cloned successfully"
}

# Set up project structure
setup_project() {
    log "Setting up project structure..."
    
    cd "$PROJECT_DIR"
    
    # Make shell scripts executable
    chmod +x *.sh 2>/dev/null || true
    chmod +x scripts/*.sh 2>/dev/null || true
    
    # Set secure permissions for secrets
    chmod 600 secrets/* 2>/dev/null || true
    
    # Set permissions for config files
    chmod 644 config/* 2>/dev/null || true
    chmod 644 *.json 2>/dev/null || true
    chmod 644 docker-compose.yml
    
    success "Project structure configured"
}

# Install Python dependencies
install_python_deps() {
    log "Installing Python dependencies..."
    
    # Check if Python 3 is installed
    if ! command -v python3 &> /dev/null; then
        log "Installing Python 3..."
        apt-get install -y python3 python3-pip python3-venv python3-full
    fi
    
    # Install pip and venv if not present
    if ! command -v pip3 &> /dev/null; then
        log "Installing pip3 and venv..."
        apt-get install -y python3-pip python3-venv python3-full
    fi
    
    # Try to install Redis client via system package manager first
    log "Attempting to install Redis client via system package manager..."
    if apt-get install -y python3-redis 2>/dev/null; then
        log "Redis client installed via system package manager"
        
        # Create a simple wrapper script for system Python
        cat > run-tests.sh << 'EOF'
#!/bin/bash
cd /opt/redis-cluster
python3 "$@"
EOF
        chmod +x run-tests.sh
        success "Python dependencies installed via system packages"
        return 0
    else
        log "System package not available, using virtual environment..."
    fi
    
    # Create virtual environment for the project
    log "Creating Python virtual environment..."
    cd "$PROJECT_DIR"
    python3 -m venv venv
    
    # Activate virtual environment and install Redis client
    log "Installing Redis Python client in virtual environment..."
    source venv/bin/activate
    pip install redis
    
    # Create a wrapper script for running tests with the virtual environment
    cat > run-tests.sh << 'EOF'
#!/bin/bash
cd /opt/redis-cluster
source venv/bin/activate
python3 "$@"
EOF
    chmod +x run-tests.sh
    
    success "Python dependencies installed in virtual environment"
}

# Deploy and start services
deploy_services() {
    log "Deploying Redis cluster services..."
    
    cd "$PROJECT_DIR"
    
    # Stop any existing containers
    docker-compose down 2>/dev/null || true
    
    # Pull latest images
    docker-compose pull
    
    # Start services
    docker-compose up -d
    
    success "Redis cluster services deployed"
}

# Verify deployment
verify_deployment() {
    log "Verifying deployment..."
    
    cd "$PROJECT_DIR"
    
    echo "=== Container Status ==="
    docker-compose ps
    
    echo ""
    echo "=== Redis Master Health ==="
    docker-compose exec -T redis-master redis-cli -a $(cat secrets/redis_master_password) ping || echo "Master not ready yet"
    
    echo ""
    echo "=== Redis Replicas Health ==="
    docker-compose exec -T redis-replica-1 redis-cli -a $(cat secrets/redis_master_password) ping || echo "Replica-1 not ready yet"
    docker-compose exec -T redis-replica-2 redis-cli -a $(cat secrets/redis_master_password) ping || echo "Replica-2 not ready yet"
    
    echo ""
    echo "=== Sentinel Status ==="
    docker-compose exec -T redis-sentinel-1 redis-cli -p 26379 -a $(cat secrets/redis_sentinel_password) ping || echo "Sentinel-1 not ready yet"
    docker-compose exec -T redis-sentinel-2 redis-cli -p 26379 -a $(cat secrets/redis_sentinel_password) ping || echo "Sentinel-2 not ready yet"
    docker-compose exec -T redis-sentinel-3 redis-cli -p 26379 -a $(cat secrets/redis_sentinel_password) ping || echo "Sentinel-3 not ready yet"
    
    echo ""
    echo "=== Network Information ==="
    docker network ls | grep redis || echo "No Redis networks found"
    docker network inspect redisnet 2>/dev/null | grep -A 5 "Containers" || echo "Network not ready yet"
    
    success "Deployment verification completed"
}

# Run tests
run_tests() {
    log "Running Redis cluster tests..."
    
    cd "$PROJECT_DIR"
    
    # Run Python tests if they exist using virtual environment
    if [ -f "test-redis-cluster.py" ]; then
        log "Running Redis cluster tests..."
        ./run-tests.sh test-redis-cluster.py || warning "Some tests failed"
    fi
    
    if [ -f "test-sentinel-simple.py" ]; then
        log "Running Sentinel tests..."
        ./run-tests.sh test-sentinel-simple.py || warning "Some tests failed"
    fi
    
    success "Tests completed"
}

# Display access information
show_access_info() {
    log "Deployment completed successfully!"
    echo ""
    echo "=== Access Information ==="
    echo "Redis Master:     localhost:6379"
    echo "Redis Replica-1:  localhost:6380"
    echo "Redis Replica-2:  localhost:6381"
    echo "Redis Sentinel-1: localhost:26379"
    echo "Redis Sentinel-2: localhost:26380"
    echo "Redis Sentinel-3: localhost:26381"
    echo "RedisInsight:     http://localhost:8001"
    echo ""
    echo "=== Connection Commands ==="
    echo "Check status:     cd $PROJECT_DIR && docker-compose ps"
    echo "View logs:        cd $PROJECT_DIR && docker-compose logs -f"
    echo "Stop services:    cd $PROJECT_DIR && docker-compose down"
    echo "Start services:   cd $PROJECT_DIR && docker-compose up -d"
    echo "Restart services: cd $PROJECT_DIR && docker-compose restart"
    echo ""
    echo "=== Test Commands ==="
    echo "Run cluster tests: cd $PROJECT_DIR && ./run-tests.sh test-redis-cluster.py"
    echo "Run sentinel tests: cd $PROJECT_DIR && ./run-tests.sh test-sentinel-simple.py"
    echo "Activate venv: cd $PROJECT_DIR && source venv/bin/activate"
    echo ""
    echo "=== Management Commands ==="
    echo "Connect to Master:     redis-cli -h localhost -p 6379 -a \$(cat $PROJECT_DIR/secrets/redis_master_password)"
    echo "Connect to Replica-1:  redis-cli -h localhost -p 6380 -a \$(cat $PROJECT_DIR/secrets/redis_master_password)"
    echo "Connect to Replica-2:  redis-cli -h localhost -p 6381 -a \$(cat $PROJECT_DIR/secrets/redis_master_password)"
    echo "Connect to Sentinel-1: redis-cli -h localhost -p 26379 -a \$(cat $PROJECT_DIR/secrets/redis_sentinel_password)"
    echo ""
    echo "=== Security Notes ==="
    echo "- Change default passwords in $PROJECT_DIR/secrets/ directory"
    echo "- Configure firewall rules for Redis ports if needed"
    echo "- Consider using SSL/TLS for production"
    echo "- Regularly update Docker images"
    echo ""
    echo "=== Project Location ==="
    echo "Project installed at: $PROJECT_DIR"
    echo "Configuration files: $PROJECT_DIR/config/"
    echo "Secret files: $PROJECT_DIR/secrets/"
    echo "Test scripts: $PROJECT_DIR/*.py"
}

# Create management scripts
create_management_scripts() {
    log "Creating management scripts..."
    
    # Create start script
    cat > /usr/local/bin/redis-cluster-start << 'EOF'
#!/bin/bash
cd /opt/redis-cluster
docker-compose up -d
echo "Redis cluster started"
EOF
    
    # Create stop script
    cat > /usr/local/bin/redis-cluster-stop << 'EOF'
#!/bin/bash
cd /opt/redis-cluster
docker-compose down
echo "Redis cluster stopped"
EOF
    
    # Create status script
    cat > /usr/local/bin/redis-cluster-status << 'EOF'
#!/bin/bash
cd /opt/redis-cluster
docker-compose ps
EOF
    
    # Create logs script
    cat > /usr/local/bin/redis-cluster-logs << 'EOF'
#!/bin/bash
cd /opt/redis-cluster
docker-compose logs -f "$@"
EOF
    
    # Make scripts executable
    chmod +x /usr/local/bin/redis-cluster-*
    
    success "Management scripts created"
}

# Main deployment function
main() {
    log "Starting Redis cluster local deployment"
    echo "Repository: $GITHUB_REPO"
    echo "Installation directory: $PROJECT_DIR"
    echo ""
    
    check_root
    check_requirements
    install_docker
    clone_repository
    setup_project
    install_python_deps
    deploy_services
    
    # Wait for services to start
    log "Waiting for services to initialize..."
    sleep 30
    
    verify_deployment
    run_tests
    create_management_scripts
    show_access_info
    
    success "Local deployment completed successfully!"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "install-docker")
        check_root
        install_docker
        ;;
    "clone-repo")
        check_root
        clone_repository
        ;;
    "deploy-services")
        check_root
        deploy_services
        ;;
    "verify")
        check_root
        verify_deployment
        ;;
    "test")
        check_root
        run_tests
        ;;
    "status")
        cd "$PROJECT_DIR" && docker-compose ps
        ;;
    "logs")
        cd "$PROJECT_DIR" && docker-compose logs -f "${@:2}"
        ;;
    "stop")
        cd "$PROJECT_DIR" && docker-compose down
        ;;
    "start")
        cd "$PROJECT_DIR" && docker-compose up -d
        ;;
    "restart")
        cd "$PROJECT_DIR" && docker-compose restart
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  deploy           - Full deployment (default)"
        echo "  install-docker   - Install Docker only"
        echo "  clone-repo       - Clone repository only"
        echo "  deploy-services  - Deploy services only"
        echo "  verify          - Verify deployment only"
        echo "  test            - Run tests only"
        echo "  status          - Show container status"
        echo "  logs [service]  - Show logs (optionally for specific service)"
        echo "  stop            - Stop all services"
        echo "  start           - Start all services"
        echo "  restart         - Restart all services"
        echo "  help            - Show this help message"
        echo ""
        echo "Management commands (after installation):"
        echo "  redis-cluster-start   - Start the cluster"
        echo "  redis-cluster-stop    - Stop the cluster"
        echo "  redis-cluster-status  - Show status"
        echo "  redis-cluster-logs    - Show logs"
        ;;
    *)
        error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
