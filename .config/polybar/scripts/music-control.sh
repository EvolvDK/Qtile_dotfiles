#!/usr/bin/env bash

RMPC="$HOME/.cargo/bin/rmpc"
STATE_FILE="$HOME/.config/polybar/music-focus-state"

action="${1:-}"

extract_field() {
    printf '%s' "$1" | sed -n "s/.*\"$2\"[[:space:]]*:[[:space:]]*\"\\([^\"]*\\)\".*/\\1/p"
}

# Ensure directory exists
mkdir -p "$(dirname "$STATE_FILE")"

# Read current focus mode
focus_mode=$(cat "$STATE_FILE" 2>/dev/null || echo "mpd")

if [[ "$action" == "toggle-focus" ]]; then
    # Toggle and always write explicit mode
    if [[ "$focus_mode" == "playerctl" ]]; then
        echo "mpd" > "$STATE_FILE"
    else
        echo "playerctl" > "$STATE_FILE"
    fi
    exit 0
fi

rmpc_song_output=$($RMPC song 2>/dev/null)
mpd_file=$(extract_field "$rmpc_song_output" "file")

# Control logic (unchanged — already correct)
if [[ -n "$mpd_file" && "$focus_mode" != "playerctl" ]]; then
    case "$action" in
        play-pause) $RMPC togglepause ;;
        next) $RMPC next ;;
        previous) $RMPC prev ;;
        loop-toggle)
            status_output=$($RMPC status 2>/dev/null)
            single=$(extract_field "$status_output" "single")
            if [[ "$single" == "Off" || -z "$single" ]]; then
                $RMPC single on
            else
                $RMPC single off
            fi
            ;;
    esac
else
    players=$(playerctl -l 2>/dev/null)
    active=""

    if [[ -n "$players" ]]; then
        for player in $players; do
            status=$(playerctl -p "$player" status 2>/dev/null)
            [[ "$status" == "Playing" ]] && active="$player" && break
            [[ "$status" == "Paused" && -z "$active" ]] && active="$player"
        done
    fi

    if [[ -n "$active" ]]; then
        case "$action" in
            play-pause) playerctl -p "$active" play-pause ;;
            next) playerctl -p "$active" next ;;
            previous) playerctl -p "$active" previous ;;
            loop-toggle)
                loop=$(playerctl -p "$active" loop 2>/dev/null || echo "None")
                if [[ "$loop" == "Track" ]]; then
                    playerctl -p "$active" loop None
                else
                    playerctl -p "$active" loop Track
                fi
                ;;
        esac
    fi
fi
