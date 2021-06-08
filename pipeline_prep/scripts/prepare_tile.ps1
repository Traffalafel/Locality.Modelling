$tile_x = $args[0]
$tile_y = $args[1]
$data_dir = $args[2]

conda activate modelling

$tmp_dir = Join-Path $data_dir "tmp"
$heights_dir = Join-Path $data_dir "heights"

function clear_directory($dir_path) {
    Get-ChildItem $dir_path | ForEach-Object {
        Remove-Item $_.FullName -Force -Recurse
    }
}

# Download terrain heights
clear_directory($tmp_dir)
& ./download_terrain.ps1 $tile_x $tile_y $tmp_dir
$terrain_heights_1x1_dir = Join-Path $heights_dir "terrain" "1x1"
$terrain_zip_file_path = Join-Path $tmp_dir "$($tile_x)_$($tile_y).zip"
Expand-Archive $terrain_zip_file_path $terrain_heights_1x1_dir
Remove-Item $terrain_zip_file_path
& ./clean_filenames.ps1 $terrain_heights_1x1_dir

# Download surface heights
clear_directory($tmp_dir)
& ./download_surface.ps1 $tile_x $tile_y $tmp_dir
$surface_heights_1x1_dir = Join-Path $heights_dir "surface" "1x1"
$surface_zip_file_path = Join-Path $tmp_dir "$($tile_x)_$($tile_y).zip"
Expand-Archive $surface_zip_file_path $surface_heights_1x1_dir
Remove-Item $surface_zip_file_path
& ./clean_filenames.ps1 $surface_heights_1x1_dir

# # Prepare masks
& ./prepare_masks.ps1 $tile_x $tile_y $data_dir

# Download lidar
clear_directory($tmp_dir)
& ./download_lidar.ps1 $tile_x $tile_y $tmp_dir
$lidar_zip_file_path = Join-Path $tmp_dir "$($tile_x)_$($tile_y).zip"
Expand-Archive $lidar_zip_file_path $tmp_dir
Remove-Item $lidar_zip_file_path
& ./clean_filenames.ps1 $tmp_dir

# Call laz2las and remove .laz files
& ./laz2las.ps1 $tmp_dir $tmp_dir
Get-ChildItem -Path $tmp_dir -Filter "*.laz" | ForEach-Object {
    Remove-Item $_.FullName -Force
}

# Prepare heights
& ./prepare_heights.ps1 $tmp_dir $heights_dir