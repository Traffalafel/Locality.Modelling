$dir = $args[0]

$checksums = Join-Path -Path $dir -ChildPath "*.md5"
Remove-Item $checksums

Get-ChildItem -Path $dir | ForEach-Object {

    $pattern = "\w+_1km_(\d+)_(\d+)"

    if ($_.BaseName -match $pattern)
    {
        $return = Select-String -InputObject $_.BaseName -Pattern $pattern
        $y = $return.Matches.groups[1]
        $x = $return.Matches.groups[2]
        Rename-Item -Path $_.FullName -NewName "$($x)_$($y)$($_.Extension)" -Force > $null
    }

}