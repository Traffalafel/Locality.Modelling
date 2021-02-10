$path_in = $args[0]
$path_out = $args[1]

gdal_translate -of AAIGrid $path_in $path_out