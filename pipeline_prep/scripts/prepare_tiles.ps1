# Prepares a given list of tiles in a given block

. ./clear_directory.ps1

if ($args.length -lt 2) {
    Write-Output "Usage: <block_id> <tiles_ids>"
    return
}

$block_id = $args[0]
$tiles_ids = $args[1]

conda activate modelling

$data_dir = "D:\data"
$code_dir = ".."

$tmp_dir = Join-Path $data_dir "tmp"
$heights_dir = Join-Path $data_dir "heights"

$block_x, $block_y = $block_id.Split("_")

# # Download terrain heights
# clear_directory($tmp_dir)
# & ./download_terrain.ps1 $block_x $block_y $tmp_dir
# $terrain_heights_1x1_dir = Join-Path $heights_dir "terrain" "1x1"
# $terrain_zip_file_path = Join-Path $tmp_dir "$($block_x)_$($block_y).zip"
# Expand-Archive $terrain_zip_file_path $terrain_heights_1x1_dir -Force
# Remove-Item $terrain_zip_file_path
# & ./clean_filenames.ps1 $terrain_heights_1x1_dir

# # Download surface heights
# clear_directory($tmp_dir)
# & ./download_surface.ps1 $block_x $block_y $tmp_dir
# $surface_heights_1x1_dir = Join-Path $heights_dir "surface" "1x1"
# $surface_zip_file_path = Join-Path $tmp_dir "$($block_x)_$($block_y).zip"
# Expand-Archive $surface_zip_file_path $surface_heights_1x1_dir -Force
# Remove-Item $surface_zip_file_path
# & ./clean_filenames.ps1 $surface_heights_1x1_dir

clear_directory($tmp_dir)

# Prepare water masks
Write-Output "Water"
$script_split_tile_path = Join-Path $code_dir "datasets" "split_tile.py"
$data_water_input_file = Join-Path $data_dir "datasets" "OSM_water" "10x10" "$($block_id).shp"
python $script_split_tile_path $data_water_input_file $tmp_dir
$script_masks_water_path = Join-Path $code_dir "masks" "masks_water.py"
$data_water_masks_dir = Join-Path $data_dir "masks" "water"
$tiles_ids | ForEach-Object {
    $file_in_path = Join-Path $tmp_dir "$($_).shp"
    if (-not (Test-Path $file_in_path)) {
        return
    }
    python $script_masks_water_path $file_in_path $data_water_masks_dir
}

clear_directory($tmp_dir)

# Prepare buildings mask
Write-Output "Buildings"
$data_buildings_input_path = Join-Path $data_dir "datasets" "GeoDanmark_buildings" "10x10" "$($block_id).shp"
python $script_split_tile_path $data_buildings_input_path $tmp_dir 0 Polygon
$script_masks_buildings_path = Join-Path $code_dir "masks" "masks_buildings.py"
$data_buildings_masks_dir = Join-Path $data_dir "masks" "buildings"
$tiles_ids | ForEach-Object {
    $file_in_path = Join-Path $tmp_dir "$($_).shp"
    if (-not (Test-Path $file_in_path)) {
        return
    }
    python $script_masks_buildings_path $file_in_path $data_buildings_masks_dir
}

clear_directory($tmp_dir)

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

clear_directory($tmp_dir)

# Prepare green mask
Write-Output "Green"
$data_landuse_input_path = Join-Path $data_dir "datasets" "OSM_landuse" "10x10" "$($block_id).shp"
python $script_split_tile_path $data_landuse_input_path $tmp_dir
$script_masks_green_path = Join-Path $code_dir "masks" "masks_green.py"
$data_green_masks_dir = Join-Path $data_dir "masks" "green"
$tiles_ids | ForEach-Object {
    $file_in_path = Join-Path $tmp_dir "$($_).shp"
    if (-not (Test-Path $file_in_path)) {
        return
    }
    python $script_masks_green_path $file_in_path $data_green_masks_dir
}

# Download lidar
clear_directory($tmp_dir)
& ./download_lidar.ps1 $block_x $block_y $tmp_dir
$lidar_zip_file_path = Join-Path $tmp_dir "$($block_x)_$($block_y).zip"
Expand-Archive $lidar_zip_file_path $tmp_dir
Remove-Item $lidar_zip_file_path
& ./clean_filenames.ps1 $tmp_dir

# Use laszip and remove .laz files
$tiles_ids | ForEach-Object {
    $path_in = Join-Path -Path $tmp_dir -ChildPath "$($_).laz"
    $path_out = Join-Path -Path $tmp_dir -ChildPath "$($_).las"
    laszip64.exe -i $path_in -o $path_out
    Write-Output "laszip $($_)"
}
Get-ChildItem -Path $tmp_dir -Filter "*.laz" | ForEach-Object {
    Remove-Item $_.FullName -Force
}

# # Generate heights
# $script_generate_path = Join-Path $code_dir "generate_heights.py"
# $tiles_ids | ForEach-Object {
#     $file_in_path = "$($_).las"
#     python $script_generate_path $file_in_path $heights_dir
#     Write-Output "Generated $($_.BaseName)"
# }

# # Preprocess heights
# $script_preprocess_path = Join-Path $code_dir "heights" "preprocess_heights.py"
# $heights_terrain_path = Join-Path $heights_dir "terrain" "1x1"
# Get-ChildItem $heights_terrain_path -Filter "*.tif" | ForEach-Object {
#     $file_name = $_.BaseName
#     $file_name_tif = $file_name + ".tif"

#     $file_path_buildings = Join-Path $heights_dir "buildings" "1x1" $file_name_tif
#     $file_path_trees = Join-Path $heights_dir "trees" "1x1" $file_name_tif
#     $buildings_exist = Test-Path $file_path_buildings
#     $trees_exist = Test-Path $file_path_trees
#     if ($buildings_exist -or $trees_exist)
#     {
#         return
#     }

#     python $script_preprocess_path $file_name $heights_dir
#     Write-Output "Processed $($file_name)"
# }

# # Aggregate terrain
# $heights_terrain_dir = Join-Path $heights_dir "terrain"
# & ./aggregate_heights.ps1 $heights_terrain_dir

# # Aggregate surface
# $heights_surface_dir = Join-Path $heights_dir "surface"
# & ./aggregate_heights.ps1 $heights_surface_dir

# # Aggregate buildings
# $heights_buildings_dir = Join-Path $heights_dir "buildings"
# & ./aggregate_heights.ps1 $heights_buildings_dir

# # Aggregate trees
# $heights_trees_dir = Join-Path $heights_dir "trees"
# & ./aggregate_heights.ps1 $heights_trees_dir

# clear_directory($tmp_dir)