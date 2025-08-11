"""Templates blueprint."""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
import os

from ...models.email_template import EmailTemplate
from ...enums import NotificationType, TemplateFormat, TemplateStatus
from ...exceptions import ValidationError, NotificationError
from ...repositories.dynamodb_template_repository import DynamoDBTemplateRepository

logger = logging.getLogger(__name__)
bp = Blueprint('templates', __name__)

# Initialize template repository
def get_template_repository():
    """Get template repository instance."""
    return DynamoDBTemplateRepository(
        table_name=os.getenv('TEMPLATES_TABLE', 'email_templates')
    )

@bp.route('/', methods=['POST'])
def create_template():
    """Create new email template."""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")
        
        # Validate required fields
        required_fields = ['template_name', 'template_type', 'subject_template', 'body_template']
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
        
        # Create email template
        template = EmailTemplate(
            template_name=data['template_name'],
            template_type=NotificationType(data['template_type']),
            subject_template=data['subject_template'],
            body_template=data['body_template'],
            required_variables=data.get('required_variables', []),
            optional_variables=data.get('optional_variables', []),
            template_format=TemplateFormat.TEXT,  # Default to text
            description=data.get('description', '')
        )
        
        # Save template to DynamoDB
        template_repo = get_template_repository()
        template_repo.save(template)
        
        return jsonify({
            "success": True,
            "template_id": template.id,
            "template_name": template.template_name,
            "message": "Template created successfully"
        })
        
    except ValidationError as e:
        logger.error(f"Validation error in create_template: {e}")
        return jsonify({
            "success": False,
            "error": "Validation Error",
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error in create_template: {e}")
        return jsonify({
            "success": False,
            "error": "Internal Server Error",
            "message": "Failed to create template"
        }), 500

@bp.route('/<template_name>', methods=['GET'])
def get_template(template_name):
    """Get template by name."""
    try:
        # Retrieve template from DynamoDB
        template_repo = get_template_repository()
        template = template_repo.find_by_name(template_name)
        
        if not template:
            return jsonify({
                "success": False,
                "error": "Not Found",
                "message": f"Template '{template_name}' not found"
            }), 404
        
        return jsonify({
            "success": True,
            "template_id": template.id,
            "template_name": template.template_name,
            "template_type": template.template_type.value,
            "subject_template": template.subject_template,
            "body_template": template.body_template,
            "required_variables": template.required_variables,
            "optional_variables": template.optional_variables,
            "status": template.status.value,
            "created_at": template.created_at.isoformat() + "Z"
        })
        
    except Exception as e:
        logger.error(f"Error in get_template: {e}")
        return jsonify({
            "success": False,
            "error": "Internal Server Error",
            "message": "Failed to retrieve template"
        }), 500

@bp.route('/render', methods=['POST'])
def render_template():
    """Render template with variables."""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")
        
        # Validate required fields
        required_fields = ['template_name', 'template_variables']
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
        
        template_name = data['template_name']
        template_variables = data['template_variables']
        
        # Retrieve template from DynamoDB
        template_repo = get_template_repository()
        template = template_repo.find_by_name(template_name)
        
        if not template:
            return jsonify({
                "success": False,
                "error": "Not Found",
                "message": f"Template '{template_name}' not found"
            }), 404
        
        # Render template
        rendered_content = template.render(template_variables)
        
        return jsonify({
            "success": True,
            "rendered_subject": rendered_content['subject'],
            "rendered_body": rendered_content['body']
        })
        
    except ValidationError as e:
        logger.error(f"Validation error in render_template: {e}")
        return jsonify({
            "success": False,
            "error": "Validation Error",
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error in render_template: {e}")
        return jsonify({
            "success": False,
            "error": "Internal Server Error",
            "message": "Failed to render template"
        }), 500

@bp.route('/', methods=['GET'])
def list_templates():
    """List all templates."""
    try:
        # Retrieve templates from DynamoDB
        template_repo = get_template_repository()
        templates = template_repo.find_all()
        
        template_list = []
        for template in templates:
            template_list.append({
                "template_id": template.id,
                "template_name": template.template_name,
                "template_type": template.template_type.value,
                "status": template.status.value,
                "created_at": template.created_at.isoformat() + "Z"
            })
        
        return jsonify({
            "success": True,
            "templates": template_list,
            "total": len(template_list)
        })
        
    except Exception as e:
        logger.error(f"Error in list_templates: {e}")
        return jsonify({
            "success": False,
            "error": "Internal Server Error",
            "message": "Failed to list templates"
        }), 500