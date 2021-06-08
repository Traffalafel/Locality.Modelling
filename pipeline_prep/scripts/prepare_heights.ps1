$lidar_dir = $args[0]
$heights_dir = $args[1]
$code_dir = "../"

# Generate heights
& ./dir_generate_heights.ps1 $lidar_dir $heights_dir

# Preprocess heights
& ./dir_preprocess_heights.ps1 $heights_dir

# Aggregate terrain
$heights_terrain_dir = Join-Path $heights_dir "terrain"
& ./dir_aggregate_heights.ps1 $heights_terrain_dir

# Aggregate surface
$heights_surface_dir = Join-Path $heights_dir "surface"
& ./dir_aggregate_heights.ps1 $heights_surface_dir

# Aggregate buildings
$heights_buildings_dir = Join-Path $heights_dir "buildings"
& ./dir_aggregate_heights.ps1 $heights_buildings_dir

# Aggregate trees
$heights_trees_dir = Join-Path $heights_dir "trees"
& ./dir_aggregate_heights.ps1 $heights_trees_dir
