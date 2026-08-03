#!/bin/bash
# start_n8n.sh
echo "🚀 Starting n8n..."
docker-compose up -d n8n
echo "📡 n8n available at: http://localhost:5678"
echo "🔑 Login: admin / admin123"
echo "📋 Workflow webhook URLs:"
echo "   - Claim: http://localhost:5678/webhook/claim-processing"
echo "   - Email: http://localhost:5678/webhook/email-notification"
echo "   - Ticket: http://localhost:5678/webhook/ticket-email"