"""Local testing script for notification service."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from notification_service.api.main import app

if __name__ == "__main__":
    print("Starting Notification Service locally...")
    print("Available endpoints:")
    print("- GET  /health - Health check")
    print("- POST /notifications/send - Send immediate notification")
    print("- POST /notifications/schedule - Schedule notification")
    print("- GET  /notifications/<id>/status - Get notification status")
    print("- POST /notifications/<id>/retry - Retry failed notification")
    print("- POST /templates - Create email template")
    print("- GET  /templates/<name> - Get template by name")
    print("- POST /templates/render - Render template")
    print("- GET  /templates - List all templates")
    print()
    print("Note: This is running in local mode without AWS services.")
    print("For full functionality, deploy to AWS Lambda with proper IAM roles.")
    print()
    
    app.run(host="0.0.0.0", port=8000, debug=True)