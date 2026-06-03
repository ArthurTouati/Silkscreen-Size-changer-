# -*- coding: utf-8 -*-
#
# KiCad 10 Silkscreen Text Size Changer Action Plugin
#
# Installation Instructions:
# To install this plugin, copy this file (silkscreen_text_size_changer.py) into one of the following directories:
#
# - Windows:
#   %APPDATA%\kicad\10.0\plugins\ (usually C:\Users\<username>\AppData\Roaming\kicad\10.0\plugins\)
#   Or in the project local directory under a 'plugins' folder (e.g. <project_directory>/plugins/)
#
# - macOS:
#   ~/Library/Preferences/kicad/10.0/plugins/
#
# - Linux:
#   ~/.config/kicad/10.0/plugins/
#
# Once copied, restart KiCad or refresh external plugins in the PCB Editor (Tools > External Plugins > Refresh Plugins).
#

import pcbnew
import sys
import os

# Try importing wxPython for the user interface, with a fallback if running headlessly/outside KiCad
try:
    import wx
    HAS_WX = True
except ImportError:
    HAS_WX = False

# Fallback/Default variables
DEFAULT_WIDTH = 1.0       # mm
DEFAULT_HEIGHT = 1.0      # mm
DEFAULT_THICKNESS = 0.15  # mm


def make_wx_size(width_mm, height_mm):
    """
    Helper to construct a wxSize object or convert units to KiCad internal units.
    KiCad uses nanometers (1mm = 1,000,000 nm).
    """
    try:
        if hasattr(pcbnew, 'wxSizeMM'):
            return pcbnew.wxSizeMM(width_mm, height_mm)
    except Exception:
        pass

    try:
        width_iu = pcbnew.FromMM(width_mm)
        height_iu = pcbnew.FromMM(height_mm)
        return pcbnew.wxSize(width_iu, height_iu)
    except Exception:
        # Fallback manual unit conversion if pcbnew.FromMM fails
        width_iu = int(width_mm * 1000000)
        height_iu = int(height_mm * 1000000)
        return pcbnew.wxSize(width_iu, height_iu)


def set_text_properties(text_obj, width_mm, height_mm, thickness_mm):
    """
    Robust setter for text object width, height, and thickness.
    Handles legacy and modern KiCad API variations.
    """
    # 1. Update Width and Height
    try:
        width_iu = pcbnew.FromMM(width_mm)
        height_iu = pcbnew.FromMM(height_mm)
        text_obj.SetTextWidth(width_iu)
        text_obj.SetTextHeight(height_iu)
    except Exception:
        try:
            size_obj = make_wx_size(width_mm, height_mm)
            text_obj.SetTextSize(size_obj)
        except Exception as e:
            print("Failed to set text size: {}".format(e))

    # 2. Update Thickness
    try:
        thickness_iu = pcbnew.FromMM(thickness_mm)
        text_obj.SetTextThickness(thickness_iu)
    except Exception:
        try:
            thickness_iu = int(thickness_mm * 1000000)
            text_obj.SetTextThickness(thickness_iu)
        except Exception as e:
            print("Failed to set text thickness: {}".format(e))


if HAS_WX:
    class SilkscreenTextSizeDialog(wx.Dialog):
        def __init__(self, parent, title="Silkscreen Text Size Changer"):
            super(SilkscreenTextSizeDialog, self).__init__(
                parent, title=title, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
            )
            self.InitUI()
            self.Centre()

        def InitUI(self):
            panel = wx.Panel(self)
            main_sizer = wx.BoxSizer(wx.VERTICAL)

            # Info Header Text
            info_text = wx.StaticText(
                panel,
                label="Modify all text objects on Top/Bottom Silkscreen layers (F.SilkS & B.SilkS).\n"
                      "Includes board text, footprint references, values, and footprint graphical text."
            )
            info_font = info_text.GetFont()
            info_font.SetStyle(wx.FONTSTYLE_ITALIC)
            info_text.SetFont(info_font)

            # Form fields layout
            grid = wx.FlexGridSizer(rows=3, cols=2, vgap=12, hgap=12)

            self.lbl_width = wx.StaticText(panel, label="Text Width (mm):")
            self.txt_width = wx.TextCtrl(panel, value=str(DEFAULT_WIDTH))

            self.lbl_height = wx.StaticText(panel, label="Text Height (mm):")
            self.txt_height = wx.TextCtrl(panel, value=str(DEFAULT_HEIGHT))

            self.lbl_thickness = wx.StaticText(panel, label="Line Thickness (mm):")
            self.txt_thickness = wx.TextCtrl(panel, value=str(DEFAULT_THICKNESS))

            grid.AddMany([
                (self.lbl_width, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT), (self.txt_width, 1, wx.EXPAND),
                (self.lbl_height, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT), (self.txt_height, 1, wx.EXPAND),
                (self.lbl_thickness, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT), (self.txt_thickness, 1, wx.EXPAND)
            ])
            grid.AddGrowableCol(1, 1)

            # Assembly of UI parts
            pad_sizer = wx.BoxSizer(wx.VERTICAL)
            pad_sizer.Add(info_text, 0, wx.ALL | wx.EXPAND, 15)
            pad_sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)
            pad_sizer.Add(grid, 0, wx.ALL | wx.EXPAND, 15)

            # Dialog action buttons
            btn_sizer = wx.StdDialogButtonSizer()
            btn_ok = wx.Button(panel, wx.ID_OK, label="Apply Changes")
            btn_cancel = wx.Button(panel, wx.ID_CANCEL, label="Cancel")
            btn_sizer.AddButton(btn_ok)
            btn_sizer.AddButton(btn_cancel)
            btn_sizer.Realize()

            pad_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.BOTTOM | wx.RIGHT, 15)

            panel.SetSizer(pad_sizer)
            main_sizer.Add(panel, 1, wx.EXPAND)
            self.SetSizer(main_sizer)
            self.Fit()
            self.SetMinSize(self.GetSize())

        def GetValues(self):
            """
            Validate and return float inputs from text controls.
            """
            try:
                width = float(self.txt_width.GetValue().strip())
                height = float(self.txt_height.GetValue().strip())
                thickness = float(self.txt_thickness.GetValue().strip())

                if width <= 0 or height <= 0 or thickness <= 0:
                    raise ValueError("All measurements must be positive numbers (> 0).")

                return width, height, thickness
            except ValueError as e:
                wx.MessageBox(
                    "Invalid numeric input:\n{}\n\nPlease enter valid positive decimal values (e.g. 1.0, 0.15).".format(str(e)),
                    "Input Error", wx.OK | wx.ICON_ERROR, self
                )
                return None


class SilkscreenTextSizeChanger(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Change Silkscreen Text Size"
        self.category = "Modify PCB"
        self.description = "Changes width, height, and thickness of text on Silkscreen layers (F.SilkS and B.SilkS)"
        self.show_button_in_toolbar = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'icon.png')

    def Run(self):
        # Fallback variables easily editable at top of Run() method
        width = DEFAULT_WIDTH
        height = DEFAULT_HEIGHT
        thickness = DEFAULT_THICKNESS

        if not HAS_WX:
            # Running headlessly or without wxPython support
            print("wxPython is not available. Using hardcoded variables: Width={}mm, Height={}mm, Thickness={}mm".format(width, height, thickness))
            self.ApplyChanges(width, height, thickness)
            return

        # Show the GUI dialog
        parent = wx.GetActiveWindow()
        dialog = SilkscreenTextSizeDialog(parent)

        while True:
            result = dialog.ShowModal()
            if result == wx.ID_OK:
                values = dialog.GetValues()
                if values is not None:
                    width, height, thickness = values
                    dialog.Destroy()
                    self.ApplyChanges(width, height, thickness)
                    break
            else:
                dialog.Destroy()
                break

    def ApplyChanges(self, width_mm, height_mm, thickness_mm):
        try:
            board = pcbnew.GetBoard()
            if not board:
                error_msg = "No board is currently loaded in the PCB Editor."
                if HAS_WX:
                    wx.MessageBox(error_msg, "Error", wx.OK | wx.ICON_ERROR)
                else:
                    print("Error: {}".format(error_msg))
                return

            # Determine Layer IDs dynamically with hardcoded fallbacks
            f_silk = None
            b_silk = None

            if hasattr(pcbnew, "F_SilkS"):
                f_silk = pcbnew.F_SilkS
            if hasattr(pcbnew, "B_SilkS"):
                b_silk = pcbnew.B_SilkS

            if f_silk is None and hasattr(board, "GetLayerID"):
                f_silk = board.GetLayerID("F.SilkS")
            if b_silk is None and hasattr(board, "GetLayerID"):
                b_silk = board.GetLayerID("B.SilkS")

            # Default layer IDs if all else fails (37 is F.SilkS, 38 is B.SilkS in standard KiCad)
            if f_silk is None:
                f_silk = 37
            if b_silk is None:
                b_silk = 38

            modified_count = 0

            # 1. Iterate and modify standalone text objects on the board
            drawings = []
            if hasattr(board, "GetDrawings"):
                drawings = board.GetDrawings()

            for item in drawings:
                is_text = False
                if hasattr(pcbnew, "PCB_TEXT") and isinstance(item, pcbnew.PCB_TEXT):
                    is_text = True
                elif hasattr(pcbnew, "PCB_TEXTBOX") and isinstance(item, pcbnew.PCB_TEXTBOX):
                    is_text = True
                elif hasattr(pcbnew, "EDA_TEXT") and isinstance(item, pcbnew.EDA_TEXT):
                    is_text = True
                elif hasattr(item, "SetTextWidth") and hasattr(item, "SetTextHeight"):
                    is_text = True

                if is_text:
                    if hasattr(item, "GetLayer") and item.GetLayer() in (f_silk, b_silk):
                        set_text_properties(item, width_mm, height_mm, thickness_mm)
                        modified_count += 1

            # 2. Iterate and modify footprint-specific text objects
            footprints = []
            if hasattr(board, "GetFootprints"):
                footprints = board.GetFootprints()
            elif hasattr(board, "GetModules"):
                footprints = board.GetModules()

            for fp in footprints:
                # Reference Designator text
                if hasattr(fp, "Reference"):
                    ref = fp.Reference()
                    if ref and hasattr(ref, "GetLayer") and ref.GetLayer() in (f_silk, b_silk):
                        set_text_properties(ref, width_mm, height_mm, thickness_mm)
                        modified_count += 1

                # Value text
                if hasattr(fp, "Value"):
                    val = fp.Value()
                    if val and hasattr(val, "GetLayer") and val.GetLayer() in (f_silk, b_silk):
                        set_text_properties(val, width_mm, height_mm, thickness_mm)
                        modified_count += 1

                # Other footprint graphical items (e.g. FP_TEXT)
                if hasattr(fp, "GraphicalItems"):
                    for item in fp.GraphicalItems():
                        is_fp_text = False
                        if hasattr(pcbnew, "FP_TEXT") and isinstance(item, pcbnew.FP_TEXT):
                            is_fp_text = True
                        elif hasattr(pcbnew, "EDA_TEXT") and isinstance(item, pcbnew.EDA_TEXT):
                            is_fp_text = True
                        elif hasattr(item, "SetTextWidth") and hasattr(item, "SetTextHeight"):
                            is_fp_text = True

                        if is_fp_text:
                            if hasattr(item, "GetLayer") and item.GetLayer() in (f_silk, b_silk):
                                set_text_properties(item, width_mm, height_mm, thickness_mm)
                                modified_count += 1

            # Mark board as modified so KiCad UI updates and allows save
            if hasattr(board, "OnModify"):
                board.OnModify()

            # Refresh user interface
            if hasattr(pcbnew, "Refresh"):
                pcbnew.Refresh()
            if hasattr(pcbnew, "UpdateUserInterface"):
                pcbnew.UpdateUserInterface()

            # Dialog result info
            success_msg = "Successfully updated {} silkscreen text items.\n\n" \
                          "Width: {} mm\nHeight: {} mm\nThickness: {} mm".format(
                              modified_count, width_mm, height_mm, thickness_mm
                          )
            if HAS_WX:
                wx.MessageBox(success_msg, "Operation Complete", wx.OK | wx.ICON_INFORMATION)
            else:
                print(success_msg)

        except Exception as e:
            error_msg = "An error occurred during operation:\n{}".format(str(e))
            if HAS_WX:
                wx.MessageBox(error_msg, "Error", wx.OK | wx.ICON_ERROR)
            else:
                print("Error: {}".format(error_msg))


# Register the Action Plugin in KiCad PCBEditor
SilkscreenTextSizeChanger().register()
