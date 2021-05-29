$tile_x = $args[0]
$tile_y = $args[1]
$data_dir = $args[2]

$tmp_dir = Join-Path $data_dir "tmp"

function clear_directory($dir_path) {
    Get-ChildItem $dir_path | ForEach-Object {
        Remove-Item $_.FullName -Force
    }
}

clear_directory($tmp_dir)
download_terrain.ps1 $tile_x $tile_y $tmp_dir