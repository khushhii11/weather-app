import logging
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from . import models, schemas

logger = logging.getLogger(__name__)


def get_locations(db: Session, skip: int = 0, limit: int = 100) -> List[models.Location]:
    """
    Retrieve a list of saved locations.

    Args:
        db: Database session.
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.

    Returns:
        List of Location models.
    """
    return db.query(models.Location).offset(skip).limit(limit).all()


def get_location(db: Session, loc_id: int) -> Optional[models.Location]:
    """
    Retrieve a single location by its ID.

    Args:
        db: Database session.
        loc_id: ID of the location to retrieve.

    Returns:
        The Location model if found, else None.
    """
    return db.query(models.Location).filter(models.Location.id == loc_id).first()


def create_location(db: Session, loc: schemas.LocationCreate) -> models.Location:
    """
    Create a new location record.

    Args:
        db: Database session.
        loc: Pydantic schema for location creation.

    Returns:
        The newly created Location model.

    Raises:
        SQLAlchemyError: If the database commit fails.
    """
    db_loc = models.Location(**loc.dict())
    db.add(db_loc)
    try:
        db.commit()
        db.refresh(db_loc)
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception("Error creating location: %s", e)
        raise
    return db_loc


def update_location(db: Session, loc_id: int, loc: schemas.LocationUpdate) -> Optional[models.Location]:
    """
    Update an existing location record.

    Args:
        db: Database session.
        loc_id: ID of the location to update.
        loc: Pydantic schema with fields to update.

    Returns:
        The updated Location model if successful, else None if not found.

    Raises:
        SQLAlchemyError: If the database commit fails.
    """
    db_loc = get_location(db, loc_id)
    if not db_loc:
        return None

    update_data = loc.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_loc, field, value)

    try:
        db.commit()
        db.refresh(db_loc)
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception("Error updating location id %s: %s", loc_id, e)
        raise
    return db_loc


def delete_location(db: Session, loc_id: int) -> Optional[models.Location]:
    """
    Delete a location record by its ID.

    Args:
        db: Database session.
        loc_id: ID of the location to delete.

    Returns:
        The deleted Location model if found and deleted, else None.

    Raises:
        SQLAlchemyError: If the database commit fails.
    """
    db_loc = get_location(db, loc_id)
    if not db_loc:
        return None

    try:
        db.delete(db_loc)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception("Error deleting location id %s: %s", loc_id, e)
        raise
    return db_loc
