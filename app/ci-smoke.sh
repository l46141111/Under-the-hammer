#!/usr/bin/env bash
# 在 Android 模擬器上裝起來跑一次：開得起來、沒有 JS 錯誤、返回鍵不會讓 App 當掉
set -u
PKG=io.github.l46141111.underthehammer
APK=$(ls app/android/app/build/outputs/apk/debug/*.apk | head -1)
adb install -r "$APK" || { echo "::error title=smoke::安裝失敗"; exit 1; }
adb logcat -c
adb shell am start -W -n $PKG/.MainActivity
sleep 30
mkdir -p smoke
adb exec-out screencap -p > smoke/1-start.png
# 第一次開：每天開始的畫面 → 按「開始」那顆按鈕不好點，直接用返回鍵測：應該會把 App 收到背景，但不會當掉
adb shell input keyevent KEYCODE_BACK
sleep 3
PID=$(adb shell pidof $PKG | tr -d '\r')
adb shell am start -W -n $PKG/.MainActivity
sleep 6
adb exec-out screencap -p > smoke/2-back.png
adb logcat -d > smoke/logcat.txt
# Capacitor 自己在頁面還沒建好時注入 safe-area 變數會失敗（舊版 WebView；Capacitor 會改用原生的邊距，不影響畫面），這行另外列出來、不算遊戲的錯誤
CAPN=$(grep -c "Error injecting safe area CSS" smoke/logcat.txt)
ERR=$(grep -E "Capacitor/Console.*(Uncaught|Error|TypeError|ReferenceError)|FATAL EXCEPTION|AndroidRuntime: " smoke/logcat.txt | grep -v "Error injecting safe area CSS" | head -5 | tr '\n' ' ' | cut -c1-600)
LOGS=$(grep -c "Capacitor/Console" smoke/logcat.txt)
WV=$(adb shell dumpsys webviewupdate | grep -m1 -o "Current WebView package.*" | tr -d '\r')
echo "::notice title=smoke::pid-after-back=${PID:-none} console-lines=$LOGS capacitor-safe-area-msgs=$CAPN webview=$WV"
if [ -n "$ERR" ]; then echo "::error title=smoke-js::$ERR"; exit 1; fi
if [ -z "${PID:-}" ]; then echo "::error title=smoke::按返回鍵之後 App 不見了"; exit 1; fi
echo "::notice title=smoke::OK 開得起來、沒有 JS 錯誤、返回鍵正常"
