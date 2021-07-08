if ($args.length -lt 3)
{
    Write-Output "Args: <block_x> <block_y> <destination_file_path>"
    return
}

$block_x = $args[0]
$block_y = $args[1]
$destination_file_path = $args[2]

$file_name_ftp = "DSM_$($block_y)_$($block_x)_TIF_UTM32-ETRS89.zip"

$url = "ftp://ftp.kortforsyningen.dk/dhm_danmarks_hoejdemodel/DSM/$($file_name_ftp)"
$kortforsyningen_username = "thommib0b"
$kortforsyningen_password = "UY9vank@ount.joy"

Write-Output $url
 
$WebClient = New-Object System.Net.WebClient
$WebClient.Credentials = New-Object System.Net.Networkcredential($kortforsyningen_username, $kortforsyningen_password)
$WebClient.DownloadFile( $url, $destination_file_path )
