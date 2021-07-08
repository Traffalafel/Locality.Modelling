$block_id = $args[0]
$tiles_ids = $args[1]

conda activate modelling

$data_dir = "D:\data"
$code_dir = ".."

$script_split_tile_path = Join-Path $code_dir "datasets" "block_to_tiles.py"

if (-not (Test-Path $data_dir)) {
    Write-Output "Could not find data directory $($data_dir)"
    Write-Output "Please plug in your external drive"
    return
}

$tmp_dir = Join-Path $data_dir "tmp"

# Prepare roads mask
Write-Output "Roads"
$data_roads_input_path = Join-Path $data_dir "datasets" "OSM_roads" "10x10" "$($block_id).shp"
python $script_split_tile_path $data_roads_input_path $tmp_dir
$script_masks_roads_path = Join-Path $code_dir "masks" "masks_roads.py"
$data_roads_masks_dir = Join-Path $data_dir "masks" "roads"
$tiles_ids | ForEach-Object {
    $file_in_path = Join-Path $tmp_dir "$($_).shp"
    if (-not (Test-Path $file_in_path)) {
        return
    }
    python $script_masks_roads_path $file_in_path $data_roads_masks_dir
}