<h1 align="center">📺 RSILive - RSI Play TV for Enigma2</h1>

[![Version](https://img.shields.io/badge/Version-1.0-blue.svg)](https://github.com/OwnerPlugins/RSILive)
[![Enigma2](https://img.shields.io/badge/Enigma2-Plugin-ff6600.svg)](https://www.enigma2.net)
[![Python](https://img.shields.io/badge/Python-3.X-blue.svg)](https://www.python.org)
[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

![Visitors](https://komarev.com/ghpvc/?username=Belfagor2005&label=Repository%20Views&color=blueviolet)
[![Donate](https://img.shields.io/badge/_-Donate-red.svg?logo=githubsponsors&labelColor=555555&style=for-the-badge)](https://ko-fi.com/lululla)
[![Donate](https://img.shields.io/badge/_-Donate-green.svg?logo=githubsponsors&labelColor=555555&style=for-the-badge)](https://paypal.me/belfagor2005)

A comprehensive plugin for Enigma2-based receivers to watch RSI Play TV content, including YouTube channels and live streams.

---

## ✨ Features

### Core Features
- **YouTube Channel Browsing**: Browse and watch videos from RSI YouTube channels
- **Live TV Support**: Watch RSI La 1 and La 2 live streams
- **Background Video Loading**: Loads videos in batches (20 at a time) without blocking the UI
- **Channel Categories**: Organized menu structure like the Kodi addon
- **Infobar Overlay**: On-screen controls and video info with auto-hide
- **Zapping Support**: CH+/CH- navigation through video lists
- **Dynamic Skin Loading**: Automatically adapts to HD, FHD, and UHD resolutions
- **yt-dlp Integration**: Robust YouTube stream resolution

### Navigation System
- **Menu Stack Navigation**: Back button returns to previous level, doesn't exit plugin
- **CH+/CH- Navigation**: Wrap-around navigation in video lists
- **Real-time Position Display**: Shows current video index and total count
- **Background Loading**: Non-blocking video loading with progress updates

### Player Features
- **Infobar Overlay**: Shows controls and video info on OK press
- **Zapping Support**: CH+/CH- to switch between videos
- **Stop/Exit**: STOP button exits player
- **Info Display**: Shows video title and index on OK press
- **Audio Reset**: Automatic audio track reset on channel change

### Technical Features
- **Multi-threaded Loading**: Background video loading without GUI freeze
- **Batch Processing**: Loads videos in configurable batches (default 20)
- **yt-dlp Integration**: Supports all YouTube video formats
- **Dynamic Resolution Detection**: Auto-detects screen resolution for skin selection
- **User-Agent Support**: Proper headers for YouTube streams
- **GStreamer/Exteplayer3**: Supports both playback engines

---

## 🎮 Key Controls

### Main Menu
| Key | Action |
|-----|--------|
| **OK** | Enter selected category / Play video |
| **CANCEL / EXIT** | Close plugin or go back one level |

### Category View (YouTube Channels / Live TV)
| Key | Action |
|-----|--------|
| **OK** | Enter selected channel |
| **CANCEL / EXIT** | Return to main menu |
| **UP/DOWN** | Navigate channel list |
| **CH+ / CH-** | Navigate channel list |

### Video List View
| Key | Action |
|-----|--------|
| **OK** | Play selected video |
| **CANCEL / EXIT** | Return to channel list |
| **UP/DOWN** | Navigate video list |
| **CH+ / CH-** | Navigate video list |

### Player View
| Key | Action |
|-----|--------|
| **OK** | Show/hide infobar |
| **CH+** | Next video in list |
| **CH-** | Previous video in list |
| **STOP** | Exit player |
| **EXIT** | Exit player |

### Infobar Overlay (shown on OK press)
- **Top Center**: Controls help (`OK = Info | CH+/CH- = Next/Prev | STOP = Exit`)
- **Top Left**: Video title and index (`Video Title [3/42]`)

---

## 📦 Installation

### Manual Installation

```bash
# Copy plugin to Enigma2
scp -r RSILive/ root@<decoder_ip>:/usr/lib/enigma2/python/Plugins/Extensions/

# Restart Enigma2
init 4 && init 3
```

### Via Telnet/Wget (Recommended)

```bash
wget -q --no-check-certificate https://raw.githubusercontent.com/Belfagor2005/RSILive/main/installer.sh -O - | /bin/bash
```

### Dependencies

Ensure `yt-dlp` is installed:

```bash
opkg install yt-dlp
```

If not available, install manually:

```bash
wget -O /usr/bin/yt-dlp https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp
chmod +x /usr/bin/yt-dlp
```

---

## 🚀 Usage

### Basic Navigation

1. **Open the Plugin**: From the Extensions menu, select RSILive
2. **Main Menu**: Choose between:
   - 📺 **YouTube Channels** - Browse RSI YouTube channels
   - 📡 **Live TV** - Watch RSI La 1 and La 2 live streams
3. **Select a Channel**: Navigate to a channel and press OK
4. **Browse Videos**: Videos load in batches (20 at a time)
5. **Watch a Video**: Select a video and press OK to start playback
6. **Zapping**: Use CH+/CH- to switch between videos
7. **Exit**: Press STOP or EXIT to return to the list

### YouTube Channel Browsing

1. Select **YouTube Channels** from the main menu
2. Choose a channel from the list (e.g., "RSI News", "RSI Sport")
3. Videos load in the background with a loading indicator
4. After the first batch loads, continue scrolling to load more
5. Select a video to start playback

### Live TV

1. Select **Live TV** from the main menu
2. Choose RSI La 1 or RSI La 2
3. Stream starts automatically
4. Press EXIT to return to the channel list

### Navigation Stack

- **Back/EXIT** returns to the previous level
- Main Menu → YouTube Channels → Channel Videos → Player
- Pressing EXIT on the player returns to the video list
- Pressing EXIT on the video list returns to the channel list
- Pressing EXIT on the channel list returns to the main menu
- Pressing EXIT on the main menu closes the plugin

---

## 📁 File Structure

```
★ RSILive/
├── __init__.py                 # Package marker
├── plugin.py                   # Plugin entry point
├── main.py                     # Main menu and navigation
├── player.py                   # Video player with infobar
├── rsi_api.py                  # RSI API client (live streams)
├── youtube_helper.py           # YouTube stream resolver (yt-dlp)
├── helpers.py                  # Utility functions
├── data/
│   └── youtube_channels.json   # YouTube channel list
├── skins/
│   ├── hd/
│   │   └── main.xml            # HD skin (1280x720)
│   ├── fhd/
│   │   └── main.xml            # FHD skin (1920x1080)
│   └── uhd/
│       └── main.xml            # UHD skin (3840x2160)
└── images/
    ├── icon.png                # Plugin icon
    └── fanart.png              # Background fanart
```

### Data File Format

**`data/youtube_channels.json`**
```json
[
    {
        "name": "RSI News",
        "url": "https://www.youtube.com/channel/UC6UUxoC7DGUUlUHcJvulsfQ"
    },
    {
        "name": "RSI Sport",
        "url": "https://www.youtube.com/channel/UC6S8pesV-uN9lRCTNLssZOg"
    }
]
```

---

## ⚙️ Configuration

### Settings
Access configuration from the Enigma2 plugin menu:
- **Default Player**: Choose between GStreamer and Exteplayer3
- **Buffer Size**: Configure streaming buffer size (1024-8192 KB)
- **Hardware Acceleration**: Enable/disable hardware acceleration
- **Debug Logging**: Enable debug messages in logs

### Skin Customization
The plugin automatically detects screen resolution and loads the appropriate skin:
- **HD** (1280x720): `skins/hd/main.xml`
- **FHD** (1920x1080): `skins/fhd/main.xml`
- **UHD** (3840x2160): `skins/uhd/main.xml`

To customize the skin, edit the corresponding XML file.

---

## 🔧 Technical Details

### Architecture
- **Frontend**: Enigma2 Screen system with MenuList components
- **Navigation**: Stack-based navigation with history
- **Loading**: Multi-threaded background loading with batch processing
- **Player**: Enigma2 eServiceReference with GStreamer/Exteplayer3
- **YouTube**: yt-dlp integration with format fallback
- **Skin**: XML-based with dynamic resolution detection

### YouTube Resolution
`youtube_helper.py` tries formats in this order:
1. `-f 18` - MP4 360p (most compatible)
2. `-f best[ext=mp4]` - Best MP4 format
3. `-f 22/37` - MP4 720p/1080p
4. `-f best` - Any format

### Video Loading
- **Batch Size**: 20 videos per batch
- **Background Thread**: Non-blocking loading
- **UI Updates**: Real-time progress via `callWithCallback`
- **Stop Mechanism**: Thread stops on exit

### Playback Engine
- **Service Type**: `5001` for HLS, `4097` for HTTP
- **User-Agent**: `Mozilla/5.0 (Windows NT 10.0; Win64; x64)`
- **Service Reference**: `{type}:0:0:0:0:0:0:0:0:0:{url_encoded}:{name_encoded}`

---

## 🐛 Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| **No videos load** | Check internet connection and that yt-dlp is installed |
| **Videos don't play** | Ensure yt-dlp is up to date: `opkg update && opkg install yt-dlp` |
| **List not showing** | Verify `data/youtube_channels.json` exists and is valid JSON |
| **Skin errors** | Ensure `skins/` directory exists with corresponding XML files |
| **Player crashes** | Try switching between GStreamer and Exteplayer3 in settings |
| **Slow loading** | Reduce buffer size in settings |
| **No audio** | Check audio track selection or reset audio in settings |
| **Live TV not working** | URLs may change; update in `rsi_api.py` or open an issue |

### Debug Mode

Enable debug logging in settings, then check logs:

```bash
tail -f /var/log/messages | grep RSILive
```

Or on OpenPLi:

```bash
tail -f /home/root/logs/debug.log | grep RSILive
```

### Manual yt-dlp Test

Test if yt-dlp works correctly:

```bash
yt-dlp -g -f 18 "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

Should return a video URL.

---

## 📝 Changelog

### v1.0 (2026-06-26)
- Initial release
- Main menu with YouTube Channels and Live TV categories
- YouTube channel browsing with background loading (20 videos per batch)
- RSI La 1 and La 2 live streams
- Infobar overlay with controls and video info
- CH+/CH- zapping through video lists
- Dynamic skin loading (HD, FHD, UHD)
- Navigation stack (back returns to previous level)
- yt-dlp integration with format fallback
- GStreamer/Exteplayer3 support

---

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Code follows existing style and structure
- Comments are in English
- New features include appropriate configuration options
- All changes are tested on Enigma2 receivers
- Submit pull requests to the main branch

---

## 📄 License

This plugin is open-source software under the **GPLv3 License**.

---

## 🙏 Credits

- **Developer**: Lululla ([Belfagor2005](https://github.com/Belfagor2005))
- **Original Concept**: TVGarden Plugin
- **Kodi Addon Reference**: plugin.video.rsiplaytv
- **Homepage**: [www.linuxsat-support.com](https://www.linuxsat-support.com) - [www.corvoboys.org](https://www.corvoboys.org)

---

*Note: This plugin requires an Enigma2-based receiver (OpenPLi, OpenATV, etc.)*
*YouTube playback requires yt-dlp installed on the system*
*Live TV streams require internet connection and may be geoblocked*
*Some YouTube channels may have restrictions based on region*
*UHD skin requires a 4K capable receiver with appropriate resolution*
*Background loading may slow down on older receivers with limited RAM*
```
