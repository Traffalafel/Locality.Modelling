$dir_path = $args[0]

Get-Childitem $dir_path -Filter "*.md5"
| Foreach-Object {
    Remove-Item $_.FullName
}