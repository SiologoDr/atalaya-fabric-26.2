@echo off
title Atalaya - Minecraft Test
cd /d "%~dp0"
call gradlew.bat runClient --args="--quickPlaySingleplayer MiniJefes"
pause

