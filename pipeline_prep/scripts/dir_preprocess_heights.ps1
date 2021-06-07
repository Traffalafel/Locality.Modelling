$raw_buildings_path = $args[0]
$heights_dir_path = $args[1]
$code_dir = ".."

$script_path = Join-Path $code_dir "preprocess_heights.py"

Get-ChildItem $raw_buildings_path -Filter "*.tif" | ForEach-Object {
    $file_name = $_.BaseName
    python $script_path $file_name $heights_dir_path
    echo $file_name
}