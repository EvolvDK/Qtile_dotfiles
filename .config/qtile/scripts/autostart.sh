#!/bin/sh

# Screen configuration
/usr/bin/xrandr --output HDMI-1-0 --auto --right-of eDP

# polkit
lxpolkit &

# background
feh --bg-fill ~/.config/qtile/wallpaper/wallhaven-rq7jw1_3440x1440.png &

# compositor
picom --config ~/.config/qtile/picom/picom.conf --animations -b &

# Notifications
dunst -config ~/.config/qtile/dunst/dunstrc &

# Daemons and Applets
~/.cargo/bin/clipcatd &
eww daemon -c ~/.config/eww &
caffeine-indicator &