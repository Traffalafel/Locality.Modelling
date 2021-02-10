$zip_dir = $args[0]
$out_dir = $args[1]

Get-ChildItem -Path $zip_dir -Filter "*.zip" | ForEach-Object {
    Write-Output "Unzipping file $($_.Name)"
    Expand-Archive -Path $_.FullName -DestinationPath $out_dir -Force
}
