from ..database import Base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP, ARRAY


class Users(Base):
    __tablename__ = "users"

    # Metadata
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()")
    )
    last_updated = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()")
    )
    status = Column(String, nullable=False, server_default="active")
    starred = Column(ARRAY(Integer), nullable=False, server_default="{}")

    # Personal Details

    user_id = Column(String, nullable=False, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)

    # Role Scope
    scopes = Column(ARRAY(String), nullable=False, server_default="{user}")
