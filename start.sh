#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Stop any existing Streamlit processes
echo "🔄 Stopping any existing Streamlit processes..."
pkill -f "streamlit run app.py" 2>/dev/null || true

# Wait a moment for processes to stop
sleep 2

# Check if port 8501 is available
if lsof -i :8501 >/dev/null 2>&1; then
    echo "⚠️  Port 8501 is still in use. Trying alternative port..."
    streamlit run app.py --server.port 8502
else
    echo "✅ Starting Streamlit app on port 8501..."
    streamlit run app.py
fi
