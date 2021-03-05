$DIR_IN = $args[0]
$DIR_OUT = $args[1]

Get-ChildItem -Path $DIR_IN -Filter "*.laz" | ForEach-Object {
    
    $file_out = $_.BaseName -replace "PUNKTSKY_1km_"
    $items = $file_out.Split("_")
    $file_out = "$($items[1])_$($items[0]).las"
    Write-Output $file_out

    $path_out = Join-Path -Path $DIR_OUT -ChildPath $file_out

    laszip64.exe -i $_.FullName -o $path_out
}