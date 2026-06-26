@echo off
chcp 65001 > nul
echo [INFO] 开始编译 Java 源代码...
if not exist out mkdir out
javac -d out -encoding UTF-8 -cp "lib/mysql-connector-java-8.0.28.jar" src/com/sms/util/*.java src/com/sms/exception/*.java src/com/sms/entity/*.java src/com/sms/dao/*.java src/com/sms/dao/impl/*.java src/com/sms/service/*.java src/com/sms/service/impl/*.java src/com/sms/controller/*.java src/com/sms/App.java
if %errorlevel% equ 0 (
    echo [INFO] 编译成功！输出目录: out/
) else (
    echo [ERROR] 编译失败，请检查语法错误。
)
pause
