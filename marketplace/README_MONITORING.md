# Marketplace Monitoring & CI/CD Documentation

## Overview

This document describes the monitoring, alerting, and CI/CD setup for the Marketplace microservices architecture.

## Monitoring Stack

### Prometheus
- **Purpose**: Metrics collection and storage
- **Port**: 9090
- **URL**: http://localhost:9090
- **Configuration**: `monitoring/prometheus/prometheus.yml`

### Grafana
- **Purpose**: Metrics visualization and dashboards
- **Port**: 3000
- **URL**: http://localhost:3000
- **Default Credentials**: admin/admin_password
- **Dashboards**: `monitoring/grafana/dashboards/`

### Alertmanager
- **Purpose**: Alert routing and notification
- **Port**: 9093
- **URL**: http://localhost:9093
- **Configuration**: `monitoring/alertmanager/alertmanager.yml`

## Metrics Collection

### Service Metrics
Each microservice exposes Prometheus metrics at `/metrics` endpoint:

- **HTTP Request Metrics**: Total requests, duration, status codes
- **Business Metrics**: Orders created, products viewed, user registrations
- **System Metrics**: Database connections, Redis usage, cache hit ratio
- **Error Metrics**: Error counts by service and type
- **Health Metrics**: Service health status

### Database Metrics
- PostgreSQL metrics via postgres_exporter
- Connection pool statistics
- Query performance metrics

### Infrastructure Metrics
- Redis memory usage and connections
- System resource usage (CPU, memory, disk)

## Alerts

### Critical Alerts
- Service down for > 1 minute
- Error rate > 5%
- Health check failures

### Warning Alerts
- High response time (> 2 seconds 95th percentile)
- High database connections (> 100)
- High Redis memory usage (> 80%)
- High system resource usage

### Rate Limiting Alerts
- Rate limit exceeded events

## CI/CD Pipeline

### GitHub Actions Workflow
Location: `.github/workflows/ci-cd.yml`

### Stages

#### 1. Test Stage
- **Triggers**: Push to main/develop, Pull Requests
- **Services**: PostgreSQL, Redis
- **Actions**:
  - Install dependencies with uv
  - Run linting (ruff)
  - Run type checking (mypy)
  - Run tests with coverage
  - Upload coverage to Codecov

#### 2. Build Stage
- **Triggers**: After successful test
- **Actions**:
  - Build Docker images for all microservices
  - Test service builds
  - Security scanning (Bandit, Safety)

#### 3. Deploy Stage
- **Staging**: Deploy to staging on develop branch
- **Production**: Deploy to production on main branch

### Security Scanning
- **Bandit**: Python security linting
- **Safety**: Dependency vulnerability scanning
- **Docker**: Image security scanning

## Database Migrations

### Automatic Migrations
- Migrations run automatically on service startup
- Script: `scripts/migrate_db.py`
- Retry logic with exponential backoff
- Health checks ensure database readiness

### Manual Migration Commands
```bash
# Run migrations
uv run python scripts/migrate_db.py --action migrate

# Create new migration
uv run python scripts/migrate_db.py --action create

# Check migration status
uv run python scripts/migrate_db.py --action check
```

## Environment Configuration

### Environment Variables
See `env.example` for all available configuration options:

- **Database**: Connection settings
- **Redis**: Cache configuration
- **Security**: JWT, CORS, rate limiting
- **Monitoring**: Prometheus, Grafana, Sentry
- **External Services**: Payment, shipping APIs

### Docker Compose
All services use environment variables from docker-compose:
```yaml
environment:
  DATABASE_HOST: postgres
  DATABASE_PORT: 5432
  # ... other variables
```

## Monitoring Dashboards

### Marketplace Overview Dashboard
- Service health status
- Request rates and response times
- Error rates and system metrics
- Database and Redis usage

### Service-Specific Dashboards
- Individual service metrics
- Business KPIs
- Performance indicators

## Alerting Rules

### Service Health
```yaml
- alert: ServiceDown
  expr: up == 0
  for: 1m
  labels:
    severity: critical
```

### Performance
```yaml
- alert: HighResponseTime
  expr: http_request_duration_seconds{quantile="0.95"} > 2
  for: 5m
  labels:
    severity: warning
```

### Error Rates
```yaml
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
  for: 2m
  labels:
    severity: critical
```

## Getting Started

### 1. Start Monitoring Stack
```bash
# Start all services including monitoring
docker-compose -f docker-compose.microservices.yml up -d

# Access monitoring tools
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin_password)
# Alertmanager: http://localhost:9093
```

### 2. Import Dashboards
1. Open Grafana at http://localhost:3000
2. Add Prometheus as data source (http://prometheus:9090)
3. Import dashboard from `monitoring/grafana/dashboards/marketplace-overview.json`

### 3. Configure Alerts
1. Update `monitoring/prometheus/alerts.yml` with your alert rules
2. Configure Alertmanager for notifications (email, Slack, etc.)
3. Restart Prometheus to apply changes

### 4. Set Up CI/CD
1. Fork the repository
2. Configure GitHub Actions secrets
3. Set up deployment environments
4. Configure branch protection rules

## Troubleshooting

### Common Issues

#### Prometheus Can't Scrape Services
- Check service health endpoints
- Verify network connectivity
- Check firewall settings

#### Grafana Can't Connect to Prometheus
- Verify Prometheus is running
- Check data source configuration
- Ensure correct URL and port

#### Alerts Not Firing
- Check alert rules syntax
- Verify metric names and labels
- Check Alertmanager configuration

#### Database Migration Failures
- Check database connectivity
- Verify credentials
- Check migration script permissions

### Logs
```bash
# View service logs
docker-compose -f docker-compose.microservices.yml logs [service-name]

# View monitoring logs
docker-compose -f docker-compose.microservices.yml logs prometheus
docker-compose -f docker-compose.microservices.yml logs grafana
docker-compose -f docker-compose.microservices.yml logs alertmanager
```

## Best Practices

### Monitoring
- Use meaningful metric names and labels
- Set appropriate alert thresholds
- Monitor business metrics alongside technical metrics
- Regular dashboard reviews and updates

### CI/CD
- Keep dependencies updated
- Run security scans regularly
- Use semantic versioning
- Implement proper rollback procedures

### Database
- Test migrations in staging first
- Backup before major migrations
- Monitor migration performance
- Use connection pooling

### Security
- Rotate secrets regularly
- Use least privilege principle
- Monitor for security events
- Keep monitoring tools updated 