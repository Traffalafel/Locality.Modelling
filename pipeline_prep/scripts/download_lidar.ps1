if ($args.length -lt 3)
{
    Write-Output "Args: <tile_x> <tile_y> <destination_dir_path>"
    return
}

$tile_x = $args[0]
$tile_y = $args[1]
$destination_dir_path = $args[2]

$file_name_ftp = "PUNKTSKY_$($tile_y)_$($tile_x)_TIF_UTM32-ETRS89.zip"
$destination_file_name = "$($tile_x)_$($tile_y).zip"
$destination_file_path = Join-Path $destination_dir_path $destination_file_name

$url = "ftp://ftp.kortforsyningen.dk/dhm_danmarks_hoejdemodel/PUNKTSKY/$($file_name_ftp)"
$kortforsyningen_username = "thommib0b"
$kortforsyningen_password = "UY9vank@ount.joy"

Write-Output $url
 
$WebClient = New-Object System.Net.WebClient
$WebClient.Credentials = New-Object System.Net.Networkcredential($kortforsyningen_username, $kortforsyningen_password)
$WebClient.DownloadFile( $url, $destination_file_path )
