# Modified from https://github.com/StephLin/click-pwsh/blob/main/click_pwsh/shell_completion.py#L11
Register-ArgumentCompleter -Native -CommandName pros -ScriptBlock {
  param($wordToComplete, $commandAst, $cursorPosition)
  $env:COMP_WORDS = $commandAst
  $env:COMP_WORDS = $env:COMP_WORDS.replace('\\', '/')
  $incompleteCommand = $commandAst.ToString()
  $myCursorPosition = $cursorPosition
  if ($myCursorPosition -gt $incompleteCommand.Length) {
    $myCursorPosition = $incompleteCommand.Length
  }
  $env:COMP_CWORD = @($incompleteCommand.substring(0, $myCursorPosition).Split(" ") | Where-Object { $_ -ne "" }).Length
  if ( $wordToComplete.Length -gt 0) { $env:COMP_CWORD -= 1 }
  $env:_PROS_COMPLETE = "powershell_complete"
  pros | ForEach-Object {
    $type, $value, $help = $_.Split(",", 3)
    if ( ($type -eq "plain") -and ![string]::IsNullOrEmpty($value) ) {
      [System.Management.Automation.CompletionResult]::new($value, $value, "ParameterValue", $value)
    }
    elseif ( ($type -eq "file") -or ($type -eq "dir") ) {
      if ([string]::IsNullOrEmpty($wordToComplete)) {
        $dir = "./"
      }
      else {
        $dir = $wordToComplete.replace('\\', '/')
      }
      if ( (Test-Path -Path $dir) -and ((Get-Item $dir) -is [System.IO.DirectoryInfo]) ) {
        [System.Management.Automation.CompletionResult]::new($dir, $dir, "ParameterValue", $dir)
      }
      Get-ChildItem -Path $dir | Resolve-Path -Relative | ForEach-Object {
        $path = $_.ToString().replace('\\', '/').replace('Microsoft.PowerShell.Core/FileSystem::', '')
        $isDir = $false
        if ((Get-Item $path) -is [System.IO.DirectoryInfo]) {
          $path = $path + "/"
          $isDir = $true
        }
        if ( ($type -eq "file") -or ( ($type -eq "dir") -and $isDir ) ) {
          [System.Management.Automation.CompletionResult]::new($path, $path, "ParameterValue", $path)
        }
      }
    }
  }
  $env:COMP_WORDS = $null | Out-Null
  $env:COMP_CWORD = $null | Out-Null
  $env:_PROS_COMPLETE = $null | Out-Null
}
