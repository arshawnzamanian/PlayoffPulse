#!/bin/bash

echo " Launching NBA Prediction App..."

# Start backend
echo " Starting FastAPI backend on port 9000..."
cd backend || exit
source venv/bin/activate 2>/dev/null || echo " No venv, using global Python"
uvicorn app:app --reload --port 9000 > ../backend.log 2>&1 & 
BACK_PID=$!
cd ..

# Start frontend
echo "️  Starting Next.js frontend on port 3000..."
cd frontend || exit
npm run dev > ./frontend

