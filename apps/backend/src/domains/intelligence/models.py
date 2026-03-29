"""Intelligence domain – SQLAlchemy models for the knowledge graph."""

from sqlalchemy import Column, Float, Integer, String, Text

from ...models_base import Base


class SermonEntity(Base):
    """An extracted entity (theme, scripture, concept, preacher, tradition) linked to a sermon."""
    __tablename__ = "sermon_entities"

    id = Column(Integer, primary_key=True, index=True)
    sermon_id = Column(Integer, nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_value = Column(String(500), nullable=False, index=True)


class SermonEdge(Base):
    """A weighted edge between two sermons based on shared entities."""
    __tablename__ = "sermon_edges"

    id = Column(Integer, primary_key=True, index=True)
    source_sermon_id = Column(Integer, nullable=False, index=True)
    target_sermon_id = Column(Integer, nullable=False, index=True)
    edge_type = Column(String(50), nullable=False)
    weight = Column(Float, nullable=False, default=0.0)
    shared_data = Column(Text, default="")  # JSON array of shared entity values
