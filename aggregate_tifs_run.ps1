$input_dir = $args[0]
$output_dir = $args[1]

mkdir $output_dir -Force > $null

# Remove all .md5 files
$input_dir_all = Join-Path -Path $input_dir -ChildPath "*"
Remove-Item -Path $input_dir_all -Filter "*.md5"

Get-ChildItem $input_dir -Filter "*.tif" | ForEach-Object {

    $file_out_path = Join-Path -Path $output_dir -ChildPath $_.Name

    Write-Output "Processing file $($_.Name)"
    python aggregate_tifs.py $_.FullName $file_out_path

}