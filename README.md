# StreamRec - Stream Recorder

Record a live TV stream for a given start time, end time and TV channel URL (m3u).

This is my first attempt to create a Windows desktop app with Eel.

[Eel](https://github.com/ChrisKnott/Eel) is an excellent, simple to use framework to implement a Python backend with an HTML/JavaScript/whatever UI running in your browser.

Briefly
- A playlist (m3u8 or pls format) is used for the channel name drop down to select the live stream URL for the recording.
- In a cmd file different FFmpeg commands are specified under goto-labels ("modes"), e.g. to tell which audio streams shall be recorded. The mode can be selected in the UI from a drop down.
- Start time, end time and title of the recording are entered in text boxes.
- Clicking the "Create" button will add an event to the Windows task scheduler with the given parameters.

Buttons:
- Create: schedule recording.
- Playlist: show the m3u8 document of the currently selected channel.
- Play: one the live stream in the video player configured in the settings.
- Tasks: show the Windows task scheduler. Your planned recordings can be found in the Record folder.
- CmdFile: edit the command file with your different modes (FFmpeg commands)-
- ChanFile: Edit the channel file (playlist).

Settings:
- Download directory where to save the recordings.
- Offset: Number of minutes to extend start and end time when pasting via the Start label (see below).
- Plaer: the video player application the be used with the Play button.

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