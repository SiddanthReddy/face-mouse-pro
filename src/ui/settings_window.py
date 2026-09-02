"""
Modern Desktop Settings Control Panel for Face Mouse Pro.
Built with CustomTkinter for real-time bidirectional parameter tuning.
"""

import threading
import tkinter as tk
from collections.abc import Callable
from typing import Any

import customtkinter as ctk

from src.config.config_manager import ConfigManager
from src.utils.logger import setup_logger

logger = setup_logger("SettingsPanel")


class SettingsPanel(ctk.CTk):
    """
    Modern dark-mode GUI control panel providing live slider adjustments for all tracking parameters.
    """

    def __init__(self, config_manager: ConfigManager, on_change_callback: Callable | None = None):
        super().__init__()
        self.config_manager = config_manager
        self.on_change_callback = on_change_callback

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Face Mouse Pro — Settings & Calibration")
        self.geometry("640x720")
        self.minsize(580, 650)

        # Build UI layout
        self._build_ui()
        logger.info("SettingsPanel GUI initialized.")

    def _build_ui(self):
        # Header banner
        header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("#1E293B", "#0F172A"))
        header_frame.pack(fill="x", padx=0, pady=0)

        title_lbl = ctk.CTkLabel(
            header_frame,
            text="FACE MOUSE PRO",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#00F5D4",
        )
        title_lbl.pack(pady=(12, 2))

        subtitle_lbl = ctk.CTkLabel(
            header_frame,
            text="Real-Time Human-Computer Interface Settings",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#94A3B8",
        )
        subtitle_lbl.pack(pady=(0, 12))

        # Scrollable container for settings sections
        scroll_frame = ctk.CTkScrollableFrame(self, corner_radius=8, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # -------------------------------------------------------------
        # Section 1: Cursor Motion Tuning
        # -------------------------------------------------------------
        self._build_section_header(scroll_frame, "🎯 Cursor Motion & Sensitivity")

        cursor_cfg = self.config_manager.get("cursor")
        self.sens_x_slider, self.sens_x_val = self._create_slider(
            scroll_frame,
            "X Sensitivity",
            0.5,
            5.0,
            cursor_cfg.get("sensitivity_x", 2.2),
            0.1,
            lambda v: self._update_config("cursor", "sensitivity_x", round(float(v), 2)),
        )
        self.sens_y_slider, self.sens_y_val = self._create_slider(
            scroll_frame,
            "Y Sensitivity",
            0.5,
            5.0,
            cursor_cfg.get("sensitivity_y", 2.0),
            0.1,
            lambda v: self._update_config("cursor", "sensitivity_y", round(float(v), 2)),
        )
        self.deadzone_slider, self.deadzone_val = self._create_slider(
            scroll_frame,
            "Motion Deadzone",
            0.001,
            0.030,
            cursor_cfg.get("deadzone_x", 0.008),
            0.001,
            lambda v: self._update_deadzone(float(v)),
        )
        self.accel_slider, self.accel_val = self._create_slider(
            scroll_frame,
            "Acceleration Curve",
            1.0,
            2.0,
            cursor_cfg.get("acceleration_curve", 1.2),
            0.05,
            lambda v: self._update_config("cursor", "acceleration_curve", round(float(v), 2)),
        )

        # Inversion checkboxes
        inv_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        inv_frame.pack(fill="x", pady=6)

        self.inv_x_var = tk.BooleanVar(value=cursor_cfg.get("invert_x", False))
        self.inv_x_chk = ctk.CTkCheckBox(
            inv_frame,
            text="Invert X Axis",
            variable=self.inv_x_var,
            command=lambda: self._update_config("cursor", "invert_x", self.inv_x_var.get()),
        )
        self.inv_x_chk.pack(side="left", padx=10)

        self.inv_y_var = tk.BooleanVar(value=cursor_cfg.get("invert_y", False))
        self.inv_y_chk = ctk.CTkCheckBox(
            inv_frame,
            text="Invert Y Axis",
            variable=self.inv_y_var,
            command=lambda: self._update_config("cursor", "invert_y", self.inv_y_var.get()),
        )
        self.inv_y_chk.pack(side="left", padx=10)

        # -------------------------------------------------------------
        # Section 2: Gesture & Blink Thresholds
        # -------------------------------------------------------------
        self._build_section_header(scroll_frame, "👁️ Blink & Gesture Recognition")

        gestures_cfg = self.config_manager.get("gestures")
        self.ear_slider, self.ear_val = self._create_slider(
            scroll_frame,
            "Blink EAR Threshold",
            0.12,
            0.35,
            gestures_cfg.get("blink_ear_threshold", 0.21),
            0.01,
            lambda v: self._update_config("gestures", "blink_ear_threshold", round(float(v), 2)),
        )
        self.dbl_slider, self.dbl_val = self._create_slider(
            scroll_frame,
            "Double Click Window (s)",
            0.20,
            0.80,
            gestures_cfg.get("double_click_window_sec", 0.40),
            0.05,
            lambda v: self._update_config("gestures", "double_click_window_sec", round(float(v), 2)),
        )
        self.drag_slider, self.drag_val = self._create_slider(
            scroll_frame,
            "Long Blink Drag Duration (s)",
            0.40,
            1.50,
            gestures_cfg.get("long_blink_duration_sec", 0.80),
            0.05,
            lambda v: self._update_config("gestures", "long_blink_duration_sec", round(float(v), 2)),
        )
        self.mar_slider, self.mar_val = self._create_slider(
            scroll_frame,
            "Mouth Open (MAR) Threshold",
            0.25,
            0.70,
            gestures_cfg.get("mouth_mar_threshold", 0.45),
            0.02,
            lambda v: self._update_config("gestures", "mouth_mar_threshold", round(float(v), 2)),
        )

        # -------------------------------------------------------------
        # Section 3: Scrolling Speed
        # -------------------------------------------------------------
        self._build_section_header(scroll_frame, "📜 Scroll Settings")

        scroll_cfg = self.config_manager.get("scroll")
        self.scroll_slider, self.scroll_val = self._create_slider(
            scroll_frame,
            "Scroll Speed (Clicks)",
            5,
            80,
            scroll_cfg.get("scroll_speed", 30),
            1,
            lambda v: self._update_config("scroll", "scroll_speed", int(float(v))),
        )

        # -------------------------------------------------------------
        # Action Buttons Footer
        # -------------------------------------------------------------
        action_frame = ctk.CTkFrame(self, fg_color=("#1E293B", "#0F172A"), corner_radius=0)
        action_frame.pack(fill="x", side="bottom", padx=0, pady=0)

        btn_container = ctk.CTkFrame(action_frame, fg_color="transparent")
        btn_container.pack(pady=12)

        reset_btn = ctk.CTkButton(
            btn_container,
            text="Reset Defaults",
            fg_color="#475569",
            hover_color="#334155",
            width=130,
            command=self._reset_defaults,
        )
        reset_btn.pack(side="left", padx=10)

        save_btn = ctk.CTkButton(
            btn_container,
            text="Save to Disk",
            fg_color="#00F5D4",
            text_color="#0F172A",
            hover_color="#00D2B4",
            font=ctk.CTkFont(weight="bold"),
            width=130,
            command=self._save_config,
        )
        save_btn.pack(side="left", padx=10)

        close_btn = ctk.CTkButton(
            btn_container,
            text="Close Panel",
            fg_color="#F43F5E",
            hover_color="#E11D48",
            width=110,
            command=self.destroy,
        )
        close_btn.pack(side="left", padx=10)

    def _build_section_header(self, parent, title: str):
        lbl = ctk.CTkLabel(
            parent,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="#38BDF8",
            anchor="w",
        )
        lbl.pack(fill="x", pady=(15, 6))

    def _create_slider(
        self, parent, label: str, min_val: float, max_val: float, init_val: float, step: float, on_change: Callable
    ):
        container = ctk.CTkFrame(parent, fg_color="#1E293B", corner_radius=6)
        container.pack(fill="x", pady=4, padx=2)

        top_row = ctk.CTkFrame(container, fg_color="transparent")
        top_row.pack(fill="x", padx=10, pady=(6, 2))

        lbl = ctk.CTkLabel(top_row, text=label, font=ctk.CTkFont(size=13), text_color="#E2E8F0")
        lbl.pack(side="left")

        val_lbl = ctk.CTkLabel(
            top_row,
            text=f"{init_val:.3f}" if isinstance(init_val, float) else str(init_val),
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#00F5D4",
        )
        val_lbl.pack(side="right")

        def _slider_callback(v):
            val_lbl.configure(text=f"{float(v):.3f}" if step < 0.1 else f"{float(v):.2f}")
            on_change(v)

        slider = ctk.CTkSlider(
            container,
            from_=min_val,
            to=max_val,
            number_of_steps=int((max_val - min_val) / step) if step > 0 else 50,
            command=_slider_callback,
            progress_color="#00F5D4",
            button_color="#38BDF8",
            button_hover_color="#0EA5E9",
        )
        slider.set(init_val)
        slider.pack(fill="x", padx=10, pady=(0, 8))

        return slider, val_lbl

    def _update_config(self, section: str, key: str, value: Any):
        self.config_manager.set(section, key, value, auto_save=True)
        if self.on_change_callback:
            self.on_change_callback(section, key, value)

    def _update_deadzone(self, value: float):
        v = round(value, 3)
        self.config_manager.set("cursor", "deadzone_x", v, auto_save=False)
        self.config_manager.set("cursor", "deadzone_y", v, auto_save=True)
        if self.on_change_callback:
            self.on_change_callback("cursor", "deadzone_x", v)
            self.on_change_callback("cursor", "deadzone_y", v)

    def _reset_defaults(self):
        self.config_manager.reset_to_defaults()
        if self.on_change_callback:
            self.on_change_callback("all", "reset", None)
        self.destroy()
        logger.info("Settings reset to defaults from UI.")

    def _save_config(self):
        self.config_manager.save()
        logger.info("Settings manually saved to disk.")


def launch_settings_async(
    config_manager: ConfigManager, on_change_callback: Callable | None = None
) -> threading.Thread:
    """
    Spawns the CustomTkinter settings window in a dedicated non-blocking thread.
    """

    def _run():
        app = SettingsPanel(config_manager, on_change_callback)
        app.mainloop()

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return thread
