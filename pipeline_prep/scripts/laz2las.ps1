$DIR_IN = $args[0]
$DIR_OUT = $args[1]

Get-ChildItem -Path $DIR_IN -Filter "*.laz" | ForEach-Object {
    
    $file_out = "$($_.BaseName).las"
    Write-Output $file_out

    $path_out = Join-Path -Path $DIR_OUT -ChildPath $file_out

    laszip64.exe -i $_.FullName -o $path_out
}