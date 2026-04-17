# bday_card_gui.py
# =============================================================================
# B-DAY E-CARD TEMPLATE (PySide6) — GUI FILE
# =============================================================================
# What this version fixes:
#
# ✅ TOOLBAR VISIBILITY (for real this time):
#    - Some Windows styles / themes override global app stylesheets for toolbars.
#    - So we now set a *direct stylesheet* on the QToolBar itself.
#    - We also make the toolbar taller and give the buttons a clear "button" look.
#
# ✅ Menu bar fallback remains:
#    - File -> Load Image...
#    - File -> Export PNG...
#
# ✅ Keyboard shortcuts remain:
#    Ctrl+I load image
#    Ctrl+G export
#    Ctrl+P print settings
#    Ctrl+H help
#    Ctrl+Q quit
#
# Run:
#   python bday_card_gui.py
# =============================================================================

from __future__ import annotations

import sys
import threading
from typing import Optional, List

from PySide6.QtCore import Qt, QSize, QObject, Signal, QTimer
from PySide6.QtGui import QAction, QKeySequence, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

import bday_ecard_logic as logic


# =============================================================================
# SECTION 1 — TERMINAL COMMAND BRIDGE (stdin -> Qt-safe signals)
# =============================================================================

class TerminalCommandBridge(QObject):
    request_export = Signal()
    request_print_settings = Signal()
    request_help = Signal()
    request_quit = Signal()
    request_load_image = Signal()


class TerminalCommandListener(threading.Thread):
    """
    Background thread that accepts terminal commands while the GUI is open.
    If stdin isn't available (common in some IDE consoles), the thread exits.
    """
    def __init__(self, bridge: TerminalCommandBridge) -> None:
        super().__init__(daemon=True)
        self.bridge = bridge
        self._stop_flag = False

    def stop(self) -> None:
        self._stop_flag = True

    def run(self) -> None:
        while not self._stop_flag:
            try:
                cmd = input("Command (h for help)> ").strip().lower()

                if cmd in {"g", "gen", "generate", "export"}:
                    self.bridge.request_export.emit()
                elif cmd in {"i", "img", "image", "load"}:
                    self.bridge.request_load_image.emit()
                elif cmd in {"p", "print", "status"}:
                    self.bridge.request_print_settings.emit()
                elif cmd in {"h", "help", "?"}:
                    self.bridge.request_help.emit()
                elif cmd in {"q", "quit", "exit"}:
                    self.bridge.request_quit.emit()
                elif cmd == "":
                    continue
                else:
                    self.bridge.request_help.emit()

            except EOFError:
                return
            except Exception:
                continue


# =============================================================================
# SECTION 2 — MAIN WINDOW (CARD DISPLAY ONLY)
# =============================================================================

class BirthdayECardMainWindow(QMainWindow):
    """
    The card itself is the splitter area.
    The toolbar/menu are outside the card and can be used without cluttering exports.
    """

    def __init__(self, runtime: logic.CardRuntimeOptions) -> None:
        super().__init__()

        # ---------------------------------------------------------------------
        # RUNTIME OPTIONS (from terminal)
        # ---------------------------------------------------------------------
        self.runtime = runtime
        self.current_palette = logic.palette_from_name(runtime.palette_name)
        self.use_unified_canvas_color = runtime.use_unified_canvas_color
        self.image_fit_mode = runtime.image_fit_mode
        self.loaded_image_path: str = runtime.image_path or logic.DEFAULT_IMAGE_PATH
        self.loaded_image_pixmap: Optional[QPixmap] = None
        
        # Slideshow variables
        self.slideshow_enabled = runtime.enable_slideshow
        self.slideshow_images: List[str] = []  # List of image file paths
        self.slideshow_current_index: int = 0
        self.slideshow_timer: Optional[QTimer] = None

        # ---------------------------------------------------------------------
        # WINDOW BASICS
        # ---------------------------------------------------------------------
        self.setWindowTitle("B-Day e-card template (PySide6 Splitter)")
        self.setMinimumSize(QSize(1050, 650))

        # ---------------------------------------------------------------------
        # MENU BAR (FALLBACK CONTROLS)
        # ---------------------------------------------------------------------
        self._build_menu_bar()

        # ---------------------------------------------------------------------
        # ROOT
        # ---------------------------------------------------------------------
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(14, 14, 14, 14)
        root_layout.setSpacing(10)

        # ---------------------------------------------------------------------
        # CARD CANVAS
        # ---------------------------------------------------------------------
        self.canvas_splitter = QSplitter(Qt.Horizontal)
        self.canvas_splitter.setChildrenCollapsible(False)
        self.canvas_splitter.setHandleWidth(logic.SPLITTER_HANDLE_WIDTH_PX)

        self.image_panel = self._build_image_panel()
        self.message_panel = self._build_message_panel()

        self.canvas_splitter.addWidget(self.image_panel)
        self.canvas_splitter.addWidget(self.message_panel)

        if self.runtime.orientation.lower().strip().startswith("v"):
            self.canvas_splitter.setOrientation(Qt.Vertical)
        else:
            self.canvas_splitter.setOrientation(Qt.Horizontal)

        root_layout.addWidget(self.canvas_splitter, stretch=1)

        # ---------------------------------------------------------------------
        # TOOLBAR (VISIBILITY FIX: DIRECT STYLESHEET)
        # ---------------------------------------------------------------------
        self.toolbar = self._build_toolbar()

        # ---------------------------------------------------------------------
        # SHORTCUTS
        # ---------------------------------------------------------------------
        self._install_shortcuts()

        # ---------------------------------------------------------------------
        # APPLY STYLES + LOAD IMAGE
        # ---------------------------------------------------------------------
        self._apply_all_styles()
        self._load_default_image_if_available()

        logic.apply_readable_text_style(
            self.message_textedit,
            text_color_hex=self.current_palette.text_fg,
            font_point_size=self.runtime.message_font_pt or logic.DEFAULT_MESSAGE_FONT_PT,
        )

        QTimer.singleShot(0, self._apply_initial_splitter_sizes)

    # =============================================================================
    # SECTION 3 — MENU BAR
    # =============================================================================

    def _build_menu_bar(self) -> None:
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        load_action = QAction("Load Image…", self)
        load_action.triggered.connect(self._on_load_image_clicked)
        file_menu.addAction(load_action)

        export_action = QAction("Export PNG…", self)
        export_action.triggered.connect(self.export_card_to_png_dialog)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.terminal_quit)
        file_menu.addAction(quit_action)

    # =============================================================================
    # SECTION 4 — PANEL BUILDERS
    # =============================================================================

    def _build_image_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("ImagePanelFrame")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("Image")
        title.setObjectName("PanelTitleLabel")

        self.image_label = QLabel()
        self.image_label.setObjectName("ImageDisplayLabel")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(260)
        self.image_label.setWordWrap(True)
        self.image_label.setText("No image found.\n\nUse File → Load Image… or Ctrl+I.")

        # Single, more visible save-image button
        self.save_image_button = QPushButton("Save Current Image")
        self.save_image_button.setObjectName("DownloadButton")
        self.save_image_button.clicked.connect(self._save_current_image)

        layout.addWidget(title)
        layout.addWidget(self.image_label, stretch=1)
        layout.addWidget(self.save_image_button)
        return panel

    def _build_message_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("MessagePanelFrame")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("Birthday Message")
        title.setObjectName("PanelTitleLabel")

        self.message_textedit = QTextEdit()
        self.message_textedit.setObjectName("MessageTextEdit")
        self.message_textedit.setPlainText(self.runtime.birthday_message or logic.BIRTHDAY_MESSAGE)
        self.message_textedit.setLineWrapMode(QTextEdit.WidgetWidth)

        layout.addWidget(title)
        layout.addWidget(self.message_textedit, stretch=1)
        return panel

    # =============================================================================
    # SECTION 5 — SPLITTER SIZES
    # =============================================================================

    def _apply_initial_splitter_sizes(self) -> None:
        ratio = float(self.runtime.image_panel_ratio)

        if self.canvas_splitter.orientation() == Qt.Horizontal:
            total = max(1, self.canvas_splitter.width())
        else:
            total = max(1, self.canvas_splitter.height())

        first = int(total * ratio)
        second = max(1, total - first)
        self.canvas_splitter.setSizes([first, second])

        self._refresh_image_display()

    # =============================================================================
    # SECTION 6 — TOOLBAR (DIRECT STYLING)
    # =============================================================================

    def _build_toolbar(self) -> QToolBar:
        toolbar = QToolBar("Toolbar")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextOnly)

        # Create actions
        load_action = QAction("Load Image…", self)
        load_action.triggered.connect(self._on_load_image_clicked)

        export_action = QAction("Export PNG", self)
        export_action.triggered.connect(self.export_card_to_png_dialog)

        toolbar.addAction(load_action)
        toolbar.addAction(export_action)

        # Add toolbar to the window
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        # ---- CRITICAL: FORCE VISIBILITY WITH DIRECT STYLESHEET ----
        # This bypasses the issue where Windows theme overrides the global app stylesheet.
        palette = self.current_palette
        toolbar_bg = "rgba(255,255,255,0.08)"   # slightly lighter band
        button_bg = "rgba(255,255,255,0.10)"
        button_hover = "rgba(255,255,255,0.16)"
        button_border = "rgba(255,255,255,0.28)"

        toolbar.setStyleSheet(
            f"""
            QToolBar {{
                background: {toolbar_bg};
                border: 1px solid rgba(255,255,255,0.12);
                padding: 10px;
                spacing: 10px;
                min-height: 54px;
            }}
            QToolButton {{
                color: {palette.text_fg};
                background: {button_bg};
                border: 2px solid {button_border};
                border-radius: 12px;
                padding: 10px 18px;
                font-size: 15px;
                font-weight: 800;
            }}
            QToolButton:hover {{
                background: {button_hover};
                border: 2px solid {palette.accent};
            }}
            QToolButton:pressed {{
                background: rgba(255,255,255,0.22);
            }}
            """
        )

        return toolbar

    # =============================================================================
    # SECTION 7 — KEYBOARD SHORTCUTS
    # =============================================================================

    def _install_shortcuts(self) -> None:
        export_shortcut = QAction(self)
        export_shortcut.setShortcut(QKeySequence("Ctrl+G"))
        export_shortcut.triggered.connect(self.terminal_export_quick)
        self.addAction(export_shortcut)

        load_shortcut = QAction(self)
        load_shortcut.setShortcut(QKeySequence("Ctrl+I"))
        load_shortcut.triggered.connect(self._on_load_image_clicked)
        self.addAction(load_shortcut)

        print_shortcut = QAction(self)
        print_shortcut.setShortcut(QKeySequence("Ctrl+P"))
        print_shortcut.triggered.connect(self.terminal_print_settings)
        self.addAction(print_shortcut)

        help_shortcut = QAction(self)
        help_shortcut.setShortcut(QKeySequence("Ctrl+H"))
        help_shortcut.triggered.connect(self.terminal_help)
        self.addAction(help_shortcut)

        quit_shortcut = QAction(self)
        quit_shortcut.setShortcut(QKeySequence("Ctrl+Q"))
        quit_shortcut.triggered.connect(self.terminal_quit)
        self.addAction(quit_shortcut)

    # =============================================================================
    # SECTION 8 — STYLES
    # =============================================================================

    def _apply_all_styles(self) -> None:
        # General app + panel styling (NOT toolbar)
        self.setStyleSheet(
            logic.build_app_stylesheet(
                palette=self.current_palette,
                use_unified_canvas_color=self.use_unified_canvas_color,
            )
        )

        # Splitter handle styling
        self.canvas_splitter.setStyleSheet(
            logic.build_splitter_stylesheet(self.current_palette.splitter)
        )
        
        # Save-image button styling
        if hasattr(self, 'save_image_button'):
            button_bg = "rgba(255,255,255,0.10)"
            button_hover = "rgba(255,255,255,0.16)"
            button_border = "rgba(255,255,255,0.28)"
            
            self.save_image_button.setStyleSheet(
                f"""
                QPushButton#DownloadButton {{
                    color: {self.current_palette.text_fg};
                    background: rgba(255,255,255,0.18);
                    border: 2px solid {self.current_palette.accent};
                    border-radius: 12px;
                    padding: 12px 20px;
                    font-size: 15px;
                    font-weight: 800;
                }}
                QPushButton#DownloadButton:hover {{
                    background: rgba(255,255,255,0.24);
                    border: 2px solid {self.current_palette.splitter};
                }}
                QPushButton#DownloadButton:pressed {{
                    background: rgba(255,255,255,0.30);
                }}
                """
            )

        self._refresh_image_display()

    # =============================================================================
    # SECTION 9 — IMAGE LOADING + DISPLAY
    # =============================================================================

    def _load_default_image_if_available(self) -> None:
        """Load image(s) - either single image or slideshow from folder"""
        if self.slideshow_enabled and self.runtime.image_folder:
            self._load_slideshow_images()
        else:
            # Single image mode
            pixmap = logic.try_load_pixmap(self.loaded_image_path)
            if pixmap is None:
                self.loaded_image_pixmap = None
                return
            self.loaded_image_pixmap = pixmap
            self._refresh_image_display()
    
    def _load_slideshow_images(self) -> None:
        """Load images from folder for slideshow"""
        import os
        import glob
        
        folder = self.runtime.image_folder
        if not os.path.isdir(folder):
            self.image_label.setText(f"Image folder not found:\n{folder}")
            return
        
        # Find image files (common formats)
        patterns = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.webp']
        image_files = []
        for pattern in patterns:
            image_files.extend(glob.glob(os.path.join(folder, pattern)))
            # Also check uppercase extensions
            image_files.extend(glob.glob(os.path.join(folder, pattern.upper())))
        
        # Limit to max_images
        image_files = sorted(set(image_files))[:self.runtime.slideshow_max_images]
        
        if not image_files:
            self.image_label.setText(f"No images found in:\n{folder}")
            return
        
        self.slideshow_images = image_files
        self.slideshow_current_index = 0
        
        
        # Load first image
        self._show_slideshow_image(0)
        
        # Start timer if more than one image
        if len(self.slideshow_images) > 1:
            self.slideshow_timer = QTimer(self)
            self.slideshow_timer.timeout.connect(self._next_slideshow_image)
            # Convert seconds to milliseconds
            interval_ms = int(self.runtime.slideshow_pause_seconds * 1000)
            self.slideshow_timer.start(interval_ms)
    
    def _save_current_image(self) -> None:
        """Save the currently displayed image to the exports folder."""
        image_path = self.loaded_image_path
        if not image_path:
            print("✗ No image is currently loaded.")
            return

        import os
        import shutil
        from datetime import datetime

        exports_dir = logic.get_exports_dir()
        os.makedirs(exports_dir, exist_ok=True)

        # Create filename with timestamp
        basename = os.path.basename(image_path)
        name, ext = os.path.splitext(basename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest_filename = f"{name}_{timestamp}{ext}"
        dest_path = os.path.join(exports_dir, dest_filename)

        try:
            shutil.copy2(image_path, dest_path)
            print(f"✓ Image saved to: {dest_path}")
        except Exception as e:
            print(f"✗ Error saving image: {e}")

    def _show_slideshow_image(self, index: int) -> None:
        """Display a specific slideshow image by index"""
        if not self.slideshow_images or index >= len(self.slideshow_images):
            return
        
        img_path = self.slideshow_images[index]
        pixmap = logic.try_load_pixmap(img_path)
        
        if pixmap is None:
            return
        
        self.loaded_image_pixmap = pixmap
        self.loaded_image_path = img_path
        self.slideshow_current_index = index
        self._refresh_image_display()
    
    def _next_slideshow_image(self) -> None:
        """Advance to next image in slideshow (called by timer)"""
        if not self.slideshow_images:
            return
        
        # Move to next image (loop back to start)
        next_index = (self.slideshow_current_index + 1) % len(self.slideshow_images)
        self._show_slideshow_image(next_index)

    def _refresh_image_display(self) -> None:
        if self.loaded_image_pixmap is None:
            return

        mode = self.image_fit_mode.lower().strip().replace("-", "_")

        # ------------------------------------------------------------
        # Fit Mode Handling
        #   - contain     : scale to fit, center inside label
        #   - t_contain   : scale to fit, align toward TOP (helpful for tall images / accessibility)
        #   - cover       : fill label, crop overflow (best for "full bleed" look)
        # ------------------------------------------------------------
        if mode in ("contain", "t_contain", "tcontain"):
            scaled = logic.scale_pixmap_to_label_contain(self.loaded_image_pixmap, self.image_label)

            # Alignment: top for t_contain, center otherwise
            if mode in ("t_contain", "tcontain"):
                self.image_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
            else:
                self.image_label.setAlignment(Qt.AlignCenter)
        else:
            scaled = logic.scale_pixmap_to_label_cover(self.loaded_image_pixmap, self.image_label)
            self.image_label.setAlignment(Qt.AlignCenter)

        if scaled is not None:
            self.image_label.setPixmap(scaled)
            self.image_label.setText("")

    def _on_load_image_clicked(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose an image for the card",
            "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp);;All Files (*)",
        )
        if not file_path:
            return

        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            QMessageBox.warning(self, "Image Load Failed", "That file could not be loaded as an image.")
            return

        self.loaded_image_path = file_path
        self.loaded_image_pixmap = pixmap
        self._refresh_image_display()

    # =============================================================================
    # SECTION 10 — EXPORT
    # =============================================================================

    def export_card_to_png(self, output_path: str) -> bool:
        return logic.export_widget_to_png(self.canvas_splitter, output_path)

    def export_card_to_png_dialog(self) -> None:
        suggested = logic.default_export_filename()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Card to PNG",
            suggested,
            "PNG (*.png)",
        )
        if not file_path:
            return

        ok = self.export_card_to_png(file_path)
        if ok:
            QMessageBox.information(self, "Export Complete", f"Saved:\n{file_path}")
        else:
            QMessageBox.warning(self, "Export Failed", "Could not export the card to PNG.")

    # =============================================================================
    # SECTION 11 — TERMINAL COMMAND HANDLERS
    # =============================================================================

    def terminal_export_quick(self) -> None:
        output_path = logic.default_export_filename()
        ok = self.export_card_to_png(output_path)
        if ok:
            print(f"\n[EXPORT] Saved card to:\n  {output_path}\n")
        else:
            print("\n[EXPORT] FAILED\n")

    def terminal_print_settings(self) -> None:
        print("\n=== Current Card Settings ===")
        print(f"Orientation            : {'vertical' if self.canvas_splitter.orientation() == Qt.Vertical else 'horizontal'}")
        print(f"Palette                : {self.current_palette.name}")
        print(f"Unified canvas color   : {self.use_unified_canvas_color}")
        print(f"Image fit mode         : {self.image_fit_mode}")
        print(f"Image panel ratio      : {self.runtime.image_panel_ratio}")
        print(f"Image path             : {self.loaded_image_path}")
        print(f"Message font size (pt) : {self.runtime.message_font_pt or logic.DEFAULT_MESSAGE_FONT_PT}")
        print(f"Exports folder         : {logic.get_exports_dir()}")
        print("=============================\n")

    def terminal_help(self) -> None:
        logic.print_terminal_runtime_help()

    def terminal_quit(self) -> None:
        QApplication.instance().quit()

    def terminal_load_image_dialog(self) -> None:
        self._on_load_image_clicked()

    # =============================================================================
    # SECTION 12 — QT OVERRIDES
    # =============================================================================

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._refresh_image_display()


# =============================================================================
# SECTION 13 — APP ENTRY POINT
# =============================================================================

def main() -> None:
    runtime = logic.prompt_user_for_runtime_options()

    app = QApplication(sys.argv)
    window = BirthdayECardMainWindow(runtime)
    window.show()

    bridge = TerminalCommandBridge()
    bridge.request_export.connect(window.terminal_export_quick)
    bridge.request_print_settings.connect(window.terminal_print_settings)
    bridge.request_help.connect(window.terminal_help)
    bridge.request_quit.connect(window.terminal_quit)
    bridge.request_load_image.connect(window.terminal_load_image_dialog)

    logic.ensure_exports_dir_exists()
    logic.print_terminal_runtime_help()
    print(f"Exports will be saved to:\n  {logic.get_exports_dir()}\n")

    listener = TerminalCommandListener(bridge)
    listener.start()

    try:
        sys.exit(app.exec())
    finally:
        listener.stop()


if __name__ == "__main__":
    main()
