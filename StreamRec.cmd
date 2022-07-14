:::::::::::::::::::::::::::::::
:: Stream record
:: %1 : url
:: %2 : dest file
:: %3 : mode
:::::::::::::::::::::::::::::::
set ffmpeg="D:\Programme\ffmpeg\bin\ffmpeg.exe"
set ffmpeg1=%ffmpeg% -http_persistent 0 -analyzeduration 15000000 -ignore_unknown

set ffmpeg2=%ffmpeg% -http_persistent 0 -analyzeduration 15000000 -ignore_unknown -reconnect 1 -reconnect_streamed 1 -reconnect_on_network_error 1 -reconnect_delay_max 2

::set ffmpeg2=%ffmpeg% -http_persistent 0 -analyzeduration 15000000 -ignore_unknown -reconnect 1 -reconnect_at_eof 1 -reconnect_streamed 1 -reconnect_delay_max 2

set n=0
set fn=%2
:retry
goto %3

:mode_Default
%ffmpeg1% -i %1 -c copy %fn% 2>&1 | find /V "Skip ("
goto end

:mode_AllStreams
%ffmpeg1% -i %1 -c copy -map 0 %fn%
goto end

:mode_V0_AllAudio
%ffmpeg1% -i %1 -c copy -map 0:v:0 -map 0:a %fn%
goto end

:mode_V0_A0_A1_(Neo)
%ffmpeg1% -i %1 -c copy -map 0:v:0 -map 0:a:0 -map 0:a:1 %fn% 2>&1 | find /V "Skip ("
goto end

:mode_V3_A0_A5_(One)
%ffmpeg1% -i %1 -c copy -map 0:v:3 -map 0:a:0 -map 0:a:5 %fn% 2>&1 | find /V "Skip ("
goto end

:mode_Test
::%ffmpeg2% -i %1 -c copy %fn%
%ffmpeg2% -i %1 -c copy -map 0:v:3 -map 0:a:0 -map 0:a:5 %fn% 2>&1 | find /V "Skip ("
goto exit

:end
set /a n=n+1
set fn="%~dpn2%n%%~x2"
goto retry

:exit
pause
