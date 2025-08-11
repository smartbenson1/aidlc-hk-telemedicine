"""Template caching service for performance optimization."""

import json
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from ..models.email_template import EmailTemplate
from ..repositories.dynamodb_template_repository import DynamoDBTemplateRepository
from ..exceptions import NotificationError

logger = logging.getLogger(__name__)

class TemplateCache:
    """In-memory cache for email templates with TTL support."""
    
    def __init__(self, ttl_seconds: int = 3600):  # 1 hour default TTL
        """Initialize template cache."""
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_count: Dict[str, int] = {}
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 minutes
    
    def get(self, template_name: str) -> Optional[EmailTemplate]:
        """Get template from cache."""
        self._cleanup_expired()
        
        if template_name not in self.cache:
            return None
        
        cache_entry = self.cache[template_name]
        
        # Check if expired
        if time.time() > cache_entry['expires_at']:
            del self.cache[template_name]
            if template_name in self.access_count:
                del self.access_count[template_name]
            return None
        
        # Update access count
        self.access_count[template_name] = self.access_count.get(template_name, 0) + 1
        
        # Return cached template
        return cache_entry['template']
    
    def put(self, template: EmailTemplate) -> None:
        """Put template in cache."""
        expires_at = time.time() + self.ttl_seconds
        
        self.cache[template.template_name] = {
            'template': template,
            'cached_at': time.time(),
            'expires_at': expires_at
        }
        
        logger.debug(f"Cached template {template.template_name} until {datetime.fromtimestamp(expires_at)}")
    
    def invalidate(self, template_name: str) -> bool:
        """Invalidate specific template from cache."""
        if template_name in self.cache:
            del self.cache[template_name]
            if template_name in self.access_count:
                del self.access_count[template_name]
            logger.info(f"Invalidated template {template_name} from cache")
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cached templates."""
        cleared_count = len(self.cache)
        self.cache.clear()
        self.access_count.clear()
        logger.info(f"Cleared {cleared_count} templates from cache")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        self._cleanup_expired()
        
        total_templates = len(self.cache)
        total_access_count = sum(self.access_count.values())
        
        # Calculate hit rate (approximate)
        most_accessed = []
        if self.access_count:
            sorted_access = sorted(self.access_count.items(), key=lambda x: x[1], reverse=True)
            most_accessed = sorted_access[:5]  # Top 5
        
        return {
            'total_cached_templates': total_templates,
            'total_access_count': total_access_count,
            'cache_size_bytes': self._estimate_cache_size(),
            'ttl_seconds': self.ttl_seconds,
            'most_accessed_templates': most_accessed,
            'cache_entries': list(self.cache.keys())
        }
    
    def _cleanup_expired(self) -> None:
        """Clean up expired cache entries."""
        current_time = time.time()
        
        # Only cleanup periodically to avoid excessive processing
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        expired_keys = []
        for template_name, cache_entry in self.cache.items():
            if current_time > cache_entry['expires_at']:
                expired_keys.append(template_name)
        
        # Remove expired entries
        for key in expired_keys:
            del self.cache[key]
            if key in self.access_count:
                del self.access_count[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired templates from cache")
        
        self.last_cleanup = current_time
    
    def _estimate_cache_size(self) -> int:
        """Estimate cache size in bytes."""
        try:
            # Rough estimation by serializing cache content
            cache_data = {
                'templates': len(self.cache),
                'access_counts': self.access_count
            }
            return len(json.dumps(cache_data, default=str))
        except:
            return 0

class CachedTemplateRepository:
    """Template repository with caching layer."""
    
    def __init__(self, 
                 base_repository: DynamoDBTemplateRepository,
                 cache_ttl_seconds: int = 3600):
        """Initialize cached template repository."""
        self.base_repository = base_repository
        self.cache = TemplateCache(ttl_seconds=cache_ttl_seconds)
        self.cache_hits = 0
        self.cache_misses = 0
    
    def find_by_name(self, template_name: str) -> Optional[EmailTemplate]:
        """Find template by name with caching."""
        # Try cache first
        template = self.cache.get(template_name)
        if template:
            self.cache_hits += 1
            logger.debug(f"Cache hit for template {template_name}")
            return template
        
        # Cache miss - fetch from database
        self.cache_misses += 1
        logger.debug(f"Cache miss for template {template_name}")
        
        template = self.base_repository.find_by_name(template_name)
        if template:
            # Cache the template
            self.cache.put(template)
        
        return template
    
    def find_by_id(self, template_id: str) -> Optional[EmailTemplate]:
        """Find template by ID (no caching for ID lookups)."""
        return self.base_repository.find_by_id(template_id)
    
    def find_active(self) -> List[EmailTemplate]:
        """Find all active templates (no caching for bulk operations)."""
        return self.base_repository.find_active()
    
    def find_all(self) -> List[EmailTemplate]:
        """Find all templates (no caching for bulk operations)."""
        return self.base_repository.find_all()
    
    def save(self, template: EmailTemplate) -> EmailTemplate:
        """Save template and update cache."""
        saved_template = self.base_repository.save(template)
        
        # Update cache
        self.cache.put(saved_template)
        logger.info(f"Saved and cached template {template.template_name}")
        
        return saved_template
    
    def update_status(self, template_name: str, status) -> None:
        """Update template status and invalidate cache."""
        self.base_repository.update_status(template_name, status)
        
        # Invalidate cache entry
        self.cache.invalidate(template_name)
        logger.info(f"Updated template {template_name} status and invalidated cache")
    
    def delete(self, template_name: str) -> None:
        """Delete template and remove from cache."""
        self.base_repository.delete(template_name)
        
        # Remove from cache
        self.cache.invalidate(template_name)
        logger.info(f"Deleted template {template_name} and removed from cache")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        cache_stats = self.cache.get_stats()
        
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate_percentage': round(hit_rate, 2),
            'total_requests': total_requests,
            **cache_stats
        }
    
    def clear_cache(self) -> None:
        """Clear template cache."""
        self.cache.clear()
        logger.info("Cleared template cache")
    
    def warm_cache(self, template_names: List[str] = None) -> Dict[str, Any]:
        """Warm cache with frequently used templates."""
        try:
            if template_names:
                # Warm specific templates
                warmed_count = 0
                for template_name in template_names:
                    template = self.base_repository.find_by_name(template_name)
                    if template:
                        self.cache.put(template)
                        warmed_count += 1
                
                logger.info(f"Warmed cache with {warmed_count} specific templates")
                return {
                    'success': True,
                    'warmed_count': warmed_count,
                    'requested_count': len(template_names)
                }
            else:
                # Warm with all active templates
                active_templates = self.base_repository.find_active()
                for template in active_templates:
                    self.cache.put(template)
                
                logger.info(f"Warmed cache with {len(active_templates)} active templates")
                return {
                    'success': True,
                    'warmed_count': len(active_templates),
                    'message': 'Warmed cache with all active templates'
                }
                
        except Exception as e:
            logger.error(f"Failed to warm cache: {e}")
            raise NotificationError(f"Failed to warm cache: {e}")

class TemplateVersionManager:
    """Manager for template versioning and rollback."""
    
    def __init__(self, repository: DynamoDBTemplateRepository):
        """Initialize template version manager."""
        self.repository = repository
    
    def create_version(self, template: EmailTemplate, version_notes: str = "") -> EmailTemplate:
        """Create a new version of a template."""
        try:
            # Generate new version number
            current_version = template.version
            version_parts = current_version.split('.')
            
            # Increment patch version
            if len(version_parts) >= 3:
                patch_version = int(version_parts[2]) + 1
                new_version = f"{version_parts[0]}.{version_parts[1]}.{patch_version}"
            else:
                new_version = f"{current_version}.1"
            
            # Create new template with updated version
            new_template = EmailTemplate(
                template_name=template.template_name,
                template_type=template.template_type,
                subject_template=template.subject_template,
                body_template=template.body_template,
                required_variables=template.required_variables,
                optional_variables=template.optional_variables,
                template_format=template.template_format,
                css_styles=template.css_styles,
                description=f"{template.description} | Version {new_version}: {version_notes}",
                version=new_version,
                status=template.status
            )
            
            # Save new version
            saved_template = self.repository.save(new_template)
            logger.info(f"Created template version {new_version} for {template.template_name}")
            
            return saved_template
            
        except Exception as e:
            logger.error(f"Failed to create template version: {e}")
            raise NotificationError(f"Failed to create template version: {e}")
    
    def get_template_history(self, template_name: str) -> List[Dict[str, Any]]:
        """Get version history for a template."""
        try:
            # This would require a GSI on template_name in DynamoDB
            # For now, return basic info
            template = self.repository.find_by_name(template_name)
            if not template:
                return []
            
            return [{
                'version': template.version,
                'created_at': template.created_at.isoformat(),
                'updated_at': template.updated_at.isoformat(),
                'created_by': template.created_by,
                'status': template.status.value,
                'description': template.description
            }]
            
        except Exception as e:
            logger.error(f"Failed to get template history: {e}")
            raise NotificationError(f"Failed to get template history: {e}")

# Global cached repository instance
_cached_repository = None

def get_cached_template_repository(base_repository: DynamoDBTemplateRepository = None) -> CachedTemplateRepository:
    """Get or create cached template repository instance."""
    global _cached_repository
    
    if _cached_repository is None:
        if base_repository is None:
            base_repository = DynamoDBTemplateRepository()
        _cached_repository = CachedTemplateRepository(base_repository)
    
    return _cached_repository