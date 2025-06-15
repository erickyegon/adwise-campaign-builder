# AdWise AI Digital Marketing Campaign Builder - Docker Configuration Initialization
# Comprehensive script to initialize Docker volumes with configuration files

param(
    [switch]$Force,
    [switch]$Verbose
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Cyan"
$White = "White"

function Write-Status {
    param($Message, $Color = $White)
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

Write-Status "AdWise AI Docker Configuration Initialization" $Blue
Write-Status "================================================" $Blue

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Success "Docker is running"
} catch {
    Write-Error "Docker is not running. Please start Docker Desktop"
    exit 1
}

# Create Prometheus configuration in volume
Write-Status "Initializing Prometheus configuration..."
$prometheusConfig = @"
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    monitor: 'adwise-ai-monitor'
    environment: 'development'

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

rule_files: []

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 5s
    metrics_path: /metrics

  - job_name: 'adwise-api'
    static_configs:
      - targets: ['host.docker.internal:8000']
    scrape_interval: 10s
    metrics_path: /metrics
    scrape_timeout: 5s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
    scrape_interval: 30s
    metrics_path: /metrics

  - job_name: 'mongodb'
    static_configs:
      - targets: ['mongodb:27017']
    scrape_interval: 30s
    metrics_path: /metrics

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 30s
    metrics_path: /metrics

  - job_name: 'rabbitmq'
    static_configs:
      - targets: ['rabbitmq:15672']
    scrape_interval: 30s
    metrics_path: /api/metrics

  - job_name: 'minio'
    static_configs:
      - targets: ['minio:9000']
    scrape_interval: 30s
    metrics_path: /minio/v2/metrics/cluster

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['host.docker.internal:9100']
    scrape_interval: 30s
    metrics_path: /metrics

  - job_name: 'docker'
    static_configs:
      - targets: ['host.docker.internal:9323']
    scrape_interval: 30s
    metrics_path: /metrics
"@

try {
    # Create temporary container to initialize Prometheus config
    docker run --rm -v adwise_prometheus_config_dev:/config alpine sh -c "echo '$prometheusConfig' > /config/prometheus.yml"
    Write-Success "Prometheus configuration initialized"
} catch {
    Write-Error "Failed to initialize Prometheus configuration: $_"
}

# Create Grafana datasources configuration
Write-Status "Initializing Grafana datasources configuration..."
$grafanaDatasources = @"
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
    jsonData:
      timeInterval: "5s"
      queryTimeout: "60s"
      httpMethod: "POST"
    secureJsonData: {}

  - name: PostgreSQL
    type: postgres
    access: proxy
    url: postgres:5432
    database: adwise_campaigns
    user: adwise_user
    secureJsonData:
      password: adwise_dev_password_2024
    jsonData:
      sslmode: "disable"
      maxOpenConns: 0
      maxIdleConns: 2
      connMaxLifetime: 14400
      postgresVersion: 1500
      timescaledb: false

  - name: MongoDB
    type: grafana-mongodb-datasource
    access: proxy
    url: mongodb://admin:admin_password_2024@mongodb:27017/adwise_campaigns
    jsonData:
      authSource: "admin"
      ssl: false
    editable: true
"@

try {
    # Create temporary container to initialize Grafana config
    docker run --rm -v adwise_grafana_config_dev:/config alpine sh -c "mkdir -p /config/datasources && echo '$grafanaDatasources' > /config/datasources/prometheus.yml"
    Write-Success "Grafana datasources configuration initialized"
} catch {
    Write-Error "Failed to initialize Grafana configuration: $_"
}

# Create Grafana dashboards configuration
Write-Status "Initializing Grafana dashboards configuration..."
$grafanaDashboards = @"
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
"@

try {
    docker run --rm -v adwise_grafana_config_dev:/config alpine sh -c "mkdir -p /config/dashboards && echo '$grafanaDashboards' > /config/dashboards/dashboard.yml"
    Write-Success "Grafana dashboards configuration initialized"
} catch {
    Write-Error "Failed to initialize Grafana dashboards configuration: $_"
}

# Create a comprehensive AdWise AI dashboard
Write-Status "Creating AdWise AI monitoring dashboard..."
$adwiseDashboard = @"
{
  "dashboard": {
    "id": null,
    "title": "AdWise AI - System Overview",
    "tags": ["adwise", "monitoring"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "Requests/sec"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      },
      {
        "id": 3,
        "title": "Database Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "pg_stat_database_numbackends",
            "legendFormat": "PostgreSQL Connections"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
      },
      {
        "id": 4,
        "title": "Redis Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "redis_memory_used_bytes",
            "legendFormat": "Memory Used"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
      }
    ],
    "time": {"from": "now-1h", "to": "now"},
    "refresh": "5s"
  }
}
"@

try {
    docker run --rm -v adwise_grafana_config_dev:/config alpine sh -c "echo '$adwiseDashboard' > /config/dashboards/adwise-overview.json"
    Write-Success "AdWise AI dashboard created"
} catch {
    Write-Error "Failed to create AdWise AI dashboard: $_"
}

Write-Status "Configuration Summary:" $Blue
Write-Info "✓ Prometheus configuration: /etc/prometheus/prometheus.yml"
Write-Info "✓ Grafana datasources: /etc/grafana/provisioning/datasources/"
Write-Info "✓ Grafana dashboards: /etc/grafana/provisioning/dashboards/"
Write-Info "✓ AdWise AI monitoring dashboard included"

Write-Success "Docker configuration initialization completed!"
Write-Info "You can now start the services with: docker-compose -f docker-compose.dev.yml up -d"
