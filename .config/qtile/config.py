# Copyright (c) 2025 JustAGuyLinux

from libqtile import bar, layout, widget, qtile
from libqtile.config import Click, Drag, Group, Key, Match, Screen, ScratchPad, DropDown
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal
import os
import subprocess
import re
from typing import List

from libqtile import hook
from colors import *

from widgets.network_status import NetworkStatus

# --------------------------------------------------------
# User Configuration
# --------------------------------------------------------

mod = "mod4"
terminal = "terminator"
browser = "brave-browser"
editor = "geany"
file_manager = "thunar"
font_name = 'Roboto Mono Nerd Font'

# Choice of bar: "qtile" or "polybar"
wm_bar = "polybar"
polybar_gap = 40

home = os.path.expanduser('~')

network_interfaces = {
    "wifi": "wlo1",
    "ethernet": "enp2s0",
}

# --------------------------------------------------------
# Functions
# --------------------------------------------------------

def notify_layout():
    """Show current layout in notification"""
    def _notify_layout(qtile):
        layout_name = qtile.current_group.layout.name
        layout_map = {
            "monadtall": "Monad Tall",
            "columns": "Columns", 
            "bsp": "BSP",
            "treetab": "Tree Tab",
            "matrix": "Matrix",
            "plasma": "Plasma",
            "floating": "Floating",
            "spiral": "Spiral",
            "ratiotile": "Ratio Tile",
            "max": "Maximized",
            "monadwide": "Monad Wide",
            "tile": "Tile",
            "verticaltile": "Vertical Tile",
            "stack": "Stack",
            "zoomy": "Zoomy"
        }
        display_name = layout_map.get(layout_name, layout_name.title())
        subprocess.run(["notify-send", "Layout", display_name, "-t", "1500", "-u", "low"])
    return _notify_layout

def notify_restart():
    """Show restart notification"""
    def _notify_restart(qtile):
        subprocess.run(["notify-send", "Qtile", "Restarting...", "-t", "2000", "-u", "normal"])
    return _notify_restart

def toggle_float_center():
    """Toggle floating and center at 75% size"""
    def _toggle_float_center(qtile):
        window = qtile.current_window
        if window:
            was_floating = window.floating
            window.toggle_floating()
            if not was_floating and window.floating:
                # Only resize/center when going from tiled to floating
                screen = qtile.current_screen
                width = int(screen.width * 0.70)
                height = int(screen.height * 0.60)
                window.set_size_floating(width, height)
                window.center()
    return _toggle_float_center

def resize_left():
    """Resize window left - intuitive based on focus"""
    def _resize_left(qtile):
        current_layout_name = qtile.current_layout.name
        group = qtile.current_group
        
        # For BSP/Columns layouts with directional resize
        if current_layout_name in ["bsp", "columns"]:
            qtile.current_layout.cmd_grow_left()
        # For MonadTall/Tile - check if we're in main or stack area
        elif current_layout_name in ["monadtall", "monadwide", "tile", "ratiotile"]:
            # Get current window index
            current_idx = group.windows.index(qtile.current_window)
            # First window is usually main, so reverse the behavior
            if current_idx == 0:
                qtile.current_layout.cmd_shrink()
            else:
                qtile.current_layout.cmd_grow()
        else:
            # Default behavior for other layouts
            qtile.current_layout.cmd_shrink()
    return _resize_left

def resize_right():
    """Resize window right - intuitive based on focus"""
    def _resize_right(qtile):
        current_layout_name = qtile.current_layout.name
        group = qtile.current_group
        
        # For BSP/Columns layouts with directional resize
        if current_layout_name in ["bsp", "columns"]:
            qtile.current_layout.cmd_grow_right()
        # For MonadTall/Tile - check if we're in main or stack area
        elif current_layout_name in ["monadtall", "monadwide", "tile", "ratiotile"]:
            # Get current window index
            current_idx = group.windows.index(qtile.current_window)
            # First window is usually main, so reverse the behavior
            if current_idx == 0:
                qtile.current_layout.cmd_grow()
            else:
                qtile.current_layout.cmd_shrink()
        else:
            # Default behavior for other layouts
            qtile.current_layout.cmd_grow()
    return _resize_right

def focus_left():
    """Focus window to the left, or cycle if floating"""
    def _focus_left(qtile):
        if qtile.current_layout.name == "floating" or qtile.current_window.floating:
            qtile.current_group.cmd_prev_window()
        else:
            qtile.current_layout.cmd_left()
    return _focus_left

def focus_right():
    """Focus window to the right, or cycle if floating"""
    def _focus_right(qtile):
        if qtile.current_layout.name == "floating" or qtile.current_window.floating:
            qtile.current_group.cmd_next_window()
        else:
            qtile.current_layout.cmd_right()
    return _focus_right

@hook.subscribe.startup_once
def autostart():
   home_script = os.path.expanduser('~/.config/qtile/scripts/autostart.sh')
   subprocess.run([home_script])

@hook.subscribe.startup
def launch_polybar():
    if wm_bar == "polybar":
        home_polybar = os.path.expanduser('~/.config/polybar/launch.sh')
        subprocess.run([home_polybar])

@hook.subscribe.setgroup
def notify_group():
    names = {
        " ": "web",
        "": "dev",
        "󰭆 ": "ros",
        " ": "dir",
        " ": "txt",
        " ": "mus",
        " ": "dis",
        " ": "gen"
    }
    group_name = qtile.current_group.name
    display_name = names.get(group_name, group_name)
    subprocess.run(["notify-send", f"{display_name}", "-t", "500", "-u", "low"])

# --------------------------------------------------------
# Appearance
# --------------------------------------------------------

colors, backgroundColor, foregroundColor, workspaceColor, foregroundColorTwo = github_dark()

# --------------------------------------------------------
# Keybindings
# --------------------------------------------------------

keys = [

# Add dedicated sxhkdrc to autostart.sh script

# CLOSE WINDOW, RELOAD AND QUIT QTILE
    Key([mod], "q", lazy.window.kill(), desc="Close focused window"),
# Qtile System Actions
    Key([mod, "shift"], "r", lazy.function(notify_restart()), lazy.spawn(f"{home}/.config/qtile/scripts/reload_environment.sh"), desc="Restart Qtile"),
    Key([mod, "shift"], "q", lazy.shutdown(), desc="Exit Qtile"),
   #  Key([mod], "r", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),

# CHANGE FOCUS USING VIM OR DIRECTIONAL KEYS
    Key([mod], "Up", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "Down", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "Left", lazy.function(focus_left()), desc="Move focus left"),
    Key([mod], "Right", lazy.function(focus_right()), desc="Move focus right"),
    
    # CYCLE THROUGH ALL WINDOWS (INCLUDING FLOATING)
    Key([mod], "m", lazy.group.next_window(), desc="Focus next window"),
    Key([mod], "l", lazy.group.prev_window(), desc="Focus previous window"),
    Key(["mod1"], "Tab", lazy.group.next_window(), desc="Alt-Tab window switching"),


# MOVE WINDOWS UP OR DOWN,LEFT OR RIGHT USING VIM KEYS
    Key([mod, "shift"], "k", 
        lazy.layout.shuffle_up(),
        lazy.layout.shuffle_left(),
        desc="Move window up/left"),
    Key([mod, "shift"], "j", 
        lazy.layout.shuffle_down(),
        lazy.layout.shuffle_right(),
        desc="Move window down/right"),

# MOVE WINDOWS UP OR DOWN,LEFT OR RIGHT USING DIRECTIONAL KEYS
    Key([mod, "shift"], "Left", 
        lazy.layout.shuffle_left(),
        lazy.layout.swap_left(),
        desc="Move window left"),
    Key([mod, "shift"], "Right", 
        lazy.layout.shuffle_right(),
        lazy.layout.swap_right(),
        desc="Move window right"),
    Key([mod, "shift"], "Up", 
        lazy.layout.shuffle_up(),
        desc="Move window up"),
    Key([mod, "shift"], "Down", 
        lazy.layout.shuffle_down(),
        desc="Move window down"),

# RESIZE UP, DOWN, LEFT, RIGHT USING DIRECTIONAL KEYS
    Key([mod, "control"], "Right",
        lazy.function(resize_right()),
        desc="Resize window right"
        ),
    Key([mod, "control"], "Left",
        lazy.function(resize_left()),
        desc="Resize window left"
        ),
    Key([mod, "control"], "Up",
        lazy.layout.grow_up(),
        lazy.layout.grow(),
        lazy.layout.decrease_nmaster(),
        desc="Grow window up"
        ),
    Key([mod, "control"], "Down",
        lazy.layout.grow_down(),
        lazy.layout.shrink(),
        lazy.layout.increase_nmaster(),
        desc="Grow window down"
        ),

    Key([mod], "f", lazy.window.toggle_fullscreen(), desc="Plein écran"),
    Key([mod, "shift"], "f", lazy.window.bring_to_front(), desc="Amener au premier plan"),

# QTILE LAYOUT KEYS
    Key([mod], "Tab", lazy.next_layout(), lazy.function(notify_layout()), desc="Toggle between layouts"),
    Key([mod, "shift"], "l", lazy.spawn(f"{home}/.config/qtile/scripts/layoutmenu"), desc="Layout menu"),

# TOGGLE FLOATING LAYOUT
    Key([mod, "shift"], "space", 
        lazy.function(toggle_float_center()),
        desc="Toggle floating and center at 75%"),
    Key([mod, "shift"], "z", lazy.layout.normalize(), desc="Reset all window sizes"),
    Key([mod], "s", lazy.layout.toggle_split(), desc="Toggle split direction in BSP"),

# APPLICATION LAUNCHERS
    Key([mod], "b", lazy.spawn(browser), desc="Launch browser"),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    Key([mod], "space", lazy.spawn("rofi -show drun -modi drun,run,window,filebrowser -theme ~/.config/rofi/themes/config.rasi"), desc="Launch Rofi"),
    Key([mod], "h", lazy.spawn(f"{home}/.config/qtile/scripts/help"), desc="Show keybindings"),
    Key([mod], "t", lazy.spawn(file_manager), desc="Launch file manager"),
    Key([mod], "g", lazy.group["scratchpad"].dropdown_toggle("editor"), desc="Launch text editor"),
    Key([mod], "d", lazy.spawn("Discord"), desc="Launch Discord"),
    Key([mod], "o", lazy.spawn("obsidian"), desc="Launch Obsidian"),
    Key([mod], "v", lazy.spawn("code"), desc="Lancer VS Code"),
    Key([mod], "c", lazy.spawn(f"{home}/.cargo/bin/clipcat-menu"), desc="Afficher l'historique du presse-papiers"),
    Key([mod, "shift"], "p", lazy.spawn(f"{home}/.config/qtile/scripts/power"), desc="Power menu"),

# VOLUME CONTROLS
    Key([mod], "F3", lazy.spawn(f"{home}/.config/qtile/scripts/changevolume up"), desc="Volume up"),
    Key([mod], "F2", lazy.spawn(f"{home}/.config/qtile/scripts/changevolume down"), desc="Volume down"),
    Key([mod], "F1", lazy.spawn(f"{home}/.config/qtile/scripts/changevolume mute"), desc="Mute/Unmute"),
    Key([mod], "F4", lazy.spawn(f"{home}/.config/qtile/scripts/mic-toggle.sh"), desc="Activer/Désactiver le micro"),

# BRIGHTNESS CONTROLS
    Key([mod], "F6", lazy.spawn([f"{home}/.config/qtile/scripts/brightness_notify.sh", "inc"]), desc="Brightness up"),
    Key([mod], "F5", lazy.spawn([f"{home}/.config/qtile/scripts/brightness_notify.sh", "dec"]), desc="Brightness down"),
    Key([mod], "n", lazy.spawn(f"{home}/.config/qtile/scripts/gammastep-toggle.sh"), desc="Toggle night mode"),

# SCREENSHOTS
    Key([], "Print", lazy.spawn("flameshot gui --path " + f"{home}/Pictures/Screenshots/"), desc="Screenshot (region select)"),
    ]

# Scratchpad keybindings
keys.extend([
    Key([mod, "shift"], "Return", lazy.group['scratchpad'].dropdown_toggle('terminal')),
    Key([mod], "p", lazy.group['scratchpad'].dropdown_toggle('volume'), desc="Toggle volume scratchpad"),
])

# end of keys

# --------------------------------------------------------
# Groups
# --------------------------------------------------------

group_configs = [
    ("ampersand", " ", "monadtall", [Match(wm_class='Brave-browser')]),
    ("eacute", "", "monadtall", [Match(wm_class='Code')]),
    ("quotedbl", "󰭆 ", "monadtall", None),
    ("apostrophe", " ", "monadtall", [Match(wm_class='Thunar')]),
    ("parenleft", " ", "monadtall", [Match(wm_class='obsidian')]),
    ("minus", " ", "monadtall", [Match(wm_class='rmpc')]),
    ("egrave", " ", "monadtall", [Match(wm_class='discord')]),
    ("underscore", " ", "max", [Match(wm_class=re.compile(r"^(steamwebhelper|Lutris|heroic)$"))]),
]

groups = [Group(icon, layout=layout_name, matches=matches) for key, icon, layout_name, matches in group_configs]

# Define scratchpads
groups.append(ScratchPad("scratchpad", [
    DropDown("terminal", "st", width=0.6, height=0.6, x=0.2, y=0.02, opacity=0.95, on_focus_lost_hide=False),
    DropDown("volume", "st -c volume -e pulsemixer", width=0.5, height=0.5, x=0.25, y=0.02, opacity=0.95, on_focus_lost_hide=False),
    DropDown("keepass", "flatpak run --command=bottles-cli com.usebottles.bottles run -b KeePass2 -p KeePass",
             width=0.6, height=0.7, x=0.3, y=0.15, opacity=0.95, on_focus_lost_hide=False),
    DropDown("editor", editor,
             width=0.8, height=0.8, x=0.1, y=0.1, opacity=0.95, on_focus_lost_hide=False),
]))

for key, icon, layout_name, matches in group_configs:
    keys.extend(
        [
            # mod + key = switch to group
            Key(
                [mod],
                key,
                lazy.group[icon].toscreen(),
                desc="Switch to group {}".format(icon),
            ),
            # mod + shift + key = switch to & move focused window to group
            Key(
                [mod, "shift"],
                key,
                lazy.window.togroup(icon, switch_group=True),
                desc="Switch to & move focused window to group {}".format(icon),
            ),
        ]
    )

# --------------------------------------------------------
# Layouts
# --------------------------------------------------------

# Define layouts and layout themes
layout_theme = {
        "margin":10,
        "border_width": 4,
        "border_focus": colors[3],
        "border_normal": colors[1]
    }

# Layout preference by monitor type:
# MonadTall - Default layout (master-stack tiling)
# BSP - Traditional monitors (16:9, 4:3)
# Columns - Ultrawide monitors (21:9, 32:9)
layouts = [
    layout.MonadTall(**layout_theme),
    layout.Bsp(**layout_theme),
    layout.Columns(**layout_theme, num_columns=3),
    layout.Max(**layout_theme),
    layout.Floating(**layout_theme),
    layout.Zoomy(**layout_theme),
]

# --------------------------------------------------------
# Widgets and Screens
# --------------------------------------------------------

# Updated widget defaults to match Polybar styling
widget_defaults = dict(
    font=font_name,  # Match Polybar font
    background=backgroundColor,
    foreground=foregroundColor,
    fontsize=16,  # Increased font size
    padding=4,
)
extension_defaults = widget_defaults.copy()

# Custom separator to match Polybar
def create_separator():
    return widget.TextBox(
        text="|",
        foreground=foregroundColorTwo,  # disabled color
        padding=8,
        fontsize=14
    )

# Toggle clock state
clock_showing_time = [True]  # Use list to make it mutable in nested function

def get_clock_text():
    """Get the clock text based on the current toggle state"""
    if clock_showing_time[0]:
        return f"<span color='#9c27b0' size='large'>󰥔</span> {subprocess.run(['date', '+%I:%M:%S %p'], capture_output=True, text=True).stdout.strip()}"
    else:
        return f"<span color='#80bfff' size='large'>󰸗</span> {subprocess.run(['date', '+%A, %d %B'], capture_output=True, text=True).stdout.strip()}"

def toggle_clock_format():
    """Toggle between time and date display"""
    def _toggle(qtile):
        clock_showing_time[0] = not clock_showing_time[0]
        widget = qtile.widgets_map.get('clock_toggle')
        if widget:
            widget.update(get_clock_text())
    return _toggle

# Custom widget for keyboard lock indicator
# Using built-in CapsNumLockIndicator widget instead of custom implementation


screens = [
    Screen(
        top=bar.Bar(
            [
                # Left modules - Layout icon, workspaces, window title
                widget.Spacer(length=8),
                widget.CurrentLayoutIcon(
                    custom_icon_paths=[f"{home}/.config/qtile/icons/layouts"],
                    foreground=colors[6][0],
                    scale=0.65,
                    padding=4
                ),
                create_separator(),
                widget.GroupBox(
                    disable_drag=True,
                    use_mouse_wheel=False,
                    active=foregroundColor,
                    inactive=foregroundColorTwo,
                    highlight_method='line',
                    highlight_color=[backgroundColor, backgroundColor],
                    this_current_screen_border=colors[3][0],  # Light cyan like waybar
                    this_screen_border=colors[1][0],
                    other_current_screen_border=colors[1][0],
                    other_screen_border=backgroundColor,
                    urgent_alert_method='text',
                    urgent_text=colors[10][0],
                    rounded=False,
                    margin_x=0,
                    margin_y=3,
                    padding_x=10,
                    padding_y=6,
                    borderwidth=3,
                    hide_unused=True,
                ),
                create_separator(),
                widget.WindowName(
                    format='{name}',
                    max_chars=60,
                    foreground=foregroundColor,
                    padding=6
                ),

                # Center - Clock (matching waybar center placement)
                widget.Spacer(),
                widget.GenPollText(
                    name='clock_toggle',
                    func=get_clock_text,
                    update_interval=0.1,
                    markup=True,
                    padding=6,
                    mouse_callbacks={
                        'Button1': lazy.function(toggle_clock_format()),
                        'Button3': lazy.spawn(f"/usr/local/bin/eww -c {home}/.config/eww open --toggle date")
                    }
                ),
                widget.TextBox(
                    text="", foreground=foregroundColor, padding=10,
                    mouse_callbacks={'Button1': lazy.spawn('dunstctl history-pop')}
                ),
                widget.Sep(linewidth=0, padding=5),
                widget.Pomodoro(
                    color_active=colors[4][0], color_break=colors[6][0], color_inactive=colors[9][0],
                    prefix_inactive='󱎫', length_pomodori=25, length_short_break=5, length_long_break=15,
                    num_pomodori=4, padding=5
                ),
                widget.Spacer(),

                # Right modules - System info (matching waybar order)
                NetworkStatus(
                    interface=network_interfaces["wifi"],
                    interface_type='wireless',
                    home=home,
                    foreground=colors[2][0],
                    background_connected=colors[4][0],
                    background_disconnected=colors[1][0],
                ),
                NetworkStatus(
                    interface=network_interfaces["ethernet"],
                    interface_type='wired',
                    home=home,
                    foreground=colors[2][0],
                    background_connected=colors[4][0],
                    background_disconnected=colors[1][0],
                ),
                create_separator(),
                widget.ThermalSensor(
                    foreground=colors[2][0], background=backgroundColor,
                    tag_sensor="Tctl", fmt=' {}', padding=5
                ),
                create_separator(),
                widget.TextBox(
                    text="󰻠",
                    foreground="#ff6b6b",
                    padding=4,
                    fontsize=18
                ),
                widget.CPU(
                    format="{load_percent:2.0f}%",
                    foreground="#FFFFFF",
                    padding=2
                ),
                create_separator(),
                widget.TextBox(
                    text="▓▓▓",
                    foreground="#4fc3f7",
                    padding=4,
                    fontsize=18
                ),
                widget.Memory(
                    format='{MemPercent:2.0f}%',
                    foreground="#FFFFFF",
                    padding=2
                ),
                create_separator(),
                widget.TextBox(
                    text="󰕾",
                    foreground="#b3e5fc",
                    padding=4,
                    fontsize=18
                ),
                widget.Volume(
                    fmt="{}",
                    mute_command="pamixer -t",
                    volume_up_command="pamixer -i 2",
                    volume_down_command="pamixer -d 2",
                    get_volume_command="pamixer --get-volume-human",
                    check_mute_command="pamixer --get-mute",
                    check_mute_string="true",
                    foreground=foregroundColor,
                    update_interval=0.1,
                    padding=2
                ),
                create_separator(),
                widget.Battery(
                    battery="BAT1",
                    charge_char='',
                    discharge_char='',
                    format='{char} {percent:2.0%}',
                    show_short_text=True,
                    full_short_text='Charged ',
                    foreground=foregroundColor,
                    background=backgroundColor,
                    charging_background=colors[6][0],
                    padding=5,
                    low_foreground=colors[9][0]
                ),
                widget.Systray(
                    icon_size=20,
                    padding=6,
                ),
                widget.Spacer(length=8),
            ],
            34,  # Match waybar's 34px height
            background=backgroundColor,
            margin=[0, 0, 0, 0],
        ) if wm_bar == "qtile" else bar.Gap(polybar_gap),
    ),
]

# --------------------------------------------------------
# Mouse and Others
# --------------------------------------------------------

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = False
floating_layout = layout.Floating(
border_width=4,
border_focus=colors[3],
border_normal=colors[1],
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="qimgv"),  # q image viewer
        Match(wm_class="lxappearance"),  # lxappearance
        Match(wm_class="pavucontrol"),  # pavucontrol
        Match(wm_class="Galculator"),  # calculator
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
