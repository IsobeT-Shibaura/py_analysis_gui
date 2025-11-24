#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
from wx.lib.buttons import GenButton
import os
import sys
import locale
import ctypes
from ctypes import wintypes

# Windows 専用実装: Ubuntu/Linux 用フォールバックとリモート取得機能は削除済み
# ダークテーマ用の簡易カラーパレット
PALETTE = {
    "bg": "#1e1f22",
    "panel_bg": "#25262a",
    "content_bg": "#2c2d31",
    "accent": "#3d7bff",
    "accent_hover": "#5d8dff",
    "text": "#d8d9dc",
    "muted": "#9aa0a6",
    "border": "#34363a",
}

PAGES = [
    ("log", "Register Log"),
    ("results", "View Results"),
    ("correction", "Calculate Correction"),
    ("config", "Configuration"),
]

class Sidebar(wx.Panel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.buttons = {}
        self.active_key = None
        self._build_ui()

    def _build_ui(self):
        self.SetBackgroundColour(PALETTE["panel_bg"])
        sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, label="MENU")
        title.SetForegroundColour(PALETTE["text"])
        font = title.GetFont(); title.SetFont(font.Bold())
        sizer.Add(title, flag=wx.LEFT | wx.TOP | wx.BOTTOM, border=10)
        for idx, (key, label) in enumerate(PAGES):
            btn = GenButton(self, -1, label=label, name=key)
            btn.SetBezelWidth(0)
            btn.SetUseFocusIndicator(False)
            btn.SetForegroundColour(PALETTE["text"])
            btn.SetBackgroundColour(PALETTE["panel_bg"])
            btn.Bind(wx.EVT_BUTTON, self.on_select)
            self.buttons[key] = btn
            sizer.Add(btn, 0, wx.EXPAND)
            if idx < len(PAGES) - 1:
                line = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
                line.SetBackgroundColour(PALETTE["border"])
                sizer.Add(line, 0, wx.EXPAND)
        sizer.AddStretchSpacer()
        self.SetSizer(sizer)
        self._apply_active_style("log")

    def _apply_active_style(self, key):
        for k, b in self.buttons.items():
            if k == key:
                b.SetBackgroundColour(PALETTE["accent"])
                b.SetForegroundColour("#ffffff")
            else:
                b.SetBackgroundColour(PALETTE["panel_bg"])
                b.SetForegroundColour(PALETTE["text"])
        self.active_key = key
        self.Refresh()

    def on_select(self, event):
        key = event.GetEventObject().GetName()
        self._apply_active_style(key)
        self.callback(key)

class FileDropTarget(wx.FileDropTarget):
    """Drag & Drop handler for file paths."""
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def OnDropFiles(self, x, y, filenames):
        if filenames:
            self.callback(filenames[0])
        return True

class ContentPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.pages = {}
        self.current = None
        self._build_pages()

    def _build_pages(self):
        for key, _ in PAGES:
            panel = wx.Panel(self)
            vs = wx.BoxSizer(wx.VERTICAL)
            panel.SetBackgroundColour(PALETTE["content_bg"])
            if key == "log":
                title = wx.StaticText(panel, label="Select a log file")
                title.SetForegroundColour(PALETTE["text"])
                font = title.GetFont(); title.SetFont(font.Bold())
                vs.Add(title, flag=wx.ALL, border=12)
                file_btn = wx.Button(panel, label="Select Log File")
                file_btn.Bind(wx.EVT_BUTTON, self.on_open_file)
                file_btn.SetForegroundColour(PALETTE["text"])
                vs.Add(file_btn, flag=wx.LEFT | wx.RIGHT | wx.TOP, border=12)
                self.path_ctrl = wx.TextCtrl(panel, style=wx.TE_READONLY)
                self.path_ctrl.SetBackgroundColour(PALETTE["panel_bg"])
                self.path_ctrl.SetForegroundColour(PALETTE["text"])
                vs.Add(self.path_ctrl, flag=wx.EXPAND | wx.ALL, border=12)
                drop_target = FileDropTarget(self._on_file_dropped)
                self.path_ctrl.SetDropTarget(drop_target)
            else:
                msg = wx.StaticText(panel, label=f"{key.capitalize()} page (placeholder)")
                msg.SetForegroundColour(PALETTE["muted"])
                vs.Add(msg, flag=wx.ALL, border=16)
            panel.SetSizer(vs)
            panel.Hide()
            self.pages[key] = panel
        root_sizer = wx.BoxSizer(wx.VERTICAL)
        for p in self.pages.values():
            root_sizer.Add(p, 1, wx.EXPAND)
        self.SetSizer(root_sizer)

    def show_page(self, key):
        if self.current:
            self.pages[self.current].Hide()
        self.pages[key].Show()
        self.current = key
        self.Layout()

    def on_open_file(self, event):
        path = self._select_file()
        if path:
            self.path_ctrl.SetValue(path)

    def _on_file_dropped(self, path):
        """Callback for drag & drop files from explorer."""
        self.path_ctrl.SetValue(path)

    def _select_file(self):
        """Return a selected file path (Windows only) with wx fallback."""
        if not sys.platform.startswith('win'):
            return None
        # Try native dialog first
        try:
            class OPENFILENAMEW(ctypes.Structure):
                _fields_ = [
                    ("lStructSize", wintypes.DWORD),
                    ("hwndOwner", wintypes.HWND),
                    ("hInstance", wintypes.HINSTANCE),
                    ("lpstrFilter", wintypes.LPWSTR),
                    ("lpstrCustomFilter", wintypes.LPWSTR),
                    ("nMaxCustFilter", wintypes.DWORD),
                    ("nFilterIndex", wintypes.DWORD),
                    ("lpstrFile", wintypes.LPWSTR),
                    ("nMaxFile", wintypes.DWORD),
                    ("lpstrFileTitle", wintypes.LPWSTR),
                    ("nMaxFileTitle", wintypes.DWORD),
                    ("lpstrInitialDir", wintypes.LPWSTR),
                    ("lpstrTitle", wintypes.LPWSTR),
                    ("Flags", wintypes.DWORD),
                    ("nFileOffset", wintypes.WORD),
                    ("nFileExtension", wintypes.WORD),
                    ("lpstrDefExt", wintypes.LPWSTR),
                    ("lCustData", wintypes.LPARAM),
                    ("lpfnHook", wintypes.LPVOID),
                    ("lpTemplateName", wintypes.LPWSTR),
                    ("pvReserved", wintypes.LPVOID),
                    ("dwReserved", wintypes.DWORD),
                    ("FlagsEx", wintypes.DWORD),
                ]
            ofn = OPENFILENAMEW()
            buffer_size = 65535
            file_buffer = ctypes.create_unicode_buffer(buffer_size)
            ofn.lStructSize = ctypes.sizeof(OPENFILENAMEW)
            ofn.hwndOwner = 0
            ofn.hInstance = 0
            ofn.lpstrFilter = "All Files\0*.*\0Log Files (*.log)\0*.log\0\0"
            ofn.nFilterIndex = 1
            ofn.lpstrFile = file_buffer
            ofn.nMaxFile = buffer_size
            ofn.lpstrTitle = "Select log file"
            OFN_FILEMUSTEXIST = 0x00001000
            OFN_PATHMUSTEXIST = 0x00000800
            ofn.Flags = OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST
            if ctypes.windll.comdlg32.GetOpenFileNameW(ctypes.byref(ofn)):
                path = file_buffer.value.strip()
                if path:
                    return path
        except Exception:
            pass
        # Fallback wx dialog
        with wx.FileDialog(
            self,
            message="Select log file",
            wildcard="Log Files (*.log)|*.log|All Files (*.*)|*.*",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
        ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                return dlg.GetPath()
        return None

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="wxPython GUI Tool", size=(960, 620))
        self.SetBackgroundColour(PALETTE["bg"])
        self.splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        self.splitter.SetBackgroundColour(PALETTE["bg"])
        self.sidebar = Sidebar(self.splitter, self.show_page)
        self.content = ContentPanel(self.splitter)
        self.splitter.SplitVertically(self.sidebar, self.content, 230)
        self.content.show_page("log")
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetBackgroundColour(PALETTE["panel_bg"])
        # SetForegroundColour は戻り値 bool のため末尾の () は不要
        self.statusbar.SetForegroundColour(PALETTE["muted"])
        self.statusbar.SetStatusText("Ready")
        self.Centre()

    def show_page(self, key):
        self.content.show_page(key)
        if hasattr(self.sidebar, "_apply_active_style"):
            self.sidebar._apply_active_style(key)
        label = dict(PAGES)[key]
        self.statusbar.SetStatusText(f"Current: {label}")

class App(wx.App):
    def OnInit(self):
        # ロケール取得 (getdefaultlocale 非推奨のため代替)
        try:
            sys_loc = (locale.getlocale()[0] or os.environ.get('LANG', '')).lower()
        except Exception:
            sys_loc = os.environ.get('LANG', '').lower()
        want_ja = 'ja' in sys_loc or os.environ.get('APP_LANG', '').startswith('ja')
        if want_ja:
            try:
                self.locale = wx.Locale(wx.LANGUAGE_JAPANESE)
            except Exception:
                self.locale = None
        frame = MainFrame()
        ja_font_candidates = ["Noto Sans JP", "Yu Gothic UI", "Meiryo", "IPAGothic"]
        if want_ja:
            for fam in ja_font_candidates:
                font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, fam)
                if font.IsOk():
                    frame.SetFont(font)
                    break
        frame.Show()
        return True

if __name__ == "__main__":
    app = App()
    app.MainLoop()
