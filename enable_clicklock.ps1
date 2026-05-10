param(
    [Nullable[int]]$LockTime
)

reg add "HKCU\Control Panel\Mouse" /v MouseClickLock /t REG_SZ /d 1 /f

if ($null -ne $LockTime) {
    reg add "HKCU\Control Panel\Mouse" /v MouseClickLockTime /t REG_SZ /d $LockTime /f
}

$code = @'
[DllImport("user32.dll", SetLastError=true)]
public static extern IntPtr SendMessageTimeout(IntPtr hWnd, uint Msg, UIntPtr wParam, string lParam, uint fuFlags, uint uTimeout, out UIntPtr lpdwResult);
'@
$type = Add-Type -MemberDefinition $code -Name WinAPI -Namespace User32 -PassThru
$result = [UIntPtr]::Zero
$type::SendMessageTimeout([IntPtr]0xFFFF, 0x001A, [UIntPtr]::Zero, "Mouse", 2, 5000, [ref]$result)

Write-Host "ClickLock enabled."
if ($null -ne $LockTime) {
    Write-Host "LockTime set to ${LockTime}ms."
}
