#!/usr/bin/env bash

# List to track failed reloads
failed_instances=""

# Function to track failures
check_status() {
    if [ $? -ne 0 ]; then
        if [ -z "$failed_instances" ]; then
            failed_instances="$1"
        else
            failed_instances="$failed_instances, $1"
        fi
    fi
}

# 1. Screen Configuration
/usr/bin/xrandr --output HDMI-1-0 --auto --right-of eDP
check_status "xrandr"

# 2. Wallpaper
feh --bg-fill ~/.config/qtile/wallpaper/wallhaven-rq7jw1_3440x1440.png
check_status "feh"

# 3. Compositor (picom)
killall -q picom
/usr/local/bin/picom --config ~/.config/picom/picom.conf
check_status "picom"

# 4. Notifications (dunst)
dunstctl reload
check_status "dunst"

# 5. Clipcat Daemon
killall -q clipcatd
~/.cargo/bin/clipcatd &
check_status "clipcatd"

# 6. Eww Daemon
eww reload 2>/dev/null || eww daemon -c ~/.config/eww &
check_status "eww"

# 7. Caffeine Indicator
killall -q caffeine-indicator
caffeine-indicator &
check_status "caffeine"

# 8. Polybar Management
if grep -q 'wm_bar = "polybar"' "$HOME/.config/qtile/config.py"; then
    if pgrep -x polybar >/dev/null; then
        polybar-msg cmd restart
        check_status "polybar-restart"
    else
        if [ -f "$HOME/.config/polybar/launch.sh" ]; then
            "$HOME/.config/polybar/launch.sh"
            check_status "polybar-launch"
        fi
    fi
else
    if pgrep -x polybar >/dev/null; then
        polybar-msg cmd quit
        check_status "polybar-quit"
    fi
fi

# 9. Qtile Restart
$HOME/.local/bin/qtile cmd-obj -o cmd -f restart
check_status "qtile"

# Final Notification
if [ -z "$failed_instances" ]; then
    notify-send "Environment" "Environment successfully reloaded!" -u low -t 3000
else
    notify-send "Environment Error" "Failed to reload: $failed_instances" -u critical
fi
