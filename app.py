import tkinter as tk
from tkinter import ttk

class CounterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Python GUI Tool")
        self.geometry("360x180")
        self.count = 0
        self._build_ui()

    def _build_ui(self):
        root_frame = ttk.Frame(self, padding=16)
        root_frame.pack(fill=tk.BOTH, expand=True)

        self.label = ttk.Label(root_frame, text="ボタンを押してカウント")
        self.label.pack(pady=(0, 12))

        self.counter_var = tk.StringVar(value="カウント: 0")
        self.counter_label = ttk.Label(root_frame, textvariable=self.counter_var, font=("Helvetica", 14, "bold"))
        self.counter_label.pack(pady=(0, 12))

        btn = ttk.Button(root_frame, text="インクリメント", command=self.increment)
        btn.pack()

        quit_btn = ttk.Button(root_frame, text="閉じる", command=self.destroy)
        quit_btn.pack(pady=(12, 0))

    def increment(self):
        self.count += 1
        self.counter_var.set(f"カウント: {self.count}")

if __name__ == "__main__":
    app = CounterApp()
    app.mainloop()
