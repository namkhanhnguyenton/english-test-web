@echo off
chcp 65001 > nul
echo ===================================================================
echo   DAY DU AN LEN GITHUB (namkhanhnguyenton/english-test-web)
echo ===================================================================
echo.
echo Dang day ma nguon len GitHub...
echo (Neu cua so trinh duyet hien len, vui long nhan "Sign in" de xac nhan)
echo.
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ===================================================================
    echo [THANH CONG] Ma nguon da duoc day len GitHub thanh cong!
    echo Ban co the truy cap: https://github.com/namkhanhnguyenton/english-test-web
    echo ===================================================================
) else (
    echo.
    echo [LƯU Y XAC THUC GITHUB]
    echo GitHub khong con cho phep dang nhap bang mat khau thuong.
    echo Ban hay tao 1 Token tai: https://github.com/settings/tokens
    echo (Chon quyen "repo", copy ma token ghp_xxx)
    echo Sau do chay lenh:
    echo   git push https://YOUR_TOKEN@github.com/namkhanhnguyenton/english-test-web.git main
)
echo.
pause
