from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field

# --- ENUMS PARA ESTANDARIZACIÓN ---
class ProductionType(str, Enum):
    AVICOLA = "avícola"
    GANADERA = "ganadera"
    PORCINA = "porcina"
    PISCICOLA = "piscícola"

class AnimalStatus(str, Enum):
    CRIA = "cría"
    LEVANTE = "levante"
    PRODUCCION = "producción"

# --- MÓDULO 1: INFORMACIÓN GENERAL ---
class ProductiveCycleBase(BaseModel):
    farm_name: str
    location: str
    manager: str
    production_type: ProductionType
    batch_code: str
    start_date: datetime
    end_date: Optional[datetime]
    initial_animal_count: int

class ProductiveCycleCreate(ProductiveCycleBase):
    pass

class ProductiveCycle(ProductiveCycleBase):
    id: int
    class Config:
        from_attributes = True

# --- MÓDULO 2: REGISTRO DE ANIMALES ---
class AnimalBase(BaseModel):
    animal_id: str  # ID o QR
    breed: str
    sex: str
    age_months: int
    initial_weight: float
    current_weight: float
    status: AnimalStatus
    history: List[str] = []
    cycle_id: int

class AnimalCreate(AnimalBase):
    pass

class Animal(AnimalBase):
    id: int
    class Config:
        from_attributes = True

# --- MÓDULO 3: ALIMENTACIÓN Y NUTRICIÓN ---
class FeedingRecord(BaseModel):
    animal_id: Optional[str]  # Puede ser por lote o individual
    feed_type: str
    quantity_kg: float
    frequency_daily: int
    supplier: str
    unit_cost: float
    supplements: Optional[List[str]]
    timestamp: datetime = Field(default_factory=datetime.now)

# --- MÓDULO 4: SALUD ANIMAL ---
class HealthRecord(BaseModel):
    animal_id: str
    vaccines: List[str]
    medications: List[str]
    symptoms: Optional[str]
    diagnosis: Optional[str]
    treatment: Optional[str]
    deworming_date: datetime
    vet_observations: str

# --- MÓDULO 5: PRODUCCIÓN (Ejemplo Ganadería) ---
class CattleProduction(BaseModel):
    animal_id: str
    milk_liters: Optional[float]
    weight_gain: float
    births: int = 0
    weaning_date: Optional[datetime]

# --- MÓDULO 6: AMBIENTE ---
class EnvironmentRecord(BaseModel):
    temperature: float
    humidity: float
    water_quality_ph: float
    ventilation_status: str
    rainfall_mm: float
    observation: str

# --- MÓDULO 7: COSTOS Y GASTOS ---
class Expense(BaseModel):
    category: str  # Alimento, Medicina, Mano de obra, etc.
    amount: float
    description: str
    date: datetime

# --- MÓDULO 8: ALERTAS INTELIGENTES ---
class SmartAlert(BaseModel):
    alert_type: str  # "Salud", "Producción", "Bajo Crecimiento"
    message: str
    severity: str  # "Alta", "Media", "Baja"
    is_resolved: bool = False
    created_at: datetime = Field(default_factory=datetime.now)

# --- MÓDULO 9: REPORTES (Esquema de salida) ---
class ReportSummary(BaseModel):
    total_productivity: float
    total_costs: float
    net_profit: float
    mortality_rate: float

# --- MÓDULO 10: EVIDENCIAS ---
class Evidence(BaseModel):
    type: str  # "foto", "video", "nota_voz", "documento"
    file_url: str
    description: Optional[str]
    linked_entity_id: str  # ID del animal o lote relacionado
    timestamp: datetime = Field(default_factory=datetime.now)