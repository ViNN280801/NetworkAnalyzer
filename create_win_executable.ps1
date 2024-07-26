# Function to get the installed Python version
function Get-PythonVersion {
    $pythonVersion = & python --version 2>&1
    if ($pythonVersion -match "Python (\d+\.\d+)") {
        return $matches[1]
    }
    else {
        Write-Output "Python is not installed or not added to the PATH."
        exit 1
    }
}

# Check if pyinstaller is installed, if not, install it
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Output "Installing PyInstaller..."
    pip install pyinstaller
}

# Get the Python version
$pythonVersion = Get-PythonVersion

# Add the Scripts directory to PATH temporarily
$env:PATH += ";$($env:USERPROFILE)\AppData\Roaming\Python\Python$($pythonVersion.Replace('.', ''))\Scripts"

# Remove dist, build directories file if they exist
if (Test-Path "dist") {
    Remove-Item "dist" -Recurse -Force
}
if (Test-Path "build") {
    Remove-Item "build" -Recurse -Force
}

# Create the executable using pyinstaller
Write-Output "Building na-cli.exe..."
pyinstaller .\na-cli.spec

# Move the executable to the desired directory (if necessary)
if (Test-Path "dist\na-cli.exe") {
    Write-Output "Moving na-cli.exe to the current directory..."
    Move-Item "dist\na-cli.exe" "." -Force
    Write-Output "Build completed successfully."
}
else {
    Write-Output "Build failed."
}

Write-Output "Note: This script was tested on Python 3.12."
