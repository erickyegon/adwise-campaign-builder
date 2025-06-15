# AdWise AI Digital Marketing Campaign Builder - Docker Troubleshooting Script
# Comprehensive Docker connectivity and setup troubleshooting

param(
    [switch]$Verbose,
    [switch]$FixNetworking,
    [switch]$RestartDocker,
    [switch]$PullImages,
    [switch]$StartServices
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Cyan"

function Write-Status {
    param($Message, $Color = "White")
    Write-Host "🔧 $Message" -ForegroundColor $Color
}

function Write-Success {
    param($Message)
    Write-Host "✅ $Message" -ForegroundColor $Green
}

function Write-Error {
    param($Message)
    Write-Host "❌ $Message" -ForegroundColor $Red
}

function Write-Warning {
    param($Message)
    Write-Host "⚠️ $Message" -ForegroundColor $Yellow
}

function Write-Info {
    param($Message)
    Write-Host "ℹ️ $Message" -ForegroundColor $Blue
}

Write-Status "AdWise AI Docker Troubleshooting Script" $Blue
Write-Status "=======================================" $Blue

# Check Docker installation
Write-Status "Checking Docker installation..."
try {
    $dockerVersion = docker --version
    Write-Success "Docker is installed: $dockerVersion"
} catch {
    Write-Error "Docker is not installed or not in PATH"
    exit 1
}

# Check Docker daemon
Write-Status "Checking Docker daemon..."
try {
    $dockerInfo = docker info --format "{{.ServerVersion}}"
    Write-Success "Docker daemon is running: Version $dockerInfo"
} catch {
    Write-Error "Docker daemon is not running"
    Write-Info "Please start Docker Desktop"
    exit 1
}

# Check Docker Compose
Write-Status "Checking Docker Compose..."
try {
    $composeVersion = docker-compose --version
    Write-Success "Docker Compose is available: $composeVersion"
} catch {
    Write-Error "Docker Compose is not available"
    exit 1
}

# Check network connectivity
Write-Status "Testing Docker Hub connectivity..."
try {
    $testPull = docker pull hello-world 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker Hub connectivity is working"
        docker rmi hello-world -f | Out-Null
    } else {
        Write-Warning "Docker Hub connectivity issues detected"
        Write-Info "Error: $testPull"
    }
} catch {
    Write-Warning "Network connectivity test failed"
}

# Fix networking if requested
if ($FixNetworking) {
    Write-Status "Attempting to fix Docker networking..." $Yellow
    
    # Restart Docker networking
    Write-Status "Restarting Docker networks..."
    docker network prune -f
    
    # Clear DNS cache
    Write-Status "Clearing DNS cache..."
    ipconfig /flushdns
    
    # Reset Docker daemon
    Write-Status "Resetting Docker daemon..."
    docker system prune -f
    
    Write-Success "Network fixes applied"
}

# Restart Docker if requested
if ($RestartDocker) {
    Write-Status "Restarting Docker Desktop..." $Yellow
    Write-Warning "This will stop all running containers"
    
    # Stop Docker Desktop
    Stop-Process -Name "Docker Desktop" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 5
    
    # Start Docker Desktop
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Write-Status "Waiting for Docker to start..."
    
    # Wait for Docker to be ready
    $timeout = 60
    $elapsed = 0
    while ($elapsed -lt $timeout) {
        try {
            docker info | Out-Null
            Write-Success "Docker is ready"
            break
        } catch {
            Start-Sleep -Seconds 2
            $elapsed += 2
            Write-Host "." -NoNewline
        }
    }
    
    if ($elapsed -ge $timeout) {
        Write-Error "Docker failed to start within $timeout seconds"
        exit 1
    }
}

# Pull required images if requested
if ($PullImages) {
    Write-Status "Pulling required Docker images..." $Yellow
    
    $images = @(
        "mongo:7.0",
        "redis:7-alpine",
        "postgres:15",
        "mongo-express:latest",
        "rediscommander/redis-commander:latest",
        "dpage/pgadmin4:latest",
        "prom/prometheus:latest",
        "grafana/grafana:latest",
        "rabbitmq:3-management-alpine",
        "mailhog/mailhog:latest",
        "minio/minio:latest"
    )
    
    foreach ($image in $images) {
        Write-Status "Pulling $image..."
        try {
            docker pull $image
            Write-Success "Successfully pulled $image"
        } catch {
            Write-Error "Failed to pull $image"
            Write-Info "You may need to pull this image manually later"
        }
    }
}

# Start services if requested
if ($StartServices) {
    Write-Status "Starting AdWise AI development services..." $Yellow
    
    # Check if docker-compose.dev.yml exists
    if (Test-Path "docker-compose.dev.yml") {
        try {
            docker-compose -f docker-compose.dev.yml up -d
            Write-Success "Services started successfully"
            
            # Show running services
            Write-Status "Running services:"
            docker-compose -f docker-compose.dev.yml ps
            
        } catch {
            Write-Error "Failed to start services"
            Write-Info "Error: $_"
        }
    } else {
        Write-Error "docker-compose.dev.yml not found"
        Write-Info "Please run this script from the project root directory"
    }
}

# Display helpful information
Write-Status "Troubleshooting Tips:" $Blue
Write-Info "1. If you have network issues, try: .\scripts\docker_troubleshoot.ps1 -FixNetworking"
Write-Info "2. If Docker is unresponsive, try: .\scripts\docker_troubleshoot.ps1 -RestartDocker"
Write-Info "3. To pre-pull all images, try: .\scripts\docker_troubleshoot.ps1 -PullImages"
Write-Info "4. To start all services, try: .\scripts\docker_troubleshoot.ps1 -StartServices"
Write-Info "5. For verbose output, add -Verbose to any command"

# Check current Docker status
Write-Status "Current Docker Status:" $Blue
try {
    $containers = docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    if ($containers) {
        Write-Info "Running containers:"
        Write-Host $containers
    } else {
        Write-Info "No containers currently running"
    }
} catch {
    Write-Warning "Could not retrieve container status"
}

Write-Status "Troubleshooting complete!" $Green
