$file_name = $args[0]

$Url = "ftp://ftp.kortforsyningen.dk/dhm_danmarks_hoejdemodel/PUNKTSKY/$file_name.zip"
$Path = "D:\tmp\lidar.zip"
$Username = "thommib0b"
$Password = "UY9vank@ount.joy"

Write-Output $Url
 
$WebClient = New-Object System.Net.WebClient
$WebClient.Credentials = New-Object System.Net.Networkcredential($Username, $Password)
$WebClient.DownloadFile( $url, $path )
