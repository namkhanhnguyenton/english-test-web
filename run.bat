@echo off
chcp 65001 > nul
echo ===================================================================
echo   HỆ THỐNG KIỂM TRA TRÌNH ĐỘ TIẾNG ANH (ENGLISH TEST PRO)
echo ===================================================================
echo.
echo [1] Truy cap tren may tinh nay:
echo     http://localhost:5000
echo.
echo [2] Truy cap tren dien thoai / may tinh bang / thiet bi khac (Cung Wi-Fi):
echo     http://192.168.1.223:5000
echo.
echo   * Luu y: Neu dien thoai khong vao duoc, hay chay file "mo_tuong_lua.bat" 
echo     (Chon Run as administrator) de Windows cho phep ket noi qua Wi-Fi.
echo ===================================================================
echo.
echo Dang khoi dong may chu web...
python app.py
pause
