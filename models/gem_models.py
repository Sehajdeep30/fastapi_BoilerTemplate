from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum as Enum_, IntEnum

from models.user_models import User  # Import the User model to reference in relationships

# Custom Enum class with a helper method to list enum values
class Enum(Enum_):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

# Enum for different gem types
class GemTypes(str, Enum):
    DIAMOND = 'DIAMOND'
    RUBY = 'RUBY'
    EMERALD = 'EMERALD'

# Enum for gem clarity, represented as an integer enum
class GemClarity(IntEnum):
    SI = 1
    VS = 2
    VVS = 3
    FL = 4

# Enum for gem color, inheriting from str for easy comparison
class GemColor(str, Enum):
    D = 'D'
    E = 'E'
    G = 'G'
    F = 'F'
    H = 'H'
    I = 'I'

# SQLModel for gem properties; represents a table in the DB
class GemProperties(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)  # Primary key column
    size: float = 1  # Default size is set to 1
    clarity: Optional[GemClarity] = None  # Gem clarity (optional)
    color: Optional[GemColor] = None  # Gem color (optional)
    # Relationship to Gem: one-to-one or one-to-many depending on your schema design
    gem: Optional['Gem'] = Relationship(back_populates='gem_properties')

# SQLModel for Gem; represents the main gem table
class Gem(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    price: float  # Price of the gem
    available: bool = True  # Availability status
    gem_type: GemTypes = GemTypes.DIAMOND  # Default gem type is DIAMOND
    # Foreign key referencing GemProperties table
    gem_properties_id: Optional[int] = Field(default=None, foreign_key='gemproperties.id')
    # Relationship to GemProperties
    gem_properties: Optional[GemProperties] = Relationship(back_populates='gem')
    # Foreign key referencing User (seller)
    seller_id: Optional[int] = Field(default=None, foreign_key='user.id')
    # Relationship to User (seller)
    seller: Optional[User] = Relationship()

# SQLModel for patching a gem (partial updates)
class GemPatch(SQLModel):
    id: Optional[int] = Field(primary_key=True)
    price: Optional[float] = 1000  # Default price value; customize as needed
    available: Optional[bool] = True
    gem_type: Optional[GemTypes] = GemTypes.DIAMOND

    # Foreign key referencing GemProperties
    gem_properties_id: Optional[int] = Field(default=None, foreign_key='gemproperties.id')
    # Relationship to GemProperties (used for partial update operations)
    gem_properties: Optional[GemProperties] = Relationship(back_populates='gem')
