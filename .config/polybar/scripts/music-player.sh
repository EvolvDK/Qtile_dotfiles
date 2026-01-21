#!/usr/bin/env bash

RMPC="$HOME/.cargo/bin/rmpc"
STATE_FILE="$HOME/.config/polybar/music-focus-state"

trim_title() {
    local text="$1"
    local max=30
    (( ${#text} > max )) && text="${text:0:max-2}.."
    echo "$text"
}

extract_field() {
    printf '%s' "$1" | sed -n "s/.*\"$2\"[[:space:]]*:[[:space:]]*\"\\([^\"]*\\)\".*/\\1/p"
}

prev=""

while true; do
    # Re-read focus mode every iteration (this was the bug — it was read only once before)
    focus_mode=$(cat "$STATE_FILE" 2>/dev/null || echo "mpd")

    rmpc_song_output=$($RMPC song 2>/dev/null)

    mpd_title=$(extract_field "$rmpc_song_output" "title")
    mpd_artist=$(extract_field "$rmpc_song_output" "artist")
    mpd_file=$(extract_field "$rmpc_song_output" "file")

    # Decide what to display
    if [[ -n "$mpd_file" && "$focus_mode" != "playerctl" ]]; then
        # MPD priority (default focus)
        if [[ -n "$mpd_title" ]]; then
            display_text="${mpd_artist:+$mpd_artist - }$mpd_title"
        else
            # Fallback for no metadata
            if [[ "$mpd_file" == *"#id="* ]]; then
                fallback="${mpd_file##*#id=}"
            else
                fallback="${mpd_file##*/}"
                fallback="${fallback%%\?*}"
            fi
            display_text="$fallback"
        fi
        output="󰝚 $(trim_title "$display_text")"
    else
        # Forced playerctl focus OR no MPD song
        players=$(playerctl -l 2>/dev/null)
        title=""
        player_name=""

        if [[ -n "$players" ]]; then
            for player in $players; do
                status=$(playerctl -p "$player" status 2>/dev/null)
                t=$(playerctl -p "$player" metadata title 2>/dev/null)

                if [[ "$status" == "Playing" ]]; then
                    title="$t"
                    player_name="$player"
                    break
                elif [[ "$status" == "Paused" && -z "$title" ]]; then
                    title="$t"
                    player_name="$player"
                fi
            done
        fi

        if [[ -n "$title" ]]; then
            trimmed=$(trim_title "$title")
            if [[ "$player_name" == *"spotify"* ]]; then
                output="󰓇 $trimmed"
            else
                output="󰝚 $trimmed"
            fi
        else
            output=" 󰝚 "
        fi
    fi

    [[ "$output" != "$prev" ]] && echo "$output" && prev="$output"

    sleep 1
done
