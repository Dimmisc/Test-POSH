import enum
import sqlalchemy as sq
from sqlalchemy import JSON
from  sqlalchemy.orm  import DeclarativeBase, mapped_column, Mapped, relationship
from typing import List

class Base(DeclarativeBase):
    pass

class Chunk(Base):
    __tablename__ = "chunks"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    field: Mapped[List[List[int]]] = mapped_column(JSON)
    
    map: Mapped["Map"] = relationship(back_populates="chunks")


class Map(Base):
    __tablename__ = "maps"
    id: Mapped[int] = mapped_column(primary_key=True)

    chunks: Mapped[List["Chunk"]] = relationship(back_populates="map")
    modules: Mapped[List["Module"]] = relationship(back_populates="map")

    cuper_price: Mapped[float]
    engel_price: Mapped[float]
    

class ModuleType(enum.Enum, str):
    SENDER = "sender"
    LISTENER = "listener"
    CUPER = "cuper"
    ENGEL = "engel"


class Module(Base):
    __tablename__ = "modules"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[ModuleType] = mapped_column()
    x: Mapped[int] = mapped_column(nullable=False)
    y: Mapped[int] = mapped_column(nullable=False)

    map: Mapped["Map"] = relationship(back_populates="modules")