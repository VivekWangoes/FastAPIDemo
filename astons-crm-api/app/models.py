from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
Base = declarative_base()


class Member(Base):
    __tablename__ = "member"

    id = Column(Integer, primary_key=True, index=True)
    odoo_member_id = Column(String)
    fastapi_member_id = Column(String)

    def dict(self):
        return {
            "odoo": self.odoo_member_id,
            "fastapi" : self.fastapi_member_id
        }

class UserRegister(Base):
    __tablename__="register_member"

    id = Column(Integer, primary_key=True, index=True)
    odoo_member_id = Column(String)

    def dict(self):
        return {
            "odoo": self.odoo_member_id,
        }