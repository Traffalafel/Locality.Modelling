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

        $new_path = Join-Path $dir "$($x)_$($y)$($_.Extension)"
        $already_exists = Test-Path $new_path
        if (-not $already_exists)
        {
            Rename-Item -Path $_.FullName -NewName "$($x)_$($y)$($_.Extension)" > $null
        }
        else
        {
            Remove-Item $_.FullName
        }
    }

}