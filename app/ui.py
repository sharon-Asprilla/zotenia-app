import streamlit as st
from datetime import datetime
import os

# Importación robusta para compatibilidad con Streamlit
try:
    from database import engine, SessionLocal
    from db_models import (
        Base, UserDB, ProductiveCycleDB, AnimalDB, ExpenseDB,
        FeedingRecordDB, HealthRecordDB, ProductionDB,
        EnvironmentRecordDB, SmartAlertDB, EvidenceDB, AnimalDefaultProductionDB
    )
    from models import ProductionType, AnimalStatus
except ImportError:
    from app.database import engine, SessionLocal
    from app.db_models import (
        Base, UserDB, ProductiveCycleDB, AnimalDB, ExpenseDB,
        FeedingRecordDB, HealthRecordDB, ProductionDB,
        EnvironmentRecordDB, SmartAlertDB, EvidenceDB, AnimalDefaultProductionDB
    )
    from app.models import ProductionType, AnimalStatus

# Configuración de página debe ser lo primero
st.set_page_config(page_title="Zootecnia - Gestión Agropecuaria", layout="wide")

# --- ESTILOS PERSONALIZADOS (azul-verde / blanco) ---
def inject_styles():
    st.markdown(
        """
        <style>
        :root{ --bg-1: #e6fbf6; --bg-2: #c6efe7; --accent: #2fbf9a; --accent-dark: #1f8f77; --text: #022f2d; }
        html, body, .stApp, .main, .block-container, .reportview-container, .css-1lsmgbg.egzxvld2 {
            background: var(--bg-1) !important;
            color: var(--text) !important;
            background-image: none !important;
        }
        html[data-theme="dark"], body[data-theme="dark"], html[data-theme="dark"] .stApp, body[data-theme="dark"] .stApp {
            background: var(--bg-1) !important;
            color: var(--text) !important;
        }
        .block-container{ background: white; border-radius: 16px; padding: 1.8rem; box-shadow: 0 12px 28px rgba(2,47,45,0.08); border: 1px solid var(--accent) !important; }
        header, footer { background: transparent !important; }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #c6efe7 0%, #2fbf9a 45%, #022b2a 100%) !important;
            color: white !important;
            box-shadow: 6px 0 20px rgba(2,47,45,0.18);
            border-right: 1px solid rgba(255,255,255,0.16);
        }
        section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] label {
            color: #ffffff !important;
        }
        section[data-testid="stSidebar"] .stButton>button, section[data-testid="stSidebar"] button {
            background: rgba(255,255,255,0.12) !important;
            border: 1px solid rgba(255,255,255,0.24) !important;
            color: #ffffff !important;
        }
        .css-1lsmgbg.egzxvld2 { background: transparent !important; }
        /* Inputs y selects */
        input, textarea, select { background: white !important; color: var(--text) !important; border: 1px solid var(--accent) !important; border-radius: 10px !important; }
        /* Botones */
        button, .stButton>button { background: var(--accent) !important; color: white !important; border: 1px solid var(--accent-dark) !important; border-radius: 12px !important; padding: 8px 14px !important; font-weight: 600 !important; }
        button:hover, .stButton>button:hover { background: var(--accent-dark) !important; }
        /* Títulos */
        h1, h2, h3, .stMarkdown h1, .stMarkdown h2 { color: #014b47 !important; }
        /* Métricas y tablas */
        .stMetric { background: white !important; border-radius: 12px !important; padding: 10px !important; border: 1px solid var(--accent) !important; }
        .stDataFrame table { background: white !important; }
        .stDataFrame thead th { background: var(--accent) !important; color: white !important; }
        .stDataFrame tbody tr:hover { background: rgba(47,191,154,0.10) !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

inject_styles()

# Crear la base de datos y las tablas al iniciar
Base.metadata.create_all(bind=engine)

# --- FUNCIONES DE UTILIDAD ---
def get_db():
    return SessionLocal()

# --- LÓGICA DE SESIÓN Y LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def login_user(username, password):
    db = SessionLocal()
    user = db.query(UserDB).filter(
        UserDB.username == username, 
        UserDB.password == password
    ).first()
    db.close()
    return user

def register_user(username, password):
    db = SessionLocal()
    existing = db.query(UserDB).filter(UserDB.username == username).first()
    if existing:
        db.close()
        return False, "El usuario ya existe"
    new_user = UserDB(username=username, password=password)
    db.add(new_user)
    db.commit()
    db.close()
    return True, "Usuario creado con éxito"

def create_default_user():
    db = SessionLocal()
    if not db.query(UserDB).first():
        default_user = UserDB(username="admin", password="123")
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
                st.session_state['username'] = user.username
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
                elif " " in reg_user:
                    st.error("El usuario no puede contener espacios")
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
    st.sidebar.title(f"🌱 Zootecnia")
    menu = ["Dashboard", "1. Info General", "2. Registro Animal", "3. Alimentación", 
            "4. Salud", "5. Producción", "6. Ambiente", "7. Costos", "8. Alertas", 
            "9. Reportes", "10. Evidencias"]
    choice = st.sidebar.selectbox("Módulos", menu)
    
    db = get_db()

    # Mostrar saludo en la barra lateral y en la cabecera principal
    username = st.session_state.get('username')
    if username:
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Buenos días"
        elif hour < 19:
            greeting = "Buenas tardes"
        else:
            greeting = "Buenas noches"
        st.sidebar.markdown(f"### 👋 {greeting}, {username}")
        st.sidebar.markdown("---")
        st.markdown(f"#### {greeting}, {username} — bienvenido a Zootecnia 👋")
        st.markdown("---")


    if choice == "Dashboard":
        st.title("📊 Resumen General")
        st.markdown("---")
        st.write("esta aplicacion fue creada con el fin de automatizar trabajos y " \
        "tener almacenamiento de ello y poder hacer consultas  predeminadas  de lo que se registra " \
        "como tal este es un panel donde muestra la inversion y los animales  registrados, " \
        "con el fin de que las personas puedan acceder facil")
        st.markdown("---")
        total_animals = db.query(AnimalDB).count()
        total_investment = db.query(ExpenseDB).with_entities(ExpenseDB.amount).all()
        total_investment = sum(x[0] for x in total_investment)
        col1, col2 = st.columns(2)
        st.markdown("---")
        col1.metric("Animales Registrados", total_animals)
        col2.metric("Inversión Total ($)", f"{total_investment:,.2f}")

        st.write("en la parte superior de mano izquierda hay una flecha >>> donde es el menu desplegable" \
        " donde se podra ver vaias paginas que tiene entrelaza la informacion y cada una tiene su funcion" \
        "")
        st.markdown("---")
        

    elif choice == "1. Info General":
        st.subheader("Nuevo Ciclo Productivo")
        with st.form("cycle_form"):
            farm = st.text_input("Nombre de la Finca")
            location = st.text_input("Ubicación")
            manager = st.text_input("Responsable")
            prod_type = st.selectbox("Tipo", [e.value for e in ProductionType])
            batch = st.text_input("Código de Lote")
            count = st.number_input("Número inicial de animales", min_value=1)
            st.markdown("---")
            
            if st.form_submit_button("Guardar Ciclo"):
                new_cycle = ProductiveCycleDB(
                    farm_name=farm, location=location, manager=manager,
                    production_type=prod_type, batch_code=batch,
                    start_date=datetime.now(), initial_animal_count=int(count)
                )
                db.add(new_cycle)
                db.commit()
                st.success("Ciclo creado con éxito")

        st.subheader("Ciclos Existentes")
        cycles = db.query(ProductiveCycleDB).all()
        if cycles:
            st.dataframe([{
                "Finca": c.farm_name, 
                "Lote": c.batch_code, 
                "Tipo": c.production_type, 
                "Inicio": c.start_date.strftime("%Y-%m-%d")
            } for c in cycles], use_container_width=True)

    elif choice == "2. Registro Animal":
        st.subheader("Registro de Animales")
        cycles = db.query(ProductiveCycleDB).all()
        
        if not cycles:
            st.warning("Primero debes crear un Ciclo Productivo.")
        else:
            cycle_options = {c.batch_code: c.id for c in cycles}
            selected_cycle_code = st.selectbox("Seleccionar Lote/Ciclo", list(cycle_options.keys()))
            
            with st.form("animal_form"):
                a_id = st.text_input("ID o QR del Animal")
                breed = st.text_input("Raza")
                sex = st.selectbox("Sexo", ["Macho", "Hembra"])
                prod_type_default = st.selectbox("Tipo de producción", ["huevos", "carne", "leche", "otro"])
                if prod_type_default == "otro":
                    prod_type_default_custom = st.text_input("Especificar tipo de producción (otro)")
                    if prod_type_default_custom:
                        prod_type_default_save = prod_type_default_custom.strip()
                    else:
                        prod_type_default_save = "otro"
                else:
                    prod_type_default_save = prod_type_default
                prod_unit_default = st.selectbox("Unidad de medida", ["kg", "unidades", "litros", "n/a"])
                weight = st.number_input("Peso Inicial (kg)", min_value=0.0)
                age = st.number_input("Edad (meses)", min_value=0)
                status = st.selectbox("Estado", [e.value for e in AnimalStatus])
                st.markdown("---")

                if st.form_submit_button("Registrar Animal"):
                    new_animal = AnimalDB(
                        animal_id=a_id, breed=breed, sex=sex,
                        age_months=age, initial_weight=weight, current_weight=weight,
                        status=status, cycle_id=cycle_options[selected_cycle_code],
                        history=""
                    )
                    db.add(new_animal)
                    db.commit()
                    try:
                        existing_def = db.query(AnimalDefaultProductionDB).filter(AnimalDefaultProductionDB.animal_id==a_id).first()
                        if not existing_def:
                            default = AnimalDefaultProductionDB(animal_id=a_id, production_type=prod_type_default_save, production_unit=prod_unit_default)
                            db.add(default)
                            db.commit()
                        else:
                            # actualizar si cambió el tipo por defecto
                            existing_def.production_type = prod_type_default_save
                            existing_def.production_unit = prod_unit_default
                            db.commit()
                    except Exception:
                        db.rollback()
                    st.success(f"Animal {a_id} registrado correctamente")

        st.subheader("Lista de Animales")
        animals = db.query(AnimalDB).all()
        if animals:
            st.dataframe([{
                "ID/QR": a.animal_id, "Raza": a.breed, "Peso": a.current_weight, "Estado": a.status
            } for a in animals], use_container_width=True)

    elif choice == "3. Alimentación":
        st.subheader("Control de Alimentación")
        # Formulario básico para Módulo 3
        with st.form("feed_form"):
            a_id = st.text_input("Animal o Lote")
            f_type = st.text_input("Tipo de Alimento")
            qty = st.number_input("Cantidad (kg)", min_value=0.0)
            cost = st.number_input("Costo Unitario", min_value=0.0)
            if st.form_submit_button("Registrar Consumo"):
                db.add(FeedingRecordDB(animal_id=a_id, feed_type=f_type, quantity_kg=qty, unit_cost=cost, timestamp=datetime.now()))
                db.commit()
                st.success("Registro de alimentación guardado")

    elif choice == "4. Salud":
        st.subheader("Seguimiento Veterinario")
        with st.form("health_form"):
            a_id = st.text_input("ID Animal")
            vaccine = st.text_input("Vacuna/Medicamento")
            diag = st.text_area("Diagnóstico/Observaciones")
            if st.form_submit_button("Guardar Registro Médico"):
                new_health = HealthRecordDB(
                    animal_id=a_id, 
                    vaccines=vaccine, 
                    diagnosis=diag,
                    symptoms="",
                    treatment="",
                    deworming_date=datetime.now(),
                    vet_observations="Registro desde UI"
                )
                db.add(new_health)
                db.commit()
                st.success("Historial médico actualizado")

    elif choice == "5. Producción":
        st.subheader("Producción Animal")
        animals = db.query(AnimalDB).all()
        animal_ids = [a.animal_id for a in animals]
        if not animal_ids:
            st.warning("No hay animales registrados aún.")
        else:
            action = st.radio("Acción", ["Registrar producción", "Ver producción"])
            if action == "Registrar producción":
                selected = st.selectbox("Seleccionar animal (ID)", animal_ids)
                default = db.query(AnimalDefaultProductionDB).filter(AnimalDefaultProductionDB.animal_id==selected).first()
                default_type = default.production_type if default else "otro"
                default_unit = default.production_unit if default else "unidades"
                with st.form("register_production_form"):
                    prod_options = ["huevos", "carne", "leche", "otro"]
                    unit_options = ["kg", "unidades", "litros", "n/a"]
                    
                    # Cálculo de índices simplificado y fuera de bloques try/except innecesarios
                    type_index = prod_options.index(default_type) if default_type in prod_options else len(prod_options)-1
                    unit_index = unit_options.index(default_unit) if default_unit in unit_options else 1

                    p_type = st.selectbox("Producto", prod_options, index=type_index)
                    if p_type == "otro":
                        p_type_custom = st.text_input("Especificar producto (otro)")
                        p_type_save = p_type_custom.strip() if p_type_custom else "otro"
                    else:
                        p_type_save = p_type
                    
                    unit = st.selectbox("Unidad", unit_options, index=unit_index)
                    amount = st.number_input("Cantidad producida", min_value=0.0)
                    
                    if st.form_submit_button("Guardar producción"):
                        if not selected:
                            st.error("Selecciona un animal válido.")
                        elif amount <= 0:
                            st.error("Ingresa una cantidad mayor a 0.")
                        else:
                            try:
                                new_prod = ProductionDB(animal_id=selected, product_type=p_type_save, amount=amount, unit=unit, date=datetime.now())
                                db.add(new_prod)
                                db.commit()
                                st.success("Producción registrada")
                            except Exception as e:
                                db.rollback()
                                st.error(f"Error al guardar: {e}")

            else:  # Ver producción
                select_mode = st.radio("Seleccionar animal", ["Desde lista", "Ingresar ID manual"])
                if select_mode == "Desde lista":
                    selected_view = st.selectbox("Seleccionar animal (ID) para ver producción", [""] + animal_ids)
                    if selected_view == "":
                        st.info("Selecciona un ID de animal")
                        selected_view = None
                else:
                    manual_id = st.text_input("Ingresar ID del animal")
                    if manual_id:
                        found = db.query(AnimalDB).filter(AnimalDB.animal_id==manual_id.strip()).first()
                        if not found:
                            st.warning("Animal no registrado")
                            selected_view = None
                        else:
                            selected_view = manual_id.strip()
                    else:
                        selected_view = None

                if selected_view:
                    # permitir filtrar por producto, con opción 'otro' para especificar
                    prod_options = ["Todos", "huevos", "carne", "leche", "otro"]
                    prod_filter = st.selectbox("Filtrar por producto", prod_options)
                    if prod_filter == "otro":
                        prod_filter_custom = st.text_input("Especificar producto a filtrar")
                        filter_val = prod_filter_custom.strip() if prod_filter_custom else None
                    elif prod_filter == "Todos":
                        filter_val = None
                    else:
                        filter_val = prod_filter

                    if filter_val:
                        prods = db.query(ProductionDB).filter(ProductionDB.animal_id==selected_view, ProductionDB.product_type==filter_val).all()
                    else:
                        prods = db.query(ProductionDB).filter(ProductionDB.animal_id==selected_view).all()

                    if not prods:
                        st.warning("No hay registros de producción para este animal.")
                    else:
                        rows = [{
                            "Fecha": p.date.strftime("%Y-%m-%d %H:%M"),
                            "Producto": p.product_type,
                            "Cantidad": p.amount,
                            "Unidad": p.unit
                        } for p in prods]
                        st.dataframe(rows, use_container_width=True)
                        total = sum(p.amount for p in prods)
                        st.metric("Total producido", f"{total} {prods[0].unit}")

    elif choice == "6. Ambiente":
        st.subheader("Condiciones Ambientales")
        with st.form("env_form"):
            temp = st.number_input("Temperatura (°C)")
            hum = st.number_input("Humedad (%)")
            ph = st.number_input("pH Agua")
            if st.form_submit_button("Registrar Clima"):
                db.add(EnvironmentRecordDB(temperature=temp, humidity=hum, water_quality_ph=ph, timestamp=datetime.now()))
                db.commit()
                st.success("Datos ambientales guardados")

    elif choice == "7. Costos":
        st.subheader("Registro de Gastos")
        with st.form("expense_form"):
            category = st.selectbox("Categoría", ["Alimento", "Medicamentos", "Mano de Obra", "Otros"])
            amount = st.number_input("Monto ($)", min_value=0.0)
            desc = st.text_area("Descripción")
            if st.form_submit_button("Guardar Gasto"):
                new_expense = ExpenseDB(category=category, amount=amount, description=desc, date=datetime.now())
                db.add(new_expense)
                db.commit()
                st.success("Gasto registrado")

    elif choice == "8. Alertas":
        st.subheader("Alertas Inteligentes")
        alerts = db.query(SmartAlertDB).filter(SmartAlertDB.is_resolved == False).all()
        if not alerts:
            st.info("No hay alertas activas.")
        for alert in alerts:
            st.warning(f"**[{alert.severity}]** {alert.message}")

    elif choice == "9. Reportes":
        st.title("📊 Reportes y Análisis")
        col1, col2 = st.columns(2)
        
        total_gastos = sum(x[0] for x in db.query(ExpenseDB).with_entities(ExpenseDB.amount).all())
        count_prod = db.query(ProductionDB).count()
        
        col1.metric("Registros de Producción", count_prod)
        col2.metric("Inversión Acumulada", f"${total_gastos:,.2f}")
        
        st.info("Aquí podrás ver gráficas de rendimiento y comparativas entre ciclos próximamente.")

    elif choice == "10. Evidencias":
        st.subheader("Registro Multimedia")
        # Carpeta para almacenar uploads
        uploads_dir = os.path.join(os.getcwd(), "uploads")
        os.makedirs(uploads_dir, exist_ok=True)

        with st.form("evidence_form"):
            use_url = st.checkbox("Usar URL en lugar de subir archivo")
            if use_url:
                url = st.text_input("URL o Ruta del archivo")
                uploaded_file = None
            else:
                uploaded_file = st.file_uploader("Subir archivo (foto, video, pdf, etc.)")
                url = ""
            linked = st.text_input("ID Animal/Lote relacionado")

            if st.form_submit_button("Vincular Evidencia"):
                if use_url:
                    if not url:
                        st.error("Ingresa la URL o ruta del archivo")
                    else:
                        # inferir tipo por extensión
                        ext = url.split('.')[-1].lower() if '.' in url else ''
                        if ext in ["jpg","jpeg","png","gif"]:
                            e_type = "Foto"
                        elif ext in ["mp4","mov","avi","mkv"]:
                            e_type = "Video"
                        elif ext in ["pdf"]:
                            e_type = "Documento"
                        else:
                            e_type = "Otro"
                        db.add(EvidenceDB(type=e_type, file_url=url, linked_entity_id=linked, timestamp=datetime.now()))
                        db.commit()
                        st.success("Evidencia vinculada (URL)")
                else:
                    if not uploaded_file:
                        st.error("Selecciona un archivo para subir")
                    else:
                        try:
                            save_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uploaded_file.name}"
                            save_path = os.path.join(uploads_dir, save_name)
                            with open(save_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())

                            # inferir tipo por extensión
                            ext = uploaded_file.name.split('.')[-1].lower() if '.' in uploaded_file.name else ''
                            if ext in ["jpg","jpeg","png","gif"]:
                                e_type = "Foto"
                            elif ext in ["mp4","mov","avi","mkv"]:
                                e_type = "Video"
                            elif ext in ["pdf"]:
                                e_type = "Documento"
                            else:
                                e_type = "Otro"

                            db.add(EvidenceDB(type=e_type, file_url=save_path, linked_entity_id=linked, timestamp=datetime.now()))
                            db.commit()
                            st.success(f"Archivo subido y registrado: {save_name}")
                        except Exception as e:
                            db.rollback()
                            st.error(f"Error al subir el archivo: {e}")

    db.close()
    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state['logged_in'] = False
        st.rerun()
