from ..database import Base
from sqlalchemy import Column, String
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP


class BlacklistTokens(Base):
    __tablename__ = "blacklist_tokens"
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()")
    )
    token = Column(String, nullable=False, primary_key=True)
    expiration = Column(TIMESTAMP(timezone=True), nullable=False)
