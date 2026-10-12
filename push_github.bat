@echo off
chcp 65001 > nul
echo ===================================================================
echo   DAY DU AN LEN GITHUB (namkhanhnguyenton/english-test-web)
echo ===================================================================
echo.
echo [1/3] Dang kiem tra thay doi...
git add .

echo [2/3] Dang luu ban cap nhat...
git commit -m "Cap nhat code moi" > nul 2>&1

echo [3/3] Dang day ma nguon len GitHub...
git push origin main

if %errorlevel% equ 0 (
    echo.
    echo ===================================================================
    echo [THANH CONG] Ma nguon da duoc day len GitHub thanh cong!
    echo Render se tu dong cap nhat trang web sau 1-2 phut!
    echo Kiem tra tai: https://github.com/namkhanhnguyenton/english-test-web
    echo ===================================================================
) else (
    echo.
    echo ===================================================================
    echo [CHUA THANH CONG] Khong the day len GitHub.
    echo Hay kiem tra lai ket noi Internet hoac Token GitHub.
    echo ===================================================================
)
echo.
pause

