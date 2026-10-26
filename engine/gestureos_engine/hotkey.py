"""Windows global emergency-stop shortcut support."""

import ctypes
import threading
from ctypes import wintypes
from typing import Callable


MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
WM_HOTKEY = 0x0312
VK_X = 0x58
HOTKEY_ID = 0x4753


class GlobalEmergencyHotkey:
    """Register Ctrl+Alt+Shift+X without consuming ordinary key presses."""

    def __init__(
        self,
        callback: Callable[[], None],
        user32=None,
        kernel32=None,
    ):
        self.callback = callback
        self.user32 = user32 or ctypes.windll.user32
        self.kernel32 = kernel32 or ctypes.windll.kernel32
        self.thread = None
        self.thread_id = None
        self.registered = False
        self._stop = threading.Event()
        self._ready = threading.Event()
        self._registration_error = None

    @property
    def registration_error(self):
        return self._registration_error

    def start(self):
        if self.thread is not None:
            return self.registered

        self._stop.clear()
        self._ready.clear()
        self._registration_error = None
        self.thread = threading.Thread(
            target=self._run,
            name="GestureOS-EmergencyHotkey",
            daemon=True,
        )
        self.thread.start()
        self._ready.wait(timeout=2.0)
        return self.registered

    def _run(self):
        self.thread_id = self.kernel32.GetCurrentThreadId()
        self.registered = bool(
            self.user32.RegisterHotKey(
                None,
                HOTKEY_ID,
                MOD_CONTROL | MOD_ALT | MOD_SHIFT,
                VK_X,
            )
        )
        if not self.registered:
            self._registration_error = ctypes.WinError()
            self._ready.set()
            return

        self._ready.set()
        message = wintypes.MSG()
        try:
            while not self._stop.is_set():
                result = self.user32.PeekMessageW(
                    ctypes.byref(message), None, 0, 0, 1
                )
                if result:
                    if message.message == WM_HOTKEY:
                        self.callback()
                    self.user32.TranslateMessage(ctypes.byref(message))
                    self.user32.DispatchMessageW(ctypes.byref(message))
                else:
                    self._stop.wait(0.05)
        finally:
            self.user32.UnregisterHotKey(None, HOTKEY_ID)
            self.registered = False

    def stop(self):
        self._stop.set()
        if self.thread_id is not None:
            self.user32.PostThreadMessageW(
                self.thread_id, 0x0012, 0, 0
            )
        if self.thread is not None:
            self.thread.join(timeout=2.0)
            if self.thread.is_alive():
                raise RuntimeError("Emergency hotkey thread did not stop.")
        self.thread = None
        self.thread_id = None
        self.registered = False
