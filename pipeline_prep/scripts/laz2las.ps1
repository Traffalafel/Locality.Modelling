$dir_in_path = $args[0]
$dir_out_path = $args[1]

Get-ChildItem -Path $dir_in_path -Filter "*.laz" | ForEach-Object {
    
    $file_out = "$($_.BaseName).las"
    Write-Output $file_out

    $path_out = Join-Path -Path $dir_out_path -ChildPath $file_out

    laszip64.exe -i $_.FullName -o $path_out
}