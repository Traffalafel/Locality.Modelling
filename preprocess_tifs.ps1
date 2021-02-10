$input_dir = $args[0]
$output_dir = $args[1]

mkdir $output_dir -Force > $null

# Remove all .md5 files
$input_dir_all = Join-Path -Path $input_dir -ChildPath "*"
Remove-Item -Path $input_dir_all -Filter "*.md5"

$tmp_dir_path = Join-Path -Path $output_dir -ChildPath "tmp"
mkdir $tmp_dir_path -Force > $null

Get-ChildItem $input_dir -Filter "*.tif" | ForEach-Object {

    Write-Output "Processing file $($_.BaseName).tif"
    $asc_file_path = Join-Path -Path $tmp_dir_path -ChildPath "$($_.BaseName).asc"
    gdal_translate -of AAIGrid $_.FullName $asc_file_path > $null

    $bin_file_path = Join-Path -Path $output_dir -ChildPath "$($_.BaseName).bin"
    python .\preprocess_asc.py $asc_file_path $bin_file_path

    Join-Path -Path $tmp_dir_path -ChildPath "*" | Remove-Item

}

Remove-Item $tmp_dir_path