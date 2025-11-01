"""
Database initialization script - Creates admin user
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select

from app.core.logging import get_logger, setup_logging
from app.core.security import get_password_hash
from app.db.database import engine
from app.models.user import User

setup_logging()
logger = get_logger(__name__)


def init_database():
    """Create admin user if it doesn't exist"""
    with Session(engine) as session:
        # Check if admin user already exists
        statement = select(User).where(User.username == "admin")
        admin_user = session.exec(statement).first()

        if admin_user:
            logger.info("Admin user already exists")
            return

        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("pass"),
            is_active=True,
            is_superuser=True,
        )

        session.add(admin_user)
        session.commit()
        logger.info("Admin user created successfully - username: admin, password: pass")


if __name__ == "__main__":
    init_database()
