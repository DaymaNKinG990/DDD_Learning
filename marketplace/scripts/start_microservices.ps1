# Marketplace Microservices Startup Script for Windows

Write-Host "🚀 Starting Marketplace Microservices..." -ForegroundColor Green

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Docker is not running. Please start Docker first." -ForegroundColor Red
    exit 1
}

# Check if docker-compose is available
try {
    docker-compose --version | Out-Null
} catch {
    Write-Host "❌ docker-compose is not installed. Please install it first." -ForegroundColor Red
    exit 1
}

# Function to check if port is available
function Test-Port {
    param([int]$Port)
    
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    } catch {
        return $false
    }
}

# Check if required ports are available
Write-Host "🔍 Checking port availability..." -ForegroundColor Yellow

$ports = @(8000, 8001, 8002, 8003, 8004, 8005, 8006, 5432, 6379)
foreach ($port in $ports) {
    if (Test-Port -Port $port) {
        Write-Host "❌ Port $port is already in use. Please free it up first." -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ All ports are available" -ForegroundColor Green

# Start infrastructure first
Write-Host "🏗️ Starting infrastructure services..." -ForegroundColor Yellow
docker-compose -f docker-compose.microservices.yml up -d postgres redis

# Wait for infrastructure to be ready
Write-Host "⏳ Waiting for infrastructure to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if PostgreSQL is ready
Write-Host "🔍 Checking PostgreSQL..." -ForegroundColor Yellow
do {
    try {
        docker-compose -f docker-compose.microservices.yml exec -T postgres pg_isready -U marketplace_user -d marketplace | Out-Null
        break
    } catch {
        Write-Host "⏳ Waiting for PostgreSQL..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
} while ($true)

Write-Host "✅ PostgreSQL is ready" -ForegroundColor Green

# Check if Redis is ready
Write-Host "🔍 Checking Redis..." -ForegroundColor Yellow
do {
    try {
        docker-compose -f docker-compose.microservices.yml exec -T redis redis-cli ping | Out-Null
        break
    } catch {
        Write-Host "⏳ Waiting for Redis..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
} while ($true)

Write-Host "✅ Redis is ready" -ForegroundColor Green

# Start all microservices
Write-Host "🚀 Starting all microservices..." -ForegroundColor Yellow
docker-compose -f docker-compose.microservices.yml up -d

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Check service health
Write-Host "🔍 Checking service health..." -ForegroundColor Yellow

$services = @("gateway", "catalog", "orders", "users", "auth", "reviews", "notifications")
$ports = @(8000, 8001, 8002, 8003, 8004, 8005, 8006)

for ($i = 0; $i -lt $services.Length; $i++) {
    $service = $services[$i]
    $port = $ports[$i]
    
    Write-Host "🔍 Checking $service service (port $port)..." -ForegroundColor Yellow
    
    # Wait for service to be ready
    for ($attempt = 1; $attempt -le 30; $attempt++) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$port/health" -TimeoutSec 5 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ $service is healthy" -ForegroundColor Green
                break
            }
        } catch {
            if ($attempt -eq 30) {
                Write-Host "❌ $service failed to start properly" -ForegroundColor Red
                Write-Host "📋 Logs for $service" -ForegroundColor Yellow
                docker-compose -f docker-compose.microservices.yml logs --tail=20 $service
            } else {
                Write-Host "⏳ Waiting for $service... (attempt $attempt of 30)" -ForegroundColor Yellow
                Start-Sleep -Seconds 2
            }
        }
    }
}

Write-Host ""
Write-Host "🎉 Marketplace Microservices are ready!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Service URLs:" -ForegroundColor Cyan
Write-Host "  🌐 API Gateway:     http://localhost:8000" -ForegroundColor White
Write-Host "  📚 API Docs:        http://localhost:8000/docs" -ForegroundColor White
Write-Host "  📊 Health Check:    http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Individual Services:" -ForegroundColor Cyan
Write-Host "  📦 Catalog:         http://localhost:8001" -ForegroundColor White
Write-Host "  🛒 Orders:          http://localhost:8002" -ForegroundColor White
Write-Host "  👥 Users:           http://localhost:8003" -ForegroundColor White
Write-Host "  🔐 Auth:            http://localhost:8004" -ForegroundColor White
Write-Host "  ⭐ Reviews:         http://localhost:8005" -ForegroundColor White
Write-Host "  📢 Notifications:   http://localhost:8006" -ForegroundColor White
Write-Host ""
Write-Host "🛠️ Management Tools:" -ForegroundColor Cyan
Write-Host "  🗄️ pgAdmin:         http://localhost:5050 (admin@marketplace.com / admin_password)" -ForegroundColor White
Write-Host "  🔴 Redis Commander: http://localhost:8081" -ForegroundColor White
Write-Host ""
Write-Host "📋 Useful Commands:" -ForegroundColor Cyan
Write-Host "  View logs:          docker-compose -f docker-compose.microservices.yml logs -f" -ForegroundColor White
Write-Host "  Stop services:      docker-compose -f docker-compose.microservices.yml down" -ForegroundColor White
Write-Host "  Restart service:    docker-compose -f docker-compose.microservices.yml restart <service_name>" -ForegroundColor White
Write-Host "" 