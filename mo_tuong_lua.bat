@echo off
chcp 65001 > nul
echo ===================================================================
echo   MO CONG 5000 CHO THIET BI KHAC VAO WEB QUA MANG WIFI / NOI BO
echo ===================================================================
echo.
echo Dang cap quyen Windows Defender Firewall cho cong 5000...
netsh advfirewall firewall add rule name="EnglishTestPro Web Port 5000" dir=in action=allow protocol=TCP localport=5000

if %errorlevel% equ 0 (
    echo.
    echo [THANH CONG] Da mo cong 5000!
    echo Cac thiet bi khac cung mang Wi-Fi co the vao web theo dia chi:
    echo   http://192.168.1.223:5000
    echo.
) else (
    echo.
    echo [LƯU Y] Vui long nhap chuot phai vao file nay va chon "Run as administrator" de Windows cho phep mo cong!
    echo.
)
pause

