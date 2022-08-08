import sys


# Get directory paths
directory = sys.path[0]

path = f"{directory}/".replace("\\", "/")

image_path = f"{path}resources/"


# To be put into settings
theme = "yellow"

blank1 = f"{image_path}blank1.png"
blank2 = f"{image_path}blank2.png"

button = {
    f"{theme}_button_normal" : f"{image_path}{theme}_button_normal.png",
    f"{theme}_button_hover" : f"{image_path}{theme}_button_hover.png",
    f"{theme}_button_press" : f"{image_path}{theme}_button_press.png",
    f"{theme}_button_disable" : f"{image_path}{theme}_button_disable.png"
}

# TODO: add all of the filepaths into entry map, toggle map, etc.
entry_normal = f"{image_path}entry_normal.png"
entry_hover = f"{image_path}entry_hover.png"
entry_focus = f"{image_path}entry_focus.png"

toggle_true = f"{image_path}toggle_true.png"
toggle_false = f"{image_path}toggle_false.png"
toggle_true_hover = f"{image_path}toggle_true_hover.png"
toggle_false_hover = f"{image_path}toggle_false_hover.png"

slider_horizontal = f"{image_path}slider_horizontal.png"

knob = f"{image_path}knob.png"

colorchooser = f"{image_path}colorchooser.png"

none = f"{image_path}none.png"
