#!/bin/bash

# Marketplace Microservices Startup Script

echo "🚀 Starting Marketplace Microservices..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install it first."
    exit 1
fi

# Function to check if port is available
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "❌ Port $1 is already in use. Please free it up first."
        exit 1
    fi
}

# Check if required ports are available
echo "🔍 Checking port availability..."
check_port 8000  # Gateway
check_port 8001  # Catalog
check_port 8002  # Orders
check_port 8003  # Users
check_port 8004  # Auth
check_port 8005  # Reviews
check_port 8006  # Notifications
check_port 5432  # PostgreSQL
check_port 6379  # Redis

echo "✅ All ports are available"

# Start infrastructure first
echo "🏗️ Starting infrastructure services..."
docker-compose -f docker-compose.microservices.yml up -d postgres redis

# Wait for infrastructure to be ready
echo "⏳ Waiting for infrastructure to be ready..."
sleep 10

# Check if PostgreSQL is ready
echo "🔍 Checking PostgreSQL..."
until docker-compose -f docker-compose.microservices.yml exec -T postgres pg_isready -U marketplace_user -d marketplace; do
    echo "⏳ Waiting for PostgreSQL..."
    sleep 2
done

echo "✅ PostgreSQL is ready"

# Check if Redis is ready
echo "🔍 Checking Redis..."
until docker-compose -f docker-compose.microservices.yml exec -T redis redis-cli ping; do
    echo "⏳ Waiting for Redis..."
    sleep 2
done

echo "✅ Redis is ready"

# Start all microservices
echo "🚀 Starting all microservices..."
docker-compose -f docker-compose.microservices.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 15

# Check service health
echo "🔍 Checking service health..."

services=("gateway" "catalog" "orders" "users" "auth" "reviews" "notifications")
ports=(8000 8001 8002 8003 8004 8005 8006)

for i in "${!services[@]}"; do
    service=${services[$i]}
    port=${ports[$i]}
    
    echo "🔍 Checking $service service (port $port)..."
    
    # Wait for service to be ready
    for attempt in {1..30}; do
        if curl -f http://localhost:$port/health > /dev/null 2>&1; then
            echo "✅ $service is healthy"
            break
        fi
        
        if [ $attempt -eq 30 ]; then
            echo "❌ $service failed to start properly"
            echo "📋 Logs for $service:"
            docker-compose -f docker-compose.microservices.yml logs --tail=20 $service
        fi
        
        echo "⏳ Waiting for $service... (attempt $attempt/30)"
        sleep 2
    done
done

echo ""
echo "🎉 Marketplace Microservices are ready!"
echo ""
echo "📋 Service URLs:"
echo "  🌐 API Gateway:     http://localhost:8000"
echo "  📚 API Docs:        http://localhost:8000/docs"
echo "  📊 Health Check:    http://localhost:8000/health"
echo ""
echo "🔧 Individual Services:"
echo "  📦 Catalog:         http://localhost:8001"
echo "  🛒 Orders:          http://localhost:8002"
echo "  👥 Users:           http://localhost:8003"
echo "  🔐 Auth:            http://localhost:8004"
echo "  ⭐ Reviews:         http://localhost:8005"
echo "  📢 Notifications:   http://localhost:8006"
echo ""
echo "🛠️ Management Tools:"
echo "  🗄️ pgAdmin:         http://localhost:5050 (admin@marketplace.com / admin_password)"
echo "  🔴 Redis Commander: http://localhost:8081"
echo ""
echo "📋 Useful Commands:"
echo "  View logs:          docker-compose -f docker-compose.microservices.yml logs -f"
echo "  Stop services:      docker-compose -f docker-compose.microservices.yml down"
echo "  Restart service:    docker-compose -f docker-compose.microservices.yml restart <service_name>"
echo "" 