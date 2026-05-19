from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
import enum

# Import Base and enums in a way that works when running as script or package
try:
    from database import Base
    from models import ProductionType, AnimalStatus
except Exception:
    from app.database import Base
    from app.models import ProductionType, AnimalStatus

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

class FeedingRecordDB(Base):
    __tablename__ = "feeding_records"
    id = Column(Integer, primary_key=True, index=True)
    animal_id = Column(String)
    feed_type = Column(String)
    quantity_kg = Column(Float)
    frequency_daily = Column(Integer)
    supplier = Column(String)
    unit_cost = Column(Float)
    timestamp = Column(DateTime)

class HealthRecordDB(Base):
    __tablename__ = "health_records"
    id = Column(Integer, primary_key=True, index=True)
    animal_id = Column(String)
    vaccines = Column(String)
    medications = Column(String)
    diagnosis = Column(String)
    treatment = Column(String)
    deworming_date = Column(DateTime)
    vet_observations = Column(String)

class ProductionDB(Base):
    __tablename__ = "productions"
    id = Column(Integer, primary_key=True, index=True)
    animal_id = Column(String)
    product_type = Column(String)
    amount = Column(Float)
    unit = Column(String)
    date = Column(DateTime)

class AnimalDefaultProductionDB(Base):
    __tablename__ = "animal_default_production"
    id = Column(Integer, primary_key=True, index=True)
    animal_id = Column(String, unique=True)
    production_type = Column(String)
    production_unit = Column(String)

class EnvironmentRecordDB(Base):
    __tablename__ = "environment_records"
    id = Column(Integer, primary_key=True, index=True)
    temperature = Column(Float)
    humidity = Column(Float)
    water_quality_ph = Column(Float)
    ventilation_status = Column(String)
    rainfall_mm = Column(Float)
    observation = Column(String)
    timestamp = Column(DateTime)

class SmartAlertDB(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String)
    message = Column(String)
    severity = Column(String)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime)

class EvidenceDB(Base):
    __tablename__ = "evidences"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    file_url = Column(String)
    description = Column(String)
    linked_entity_id = Column(String)
    timestamp = Column(DateTime)