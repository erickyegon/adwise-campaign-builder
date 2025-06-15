"""
Base Database Models Module

This module provides foundational database model classes with:
- UUID primary keys for security
- Automatic timestamp management
- Soft delete functionality
- Audit logging capabilities
- JSONB support for flexible data
- Full-text search capabilities
- Vector embeddings for AI features

Design Principles:
- Composition over inheritance
- Mixins for specific functionality
- Type safety with proper annotations
- Performance optimized indexes
- Extensible and maintainable
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union, Type

from sqlalchemy import (
    Boolean, Column, DateTime, String, Text, Integer, 
    Float, JSON, Index, event, text, MetaData
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates
from sqlalchemy.sql import func

# Create base with custom metadata for consistent naming
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)

Base = declarative_base(metadata=metadata)


class TimestampMixin:
    """
    Mixin for automatic timestamp management
    
    Provides:
    - created_at: Automatic creation timestamp
    - updated_at: Automatic update timestamp
    """
    
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        comment="Record creation timestamp in UTC"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        comment="Record last update timestamp in UTC"
    )
    
    @hybrid_property
    def age_in_days(self) -> int:
        """Calculate age of record in days"""
        if self.created_at:
            return (datetime.now(timezone.utc) - self.created_at).days
        return 0


class SoftDeleteMixin:
    """
    Mixin for soft delete functionality
    
    Provides:
    - is_deleted: Boolean flag for soft deletion
    - deleted_at: Timestamp of deletion
    - deleted_by: User who performed deletion
    """
    
    is_deleted = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text('false'),
        index=True,  # Index for efficient filtering
        comment="Soft delete flag"
    )
    
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Soft delete timestamp in UTC"
    )
    
    deleted_by = Column(
        UUID(as_uuid=True),
        nullable=True,
        comment="UUID of user who performed soft delete"
    )
    
    @hybrid_property
    def is_active(self) -> bool:
        """Check if record is active (not soft deleted)"""
        return not self.is_deleted
    
    def soft_delete(self, user_id: Optional[uuid.UUID] = None) -> None:
        """
        Perform soft delete
        
        Args:
            user_id: UUID of user performing the deletion
        """
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
        self.deleted_by = user_id
    
    def restore(self) -> None:
        """Restore soft deleted record"""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None


class AuditMixin:
    """
    Mixin for comprehensive audit logging
    
    Provides:
    - created_by: User who created the record
    - updated_by: User who last updated the record
    - version: Version number for optimistic locking
    - audit_log: Detailed change history
    """
    
    created_by = Column(
        UUID(as_uuid=True),
        nullable=True,
        comment="UUID of user who created the record"
    )
    
    updated_by = Column(
        UUID(as_uuid=True),
        nullable=True,
        comment="UUID of user who last updated the record"
    )
    
    version = Column(
        Integer,
        nullable=False,
        default=1,
        comment="Record version for optimistic locking"
    )
    
    audit_log = Column(
        JSONB,
        nullable=True,
        default=list,
        comment="Detailed audit log of changes"
    )
    
    def add_audit_entry(
        self, 
        action: str, 
        user_id: Optional[uuid.UUID], 
        changes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add entry to audit log
        
        Args:
            action: Type of action performed
            user_id: UUID of user performing action
            changes: Dictionary of field changes
            metadata: Additional metadata
        """
        if self.audit_log is None:
            self.audit_log = []
        
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "user_id": str(user_id) if user_id else None,
            "changes": changes or {},
            "metadata": metadata or {},
            "version": self.version
        }
        
        self.audit_log.append(entry)
    
    def get_audit_history(self, action_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get audit history with optional filtering
        
        Args:
            action_filter: Filter by specific action type
            
        Returns:
            List of audit entries
        """
        if not self.audit_log:
            return []
        
        if action_filter:
            return [entry for entry in self.audit_log if entry.get("action") == action_filter]
        
        return self.audit_log


class MetadataMixin:
    """
    Mixin for flexible metadata storage
    
    Provides:
    - metadata_json: Flexible JSONB field for custom data
    - tags: Array of tags for categorization
    """
    
    metadata_json = Column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Flexible metadata storage as JSONB"
    )
    
    tags = Column(
        JSONB,
        nullable=True,
        default=list,
        comment="Tags for categorization and filtering"
    )
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value"""
        if self.metadata_json is None:
            self.metadata_json = {}
        self.metadata_json[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value"""
        if self.metadata_json is None:
            return default
        return self.metadata_json.get(key, default)
    
    def remove_metadata(self, key: str) -> None:
        """Remove metadata key"""
        if self.metadata_json and key in self.metadata_json:
            del self.metadata_json[key]
    
    @validates('tags')
    def validate_tags(self, key: str, value: Any) -> List[str]:
        """Validate and normalize tags"""
        if value is None:
            return []
        if isinstance(value, str):
            return [tag.strip().lower() for tag in value.split(',') if tag.strip()]
        if isinstance(value, list):
            return [str(tag).strip().lower() for tag in value if str(tag).strip()]
        return []
    
    def add_tag(self, tag: str) -> None:
        """Add a tag"""
        if self.tags is None:
            self.tags = []
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag"""
        if self.tags and tag.lower() in self.tags:
            self.tags.remove(tag.lower())
    
    def has_tag(self, tag: str) -> bool:
        """Check if record has a specific tag"""
        return self.tags is not None and tag.lower() in self.tags


class SearchableMixin:
    """
    Mixin for full-text search capabilities
    
    Provides:
    - search_vector: PostgreSQL TSVECTOR for full-text search
    - Automatic GIN index for performance
    """
    
    search_vector = Column(
        TSVECTOR,
        nullable=True,
        comment="Full-text search vector"
    )
    
    @declared_attr
    def __table_args__(cls):
        """Add GIN index for search vector"""
        return (
            Index(
                f'ix_{cls.__tablename__}_search_vector', 
                'search_vector', 
                postgresql_using='gin'
            ),
        )


class VectorEmbeddingMixin:
    """
    Mixin for AI vector embeddings
    
    Provides:
    - embedding: Vector embedding for similarity search
    - embedding_model: Model used to generate embedding
    - embedding_updated_at: Timestamp of last embedding update
    """
    
    embedding = Column(
        Text,  # Will store vector as text, converted to vector type in PostgreSQL
        nullable=True,
        comment="AI-generated vector embedding for similarity search"
    )
    
    embedding_model = Column(
        String(100),
        nullable=True,
        comment="Model used to generate the embedding"
    )
    
    embedding_updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When the embedding was last updated"
    )
    
    def update_embedding(self, embedding: str, model: str) -> None:
        """Update embedding with new values"""
        self.embedding = embedding
        self.embedding_model = model
        self.embedding_updated_at = datetime.now(timezone.utc)
    
    @hybrid_property
    def has_embedding(self) -> bool:
        """Check if record has an embedding"""
        return self.embedding is not None


class BaseModel(Base, TimestampMixin, SoftDeleteMixin, AuditMixin, MetadataMixin):
    """
    Base model class with comprehensive functionality
    
    Features:
    - UUID primary keys for security
    - Automatic timestamps
    - Soft delete capability
    - Audit logging
    - Flexible metadata storage
    - Tag support
    - Optimistic locking
    """
    
    __abstract__ = True
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier (UUID)"
    )
    
    def to_dict(self, include_relationships: bool = False) -> Dict[str, Any]:
        """
        Convert model to dictionary
        
        Args:
            include_relationships: Whether to include relationship data
            
        Returns:
            Dictionary representation of the model
        """
        result = {}
        
        # Include column data
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, uuid.UUID):
                value = str(value)
            result[column.name] = value
        
        # Include relationship data if requested
        if include_relationships:
            for relationship_name in self.__mapper__.relationships.keys():
                relationship_value = getattr(self, relationship_name)
                if relationship_value is not None:
                    if hasattr(relationship_value, '__iter__') and not isinstance(relationship_value, str):
                        result[relationship_name] = [
                            item.to_dict() if hasattr(item, 'to_dict') else str(item)
                            for item in relationship_value
                        ]
                    else:
                        result[relationship_name] = (
                            relationship_value.to_dict() 
                            if hasattr(relationship_value, 'to_dict') 
                            else str(relationship_value)
                        )
        
        return result
    
    def update_from_dict(
        self, 
        data: Dict[str, Any], 
        user_id: Optional[uuid.UUID] = None,
        exclude_fields: Optional[List[str]] = None
    ) -> None:
        """
        Update model from dictionary with audit logging
        
        Args:
            data: Dictionary of field updates
            user_id: UUID of user performing update
            exclude_fields: Fields to exclude from update
        """
        exclude_fields = exclude_fields or ['id', 'created_at', 'created_by']
        changes = {}
        
        for key, value in data.items():
            if key in exclude_fields:
                continue
                
            if hasattr(self, key):
                old_value = getattr(self, key)
                if old_value != value:
                    changes[key] = {"old": old_value, "new": value}
                    setattr(self, key, value)
        
        if changes:
            self.updated_by = user_id
            self.version += 1
            self.add_audit_entry("update", user_id, changes)
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"


# Specialized base models for different use cases
class SearchableBaseModel(BaseModel, SearchableMixin):
    """Base model with full-text search capabilities"""
    __abstract__ = True


class AIEnabledBaseModel(BaseModel, VectorEmbeddingMixin):
    """Base model with AI vector embedding capabilities"""
    __abstract__ = True


class FullFeaturedBaseModel(BaseModel, SearchableMixin, VectorEmbeddingMixin):
    """Base model with all features: search, AI embeddings, audit, etc."""
    __abstract__ = True


# Event listeners for automatic functionality
@event.listens_for(BaseModel, 'before_update', propagate=True)
def receive_before_update(mapper, connection, target):
    """Update timestamp before update"""
    target.updated_at = datetime.now(timezone.utc)


@event.listens_for(VectorEmbeddingMixin, 'before_insert', propagate=True)
@event.listens_for(VectorEmbeddingMixin, 'before_update', propagate=True)
def update_embedding_timestamp(mapper, connection, target):
    """Update embedding timestamp when embedding changes"""
    if hasattr(target, 'embedding') and target.embedding:
        target.embedding_updated_at = datetime.now(timezone.utc)
