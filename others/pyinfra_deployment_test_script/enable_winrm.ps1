# Powershell script to enable WinRM for local connections
#
# Run the script with Administrator privileges. The created account is
# mutablesecurity:password. After that, you can test the connection with the
# command below:
#
# Enter-PSSession -ComputerName 127.0.0.1 -Credential mutablesecurity
#
# Resources:
# - https://gist.github.com/velotiotech/5a4cc995a5c81f24910e575abf8c09d2
# - https://github.com/windowsbox/powershellmodules/blob/master/modules/WindowsBox.WinRM/WindowsBox.WinRM.psm1

# Create a new user and mark it as an administrator
$Password = ConvertTo-SecureString "password" -AsPlainText -Force;
New-LocalUser "mutablesecurity"\
 -Password $Password -FullName "MutableSecurity"\
 -Description "MutableSecurity's Account";
Add-LocalGroupMember -Group "Administrators" -Member "mutablesecurity";

# Enable WinRM
Set-NetConnectionProfile -NetworkCategory Private;
Set-PSRepository -Name 'PSGallery' -InstallationPolicy Trusted;
Install-Module -Name WindowsBox.WinRM;
Enable-InsecureWinRM;