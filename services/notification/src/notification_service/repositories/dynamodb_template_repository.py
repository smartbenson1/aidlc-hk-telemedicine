"""DynamoDB repository for email templates."""

import boto3
import json
import logging
from typing import Optional, List, Dict, Any
from botocore.exceptions import ClientError

from ..models.email_template import EmailTemplate
from ..enums import TemplateStatus
from ..exceptions import NotificationError

logger = logging.getLogger(__name__)

class DynamoDBTemplateRepository:
    """DynamoDB repository for email template management."""
    
    def __init__(self, table_name: str = "email_templates"):
        """Initialize repository with DynamoDB table."""
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
        
    def save(self, template: EmailTemplate) -> EmailTemplate:
        """Save email template to DynamoDB."""
        try:
            item = self._template_to_item(template)
            
            self.table.put_item(Item=item)
            logger.info(f"Saved template {template.template_name} to DynamoDB")
            
            return template
            
        except ClientError as e:
            logger.error(f"Failed to save template {template.template_name}: {e}")
            raise NotificationError(f"Failed to save template: {e}")
    
    def find_by_name(self, template_name: str) -> Optional[EmailTemplate]:
        """Find template by name."""
        try:
            response = self.table.get_item(
                Key={'template_name': template_name}
            )
            
            if 'Item' not in response:
                return None
            
            return self._item_to_template(response['Item'])
            
        except ClientError as e:
            logger.error(f"Failed to find template {template_name}: {e}")
            raise NotificationError(f"Failed to find template: {e}")
    
    def find_by_id(self, template_id: str) -> Optional[EmailTemplate]:
        """Find template by ID."""
        try:
            response = self.table.scan(
                FilterExpression='id = :template_id',
                ExpressionAttributeValues={':template_id': template_id}
            )
            
            items = response.get('Items', [])
            if not items:
                return None
            
            return self._item_to_template(items[0])
            
        except ClientError as e:
            logger.error(f"Failed to find template by ID {template_id}: {e}")
            raise NotificationError(f"Failed to find template: {e}")
    
    def find_active(self) -> List[EmailTemplate]:
        """Find all active templates."""
        try:
            response = self.table.scan(
                FilterExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':status': TemplateStatus.ACTIVE.value}
            )
            
            templates = []
            for item in response.get('Items', []):
                templates.append(self._item_to_template(item))
            
            return templates
            
        except ClientError as e:
            logger.error(f"Failed to find active templates: {e}")
            raise NotificationError(f"Failed to find active templates: {e}")
    
    def find_all(self) -> List[EmailTemplate]:
        """Find all templates."""
        try:
            response = self.table.scan()
            
            templates = []
            for item in response.get('Items', []):
                templates.append(self._item_to_template(item))
            
            return templates
            
        except ClientError as e:
            logger.error(f"Failed to find all templates: {e}")
            raise NotificationError(f"Failed to find templates: {e}")
    
    def update_status(self, template_name: str, status: TemplateStatus) -> None:
        """Update template status."""
        try:
            from datetime import datetime
            
            self.table.update_item(
                Key={'template_name': template_name},
                UpdateExpression="SET #status = :status, updated_at = :updated_at",
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': status.value,
                    ':updated_at': datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Updated template {template_name} status to {status.value}")
            
        except ClientError as e:
            logger.error(f"Failed to update template {template_name} status: {e}")
            raise NotificationError(f"Failed to update template status: {e}")
    
    def delete(self, template_name: str) -> None:
        """Delete template."""
        try:
            self.table.delete_item(
                Key={'template_name': template_name}
            )
            
            logger.info(f"Deleted template {template_name}")
            
        except ClientError as e:
            logger.error(f"Failed to delete template {template_name}: {e}")
            raise NotificationError(f"Failed to delete template: {e}")
    
    def _template_to_item(self, template: EmailTemplate) -> Dict[str, Any]:
        """Convert email template to DynamoDB item."""
        item = {
            'id': template.id,
            'template_name': template.template_name,
            'template_type': template.template_type.value,
            'subject_template': template.subject_template,
            'body_template': template.body_template,
            'required_variables': template.required_variables,
            'optional_variables': template.optional_variables,
            'template_format': template.template_format.value,
            'description': template.description or '',
            'version': template.version,
            'status': template.status.value,
            'created_at': template.created_at.isoformat(),
            'updated_at': template.updated_at.isoformat(),
            'created_by': template.created_by,
            'updated_by': template.updated_by
        }
        
        # Add optional fields
        if template.css_styles:
            item['css_styles'] = template.css_styles
        
        return item
    
    def _item_to_template(self, item: Dict[str, Any]) -> EmailTemplate:
        """Convert DynamoDB item to email template."""
        from ..enums import NotificationType, TemplateFormat, TemplateStatus
        from datetime import datetime
        
        # Parse datetime fields
        created_at = datetime.fromisoformat(item['created_at'])
        updated_at = datetime.fromisoformat(item['updated_at'])
        
        return EmailTemplate(
            id=item['id'],
            template_name=item['template_name'],
            template_type=NotificationType(item['template_type']),
            subject_template=item['subject_template'],
            body_template=item['body_template'],
            required_variables=item.get('required_variables', []),
            optional_variables=item.get('optional_variables', []),
            template_format=TemplateFormat(item['template_format']),
            css_styles=item.get('css_styles'),
            description=item.get('description', ''),
            version=item.get('version', '1.0.0'),
            status=TemplateStatus(item['status']),
            created_at=created_at,
            updated_at=updated_at,
            created_by=item.get('created_by', 'system'),
            updated_by=item.get('updated_by', 'system')
        )