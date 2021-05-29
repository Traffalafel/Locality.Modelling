$tile_x = $args[0]
$tile_y = $args[1]
$data_dir = $args[2]
$code_dir = "..\"

$file_name = "$($tile_x)_$($tile_y)"

$tmp_data_dir = Join-Path $data_dir "tmp"

function clear_directory($dir_path) {
    Get-ChildItem $dir_path | ForEach-Object {
        Remove-Item $_.FullName -Force
    }
}

clear_directory($tmp_data_dir)

$script_split_tile_path = Join-Path $code_dir "datasets" "split_tile.py"

Write-Output "Water"
# Split
$data_water_input_dir = Join-Path $data_dir "datasets" "OSM_water" "10x10" "$($file_name).shp"
python $script_split_tile_path $data_water_input_dir $tmp_data_dir
# Generate masks
$script_masks_water_path = Join-Path $code_dir "masks" "masks_water.py"
$data_water_masks_dir = Join-Path $data_dir "masks" "water"
python $script_masks_water_path $tmp_data_dir $data_water_masks_dir

clear_directory($tmp_data_dir)

Write-Output "Buildings"
# Split
$data_buildings_input_path = Join-Path $data_dir "datasets" "GeoDanmark_buildings" "10x10" "$($file_name).shp"
python $script_split_tile_path $data_buildings_input_path $tmp_data_dir 0 Polygon
# Generate masks
$script_masks_buildings_path = Join-Path $code_dir "masks" "masks_buildings.py"
$data_buildings_masks_dir = Join-Path $data_dir "masks" "buildings"
python $script_masks_buildings_path $tmp_data_dir $data_buildings_masks_dir

clear_directory($tmp_data_dir)

Write-Output "Roads"
# Split
$data_roads_input_path = Join-Path $data_dir "datasets" "OSM_roads" "10x10" "$($file_name).shp"
python $script_split_tile_path $data_roads_input_path $tmp_data_dir
# Generate masks
$script_masks_roads_path = Join-Path $code_dir "masks" "masks_roads.py"
$data_roads_masks_dir = Join-Path $data_dir "masks" "roads"
python $script_masks_roads_path $tmp_data_dir $data_roads_masks_dir

clear_directory($tmp_data_dir)

Write-Output "Green"
# Split
$data_landuse_input_path = Join-Path $data_dir "datasets" "OSM_landuse" "10x10" "$($file_name).shp"
python $script_split_tile_path $data_landuse_input_path $tmp_data_dir
# Generate masks
$script_masks_green_path = Join-Path $code_dir "masks" "masks_green.py"
$data_green_masks_dir = Join-Path $data_dir "masks" "green"
python $script_masks_green_path $tmp_data_dir $data_green_masks_dir

clear_directory($tmp_data_dir)