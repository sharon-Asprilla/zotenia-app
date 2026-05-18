from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from .database import Base
import enum
from .models import ProductionType, AnimalStatus

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)  # En producción, usar hashing

class ProductiveCycleDB(Base):
    __tablename__ = "productive_cycles"

    id = Column(Integer, primary_key=True, index=True)
    farm_name = Column(String)
    location = Column(String)
    manager = Column(String)
    production_type = Column(SQLEnum(ProductionType))
    batch_code = Column(String, unique=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    initial_animal_count = Column(Integer)

    animals = relationship("AnimalDB", back_populates="cycle")

class AnimalDB(Base):
    __tablename__ = "animals"

    id = Column(Integer, primary_key=True, index=True)
    animal_id = Column(String, unique=True, index=True)
    breed = Column(String)
    sex = Column(String)
    age_months = Column(Integer)
    initial_weight = Column(Float)
    current_weight = Column(Float)
    status = Column(SQLEnum(AnimalStatus))
    
    cycle_id = Column(Integer, ForeignKey("productive_cycles.id"))
    cycle = relationship("ProductiveCycleDB", back_populates="animals")

class ExpenseDB(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    amount = Column(Float)
    description = Column(String)
    date = Column(DateTime)