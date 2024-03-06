param (
    [string]$root
)
$userFiles = Join-Path -Path $root -ChildPath 'userFiles'

# Replace backslashes with forward slashes and remove the trailing slash
$root = $root -replace '\\', '/'
$root = $root.TrimEnd('/')
$userFiles = $userFiles -replace '\\', '/'
$userFiles = $userFiles.TrimEnd('/')

Write-Output "root: $root"
Write-Output "userFiles: $userFiles"

# Function that checks if the file exists in the root directory
function validateFileExists {
    param (
        [string]$fileName
        )
    Write-Output "Checking if the file $fileName exists in $userFiles ..."
    $fullPath = Join-Path -Path $userFiles -ChildPath $fileName
    if (-not (Test-Path $fullPath)) {
        Write-Error "The file $fileName does not exist in $userFiles. \nExiting..."
        exit
    }
}

# Function that unzips a .zip file into the destination directory
function Unzip {
    param (
        [string]$zipFile,
        [string]$destDir
    )
    
    $fullPathZip = Join-Path -Path $userFiles -ChildPath $zipFile
    $fullPathDest = Join-Path -Path $root -ChildPath $destDir
    Write-Output "Extracting $fullPathZip into $fullPathDest ..."

    # if (-not (Test-Path $fullPathDest)) {
    #     New-Item -ItemType Directory -Path $fullPathDest | Out-Null
    # }

    # Expand-Archive -Path $fullPathZip -DestinationPath $fullPathDest -Force
}

# Function that updates a file by replacing all occurrences of a string with another
function Update-File {
    param (
        [string]$file
    )
    Write-Output "Updating $file"
    $oldValue = "<YOUR ROOT>"
    $newValue = $root
    $fullPath = Join-Path -Path $userFiles -ChildPath $file
    (Get-Content $fullPath) -replace $oldValue, $newValue | Set-Content $fullPath
}

# Function that moves file from current working directory to destination folder
function Copy-File {
    param (
        [string]$file,
        [string]$destDir
    )
    $fullPathFile = Join-Path -Path $userFiles -ChildPath $file
    $fullPathDest = Join-Path -Path $root -ChildPath $destDir
    Write-Output "Copying $fullPathFile to $fullPathDest"

    if (-not (Test-Path $fullPathDest)) {
        Write-Output "Could not find directory, created one at $fullPathDest"
        New-Item -ItemType Directory -Path $fullPathDest | Out-Null
    }
    Copy-Item -Path $fullPathFile -Destination $fullPathDest -Force
}

# Main

# Check if the necessary files exist
validateFileExists "Data.zip"
validateFileExists "delftdashboard.ini"
validateFileExists "data_catalog.yml"
validateFileExists "mapbox_token.txt"
validateFileExists "census_key.txt"

# Unzip the data.zip file into the _internal/data directory
Unzip "$userFiles/Data.zip" "$root/_internal/data"

# Update paths
Update-File "data_catalog.yml" 
Update-File "delftdashboard.ini"

# Copy files
Copy-File "data_catalog.yml" "_internal/delftdashboard/config"
Copy-File "delftdashboard.ini" "_internal/delftdashboard/config"
Copy-File "mapbox_token.txt" "_internal/delftdashboard/config"
Copy-File "census_key.txt" "_internal/delftdashboard/config"

Write-Output "`nSetup complete!"
Write-Output "`n`nYou can now run the FloodAdapt_ModelBuilder.exe by double clicking on it.`n"