"""Project repository with specific queries."""

from typing import List, Optional, Dict, Any
from sqlalchemy import or_
from src.models import Project, ProjectMember
from .base import BaseRepository


class ProjectRepository(BaseRepository):
    """Repository for Project model."""
    
    def __init__(self):
        super().__init__(Project)
    
    def get_by_owner(self, owner_id: int, limit: Optional[int] = None, offset: int = 0) -> List[Project]:
        """Get projects by owner."""
        query = self.session.query(Project).filter(Project.owner_id == owner_id)
        if limit:
            query = query.limit(limit).offset(offset)
        return query.all()
    
    def get_user_projects(self, user_id: int, include_owned: bool = True) -> List[Project]:
        """Get all projects a user has access to (owned + member of)."""
        query = self.session.query(Project)
        
        if include_owned:
            # User is owner OR member
            query = query.join(
                ProjectMember,
                (ProjectMember.project_id == Project.id) & (ProjectMember.user_id == user_id),
                isouter=True
            ).filter(
                or_(
                    Project.owner_id == user_id,
                    ProjectMember.user_id == user_id
                )
            ).distinct()
        else:
            # Only projects where user is a member (not owner)
            query = query.join(ProjectMember).filter(
                ProjectMember.user_id == user_id,
                Project.owner_id != user_id
            )
        
        return query.all()
    
    def search_by_name(self, search_term: str, limit: Optional[int] = None, offset: int = 0) -> List[Project]:
        """Search projects by name."""
        query = self.session.query(Project).filter(
            Project.name.ilike(f'%{search_term}%')
        ).order_by(Project.name)
        
        if limit:
            query = query.limit(limit).offset(offset)
        
        return query.all()
    
    def paginate_with_filters(
        self,
        page: int = 1,
        per_page: int = 20,
        owner_id: Optional[int] = None,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Paginate projects with filters."""
        query = self.session.query(Project)
        
        if owner_id is not None:
            query = query.filter(Project.owner_id == owner_id)
        
        if search:
            query = query.filter(Project.name.ilike(f'%{search}%'))
        
        if is_active is not None:
            query = query.filter(Project.is_active == is_active)
        
        query = query.order_by(Project.created_at.desc())
        
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
    
    def add_member(self, project_id: int, user_id: int, role: str = 'member') -> ProjectMember:
        """Add a member to a project."""
        member = ProjectMember(project_id=project_id, user_id=user_id, role=role)
        self.session.add(member)
        self.session.commit()
        self.session.refresh(member)
        return member
    
    def remove_member(self, project_id: int, user_id: int) -> bool:
        """Remove a member from a project."""
        member = self.session.query(ProjectMember).filter_by(
            project_id=project_id,
            user_id=user_id
        ).first()
        
        if member:
            self.session.delete(member)
            self.session.commit()
            return True
        return False
    
    def get_member(self, project_id: int, user_id: int) -> Optional[ProjectMember]:
        """Get project member relationship."""
        return self.session.query(ProjectMember).filter_by(
            project_id=project_id,
            user_id=user_id
        ).first()
    
    def is_member(self, project_id: int, user_id: int) -> bool:
        """Check if user is a member of project."""
        project = self.get_by_id(project_id)
        if not project:
            return False
        
        # Owner is always a member
        if project.owner_id == user_id:
            return True
        
        # Check membership
        return self.get_member(project_id, user_id) is not None
