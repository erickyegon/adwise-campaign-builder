# AdWise AI Digital Marketing Campaign Builder - Docker Development Setup
# Comprehensive Docker setup with retry logic and error handling

param(
    [switch]$Force,
    [switch]$SkipPull,
    [int]$RetryCount = 3,
    [int]$TimeoutSeconds = 300
)

# Import the troubleshooting functions
. "$PSScriptRoot\docker_troubleshoot.ps1" -Verbose:$false

function Start-DockerServices {
    param(
        [int]$MaxRetries = 3,
        [int]$TimeoutSeconds = 300
    )
    
    Write-Status "Starting AdWise AI Development Environment..." $Blue
    Write-Status "=============================================" $Blue
    
    # Validate prerequisites
    Write-Status "Validating prerequisites..."
    
    # Check if docker-compose.dev.yml exists
    if (-not (Test-Path "docker-compose.dev.yml")) {
        Write-Error "docker-compose.dev.yml not found in current directory"
        Write-Info "Please run this script from the project root directory"
        return $false
    }
    
    # Check Docker daemon
    try {
        docker info | Out-Null
        Write-Success "Docker daemon is running"
    } catch {
        Write-Error "Docker daemon is not running. Please start Docker Desktop"
        return $false
    }
    
    # Stop any existing services
    Write-Status "Stopping any existing services..."
    try {
        docker-compose -f docker-compose.dev.yml down --remove-orphans
        Write-Success "Existing services stopped"
    } catch {
        Write-Warning "No existing services to stop"
    }
    
    # Pull images with retry logic (if not skipped)
    if (-not $SkipPull) {
        Write-Status "Pulling Docker images with retry logic..."
        
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
            $success = $false
            for ($i = 1; $i -le $MaxRetries; $i++) {
                Write-Status "Pulling $image (attempt $i/$MaxRetries)..."
                try {
                    $pullResult = docker pull $image 2>&1
                    if ($LASTEXITCODE -eq 0) {
                        Write-Success "Successfully pulled $image"
                        $success = $true
                        break
                    } else {
                        Write-Warning "Attempt $i failed for $image"
                        if ($i -lt $MaxRetries) {
                            Write-Status "Retrying in 5 seconds..."
                            Start-Sleep -Seconds 5
                        }
                    }
                } catch {
                    Write-Warning "Attempt $i failed for $image : $_"
                    if ($i -lt $MaxRetries) {
                        Write-Status "Retrying in 5 seconds..."
                        Start-Sleep -Seconds 5
                    }
                }
            }
            
            if (-not $success) {
                Write-Error "Failed to pull $image after $MaxRetries attempts"
                Write-Info "You may need to check your internet connection or Docker Hub access"
                if (-not $Force) {
                    $continue = Read-Host "Continue anyway? (y/N)"
                    if ($continue -ne "y" -and $continue -ne "Y") {
                        return $false
                    }
                }
            }
        }
    }
    
    # Start services with retry logic
    Write-Status "Starting services with retry logic..."
    
    $success = $false
    for ($i = 1; $i -le $MaxRetries; $i++) {
        Write-Status "Starting services (attempt $i/$MaxRetries)..."
        try {
            # Start services
            $startResult = docker-compose -f docker-compose.dev.yml up -d 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Services started successfully"
                $success = $true
                break
            } else {
                Write-Warning "Attempt $i failed to start services"
                Write-Info "Error: $startResult"
                
                if ($i -lt $MaxRetries) {
                    Write-Status "Cleaning up and retrying in 10 seconds..."
                    docker-compose -f docker-compose.dev.yml down --remove-orphans 2>&1 | Out-Null
                    Start-Sleep -Seconds 10
                }
            }
        } catch {
            Write-Warning "Attempt $i failed: $_"
            if ($i -lt $MaxRetries) {
                Write-Status "Retrying in 10 seconds..."
                Start-Sleep -Seconds 10
            }
        }
    }
    
    if (-not $success) {
        Write-Error "Failed to start services after $MaxRetries attempts"
        return $false
    }
    
    # Wait for services to be healthy
    Write-Status "Waiting for services to be healthy..."
    $healthyServices = @()
    $unhealthyServices = @()
    
    # Wait up to TimeoutSeconds for services to be ready
    $elapsed = 0
    $checkInterval = 10
    
    while ($elapsed -lt $TimeoutSeconds) {
        try {
            $services = docker-compose -f docker-compose.dev.yml ps --format json | ConvertFrom-Json
            
            $allHealthy = $true
            $healthyServices = @()
            $unhealthyServices = @()
            
            foreach ($service in $services) {
                if ($service.State -eq "running") {
                    $healthyServices += $service.Name
                } else {
                    $unhealthyServices += $service.Name
                    $allHealthy = $false
                }
            }
            
            if ($allHealthy) {
                Write-Success "All services are healthy!"
                break
            } else {
                Write-Status "Waiting for services... ($elapsed/$TimeoutSeconds seconds)"
                Write-Info "Healthy: $($healthyServices -join ', ')"
                if ($unhealthyServices.Count -gt 0) {
                    Write-Warning "Unhealthy: $($unhealthyServices -join ', ')"
                }
            }
        } catch {
            Write-Warning "Error checking service health: $_"
        }
        
        Start-Sleep -Seconds $checkInterval
        $elapsed += $checkInterval
    }
    
    if ($elapsed -ge $TimeoutSeconds) {
        Write-Warning "Services did not become healthy within $TimeoutSeconds seconds"
        Write-Info "Some services may still be starting up"
    }
    
    return $true
}

function Show-ServiceStatus {
    Write-Status "Service Status and Access Information:" $Blue
    Write-Status "=====================================" $Blue
    
    try {
        # Show running containers
        $containers = docker-compose -f docker-compose.dev.yml ps
        Write-Host $containers
        
        Write-Status "`nService Access URLs:" $Green
        Write-Info "🌐 Main Application: http://localhost:8000"
        Write-Info "📚 API Documentation: http://localhost:8000/docs"
        Write-Info "💚 Health Check: http://localhost:8000/health"
        Write-Info ""
        Write-Info "🗄️ Database Administration:"
        Write-Info "   • pgAdmin: http://localhost:5050 (admin@adwise.ai / admin_password_2024)"
        Write-Info "   • Mongo Express: http://localhost:8081 (admin / admin_password_2024)"
        Write-Info "   • Redis Commander: http://localhost:8082 (admin / admin_password_2024)"
        Write-Info ""
        Write-Info "📊 Monitoring & Observability:"
        Write-Info "   • Grafana: http://localhost:3000 (admin / admin_password_2024)"
        Write-Info "   • Prometheus: http://localhost:9090"
        Write-Info ""
        Write-Info "🛠️ Development Tools:"
        Write-Info "   • MailHog: http://localhost:8025"
        Write-Info "   • MinIO Console: http://localhost:9001 (admin / admin_password_2024)"
        Write-Info "   • RabbitMQ Management: http://localhost:15672 (admin / admin_password_2024)"
        
    } catch {
        Write-Error "Failed to get service status: $_"
    }
}

# Main execution
Write-Status "AdWise AI Docker Development Setup" $Blue
Write-Status "==================================" $Blue

# Start services
$success = Start-DockerServices -MaxRetries $RetryCount -TimeoutSeconds $TimeoutSeconds

if ($success) {
    Write-Success "Development environment setup complete!"
    Show-ServiceStatus
    
    Write-Status "`nNext Steps:" $Green
    Write-Info "1. Start the development server: python run_dev_server.py --debug --reload"
    Write-Info "2. Access the API documentation at: http://localhost:8000/docs"
    Write-Info "3. Check service health at: http://localhost:8000/health"
    Write-Info ""
    Write-Info "To stop all services: docker-compose -f docker-compose.dev.yml down"
    
} else {
    Write-Error "Failed to setup development environment"
    Write-Info "Try running with -Force to continue despite errors"
    Write-Info "Or use the troubleshooting script: .\scripts\docker_troubleshoot.ps1"
    exit 1
}
