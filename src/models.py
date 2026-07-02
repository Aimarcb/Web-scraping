from sqlalchemy import Column, Integer, String, Float, Date, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Alojamiento(Base):
    __tablename__ = 'alojamientos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    destino = Column(String, nullable=False)
    titulo = Column(String, nullable=False)
    precio = Column(Float, nullable=False)
    
    # Almacenamos las fechas del viaje como tipo Date (no strings) para poder hacer filtros analíticos luego
    fecha_entrada = Column(Date, nullable=False)
    fecha_salida = Column(Date, nullable=False)
    
    # Registro de cuándo el bot hizo la extracción
    fecha_captura = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Alojamiento(titulo='{self.titulo}', precio={self.precio}, destino='{self.destino}')>"

def inicializar_base_datos(database_url: str):
    """
    Crea la conexión y genera las tablas si no existen.
    """
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    return Session()