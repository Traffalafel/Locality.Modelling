$clip_file_path = ".\clip.py"
$file_in_path = ".\models\Bergamo_prepped.obj"
$dir_out_path = ".\models\bergamo_grid"



for ($i = 0; $i -lt 10; $i++)
{
    for ($j = 0; $j -lt 10; $j++)
    {
        $north = ($j + 1) * 1000
        $south = ($j) * 1000
        $east = ($i + 1) * 1000
        $west = ($i) * 1000
        $file_out_name = "bergamo_${west}_${south}.obj"
        $file_out_path = Join-Path -Path $dir_out_path -ChildPath $file_out_name
        
        Write-Output $file_out_name
        python $clip_file_path $file_in_path $north $west $south $east > $file_out_path
    }
}