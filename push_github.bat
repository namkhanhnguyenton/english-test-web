@echo off
chcp 65001 > nul
echo ===================================================================
echo   DAY DU AN LEN GITHUB (namkhanhnguyenton/english-test-web)
echo ===================================================================
echo.
echo Dang kiem tra thay doi va chuan bi day len GitHub...
git add .
git commit -m "Cap nhat code moi"
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ===================================================================
    echo [THANH CONG] Ma nguon da duoc day len GitHub thanh cong!
    echo Render se tu dong cap nhat trang web sau 1-2 phut!
    echo Ban co the kiem tra tai: https://github.com/namkhanhnguyenton/english-test-web
    echo ===================================================================
) else (
    echo.
    echo [THONG BAO] Neu gap loi xac thuc hoac can nhap token:
    echo Hay dam bao token GitHub con han hoac chay lenh push voi token.
)
echo.
pause

