Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$form = New-Object System.Windows.Forms.Form
$form.Text = "Belmonte Audiovisual"
$form.Size = New-Object System.Drawing.Size(520,700)
$form.StartPosition = "CenterScreen"
$form.BackColor = "#0A3D91"
$form.WindowState = "Maximized"

# Painel com scroll
$panel = New-Object System.Windows.Forms.Panel
$panel.Dock = "Fill"
$panel.AutoScroll = $true
$form.Controls.Add($panel)

# Container central
$container = New-Object System.Windows.Forms.Panel
$container.Width = 400
$container.Height = 2000
$panel.Controls.Add($container)

function Centralizar {
    $container.Left = ($form.ClientSize.Width - $container.Width) / 2
}

$form.Add_Shown({ Centralizar })
$form.Add_Resize({ Centralizar })

function CriarBotao($texto,$y){
    $btn = New-Object System.Windows.Forms.Button
    $btn.Text = $texto
    $btn.Size = New-Object System.Drawing.Size(320,32)
    $btn.Location = New-Object System.Drawing.Point(40,$y)
    $btn.BackColor = "#1F5FBF"
    $btn.ForeColor = "White"
    $btn.FlatStyle = "Flat"
    return $btn
}

# TITULO
$titulo = New-Object System.Windows.Forms.Label
$titulo.Text = "BELMONTE AUDIOVISUAL"
$titulo.ForeColor = "White"
$titulo.Font = New-Object System.Drawing.Font("Segoe UI",14,[System.Drawing.FontStyle]::Bold)
$titulo.AutoSize = $true
$titulo.Location = New-Object System.Drawing.Point(70,20)
$container.Controls.Add($titulo)

$sub = New-Object System.Windows.Forms.Label
$sub.Text = "Otimizacao de Sistema"
$sub.ForeColor = "White"
$sub.AutoSize = $true
$sub.Location = New-Object System.Drawing.Point(110,50)
$container.Controls.Add($sub)

$y = 100

function AddBtn($text,$action){
    $btn = CriarBotao $text $script:y
    $btn.Add_Click($action)
    $container.Controls.Add($btn)
    $script:y += 40
}

AddBtn "Criar Ponto de Restauracao" {
Checkpoint-Computer -Description "BelmonteTools" -RestorePointType "MODIFY_SETTINGS"
}

AddBtn "Abrir Restauracao do Sistema" { rstrui.exe }

AddBtn "Servicos em Manual" {
Set-Service SysMain -StartupType Manual -ErrorAction SilentlyContinue
Set-Service DiagTrack -StartupType Manual -ErrorAction SilentlyContinue
}

AddBtn "Desabilitar Defender" {
Set-MpPreference -DisableRealtimeMonitoring $true
}

AddBtn "Desabilitar Firewall" {
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False
}

AddBtn "Ativar Descoberta de Rede" {
netsh advfirewall firewall set rule group="Network Discovery" new enable=Yes
}

AddBtn "Compartilhamento de Rede Completo" {

Get-NetConnectionProfile | Set-NetConnectionProfile -NetworkCategory Private

netsh advfirewall firewall set rule group="Network Discovery" new enable=Yes
netsh advfirewall firewall set rule group="File and Printer Sharing" new enable=Yes

$services = @("FDResPub","fdPHost","SSDPSRV","upnphost","LanmanServer","LanmanWorkstation")

foreach ($service in $services){
Set-Service $service -StartupType Automatic -ErrorAction SilentlyContinue
Start-Service $service -ErrorAction SilentlyContinue
}

wmic nicconfig where (IPEnabled=TRUE) call SetTcpipNetbios 1
}

AddBtn "Criar Pasta Compartilhada" {
$path="C:\BelmonteShare"
New-Item $path -ItemType Directory -Force | Out-Null
New-SmbShare -Name "BelmonteShare" -Path $path -FullAccess "Everyone" -ErrorAction SilentlyContinue
Start-Process explorer.exe $path
}

AddBtn "Mostrar IP" {
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"} | Select-Object -First 1).IPAddress
[System.Windows.Forms.MessageBox]::Show("IP do computador: $ip")
}

AddBtn "Abrir Compartilhamento na Rede" {
Start-Process explorer.exe "\\localhost"
}

AddBtn "Copiar Caminho de Rede" {
$nome = $env:COMPUTERNAME
[System.Windows.Forms.Clipboard]::SetText("\\$nome")
}

AddBtn "Modo Ultra Desempenho" {
powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61
powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61
}

AddBtn "Executar SFC /SCANNOW" {
Start-Process cmd -ArgumentList "/c sfc /scannow" -Verb runAs
}

AddBtn "Executar CHKDSK /R" {
Start-Process cmd -ArgumentList "/c chkdsk C: /f /r" -Verb runAs
}

AddBtn "Limpeza de Disco" { cleanmgr.exe }

AddBtn "Atualizar Tudo via Winget" {
Start-Process powershell -ArgumentList "winget upgrade --all --accept-source-agreements --accept-package-agreements" -Verb runAs
}

AddBtn "Desabilitar Apps em Segundo Plano" {
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications" /v GlobalUserDisabled /t REG_DWORD /d 1 /f
}

AddBtn "Abrir Google Drive Belmonte" {
Start-Process "https://drive.google.com/drive/folders/1yc2Qr_Wn2Nh8r-TgrPvBzm6AgntxsPZm"
}

AddBtn "MODO EVENTO COMPLETO" {

Checkpoint-Computer -Description "BelmonteEvento" -RestorePointType "MODIFY_SETTINGS"

Set-Service SysMain -StartupType Manual -ErrorAction SilentlyContinue
Set-Service DiagTrack -StartupType Manual -ErrorAction SilentlyContinue
Set-MpPreference -DisableRealtimeMonitoring $true
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False

powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61
powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61
}

AddBtn "Restaurar Configuracoes Padrao Windows" {

Set-MpPreference -DisableRealtimeMonitoring $false
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
powercfg -setactive SCHEME_BALANCED

Set-Service SysMain -StartupType Automatic -ErrorAction SilentlyContinue
Set-Service DiagTrack -StartupType Automatic -ErrorAction SilentlyContinue
}

$form.ShowDialog()