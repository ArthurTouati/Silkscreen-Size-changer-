# KiCad Silkscreen Text Size Changer

A KiCad 10 Action Plugin that allows you to quickly and uniformly resize and adjust the thickness of all text objects on the front (`F.SilkS`) and back (`B.SilkS`) silkscreen layers.

## Features
- Updates standalone text objects, footprint references, footprint values, and other footprint graphical text.
- Provides a simple user interface using wxPython to specify exact text Width, Height, and Thickness (in mm).
- Includes backward compatibility and fallbacks, safely modifying text without crashing if specific API features aren't present.

## Installation

1. Locate the plugin file: `silkscreen_text_size_changer.py`.
2. Copy the plugin file into your KiCad plugins directory:
   - **Windows:** `%APPDATA%\kicad\10.0\plugins\` (usually `C:\Users\<username>\AppData\Roaming\kicad\10.0\plugins\`)
   - **macOS:** `~/Library/Preferences/kicad/10.0/plugins/`
   - **Linux:** `~/.config/kicad/10.0/plugins/`
   
   *Note: You can also place the script in a `plugins` folder within your specific KiCad project directory for project-local use.*

3. Open the KiCad PCB Editor.
4. Go to **Tools > External Plugins > Refresh Plugins**.

## Usage

1. In the PCB Editor, open your board.
2. Click the **Change Silkscreen Text Size** button in the top toolbar, or select it from **Tools > External Plugins > Change Silkscreen Text Size**.
3. A dialog will appear asking for the new Text Width, Text Height, and Line Thickness.
4. Enter your desired values in millimeters and click **Apply Changes**.
5. The plugin will update all silkscreen text and notify you of how many items were modified.
