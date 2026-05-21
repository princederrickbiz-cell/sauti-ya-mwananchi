# Sauti ya Mwananchi - ngrok Quick Setup Script
# This script helps you expose your local server to the internet via ngrok
# Usage: .\setup-ngrok.ps1

param(
    [string]$Port = "8000",
    [switch]$Download = $false
)

$ErrorActionPreference = "Stop"

# Colors for output
function Write-Header {
    param([string]$Text)
    Write-Host "`n" -ForegroundColor Green
    Write-Host "=" * 60 -ForegroundColor Green
    Write-Host $Text -ForegroundColor Green
    Write-Host "=" * 60 -ForegroundColor Green
}

function Write-Info {
    param([string]$Text)
    Write-Host "ℹ️  $Text" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Text)
    Write-Host "✅ $Text" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Text)
    Write-Host "⚠️  $Text" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param([string]$Text)
    Write-Host "❌ $Text" -ForegroundColor Red
}

Write-Header "SAUTI YA MWANANCHI - NGROK SETUP"

# Step 1: Check if ngrok is installed
Write-Info "Step 1: Checking for ngrok installation..."

$ngrokPath = $null
$ngrokVersion = $null

# Check if ngrok is in PATH
try {
    $ngrokVersion = ngrok version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "ngrok is already installed"
        Write-Info "Version: $($ngrokVersion.Split([Environment]::NewLine)[0])"
        $ngrokPath = "ngrok"
    }
} catch {
    Write-Info "ngrok not found in PATH"
}

# If not found, check in common locations
if (-not $ngrokPath) {
    $commonPaths = @(
        "$env:USERPROFILE\Downloads\ngrok.exe",
        "$env:USERPROFILE\ngrok\ngrok.exe",
        "C:\Program Files\ngrok\ngrok.exe",
        "$PSScriptRoot\ngrok.exe"
    )

    foreach ($path in $commonPaths) {
        if (Test-Path $path) {
            Write-Success "Found ngrok at: $path"
            $ngrokPath = $path
            break
        }
    }
}

# Step 2: Download ngrok if needed
if (-not $ngrokPath) {
    Write-Warning "ngrok is not installed"
    Write-Info "Do you want to download ngrok? (Y/N)"
    
    if ($Download -or ((Read-Host).ToLower() -eq "y")) {
        Write-Info "Downloading ngrok..."
        
        $downloadUrl = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
        $downloadPath = "$env:TEMP\ngrok.zip"
        $extractPath = "$env:USERPROFILE\ngrok"

        try {
            # Download
            Write-Info "Downloading from: $downloadUrl"
            Invoke-WebRequest -Uri $downloadUrl -OutFile $downloadPath -UseBasicParsing
            Write-Success "Downloaded ngrok"

            # Extract
            Write-Info "Extracting ngrok..."
            if (Test-Path $extractPath) {
                Remove-Item -Path $extractPath -Recurse -Force
            }
            New-Item -ItemType Directory -Path $extractPath -Force | Out-Null
            Expand-Archive -Path $downloadPath -DestinationPath $extractPath
            Write-Success "Extracted ngrok to: $extractPath"

            # Set ngrok path
            $ngrokPath = "$extractPath\ngrok.exe"

            # Add to PATH temporarily
            $env:PATH = "$extractPath;$env:PATH"
            Write-Success "ngrok added to PATH for this session"

            # Cleanup
            Remove-Item -Path $downloadPath -Force
            Write-Info "For permanent PATH setup, add ngrok directory to Windows Environment Variables"
        }
        catch {
            Write-Error-Custom "Failed to download ngrok: $_"
            Write-Info "Manual download: $downloadUrl"
            exit 1
        }
    }
    else {
        Write-Error-Custom "ngrok is required. Please install it manually:"
        Write-Info "1. Download: https://ngrok.com/download"
        Write-Info "2. Extract to: $env:USERPROFILE\ngrok"
        Write-Info "3. Then run this script again"
        exit 1
    }
}

# Step 3: Check if server is running
Write-Info "Step 2: Checking if Sauti ya Mwananchi server is running on port $Port..."

try {
    $response = Invoke-WebRequest -Uri "http://localhost:$Port/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
    Write-Success "Server is running on http://localhost:$Port"
} catch {
    Write-Warning "Server does not appear to be running on port $Port"
    Write-Info "You can start it with: python main.py"
    Read-Host "Press Enter to continue anyway (or Ctrl+C to cancel)"
}

# Step 4: Check if ngrok auth token is set
Write-Info "Step 3: Checking ngrok authentication..."

try {
    & $ngrokPath config check 2>&1 | Out-Null
    Write-Success "ngrok is authenticated"
} catch {
    Write-Warning "ngrok may not be authenticated"
    Write-Info "To authenticate ngrok:"
    Write-Info "1. Go to: https://dashboard.ngrok.com/auth/your-authtoken"
    Write-Info "2. Copy your auth token"
    Write-Info "3. Run: ngrok config add-authtoken YOUR_TOKEN"
    Read-Host "Press Enter to continue"
}

# Step 5: Start ngrok
Write-Header "STARTING NGROK"

Write-Info "Starting ngrok tunnel on port $Port..."
Write-Info ""
Write-Info "You should see ngrok output below. Once it shows a public URL, you're ready!"
Write-Info "Next steps:"
Write-Info "1. Copy the forwarding URL (something like https://xxxx-xx-xxx-xxx.ngrok.io)"
Write-Info "2. Go to Africa's Talking dashboard: https://africastalking.com/"
Write-Info "3. Configure webhook: https://your-ngrok-url/africastalking/sms"
Write-Info "4. Send a WhatsApp message to test!"
Write-Info ""
Write-Info "Keep this window open while testing. Press Ctrl+C to stop."
Write-Info ""

# Start ngrok
& $ngrokPath http $Port --region=auto

# If ngrok exits, show the message
Write-Warning "ngrok has stopped. Your tunnel is now closed."
Read-Host "Press Enter to exit"
