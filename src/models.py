from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func

# El "Base" es el molde del que heredarán todas nuestras tablas
Base = declarative_base()

class Libro(Base):
    """
    Representa la tabla 'libros' en la base de datos.
    Cada variable es una columna.
    """
    __tablename__ = 'libros'

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String, nullable=False, unique=True)
    precio = Column(Float, nullable=False)
    stock = Column(String, nullable=True)
    # default: Se ejecuta solo al hacer INSERT
    # onupdate: Se ejecuta automáticamente cada vez que hacemos un UPDATE
    fecha_extraccion = Column(DateTime, default=func.now(), onupdate=func.now())

def inicializar_base_datos(database_url: str):
    """
    Crea la conexión y genera las tablas si no existen.
    Explicación de flags:
    - 'echo=False': Si lo pones en True, SQLAlchemy mostrará por terminal
      todo el código SQL que genera por debajo (útil para debuggear).
    """
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    
    # Creamos una fábrica de sesiones para interactuar con los datos
    Session = sessionmaker(bind=engine)
    return Session()