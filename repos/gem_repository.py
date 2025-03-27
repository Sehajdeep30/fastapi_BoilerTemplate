from db.db import engine  # Import the database engine from the DB module
from models.gem_models import Gem, GemProperties  # Import gem-related models
from sqlmodel import Session, select, or_  # SQLModel ORM functions

def select_all_gems():
    """
    Retrieve all gems along with their properties.
    Returns a list of dictionaries, each containing a gem and its properties.
    """
    with Session(engine) as session:
        # Build a query that joins Gem and GemProperties
        statement = select(Gem, GemProperties).join(GemProperties)
        # Execute the query and iterate over the results
        result = session.exec(statement)
        res = []
        for gem, props in result:
            res.append({'gem': gem, 'props': props})
        return res

def select_gem(id):
    """
    Retrieve a specific gem by its ID along with its properties.
    Returns the first matching tuple (gem, gem_properties) or None.
    """
    with Session(engine) as session:
        # Build a query with a join and filter on Gem.id
        statement = select(Gem, GemProperties).join(GemProperties)
        statement = statement.where(Gem.id == id)
        result = session.exec(statement)
        return result.first()

# select_gems()  # This line is commented out; it may be used for debugging or testing.
