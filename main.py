#Hosting	AWS ECS / Google Cloud Run
#Database	PostgreSQL (RDS / Cloud SQL)
#Cache	Redis (ElastiCache / Memorystore)
#CI/CD	GitHub Actions / GitLab CI
#Monitoring	Grafana + Prometheus
#docker stop $(docker ps -aq) 2>/dev/null; docker rm -f $(docker ps -aq) 2>/dev/null; docker rmi -f $(docker images -aq) 2>/dev/null; docker network prune -f 2>/dev/null; docker system prune -af 2>/dev/null

# TODO1 User Registration & Login [0] JWT/OAuth2
# TODO2 Password Hashing & Security [0] bcrypt/Argon2
# TODO3 OAuth Provider Integration [0] Google/GitHub/Facebook
# TODO4 Role-Based Access Control [0] RBAC implementation
# TODO5 Email Verification [0] SMTP/SendGrid

# TODO6 Token Management [0] Refresh tokens
# TODO7 Rate Limiting [0] Redis-based
# TODO8 API Documentation [0] Swagger/OpenAPI
# TODO9 Audit Logging [0] Security events

# TODO10 Multi-Factor Auth [0] TOTP/SMS
# TODO11 Session Management [0] Redis sessions
# TODO12 Social Auth UI [0] Provider buttons

# TODOEXTRA WebAuthn Support [0] Biometric auth
# TODOEXTRA Device Authorization Flow [0] TV/CLI devices
# TODOEXTRA Token Introspection [0] RFC 7662

# TODO13 CI/CD Pipeline [0] GitHub Actions
# TODO14 Monitoring [0] Prometheus/Grafana
# TODO15 Internationalization [0] i18n

# global_TODO Deployment [0] Docker+K8s
# global_TODO Security Audit [0] OWASP checklist

from fastapi import FastAPI
from contextlib import asynccontextmanager
from logging.config import dictConfig
import uvicorn
import logging

from src.core.config.config import settings
from src.core.dependencies.db_helper import db_helper
from src.core.config.logger import LOG_CONFIG

from src.api.v1.endpoints.healthcheck import router as health_router
from src.api.v1.endpoints.main_router import router as main_router
from src.api.v1.auth.authentication import router as auth_router



app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    dictConfig(LOG_CONFIG)
    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting app...")
    
    yield  # FastAPI handles requests here

    logger.info("🛑 Shutting down...")
    try:
        await db_helper.dispose()
        logger.info("✅ Connection pool closed cleanly")
    except Exception as e:
        logger.warning(f"⚠️ Error closing connection pool: {e}")


app = FastAPI(lifespan=lifespan)


app.include_router(health_router)
app.include_router(main_router)
app.include_router(auth_router)


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
        log_config=LOG_CONFIG,
        access_log=False,
        )