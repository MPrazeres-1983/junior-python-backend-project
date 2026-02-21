"""Base repository with generic CRUD operations."""

from typing import Any, Dict, List, Optional, Type, TypeVar
from sqlalchemy import and_, or_
from sqlalchemy.orm import Query
from src.models.base import db

T = TypeVar('T', bound=db.Model)


class BaseRepository:
    """Generic repository with CRUD operations."""
    
    def __init__(self, model: Type[T]):
        self.model = model
        self.session = db.session
    
    def create(self, **kwargs) -> T:
        """Create a new entity."""
        instance = self.model(**kwargs)
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get entity by ID."""
        return self.session.get(self.model, id)
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """Get all entities with optional pagination."""
        query = self.session.query(self.model)
        if limit:
            query = query.limit(limit).offset(offset)
        return query.all()
    
    def filter(self, **kwargs) -> List[T]:
        """Filter entities by attributes."""
        return self.session.query(self.model).filter_by(**kwargs).all()
    
    def filter_one(self, **kwargs) -> Optional[T]:
        """Get first entity matching filters."""
        return self.session.query(self.model).filter_by(**kwargs).first()
    
    def update(self, id: int, **kwargs) -> Optional[T]:
        """Update entity by ID."""
        instance = self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            self.session.commit()
            self.session.refresh(instance)
        return instance
    
    def delete(self, id: int) -> bool:
        """Delete entity by ID."""
        instance = self.get_by_id(id)
        if instance:
            self.session.delete(instance)
            self.session.commit()
            return True
        return False
    
    def count(self, **kwargs) -> int:
        """Count entities matching filters."""
        query = self.session.query(self.model)
        if kwargs:
            query = query.filter_by(**kwargs)
        return query.count()
    
    def paginate(self, page: int = 1, per_page: int = 20, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Paginate query results."""
        query = self.session.query(self.model)
        
        if filters:
            query = query.filter_by(**filters)
        
        total = query.count()
        offset = (page - 1) * per_page
        items = query.limit(per_page).offset(offset).all()
        
        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page if total > 0 else 0
        }
    
    def exists(self, **kwargs) -> bool:
        """Check if entity exists with given filters."""
        return self.session.query(self.model).filter_by(**kwargs).first() is not None
