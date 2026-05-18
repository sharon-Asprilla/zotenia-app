from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .database import engine, get_db, Base
from . import db_models, models

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Zotenia Management System")

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de Zotenia"}

# --- ENDPOINTS MÓDULO 1: CICLOS ---
@app.post("/cycles/", response_model=models.ProductiveCycle)
def create_cycle(cycle: models.ProductiveCycleCreate, db: Session = Depends(get_db)):
    db_cycle = db_models.ProductiveCycleDB(**cycle.model_dump())
    db.add(db_cycle)
    db.commit()
    db.refresh(db_cycle)
    return db_cycle

@app.get("/cycles/", response_model=List[models.ProductiveCycle])
def list_cycles(db: Session = Depends(get_db)):
    return db.query(db_models.ProductiveCycleDB).all()

# --- ENDPOINTS MÓDULO 2: ANIMALES ---
@app.post("/animals/", response_model=models.Animal)
def register_animal(animal: models.AnimalCreate, db: Session = Depends(get_db)):
    # Verificar si el ciclo existe
    cycle = db.query(db_models.ProductiveCycleDB).filter(db_models.ProductiveCycleDB.id == animal.cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="Ciclo productivo no encontrado")
    
    db_animal = db_models.AnimalDB(**animal.model_dump())
    db.add(db_animal)
    db.commit()
    db.refresh(db_animal)
    return db_animal

@app.get("/animals/{animal_id}", response_model=models.Animal)
def get_animal(animal_id: str, db: Session = Depends(get_db)):
    animal = db.query(db_models.AnimalDB).filter(db_models.AnimalDB.animal_id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal no encontrado")
    return animal