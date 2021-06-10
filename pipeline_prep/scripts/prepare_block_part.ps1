# Prepares a given list of tiles in a given block

if ($args.length -lt 3) {
    Write-Output "Usage: <block_id> <tiles_ids> <data_dir>"
    return
}

$block_id = $args[0]
$tiles_ids = $args[1]
$data_dir = $args[2]

conda activate modelling

$tmp_dir = Join-Path $data_dir "tmp"
$heights_dir = Join-Path $data_dir "heights"
$masks_dir = Join-Path $data_dir "masks"

$block_x = $block_id.Split("_")[0]
$block_y = $block_id.Split("_")[1]

$tiles_ids | ForEach-Object {
    $x = $_.Split("_")[0]
    $y = $_.Split("_")[1]
}