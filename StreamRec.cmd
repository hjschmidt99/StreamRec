:::::::::::::::::::::::::::::::
:: Stream record
:: %1 : url
:: %2 : dest file
:: %3 : mode
:::::::::::::::::::::::::::::::
set ffmpeg="D:\Programme\ffmpeg\bin\ffmpeg.exe"
set ffmpeg1=%ffmpeg% -http_persistent 0 -analyzeduration 15000000 -ignore_unknown

goto %3

:: 2>&1 | find /V "Skip ("

:mode_Default
%ffmpeg1% -i %1 -c copy %2 2>&1 | find /V "Skip ("
goto end

:mode_AllStreams
%ffmpeg1% -i %1 -c copy -map 0 %2
goto end

:mode_V0_AllAudio
%ffmpeg1% -i %1 -c copy -map 0:v:0 -map 0:a %2
goto end

:mode_V0_A0_A1_(Neo)
%ffmpeg1% -i %1 -c copy -map 0:v:0 -map 0:a:0 -map 0:a:1 %2 2>&1 | find /V "Skip ("
goto end

:mode_V3_A0_A5_(One)
%ffmpeg1% -i %1 -c copy -map 0:v:3 -map 0:a:0 -map 0:a:5 %2 2>&1 | find /V "Skip ("
goto end

:mode_V4_AllAudio
%ffmpeg1% -i %1 -c copy -map 0:v:4 -map 0:a %2 2>&1 | find /V "Skip ("
goto end

:mode_V7_A0
%ffmpeg1% -i %1 -c copy -map 0:v:7 -map 0:a:0 %2
goto end

:mode_V7_AllAudio
%ffmpeg1% -i %1 -c copy -map 0:v:7 -map 0:a %2
goto end

:mode_Test
%ffmpeg1% -i %1 -c copy %2
goto end

:end
if %errorlevel% 1 pause
