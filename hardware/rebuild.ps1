[CmdletBinding()]
param(
    [string]$KiCadBin = 'C:/Program Files/KiCad/10.0/bin',
    [string]$Python = 'python'
)
$ErrorActionPreference = 'Stop'
$boardDir = Join-Path $PSScriptRoot 'rev-a'
$root = Split-Path $PSScriptRoot -Parent
$cli = Join-Path $KiCadBin 'kicad-cli.exe'
$kiPython = Join-Path $KiCadBin 'python.exe'
$name = '68764-to-28pin'
function Run-Checked {
    param([string]$Exe, [string[]]$Arguments)
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Command failed ($LASTEXITCODE): $Exe $Arguments" }
}
Run-Checked $cli @('sch','erc','--format','json','--exit-code-violations','--output',"$boardDir/erc.json","$boardDir/$name.kicad_sch")
Run-Checked $cli @('pcb','drc','--format','json','--schematic-parity','--exit-code-violations','--output',"$boardDir/drc.json","$boardDir/$name.kicad_pcb")
Run-Checked $kiPython @("$PSScriptRoot/audit_adapter.py")
Run-Checked $cli @('pcb','export','gerbers','--layers','F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts','--output',"$boardDir/fabrication/","$boardDir/$name.kicad_pcb")
Run-Checked $cli @('pcb','export','drill','--format','excellon','--output',"$boardDir/fabrication/","$boardDir/$name.kicad_pcb")
Run-Checked $kiPython @("$PSScriptRoot/check_mask_gerbers.py")
Run-Checked $Python @("$root/tools/package_fabrication.py")
Run-Checked $Python @("$root/tools/verify_fabrication.py")
Run-Checked $Python @("$root/tools/render_fabrication.py")
Write-Output 'Checks complete. Visually inspect ZIP-based previews before delivery.'
