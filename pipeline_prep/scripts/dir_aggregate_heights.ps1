if ($args.length -lt 1)
{
    Write-Output "Args: <dir_path>"
    return
}

$dir_path = $args[0]
$code_dir = ".."

$script_path = Join-Path $code_dir "heights" "aggregate_heights.py"

$1x1_heights_path = Join-Path $dir_path "1x1"
echo $1x1_heights_path

Get-ChildItem $1x1_heights_path -Filter "*.tif" | ForEach-Object {
    $file_name = $_.BaseName
    $file_name_tif = $file_name + ".tif"

    $file_out_path = Join-Path $dir_path "2x2" $file_name_tif
    $already_exists = Test-Path $file_out_path
    if ($already_exists)
    {
        echo "Skiping $($file_name)"
        return
    }

    python $script_path $file_name $dir_path
    echo "Aggregated $($file_name)"
}