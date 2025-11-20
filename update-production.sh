# Script para actualizar el backend en producción
# Ejecutar en el servidor EC2

#!/bin/bash

echo "Updating FlyBlue Backend..."

cd ~/flyblue-production

echo "⬇Pulling latest image from Docker Hub..."
docker-compose pull backend

echo "Restarting backend service..."
docker-compose up -d backend

echo "Cleaning up old images..."
docker image prune -f

echo "Backend updated successfully!"
echo "Checking status..."
docker-compose ps backend

echo ""
echo "View logs with: docker-compose logs -f backend"