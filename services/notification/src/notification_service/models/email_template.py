"""Email template domain model."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..enums import NotificationType, TemplateFormat, TemplateStatus
from ..utils.helpers import generate_uuid, get_current_datetime
from ..utils.validation import validate_template_data, ValidationResult
from ..exceptions import ValidationError


@dataclass
class EmailTemplate:
    """Email template for dynamic notification content."""
    
    # Identity
    id: str = field(default_factory=generate_uuid)
    
    # Template Information
    template_name: str = ""
    template_type: NotificationType = NotificationType.APPOINTMENT_REMINDER
    
    # Content
    subject_template: str = ""
    body_template: str = ""
    
    # Template Variables
    required_variables: List[str] = field(default_factory=list)
    optional_variables: List[str] = field(default_factory=list)
    
    # Formatting and Design
    template_format: TemplateFormat = TemplateFormat.HTML
    css_styles: Optional[str] = None
    
    # Metadata
    description: str = ""
    version: str = "1.0.0"
    
    # System Fields
    status: TemplateStatus = TemplateStatus.ACTIVE
    created_at: datetime = field(default_factory=get_current_datetime)
    updated_at: datetime = field(default_factory=get_current_datetime)
    created_by: str = "system"
    updated_by: str = "system"
    
    def __post_init__(self):
        """Validate data after initialization."""
        self.validate()
    
    def validate(self) -> ValidationResult:
        """Validate template data."""
        data = self.to_dict()
        result = validate_template_data(data)
        
        if not result.is_valid:
            raise ValidationError(f"Invalid template data: {', '.join(result.errors)}")
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary."""
        return {
            'id': self.id,
            'template_name': self.template_name,
            'template_type': self.template_type.value if isinstance(self.template_type, NotificationType) else self.template_type,
            'subject_template': self.subject_template,
            'body_template': self.body_template,
            'required_variables': self.required_variables,
            'optional_variables': self.optional_variables,
            'template_format': self.template_format.value if isinstance(self.template_format, TemplateFormat) else self.template_format,
            'css_styles': self.css_styles,
            'description': self.description,
            'version': self.version,
            'status': self.status.value if isinstance(self.status, TemplateStatus) else self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmailTemplate':
        """Create template from dictionary."""
        # Convert enum strings back to enums
        if 'template_type' in data and isinstance(data['template_type'], str):
            data['template_type'] = NotificationType(data['template_type'])
        
        if 'template_format' in data and isinstance(data['template_format'], str):
            data['template_format'] = TemplateFormat(data['template_format'])
        
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = TemplateStatus(data['status'])
        
        # Convert datetime strings
        datetime_fields = ['created_at', 'updated_at']
        for field_name in datetime_fields:
            if field_name in data and isinstance(data[field_name], str):
                try:
                    data[field_name] = datetime.fromisoformat(data[field_name])
                except ValueError:
                    data[field_name] = None
        
        return cls(**data)
    
    def render(self, variables: Dict[str, Any]) -> Dict[str, str]:
        """Render template with variables."""
        # Simple string formatting - in production would use Jinja2
        try:
            rendered_subject = self.subject_template.format(**variables)
            rendered_body = self.body_template.format(**variables)
            
            return {
                'subject': rendered_subject,
                'body': rendered_body
            }
        except KeyError as e:
            raise ValidationError(f"Missing required template variable: {e}")
    
    def validate_variables(self, variables: Dict[str, Any]) -> ValidationResult:
        """Validate that all required variables are provided."""
        errors = []
        
        for required_var in self.required_variables:
            if required_var not in variables:
                errors.append(f"Missing required variable: {required_var}")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
    
    def is_active(self) -> bool:
        """Check if template is active."""
        return self.status == TemplateStatus.ACTIVE