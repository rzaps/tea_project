$flags = "ru","gb","fr","de","es","it","pt","cn","tw","jp","kr","sa","tr"
$targetDir = "backend/static/flags"
New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
$baseUrl = "https://raw.githubusercontent.com/lipis/flag-icons/main/flags/4x3"

foreach ($code in $flags) {
    $url = "$baseUrl/$code.svg"
    $outFile = "$targetDir/$code.svg"
    Invoke-WebRequest -Uri $url -OutFile $outFile
} 