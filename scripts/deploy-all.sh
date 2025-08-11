#!/bin/bash

echo "🚀 Deploying All HealMatch Services"
echo "=================================="

# Function to deploy a service
deploy_service() {
    local service_name=$1
    local service_path="services/$service_name"
    
    echo "📦 Deploying $service_name..."
    
    if [ -d "$service_path/infrastructure" ]; then
        cd "$service_path/infrastructure"
        
        # Install dependencies
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt
        fi
        
        # Deploy with CDK
        cdk deploy --require-approval never
        
        if [ $? -eq 0 ]; then
            echo "✅ $service_name deployed successfully"
        else
            echo "❌ $service_name deployment failed"
            exit 1
        fi
        
        cd - > /dev/null
    else
        echo "⚠️  No infrastructure found for $service_name"
    fi
    
    echo ""
}

# Deploy services in order
deploy_service "user-management"
deploy_service "appointment-matching"
deploy_service "notification"
deploy_service "administration"

echo "🎉 All services deployed successfully!"
echo ""
echo "📋 Next steps:"
echo "  1. Test the APIs using the service endpoints"
echo "  2. Deploy the frontend application"
echo "  3. Configure any required integrations"
