# StreamRec - Stream Recorder

Record a live TV stream for a given start time, end time and TV channel URL (m3u).

This is my first attempt to create a Windows desktop app with Eel.

[Eel](https://github.com/ChrisKnott/Eel) is an excellent, simple to use framework to implement a Python backend with an HTML/JavaScript/whatever UI running in a browser window.

Briefly
- A playlist (m3u8 or pls format) is used for the channel name drop down to select the live stream URL for the recording.
- In a cmd file different FFmpeg commands are specified under goto-labels ("modes"), e.g. to tell which audio streams shall be recorded. The mode can be selected in the UI from a drop down.
- Start time, end time and title of the recording are entered in text boxes.
- Clicking the "Create" button will add an event to the Windows task scheduler with the given parameters.

Edit the command file to set the proper ffmpeg file location on your system. You may also add modes, e.g. for special track mappings, on the fly transcoding etc.

Buttons in the Events tab:
- Create: Schedule recording from the edited/selected entries.
- Playlist: Show the m3u8 document of the currently selected channel.
- Play: Start the live stream in the video player configured in the settings.
- Tasks: Show the Windows task scheduler. Your planned recordings can be found in the Record folder.
- CmdFile: Edit the command file with your different modes (FFmpeg commands)-
- ChanFile: Edit the channel file (playlist).

Settings tab:
- Download directory where to save the recordings.
- Offset: Number of minutes to extend start and end time when pasting via the Start label (see below).
- Player: The video player application the be used with the Play button.
- CmdFile: It is started by the scheduler and does the real recording work. On first start this file must be edited to set the proper ffmpeg file location on your system.
- ChannelFile
- save playlists to disk: write m3u8 playlist files collected via the Playlist button to disk for further inspection.

## Paste Operation

I'm using TVBrowser as my favorite TV guide. It can copy a program to the clipboard in the format

`<start> <end> - <channel> - <title>`<br>
e.g.<br>
`12.04.2019 21:45–23:20 - ARD-alpha - Fawlty Towers`

TVBrowser configuration for the clipboard plugin:

`{leadingZero(start_day,"2")}.{leadingZero(start_month,"2")}.{start_year} {leadingZero(start_hour,"2")}:{leadingZero(start_minute,"2")}-{leadingZero(end_hour,"2")}:{leadingZero(end_minute,"2")} - {channel_name} - {title}`

Clicking on the Start label will 
- paste from the clipboard
- try to parse according to the format above
- extend start and end time by the configured offset
- fill the UI with the parsed data

We only need to select the desired mode before hitting "Create".

## Extensions to the Channel File

First I used "Mode" entries in the cmd file to implement special audio mappings, referrers etc. 
Since they are diffenet for all channels this can now be configured as extensions to the m3u8 channels file:
- #EXTARGS1: these ffmpeg parameters will be added before the URL (-i parameter)
- #EXTARGS2: these ffmpeg parameters will be added after the URL (-i parameter)

See the m3u8 file for examples.

The #EXTARGS1 of the channel will always be used if available, e.g. to specify a referrer.

The "use stream maps" chackbox on the UI will enable the #EXTARGS2 of the channel if available, e.g. for audio maps. 
When unchecked no mapping is done and ffmpeg takes the best video amd the best audio track by default (i.e. 1 video and 1 audio track).

The "use full timeshift period" chackbox adds " -live_start_index 1" to #EXTARGS1. 
If I missed the start time of a program, there is still a chance to record it, if the channel provides timeshift in its player. 
E.g. ARD allows 2h timeshift, ZDF 3h, but ARTE only 1min etc..
Check setting "save playlists to disk" and click button Playlist for the selected channel. Look into the playlist files to see the time range they contain.

## Command File

This file is started by the Windows task scheduler. 
It contains the ffmpeg commands for the defined modes, parameterized by the cmd file's arguments.

Sometimes I experience broken internet connections resulting in truncated recordings. 
This may be caused by the internet provider (e.g. a reset per day), overload at the video provider (prime time), etc.

To deal with that the cmd file implements an automatic restart of ffmpeg with a numbered file name (auto increment). 
The restarted recording also starts 50 m3u parts in the past (-live_start_index -50), so in best case (short internet connection break and sufficient m3u time coverage) both recorded files will overlap and can be stitched together seamlessly with a video editor.





