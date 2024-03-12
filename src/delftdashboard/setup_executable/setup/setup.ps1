param (
    [string]$root
)
$userFiles = Join-Path -Path $root -ChildPath 'userFiles'
$setupFiles = Join-Path -Path $root -ChildPath '_internal/_setup'
$ddbConfig = Join-Path -Path $root -ChildPath '_internal/delftdashboard/config'
$hydromt_fiat = Join-Path -Path $root -ChildPath '_internal/hydromt_fiat'

# Replace backslashes with forward slashes and remove the trailing slash
$root = $root -replace '\\', '/'
$root = $root.TrimEnd('/')

$userFiles = $userFiles -replace '\\', '/'
$userFiles = $userFiles.TrimEnd('/')

$setupFiles = $setupFiles -replace '\\', '/'
$setupFiles = $setupFiles.TrimEnd('/')

$ddbConfig = $ddbConfig -replace '\\', '/'
$ddbConfig = $ddbConfig.TrimEnd('/')

$hydromt_fiat = $hydromt_fiat -replace '\\', '/'
$hydromt_fiat = $hydromt_fiat.TrimEnd('/')

# Function that checks if the file exists in the root directory
function validateFileExists {
    param (
        [string]$fullFilePath
        )
        if (-not (Test-Path $fullFilePath)) {
            Write-Error "Could not find file: $fullFilePath. \nExiting..."
            exit
        }
        Write-Output "Found $fullFilePath ..."
}

# Function that unzips a .zip file into the destination directory
function Unzip {
    param (
        [string]$fullZipPath,
        [string]$fullDestPath
    )
    
    if (-not (Test-Path $fullDestPath)) {
        New-Item -ItemType Directory -Path $fullDestPath | Out-Null
    }
    
    Expand-Archive -Path $fullZipPath -DestinationPath $fullDestPath -Force
    Write-Output "Extracted $fullZipPath into $fullDestPath ..."
}

# Function that updates a file by replacing all occurrences of a string with another
function Update-File {
    param (
        [string]$fullFilePath
    )
    $oldValue = "<YOUR ROOT>"
    $newValue = $root
    (Get-Content $fullFilePath) -replace $oldValue, $newValue | Set-Content $fullFilePath
    Write-Output "Updated: $fullFilePath"
}

# Function that moves file from current working directory to destination folder
function Copy-File {
    param (
        [string]$fullSourcePath,
        [string]$fullDestPath
    )
    $destDirectory = Split-Path -Path $fullDestPath -Parent
    if (-not (Test-Path $destDirectory)) {
        New-Item -ItemType Directory -Path $destDirectory | Out-Null
    }

    Copy-Item -Path $fullSourcePath -Destination $fullDestPath -Force
    Write-Output "Copied $fullSourcePath to $fullDestPath"
}

# Main

# Check if the necessary files exist
validateFileExists "$userFiles/Data.zip"

# validateFileExists "$setupFiles/mapbox_token.txt"
# validateFileExists "$setupFiles/census_key.txt"
validateFileExists "$setupFiles/delftdashboard.ini"
validateFileExists "$setupFiles/data_catalog.yml"
validateFileExists "$setupFiles/Hazus_IWR_curves.csv"

# Unzip the data.zip file into the _internal/data directory
$dataPath = Join-Path -Path $root -ChildPath '_internal/data'
Unzip "$userFiles/Data.zip" $dataPath

# Copy files
Copy-File "$setupFiles/data_catalog.yml" "$ddbConfig/data_catalog.yml"
Copy-File "$setupFiles/delftdashboard.ini" "$ddbConfig/delftdashboard.ini"

Copy-File "$setupFiles/Hazus_IWR_curves.csv" "$hydromt_fiat/data/damage_functions/flooding/Hazus_IWR_curves.csv"

# Copy-File "$setupFiles/mapbox_token.txt" "$ddbConfig/mapbox_token.txt"
# Copy-File "$setupFiles/census_key.txt" "$ddbConfig/census_key.txt"

# Update paths
Update-File "$ddbConfig/data_catalog.yml"
Update-File "$ddbConfig/delftdashboard.ini"

Write-Output "`nSetup complete!"
Write-Output "`n`nYou can now run the FloodAdapt_ModelBuilder.exe by double clicking on it.`n"