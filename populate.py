import random  # For generating random values
from sqlmodel import Session, select
from db.db import engine  # Import the database engine
from models.gem_models import Gem, GemProperties, GemTypes, GemColor  # Import gem models

# A dictionary mapping gem colors to their price multipliers
color_multiplier = {
    'D': 1.8,
    'E': 1.6,
    'G': 1.4,
    'F': 1.2,
    'H': 1,
    'I': 0.8
}

def calculate_gem_price(gem, gem_pr):
    """
    Calculate the price of a gem based on its type, clarity, and size.
    Adjusts price using predefined multipliers.
    """
    price = 1000
    if gem.gem_type == 'Ruby':
        price = 400
    elif gem.gem_type == 'Emerald':
        price = 650

    if gem_pr.clarity == 1:
        price *= 0.75
    elif gem_pr.clarity == 3:
        price *= 1.25
    elif gem_pr.clarity == 4:
        price *= 1.5

    price = price * (gem_pr.size ** 3)

    if gem.gem_type == 'Diamond':
        multiplier = color_multiplier[gem_pr.color]
        price *= multiplier

    return price

def create_gem_props():
    """
    Create a GemProperties instance with random attributes.
    """
    size = random.randint(3, 70) / 10
    color = random.choice(GemColor.list())
    clarity = random.randint(1, 4)

    gemp_p = GemProperties(size=size, clarity=clarity,
                           color=color)
    return gemp_p

def create_gem(gem_p):
    """
    Create a Gem instance using the provided gem properties.
    Calculates the gem price using the calculate_gem_price function.
    """
    type = random.choice(GemTypes.list())
    gem = Gem(price=1000, gem_properties_id=gem_p.id, gem_type=type)
    price = calculate_gem_price(gem, gem_p)
    price = round(price, 2)
    gem.price = price
    return gem

def create_gems_db():
    """
    Populate the database with a set of gem properties and gems.
    """
    # Generate a list of random gem properties
    gem_ps = [create_gem_props() for x in range(100)]
    print(gem_ps)
    with Session(engine) as session:
        session.add_all(gem_ps)
        session.commit()
        # Create a list of gems based on the generated properties
        gems = [create_gem(gem_ps[x]) for x in range(100)]
        session.add_all(gems)
        session.commit()

# create_gems_db()  # Uncomment this line to populate the database with gems
