if ($args.length -lt 2)
{
    Write-Output "Args: <dir_in_path> <dir_out_path>"
    return
}


$dir_in_path = $args[0]
$dir_out_path = $args[1]
$code_dir = ".."

$script_path = Join-Path $code_dir "generate_heights.py"

Get-ChildItem $dir_in_path -Filter "*.las" | ForEach-Object {
    $file_in_path = $_.FullName
    python $script_path $file_in_path $dir_out_path
    echo $file_in_path
}