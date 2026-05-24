from sqlalchemy import Column,Integer,String,Boolean,DateTime,ForeignKey,Text,Enum
from sqlalchemy.orm import relationship 
from sqlalchemy.sql import func
from app.database import Base
import enum 
class TaskStatus(str,enum.Enum):
    PENDDING="pending"
    IN_PROGRESS="in_progress"
    COMPLETED="completed"
    CANCELLED="cancelled"
class TaskPriority(str,enum.Enum):
    LOW="low"
    MEDIUM="medium"
    HIGH="high"
    URGENT="urgent"
class User(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True,index=True)
    email=Column(String,unique=True,index=True,nullable=False)
    username=Column(String,unique=True,index=True,nullable=False)
    hashed_password=Column(String,nullable=False)
    is_active=Column(Boolean,default=True)
    is_admin=Column(Boolean,default=False)
    created_at=Column(DateTime(timezone=True),server_default=func.now())
    updated_at=Column(DateTime(timezone=True),onupdate=func.now())
    tasks=relationship("Task",back_populates="owner")

class Task(Base):
    __tablename__="tasks"
    id=Column(Integer,primary_key=True,index=True)
    title=Column(String,nullable=False)
    description=Column(Text)
    status=Column(Enum(TaskStatus),default=TaskStatus.PENDDING)
    priority=Column(Enum(TaskPriority),default=TaskPriority.MEDIUM)
    due_date=Column(DateTime(timezone=True))
    owner_id=Column(Integer,ForeignKey("users.id"))
    created_at=Column(DateTime(timezone=True),server_default=func.now())
    updated_at=Column(DateTime(timezone=True),onupdate=func.now())
    owner=relationship("User",back_populates="tasks")
