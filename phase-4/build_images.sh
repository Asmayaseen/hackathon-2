#!/bin/bash
set -e

echo "Building Backend Docker Image..."
docker build -t todo-backend:latest ./backend

echo "Building Frontend Docker Image..."
docker build -t todo-frontend:latest ./frontend

echo "Docker images built successfully!"
