$input_dir = $args[0]
$output_dir = $args[1]
$tmp_dir = $args[2]

# Create output and temporary directories
mkdir $output_dir -Force > $null
mkdir $tmp_dir -Force > $null

Get-ChildItem -Path $input_dir -Filter "*.zip" | ForEach-Object {
    
    Write-Output "Copying file $($_.Name)"
    $tmp_zip_file = Join-Path -Path $tmp_dir -ChildPath $_.Name
    Copy-Item -Path $_.FullName -Destination $tmp_zip_file
    
    Write-Output "Unzipping file $($_.Name)"
    Expand-Archive -Path $_.FullName -DestinationPath $tmp_dir -Force

    # Remove all .md5 files
    $tmp_dir_all = Join-Path -Path $tmp_dir -ChildPath "*"
    Remove-Item -Path $tmp_dir_all -Filter "*.md5"
    
    Get-ChildItem $tmp_dir -Filter "*.tif" | ForEach-Object {

        Write-Output "Converting $($_.Name) to ASC"
        $asc_file_path = Join-Path -Path $tmp_dir -ChildPath "$($_.BaseName).asc"
        gdal_translate -of AAIGrid $_.FullName $asc_file_path > $null
    
        Write-Output "Computing heights from $($asc_file_path)"
        $bin_file_path = Join-Path -Path $output_dir -ChildPath "$($_.BaseName).bin"
        python .\preprocess_asc.py $asc_file_path $bin_file_path

        $tmp_dir_asc = Join-Path $tmp_dir -ChildPath "*.asc"
        Remove-Item $tmp_dir_asc -Force
    }
    
    Join-Path -Path $tmp_dir -ChildPath "*" | Remove-Item -Force
}