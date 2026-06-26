@echo off
:: Set console code page to UTF-8
chcp 65001 > nul
:: Run Java app with UTF-8 encoding configuration
java -Dfile.encoding=UTF-8 -cp "out;lib/mysql-connector-java-8.0.28.jar" com.sms.App
pause
