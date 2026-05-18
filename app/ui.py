import streamlit as st
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# --- CONFIGURACIÓN DE BASE DE DATOS LOCAL ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./zotenia_local.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- DEFINICIÓN DE TABLAS (CAMPOS) ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)

class ProductiveCycle(Base):
    __tablename__ = "productive_cycles"
    id = Column(Integer, primary_key=True, index=True)
    farm_name = Column(String)
    location = Column(String)
    manager = Column(String)
    production_type = Column(String)
    batch_code = Column(String, unique=True)
    start_date = Column(DateTime)
    initial_animal_count = Column(Integer)
    animals = relationship("Animal", back_populates="cycle")

class Animal(Base):
    __tablename__ = "animals"
    id = Column(Integer, primary_key=True, index=True)
    animal_id = Column(String, unique=True)
    breed = Column(String)
    sex = Column(String)
    age_months = Column(Integer)
    initial_weight = Column(Float)
    current_weight = Column(Float)
    status = Column(String)
    cycle_id = Column(Integer, ForeignKey("productive_cycles.id"))
    cycle = relationship("ProductiveCycle", back_populates="animals")

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    amount = Column(Float)
    description = Column(String)
    date = Column(DateTime)

# Crear la base de datos y las tablas al iniciar
Base.metadata.create_all(bind=engine)

# --- FUNCIONES DE UTILIDAD ---
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass # La sesión se cierra manualmente en el flujo

# --- LÓGICA DE SESIÓN Y LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def login_user(username, password):
    db = SessionLocal()
    user = db.query(User).filter(
        User.username == username, 
        User.password == password
    ).first()
    db.close()
    return user

def register_user(username, password):
    db = SessionLocal()
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        db.close()
        return False, "El usuario ya existe"
    new_user = User(username=username, password=password)
    db.add(new_user)
    db.commit()
    db.close()
    return True, "Usuario creado con éxito"

def create_default_user():
    db = SessionLocal()
    if not db.query(User).first():
        default_user = User(username="admin", password="123")
        db.add(default_user)
        db.commit()
    db.close()

create_default_user()

if not st.session_state['logged_in']:
    st.title(" Acceso a Zotenia")
    with st.form("login_form"):
        user_input = st.text_input("Usuario")
        pass_input = st.text_input("Contraseña", type="password")
        col1, col2 = st.columns(2)
        if col1.form_submit_button("Entrar"):
            user = login_user(user_input, pass_input)
            if user:
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas. Si no tienes cuenta, regístrate abajo.")
        if col2.form_submit_button("Registrar usuario"):
            # Mostrar el formulario de registro debajo
            st.session_state['show_register'] = True

    # Formulario de registro (visible si el usuario pidió registrarse o si no existe cuenta)
    if st.session_state.get('show_register', False):
        st.subheader("Registro de Usuario")
        with st.form("register_form"):
            reg_user = st.text_input("Nombre de usuario", key="reg_user")
            reg_pass = st.text_input("Contraseña", type="password", key="reg_pass")
            reg_pass2 = st.text_input("Confirmar contraseña", type="password", key="reg_pass2")
            if st.form_submit_button("Crear cuenta"):
                if not reg_user or not reg_pass:
                    st.error("Completa usuario y contraseña")
                elif reg_pass != reg_pass2:
                    st.error("Las contraseñas no coinciden")
                else:
                    ok, msg = register_user(reg_user, reg_pass)
                    if ok:
                        st.success(msg)
                        st.session_state['show_register'] = False
                        # Iniciar sesión automáticamente tras registro
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = reg_user
                        st.rerun()
                    else:
                        st.error(msg)
else:
    # --- APLICACIÓN PRINCIPAL ---
    st.set_page_config(page_title="Zotenia - Gestión Agropecuaria", layout="wide")
    st.sidebar.title(f"🌱 Zotenia")
    menu = ["Dashboard", "Ciclos Productivos", "Registro Animal", "Costos"]
    choice = st.sidebar.selectbox("Módulos", menu)
    
    db = get_db()

    if choice == "Dashboard":
        st.title("📊 Resumen General")
        total_animals = db.query(Animal).count()
        total_cycles = db.query(ProductiveCycle).count()
        total_investment = db.query(Expense).with_entities(Expense.amount).all()
        total_investment = sum(x[0] for x in total_investment)

        col1, col2 = st.columns(2)
        col1.metric("Animales Registrados", total_animals)
        col2.metric("Inversión Total ($)", f"{total_investment:,.2f}")

    elif choice == "Ciclos Productivos":
        st.subheader("Nuevo Ciclo Productivo")
        with st.form("cycle_form"):
            farm = st.text_input("Nombre de la Finca")
            location = st.text_input("Ubicación")
            manager = st.text_input("Responsable")
            prod_type = st.selectbox("Tipo", ["avicola", "ganadera", "porcina", "piscícola,ganadera"])
            batch = st.text_input("Código de Lote")
            count = st.number_input("Número inicial de animales", min_value=1)
            
            if st.form_submit_button("Guardar Ciclo"):
                new_cycle = ProductiveCycle(
                    farm_name=farm, location=location, manager=manager,
                    production_type=prod_type, batch_code=batch,
                    start_date=datetime.now(), initial_animal_count=count
                )
                db.add(new_cycle)
                db.commit()
                st.success("Ciclo creado con éxito")

        st.subheader("Ciclos Existentes")
        cycles = db.query(ProductiveCycle).all()
        if cycles:
            st.dataframe([{
                "Finca": c.farm_name, 
                "Lote": c.batch_code, 
                "Tipo": c.production_type, 
                "Inicio": c.start_date.strftime("%Y-%m-%d")
            } for c in cycles], use_container_width=True)

    elif choice == "Registro Animal":
        st.subheader("Registro de Animales")
        cycles = db.query(ProductiveCycle).all()
        
        if not cycles:
            st.warning("Primero debes crear un Ciclo Productivo.")
        else:
            cycle_options = {c.batch_code: c.id for c in cycles}
            selected_cycle_code = st.selectbox("Seleccionar Lote/Ciclo", list(cycle_options.keys()))
            
            with st.form("animal_form"):
                a_id = st.text_input("ID o QR del Animal")
                breed = st.text_input("Raza")
                sex = st.selectbox("Sexo", ["Macho", "Hembra"])
                weight = st.number_input("Peso Inicial (kg)", min_value=0.0)
                age = st.number_input("Edad (meses)", min_value=0)
                status = st.selectbox("Estado", ["cría", "levante", "producción"])
                
                if st.form_submit_button("Registrar Animal"):
                    new_animal = Animal(
                        animal_id=a_id, breed=breed, sex=sex,
                        age_months=age, initial_weight=weight, current_weight=weight,
                        status=status, cycle_id=cycle_options[selected_cycle_code]
                    )
                    db.add(new_animal)
                    db.commit()
                    st.success(f"Animal {a_id} registrado correctamente")

        st.subheader("Lista de Animales")
        animals = db.query(Animal).all()
        if animals:
            st.dataframe([{
                "ID/QR": a.animal_id, "Raza": a.breed, "Peso": a.current_weight, "Estado": a.status
            } for a in animals], use_container_width=True)
        else:
            st.info("No hay animales registrados aún.")

    elif choice == "Costos":
        st.subheader("Registro de Gastos")
        with st.form("expense_form"):
            category = st.selectbox("Categoría", ["Alimento", "Medicamentos", "Mano de Obra", "Otros"])
            amount = st.number_input("Monto ($)", min_value=0.0)
            desc = st.text_area("Descripción")
            
            if st.form_submit_button("Guardar Gasto"):
                new_expense = Expense(
                    category=category, 
                    amount=amount, 
                    description=desc, 
                    date=datetime.now()
                )
                db.add(new_expense)
                db.commit()
                st.success("Gasto registrado")

        st.subheader("Historial de Gastos")
        expenses = db.query(Expense).all()
        if expenses:
            st.dataframe([{
                "Fecha": e.date.strftime("%Y-%m-%d"),
                "Categoría": e.category,
                "Monto": f"${e.amount:,.2f}",
                "Descripción": e.description
            } for e in expenses], use_container_width=True)

    db.close()
    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state['logged_in'] = False
        st.rerun()
