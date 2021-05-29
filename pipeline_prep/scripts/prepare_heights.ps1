$lidar_dir = $args[0]
$heights_dir = $args[1]
$code_dir = "../"

$script_generate_heights = Join-Path $code_dir "heights" "generate_heights.py"
$script_preprocess_heights = Join-Path $code_dir "heights" "preprocess_heights.py"
$script_aggregate_heights = Join-Path $code_dir "heights" "aggregate_heights.py"

python $script_generate_heights $lidar_dir $heights_dir
python $script_preprocess_heights $heights_dir
python $script_generate_heights $heights_dir