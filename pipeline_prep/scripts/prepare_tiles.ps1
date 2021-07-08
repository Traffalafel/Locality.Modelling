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

if (-not (Test-Path $data_dir)) {
    Write-Output "Could not find data directory $($data_dir)"
    Write-Output "Please plug in your external drive"
    return
}

$tmp_dir = Join-Path $data_dir "tmp"
$download_dir = Join-Path $data_dir "download"
$heights_dir = Join-Path $data_dir "heights"
$lidar_dir = Join-Path $data_dir "lidar"

$block_x, $block_y = $block_id.Split("_")

# Download terrain heights
$terrain_download_file_path = Join-Path $download_dir "terrain" "$($block_x)_$($block_y).zip"
if (-not (Test-Path $terrain_download_file_path)) {
    & ./download_terrain.ps1 $block_x $block_y $terrain_download_file_path
}
$terrain_heights_1x1_dir = Join-Path $heights_dir "terrain" "1x1"
Expand-Archive $terrain_download_file_path $terrain_heights_1x1_dir -Force
& ./clean_filenames.ps1 $terrain_heights_1x1_dir

# Download surface heights
$surface_download_file_path = Join-Path $download_dir "surface" "$($block_x)_$($block_y).zip"
if (-not (Test-Path $surface_download_file_path)) {
    & ./download_surface.ps1 $block_x $block_y $surface_download_file_path
}
$surface_heights_1x1_dir = Join-Path $heights_dir "surface" "1x1"
Expand-Archive $surface_download_file_path $surface_heights_1x1_dir -Force
& ./clean_filenames.ps1 $surface_heights_1x1_dir

clear_directory($tmp_dir)

# Prepare water masks
Write-Output "Water"
$script_split_tile_path = Join-Path $code_dir "datasets" "block_to_tiles.py"
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
$lidar_download_file_path = Join-Path $download_dir "lidar" "$($block_x)_$($block_y).zip"
if (-not (Test-Path $lidar_download_file_path)) {
    Write-Output "Downloading lidar data into ""$($lidar_download_file_path)"""
    & ./download_lidar.ps1 $block_x $block_y $lidar_download_file_path
}
Expand-Archive $lidar_download_file_path $tmp_dir
& ./clean_filenames.ps1 $tmp_dir

# Use laszip and remove .laz files
$tiles_ids | ForEach-Object {
    $path_in = Join-Path -Path $tmp_dir -ChildPath "$($_).laz"
    $path_out = Join-Path -Path $lidar_dir -ChildPath "$($_).las"
    $exists = Test-Path $path_in
    if (-not $exists) {
        Write-Output "Could not find $($_).las"
        return
    }
    laszip64.exe -i $path_in -o $path_out
    Write-Output "laszip $($_)"
}
Get-ChildItem -Path $tmp_dir -Filter "*.laz" | ForEach-Object {
    Remove-Item $_.FullName -Force
}

# Generate heights
$script_generate_path = Join-Path $code_dir "heights" "generate_heights.py"
$tiles_ids | ForEach-Object {
    $file_in_path = Join-Path $lidar_dir "$($_).las"
    python $script_generate_path $file_in_path $heights_dir
    Write-Output "Generated $($_)"
}

# Preprocess heights
$script_preprocess_path = Join-Path $code_dir "heights" "preprocess_heights.py"
$tiles_ids | ForEach-Object {
    python $script_preprocess_path $_ $heights_dir
    Write-Output "Processed $($_)"
}

# Aggregate terrain
Write-Output "Aggregating terrain"
$script_aggregate_path = Join-Path $code_dir "heights" "aggregate_heights.py"
$terrain_heights_path = Join-Path $heights_dir "terrain"
$tiles_ids | ForEach-Object {
    python $script_aggregate_path $_ $terrain_heights_path
    Write-Output "Aggregated $($_)"
}

# Aggregate surface
Write-Output "Aggregating surface"
$script_aggregate_path = Join-Path $code_dir "heights" "aggregate_heights.py"
$surface_heights_path = Join-Path $heights_dir "surface"
$tiles_ids | ForEach-Object {
    python $script_aggregate_path $_ $surface_heights_path
    Write-Output "Aggregated $($_)"
}

# Aggregate buildings
Write-Output "Aggregating buildings"
$script_aggregate_path = Join-Path $code_dir "heights" "aggregate_heights.py"
$buildings_heights_path = Join-Path $heights_dir "buildings"
$tiles_ids | ForEach-Object {
    python $script_aggregate_path $_ $buildings_heights_path
    Write-Output "Aggregated $($_)"
}

# Aggregate trees
Write-Output "Aggregating trees"
$script_aggregate_path = Join-Path $code_dir "heights" "aggregate_heights.py"
$trees_heights_path = Join-Path $heights_dir "trees"
$tiles_ids | ForEach-Object {
    python $script_aggregate_path $_ $trees_heights_path
    Write-Output "Aggregated $($_)"
}

clear_directory($tmp_dir)