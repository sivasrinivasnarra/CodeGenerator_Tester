#!/bin/bash

echo "🛑 Stopping Streamlit app..."

# Stop any Streamlit processes
pkill -f "streamlit run app.py" 2>/dev/null || true

# Check if any processes are still running
if pgrep -f "streamlit run app.py" >/dev/null; then
    echo "⚠️  Some processes may still be running. You can force stop them with:"
    echo "   pkill -9 -f 'streamlit run app.py'"
else
    echo "✅ Streamlit app stopped successfully!"
fi
