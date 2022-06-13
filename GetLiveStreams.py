import sys
import re
import httpx

mainUrl = "https://www.2ix2.com/"
#mapping 2ix2 page name to epg channel name
channels = {
	"ard": "Das Erste (ARD)",
	"zdf-live": "ZDF",
	"hr-fernsehen": "HR",
	"rtl-live": "RTL",
	"rtl2-live": "RTL2",
	"sat1": "SAT.1",
	"pro7": "ProSieben",
	"kabel-1": "Kabel Eins",
	"vox": "VOX",
	"tele-5": "TELE 5",
	"super-rtl-live": "Super RTL",
	"3sat": "3sat",	
	"arte": "arte",
	"phoenix": "PHOENIX",
	"kika": "KiKA",
	"nickelodeon": "nick",
	"disney-channel": "Disney Channel",
	"wdr-fernsehen": "WDR",
	"swr-fernsehen": "SWR BW",
	"br-fernsehen": "BR Süd",
	"ndr-fernsehen": "NDR Hamburg",
	"mdr-fernsehen": "MDR-Sachsen",
	"rbb-fernsehen": "rbb Berlin",
	"sr-fernsehen": "SR",
	"tagesschau": "tagesschau24",
	"one-tv": "ONE",
	"zdfinfo": "ZDFinfo",
	"zdfneo": "ZDFneo",
	"comedy-central": "Comedy Central",
	"sixx": "sixx",
	"rtl-nitro-hd": "NITRO",
	"prosieben-maxx": "ProSieben MAXX",
	"sat1-gold": "SAT.1 GOLD",
	"servus-tv": "ServusTV Deutschland",
	"orf1": "ORF 1",
	"orf2": "ORF 2",
	"orf3": "ORF 3",
	"srf-1": "SRF 1",
	"srf-2": "SRF zwei",
	"mtv": "MTV",
	"tlc": "TLC",
	"dmax": "DMAX",
	"kabel-1-doku": "Kabel Eins Doku",
	"welt-der-wunder": "Welt der Wunder",
	"n-tv-live": "n-tv",
	"welt": "WELT",
	"deutsche-welle": "DW Englisch",
	"bloomberg-tv": "Bloomberg TV"
}

def getm3u8(chan):
    pageUrl = mainUrl + chan  + "/"
    headers = { "Referer": mainUrl }
    r = httpx.get(pageUrl, headers=headers)

    pattern = '"(http.*\.m3u8).*"'
    match = re.search(pattern, r.text) 
    return match.group(1) if match else None

def run(chanNum, fname):
    s = "#EXTM3U8\n"
    for c in channels.keys():
        chan = channels[c]
        print(f"{c} -> {chan}")
        url = getm3u8(c)
        if url:
            if chanNum > 0:
                s += f"#EXTINF:0,{chanNum}. {chan}\n{url}\n"
                chanNum += 1
            else:
                s += f"#EXTINF:0,{chan}\n{url}\n"
    #print(s)

    with open(fname, 'w', encoding="utf-8") as f:
        f.write(s)

if __name__ == "__main__":
    n = len(sys.argv)
    # channel number start, if <1 no channel number created
    i = int(sys.argv[1]) if n > 1 else 1
    fname = sys.argv[2] if n > 2 else "2ix2.m3u8"
    run(i, fname)
