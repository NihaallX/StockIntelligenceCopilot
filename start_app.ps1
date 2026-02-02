Write-Host "Starting Stock Intelligence Copilot..."

# Start Backend (Port 8000)
Write-Host "Launching Backend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'd:\Stock Intelligence Copilot\backend'; uvicorn app.main:app --reload"

# Start Frontend (Port 3001)
Write-Host "Launching Frontend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'd:\Stock Intelligence Copilot\frontend'; npm run dev"

Write-Host "Servers started!"
Write-Host "Backend: http://localhost:8000/docs"
Write-Host "Frontend: http://localhost:3001"
