$heights_dir_path = $args[0]
$code_dir = ".."

$script_path = Join-Path $code_dir "heights" "preprocess_heights.py"
$heights_terrain_path = Join-Path $heights_dir_path "terrain" "1x1"
$heights_buildings_path = Join-Path $heights_dir_path "buildings" "1x1"
$heights_trees_path = Join-Path $heights_dir_path "trees" "1x1"

Get-ChildItem $heights_terrain_path -Filter "*.tif" | ForEach-Object {
    $file_name = $_.BaseName
    $file_name_tif = $file_name + ".tif"

    $file_path_buildings = Join-Path $heights_buildings_path $file_name_tif
    $file_path_trees = Join-Path $heights_trees_path $file_name_tif
    
    $buildings_exist = Test-Path $file_path_buildings
    $trees_exist = Test-Path $file_path_trees
    if ($buildings_exist -or $trees_exist)
    {
        echo "Skipping $($file_name)"
        return
    }

    python $script_path $file_name $heights_dir_path
    echo "Processed $($file_name)"
}