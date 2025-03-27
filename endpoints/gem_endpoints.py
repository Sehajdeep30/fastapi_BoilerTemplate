from typing import List, Dict, Union, Optional  # Added Optional for type hints

from fastapi import APIRouter, Security, Depends, Query  # Import required FastAPI classes
from fastapi.security import HTTPAuthorizationCredentials  # For bearer token credentials
from sqlmodel import select  # For constructing SQL queries
from starlette.responses import JSONResponse  # For custom JSON responses with status codes
from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED  # For HTTP status codes
from fastapi.encoders import jsonable_encoder  # To encode ORM models to JSON
import repos.gem_repository  # Custom repository for gem-related data access
from endpoints.user_endpoints import auth_handler  # Import authentication handler from user endpoints
from populate import calculate_gem_price  # Function to calculate gem price; 🔹 CUSTOMIZE if necessary
from models.gem_models import *  # Import all gem-related models; ensure namespace is managed properly
from db.db import session  # Import the shared database session

# Create an API router for gem-related endpoints
gem_router = APIRouter()

# Simple endpoint to test connectivity
@gem_router.get('/')
def greet():
    return 'Hello production'

# Endpoint to retrieve gems with optional filters
@gem_router.get('/gems', tags=['Gems'])
def gems(lte: Optional[int] = None, gte: Optional[int] = None,
         type: List[Optional[GemTypes]] = Query(None)):
    # Construct the query to join Gem and GemProperties
    gems = select(Gem, GemProperties).join(GemProperties)
    if lte:
        gems = gems.where(Gem.price <= lte)
    if gte:
        gems = gems.where(Gem.price >= gte)
    if type:
        gems = gems.where(Gem.gem_type.in_(type)).order_by(Gem.gem_type).order_by(-Gem.price).order_by(None)
    # Execute the query and fetch all results
    gems = session.exec(gems).all()
    return {'gems': gems}

# Endpoint to retrieve a single gem by ID
@gem_router.get('/gem/{id}', response_model=Gem, tags=['Gems'])
def gem(id: int):
    gem_found = session.get(Gem, id)
    if not gem_found:
        return JSONResponse(status_code=HTTP_404_NOT_FOUND)
    return gem_found

# Endpoint to create a new gem, requires authentication (seller)
@gem_router.post('/gems', tags=['Gems'])
def create_gem(gem_pr: GemProperties, gem: Gem, user=Depends(auth_handler.get_current_user)):
    """Creates gem"""
    # Only allow users with seller privileges to create gems
    if not user.is_seller:
        return JSONResponse(status_code=HTTP_401_UNAUTHORIZED)

    # Create gem properties object from provided details
    gem_properties = GemProperties(size=gem_pr.size, clarity=gem_pr.clarity,
                                   color=gem_pr.color)
    session.add(gem_properties)
    session.commit()
    # Create a Gem object linking the gem properties and seller details
    gem_ = Gem(price=gem.price, available=gem.available, gem_properties=gem_properties,
               gem_properties_id=gem_properties.id, seller_id=user.id, seller=user)
    # Calculate gem price using a custom function
    price = calculate_gem_price(gem, gem_pr)
    gem_.price = price
    session.add(gem_)
    session.commit()
    return gem

# Endpoint to update an existing gem fully
@gem_router.put('/gems/{id}', response_model=Gem, tags=['Gems'])
def update_gem(id: int, gem: Gem, user=Depends(auth_handler.get_current_user)):
    gem_found = session.get(Gem, id)
    # Only allow the seller who owns the gem to update it
    if not user.is_seller or gem_found.seller_id != user.id:
        return JSONResponse(status_code=HTTP_401_UNAUTHORIZED)
    update_item_encoded = jsonable_encoder(gem)
    update_item_encoded.pop('id', None)  # Remove id to prevent overriding primary key
    # Update each field in the found gem
    for key, val in update_item_encoded.items():
        gem_found.__setattr__(key, val)
    session.commit()
    return gem_found

# Endpoint to partially update a gem
@gem_router.patch('/gems/{id}', response_model=Gem, tags=['Gems'])
def patch_gem(id: int, gem: GemPatch, user=Depends(auth_handler.get_current_user)):
    gem_found = session.get(Gem, id)
    # Only allow update if the current user is the seller of the gem
    if not user.is_seller or gem_found.seller_id != user.id:
        return JSONResponse(status_code=HTTP_401_UNAUTHORIZED)
    update_data = gem.dict(exclude_unset=True)
    update_data.pop('id', None)  # Remove id to avoid conflicts
    # Update each provided field in the gem object
    for key, val in update_data.items():
        gem_found.__setattr__(key, val)
    session.commit()
    return gem_found

# Endpoint to delete a gem by its ID
@gem_router.delete('/gems/{id}', status_code=HTTP_204_NO_CONTENT, tags=['Gems'])
def delete_gem(id: int, user=Depends(auth_handler.get_current_user)):
    gem_found = session.get(Gem, id)
    # Only allow deletion if the current user is the seller of the gem
    if not user.is_seller or gem_found.seller_id != user.id:
        return JSONResponse(status_code=HTTP_401_UNAUTHORIZED)
    session.delete(gem_found)
    session.commit()

# Endpoint to get gems associated with the current seller
@gem_router.get('/gems/seller/me', tags=['seller'],
                response_model=List[Dict[str, Union[Gem, GemProperties]]])
def gems_seller(user=Depends(auth_handler.get_current_user)):
    if not user.is_seller:
        return JSONResponse(status_code=HTTP_401_UNAUTHORIZED)
    # Select gems and their properties for the current seller
    statement = select(Gem, GemProperties).where(Gem.seller_id == user.id).join(GemProperties)
    gems = session.exec(statement).all()
    # Format the result as a list of dictionaries
    res = [{'gem': gem, 'props': props} for gem, props in gems]
    return res
