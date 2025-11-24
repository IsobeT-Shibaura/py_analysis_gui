#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import os
import sys
import locale
import ctypes
from ctypes import wintypes
try:
    from remote_windows_dialog_client import request_windows_file  # type: ignore
except Exception:
    def request_windows_file():
        return None

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
        self._build_ui()

    def _build_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        header_box = wx.BoxSizer(wx.HORIZONTAL)
        self.toggle_btn = wx.Button(self, label="◀", size=(40, 28))
        self.toggle_btn.Bind(wx.EVT_BUTTON, self.on_toggle)
        header_box.Add(self.toggle_btn, flag=wx.LEFT | wx.TOP, border=4)
        title = wx.StaticText(self, label="Menu")
        header_box.Add(title, flag=wx.LEFT | wx.TOP | wx.ALIGN_CENTER_VERTICAL, border=4)
        sizer.Add(header_box, flag=wx.EXPAND | wx.BOTTOM, border=4)
        for key, label in PAGES:
            btn = wx.Button(self, label=label, name=key)
            btn.Bind(wx.EVT_BUTTON, self.on_select)
            sizer.Add(btn, flag=wx.EXPAND | wx.ALL, border=4)
        sizer.AddStretchSpacer()
        self.SetSizer(sizer)

    def on_select(self, event):
        key = event.GetEventObject().GetName()
        self.callback(key)

    def on_toggle(self, event):
        frame = self.GetTopLevelParent()
        frame.toggle_sidebar()

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
            if key == "log":
                title = wx.StaticText(panel, label="Please select a log file")
                font = title.GetFont(); font = font.Bold(); title.SetFont(font)
                vs.Add(title, flag=wx.ALL, border=10)
                file_btn = wx.Button(panel, label="Select Log File")
                file_btn.Bind(wx.EVT_BUTTON, self.on_open_file)
                vs.Add(file_btn, flag=wx.LEFT | wx.RIGHT | wx.TOP, border=10)
                self.path_ctrl = wx.TextCtrl(panel, style=wx.TE_READONLY)
                vs.Add(self.path_ctrl, flag=wx.EXPAND | wx.ALL, border=10)
                # Enable drag & drop from file explorer
                drop_target = FileDropTarget(self._on_file_dropped)
                self.path_ctrl.SetDropTarget(drop_target)
            else:
                # Simple placeholder panel text in English
                msg = wx.StaticText(panel, label=f"{key} page (placeholder)")
                vs.Add(msg, flag=wx.ALL, border=20)
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
        """Return a selected file path.

        Windows: use Win32 GetOpenFileNameW for the native (Common Item) dialog.
        Other OS: fallback to wx.FileDialog.
        """
        # Try remote Windows dialog first (Ubuntu -> Windows service)
        remote_path = request_windows_file()
        if remote_path:
            return remote_path
        if sys.platform.startswith('win'):
            try:
                # Structure for GetOpenFileNameW
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
                # Filter: description\0pattern\0...\0\0  (final double null)
                ofn.lpstrFilter = "All Files\0*.*\0Log Files (*.log)\0*.log\0\0"
                ofn.nFilterIndex = 1
                ofn.lpstrFile = file_buffer
                ofn.nMaxFile = buffer_size
                ofn.lpstrTitle = "Select log file"
                # Flags: OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST
                OFN_FILEMUSTEXIST = 0x00001000
                OFN_PATHMUSTEXIST = 0x00000800
                ofn.Flags = OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST
                # Call native dialog
                if ctypes.windll.comdlg32.GetOpenFileNameW(ctypes.byref(ofn)):
                    path = file_buffer.value.strip()
                    return path if path else None
            except Exception:
                # fallback below
                pass
        # Non-Windows or fallback
        with wx.FileDialog(
            self,
            message="Select log file",
            wildcard="*.*",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
        ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                return dlg.GetPath()
        return None

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="wxPython GUI Tool", size=(900, 600))
        self.splitter = wx.SplitterWindow(self)
        self.sidebar = Sidebar(self.splitter, self.show_page)
        self.content = ContentPanel(self.splitter)
        self.splitter.SplitVertically(self.sidebar, self.content, 220)
        self.content.show_page("log")
        self._build_menu()
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText("Ready")
        self.Centre()

    def _build_menu(self):
        menubar = wx.MenuBar()
        view_menu = wx.Menu()
        item_toggle = view_menu.Append(wx.ID_ANY, "Toggle Sidebar\tCtrl+B")
        self.Bind(wx.EVT_MENU, lambda evt: self.toggle_sidebar(), item_toggle)
        menubar.Append(view_menu, "View")
        self.SetMenuBar(menubar)
        accel = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('B'), item_toggle.GetId())])
        self.SetAcceleratorTable(accel)

    def toggle_sidebar(self):
        showing = self.sidebar.IsShown()
        self.sidebar.Show(not showing)
        if showing:
            self.splitter.SetSashPosition(0)
            self.statusbar.SetStatusText("Sidebar hidden")
        else:
            self.splitter.SetSashPosition(220)
            self.statusbar.SetStatusText("Sidebar visible")
        self.sidebar.GetParent().Layout()

    def show_page(self, key):
        self.content.show_page(key)
        label = dict(PAGES)[key]
        self.statusbar.SetStatusText(f"Current: {label}")

class App(wx.App):
    def OnInit(self):
        # 日本語ロケール初期化 (失敗しても英語継続)
        sys_loc = locale.getdefaultlocale()[0] or ""
        want_ja = 'ja' in sys_loc or os.environ.get('APP_LANG', '').startswith('ja')
        if want_ja:
            try:
                self.locale = wx.Locale(wx.LANGUAGE_JAPANESE)
            except Exception:
                self.locale = None
        frame = MainFrame()
        # 日本語フォントが利用可能なら適用 (存在しない場合は無視)
        ja_font_candidates = ["Noto Sans CJK JP", "Noto Sans JP", "IPAGothic", "TakaoGothic"]
        if want_ja:
            for fam in ja_font_candidates:
                font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, fam)
                if font.IsOk():
                    frame.SetFont(font)
                    break
        frame.Show()
        return True

if __name__ == "__main__":
    app = App()
    app.MainLoop()
