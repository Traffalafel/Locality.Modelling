function clear_directory($dir_path) {
    Get-ChildItem $dir_path | ForEach-Object {
        Remove-Item $_.FullName -Force -Recurse
    }
}