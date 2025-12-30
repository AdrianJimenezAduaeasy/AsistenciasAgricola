from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import urllib

# Configuración de la conexión a SQL Server
# Reemplaza los valores con tus credenciales reales
server = '46.250.163.203' 
database = 'CZPicho' 
username = 'asispicho' 
password = '1H4eW7youM48lSnRX' 
driver = 'ODBC Driver 18 for SQL Server' # O el driver que tengas instalado

# Construir la cadena de conexión
params = urllib.parse.quote_plus(
    f"DRIVER={{{driver}}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    "TrustServerCertificate=yes;" # Útil para desarrollo local
)

SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params}"

# Crear el motor de la base de datos
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    echo=True # Ponlo en False en producción
)

# Crear la sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
