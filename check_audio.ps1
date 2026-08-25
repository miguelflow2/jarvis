# Verif audio au demarrage - lance avant JARVIS
try {
  Add-Type -AssemblyName System.Speech 2>$null
  $p = New-Object System.Diagnostics.ProcessStartInfo
  $p.FileName = "python"
  $p.Arguments = "`"C:\Users\migue\OneDrive\Documents\Default Project\JARVIS\test_pyaudio.py`""
  $p.RedirectStandardOutput = $true; $p.UseShellExecute = $false
  $proc = [System.Diagnostics.Process]::Start($p)
  $out = $proc.StandardOutput.ReadToEnd()
  if($out -match "READ OK"){
    Write-Output "[CHECK] Audio OK"
    exit 0
  } else {
    Write-Output "[CHECK] Audio bloque - redemarrage service..."
    net stop Audiosrv 2>&1 | Out-Null
    Start-Sleep 2
    net start Audiosrv 2>&1 | Out-Null
    Write-Output "[CHECK] Service redemarre"
  }
} catch { Write-Output "[CHECK] Erreur: $_" }
