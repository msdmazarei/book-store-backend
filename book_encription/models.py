from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from db_session import Base, PrimaryModel



class DeviceCode(Base,PrimaryModel):
    __tablename__ = 'device_codes'
    code = Column(String,nullable=False,unique=True)
    user_id = Column(UUID,ForeignKey('users.id'),nullable=False)