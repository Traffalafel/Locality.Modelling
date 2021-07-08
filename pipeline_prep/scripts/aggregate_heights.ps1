if ($args.length -lt 1)
{
    Write-Output "Args: <dir_path>"
    return
}

$dir_path = $args[0]
$code_dir = ".."

$script_path = Join-Path $code_dir "heights" "aggregate_heights.py"

$1x1_heights_path = Join-Path $dir_path "1x1"
Write-Output $1x1_heights_path

Get-ChildItem $1x1_heights_path -Filter "*.tif" | ForEach-Object {
    $file_name = $_.BaseName
    python $script_path $file_name $dir_path
    Write-Output "Aggregated $($file_name)"
}