#!/bin/bash
## setup command=wget -q --no-check-certificate https://raw.githubusercontent.com/OwnerPlugins/rsilive/main/installer.sh -O - | /bin/bash

version='1.3'
changelog='\nAdd Live Upgrade\nFix screen'

TMPPATH=/tmp/RSILive-install
FILEPATH=/tmp/RSILive-main.tar.gz

echo "Starting RSILive installation..."

if [ ! -d /usr/lib64 ]; then
    PLUGINPATH=/usr/lib/enigma2/python/Plugins/Extensions/RSILive
else
    PLUGINPATH=/usr/lib64/enigma2/python/Plugins/Extensions/RSILive
fi

cleanup() {
    echo "Cleaning up temporary files..."
    [ -d "$TMPPATH" ] && rm -rf "$TMPPATH"
    [ -f "$FILEPATH" ] && rm -f "$FILEPATH"
    [ -d "/tmp/RSILive-main" ] && rm -rf "/tmp/RSILive-main"
}

detect_os() {
    if [ -f /var/lib/dpkg/status ]; then
        OSTYPE="DreamOs"
        STATUS="/var/lib/dpkg/status"
    elif [ -f /etc/opkg/opkg.conf ] || [ -f /var/lib/opkg/status ]; then
        OSTYPE="OE"
        STATUS="/var/lib/opkg/status"
    else
        OSTYPE="Unknown"
        STATUS=""
    fi
    echo "Detected OS type: $OSTYPE"
}

detect_os

cleanup
mkdir -p "$TMPPATH"

if ! command -v wget >/dev/null 2>&1; then
    echo "Installing wget..."
    case "$OSTYPE" in
        "DreamOs")
            apt-get update && apt-get install -y wget || { echo "Failed to install wget"; exit 1; }
            ;;
        "OE")
            opkg update && opkg install wget || { echo "Failed to install wget"; exit 1; }
            ;;
        *)
            echo "Unsupported OS type. Cannot install wget."
            exit 1
            ;;
    esac
fi

if python --version 2>&1 | grep -q '^Python 3\.'; then
    echo "Python3 image detected"
    PYTHON="PY3"
    Packagesix="python3-six"
    Packagerequests="python3-requests"
else
    echo "Python2 image detected"
    PYTHON="PY2"
    Packagerequests="python-requests"
    Packagesix="python-six"
fi

install_pkg() {
    local pkg=$1
    if [ -z "$STATUS" ] || ! grep -qs "Package: $pkg" "$STATUS" 2>/dev/null; then
        echo "Installing $pkg..."
        case "$OSTYPE" in
            "DreamOs")
                apt-get update && apt-get install -y "$pkg" || { echo "Could not install $pkg, continuing anyway..."; }
                ;;
            "OE")
                opkg update && opkg install "$pkg" || { echo "Could not install $pkg, continuing anyway..."; }
                ;;
            *)
                echo "Cannot install $pkg on unknown OS type, continuing..."
                ;;
        esac
    else
        echo "$pkg already installed"
    fi
}

# ============================================================
# INSTALL YT-DLP DEPENDENCIES
# ============================================================

echo "============================================================"
echo "  Installing yt-dlp dependencies..."
echo "============================================================"

install_pkg "python3-yt-dlp"
install_pkg "python3-youtube-dl"
install_pkg "enigma2-plugin-extensions-ytdlpwrapper"
install_pkg "enigma2-plugin-extensions-ytdlwrapper"

# ============================================================
# INSTALL PYTHON DEPENDENCIES
# ============================================================

if [ "$PYTHON" = "PY3" ]; then
    install_pkg "$Packagesix"
fi
install_pkg "$Packagerequests"

# ============================================================
# INSTALL MULTIMEDIA PACKAGES
# ============================================================

if [ "$OSTYPE" = "OE" ]; then
    echo "Installing additional multimedia packages..."
    for pkg in ffmpeg gstplayer exteplayer3 enigma2-plugin-systemplugins-serviceapp; do
        install_pkg "$pkg"
    done
fi

echo "Downloading RSILive..."
wget --no-check-certificate 'https://github.com/OwnerPlugins/rsilive/archive/refs/heads/main.tar.gz' -O "$FILEPATH"
if [ $? -ne 0 ]; then
    echo "Failed to download RSILive package!"
    cleanup
    exit 1
fi

echo "Extracting package..."
tar -xzf "$FILEPATH" -C "$TMPPATH"
if [ $? -ne 0 ]; then
    echo "Failed to extract RSILive package!"
    cleanup
    exit 1
fi

# ============================================================
# INSTALL PLUGIN FILES - CASE INSENSITIVE
# ============================================================
echo "Installing plugin files..."
mkdir -p "$PLUGINPATH"

# Cerca la cartella RSILive/rsilive ovunque nell'estratto
SOURCE_DIR=$(find "$TMPPATH" -type d -iname "rsilive" 2>/dev/null | head -1)

if [ -n "$SOURCE_DIR" ]; then
    echo "Found plugin directory: $SOURCE_DIR"
    cp -r "$SOURCE_DIR"/* "$PLUGINPATH/" 2>/dev/null
    echo "Copied from $SOURCE_DIR"
else
    # Fallback: cerca la struttura standard con case-insensitive
    FOUND=0
    for dir in "$TMPPATH"/*/usr/lib/enigma2/python/Plugins/Extensions/RSILive; do
        if [ -d "$dir" ]; then
            cp -r "$dir"/* "$PLUGINPATH/" 2>/dev/null
            echo "Copied from $dir"
            FOUND=1
            break
        fi
    done
    if [ $FOUND -eq 0 ]; then
        for dir in "$TMPPATH"/*/usr/lib64/enigma2/python/Plugins/Extensions/RSILive; do
            if [ -d "$dir" ]; then
                cp -r "$dir"/* "$PLUGINPATH/" 2>/dev/null
                echo "Copied from $dir"
                FOUND=1
                break
            fi
        done
    fi
    if [ $FOUND -eq 0 ]; then
        echo "Could not find plugin files in extracted archive"
        echo "Available directories in tmp:"
        find "$TMPPATH" -type d | head -20
        cleanup
        exit 1
    fi
fi

sync

echo "Verifying installation..."
if [ -d "$PLUGINPATH" ] && [ -n "$(ls -A "$PLUGINPATH" 2>/dev/null)" ]; then
    echo "Plugin directory found and not empty: $PLUGINPATH"
    echo "Contents:"
    ls -la "$PLUGINPATH/" | head -10
else
    echo "Plugin installation failed or directory is empty!"
    cleanup
    exit 1
fi

cleanup
sync

FILE="/etc/image-version"
box_type=$(head -n 1 /etc/hostname 2>/dev/null || echo "Unknown")
distro_value=$(grep '^distro=' "$FILE" 2>/dev/null | awk -F '=' '{print $2}')
distro_version=$(grep '^version=' "$FILE" 2>/dev/null | awk -F '=' '{print $2}')
python_vers=$(python --version 2>&1)

cat <<EOF

#########################################################
#               INSTALLED SUCCESSFULLY                  #
#                developed by LULULLA                   #
#               https://corvoboys.org                   #
#########################################################
#           your Device will RESTART Now                #
#########################################################
^^^^^^^^^^Debug information:
BOX MODEL: $box_type
OS SYSTEM: $OSTYPE
PYTHON: $python_vers
IMAGE NAME: ${distro_value:-Unknown}
IMAGE VERSION: ${distro_version:-Unknown}
PLUGIN VERSION: $version
EOF

exit 0