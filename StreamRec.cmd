:::::::::::::::::::::::::::::::
:: Stream record
:: %1 : url
:: %2 : dest file
:: %3 : mode
:: %4 : arguments in front of -i, e.g. headers
:: %5 : arguments after -1, e.g. stream maps
:::::::::::::::::::::::::::::::
set ffmpeg="D:\Programme\ffmpeg\bin\ffmpeg.exe"
set args1=-http_persistent 0 -analyzeduration 15000000 -ignore_unknown
set ffmpeg1=%ffmpeg% %args1%

set n=0
set fn=%2
:retry
goto %3

:mode_Default
%ffmpeg1% %~4 -i %1 -c copy %~5 %fn% 2>&1 | find /V "Skip ("
goto end

:mode_AllStreams
%ffmpeg1% %~4 -i %1 -c copy -map 0 %fn% 2>&1 | find /V "Skip ("
goto end

:mode_V0_AllAudio
%ffmpeg1% %~4 -i %1 -c copy -map 0:v:0 -map 0:a %fn% 2>&1 | find /V "Skip ("
goto end

:mode_Test
set ffmpeg2=%ffmpeg% %args1% -reconnect 1 -reconnect_streamed 1 -reconnect_on_network_error 1 -reconnect_delay_max 2
::set ffmpeg2=%ffmpeg% %args1% -reconnect 1 -reconnect_at_eof 1 -reconnect_streamed 1 -reconnect_delay_max 2
::%ffmpeg2% -i %1 -c copy %fn%
%ffmpeg2% -i %1 -c copy -map 0:v:3 -map 0:a:0 -map 0:a:5 %fn% 2>&1 | find /V "Skip ("
goto exit

:end
:: retry, autorename file, use start index in the past to fill the gap to the aborted file
set /a n=n+1
set fn="%~dpn2%n%%~x2"
set ffmpeg1=%ffmpeg% %args1% -live_start_index -50
goto retry

:exit
pause
