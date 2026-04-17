# bday_ecard_logic.py
# =============================================================================
# B-DAY E-CARD TEMPLATE (PySide6) — LOGIC FILE
# =============================================================================
# Fixes / improvements in this version:
#
# ✅ Adds get_exports_dir() (fixes your AttributeError immediately)
# ✅ Ensures exports folder exists: ./exports/ next to this file
# ✅ Terminal prompts appear in PyCharm (no isatty() suppression)
# ✅ Adds image_panel_ratio prompt (lets you widen image panel easily)
# ✅ Adds palette aliases:
#       - Primrose Pop  -> same as Flower Pop
#       - Seal and Lime -> same as Blue Teal Lime
# ✅ Fixes Windows-unsafe strftime in default_export_filename() (no "%-M")
# =============================================================================

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import QLabel, QTextEdit, QWidget


# =============================================================================
# SECTION 1 — DEFAULTS
# =============================================================================

BIRTHDAY_MESSAGE: str = (
    "Dear Devyn, you've worked so hard \n over the years to get to where you are now; \n endured so many difficult things, \n and yet still triumphed. \n And now, you're in a really great place \n heading into the next phase of your life: \n  you got your Graduate Degree - from, of all places, \n UC Berkeley. You seem to have found your one true love \n in life: Dani, and now you both have a new home \n that you can actually afford, which in CA \n is quite the accomplishment! \n Wishing you a very memorable birthday and the brightest of futures! Love, Dad XOXOXO"
)

DEFAULT_IMAGE_PATH: str = "default_image.png"
SPLITTER_HANDLE_WIDTH_PX: int = 12
DEFAULT_MESSAGE_FONT_PT: int = 22
DEFAULT_IMAGE_PANEL_RATIO: float = 0.55
DEFAULT_IMAGE_FIT_MODE: str = "t_contain"  # options: t_contain, contain, cover

EXPORTS_DIR_NAME: str = "exports"

# Indigo-based default backgrounds for a more colorful default look
INDIGO_CANVAS_BG: str = "#24165D"
INDIGO_MESSAGE_BG: str = "#1C144A"


# =============================================================================
# SECTION 2 — PALETTES
# =============================================================================

FARBKOMBINATIONEN_PALETTES: Dict[str, Dict[str, str]] = {
# =========================================================
# 1) ALPINE NIGHT
# =========================================================
"Alpine Night (Charcoal / Snow / Lavender)": {
    "canvas_bg": INDIGO_CANVAS_BG,
    "image_bg": "#0E0F12",
    "message_bg": INDIGO_MESSAGE_BG,
    "text_fg": "#F7F3E8",
    "splitter": "#EAE0FF",
    "accent": "#68E1FF",
},
# =========================================================
# 2) RUSSIAN VIOLET
# =========================================================
"Russian Violet (Violet / Lavender / Ceil)": {
    "canvas_bg": INDIGO_CANVAS_BG,   # derived darker for comfort (optional)
    "image_bg":  "#391B49",
    "message_bg":INDIGO_MESSAGE_BG,   # keeps message panel very readable
    "text_fg":   "#FFFFFF",   # readability for low vision
    "splitter":  "#B7BEFF",
    "accent":    "#D7B4FF",
},
# =========================================================
# 3) ROYAL BLUE BOUQUET
# =========================================================
"Royal Blue Bouquet (Blue / Silver / White)": {
    "canvas_bg": INDIGO_CANVAS_BG,   # derived dark navy (optional)
    "image_bg":  "#1B268F",
    "message_bg":INDIGO_MESSAGE_BG,
    "text_fg":   "#FFFFFF",
    "splitter":  "#BBBBBD",
    "accent":    "#FFFFFF",
},
# =========================================================
# 4) CASA CHRISTMAS
# =========================================================
"Casa Christmas (Red / Teal / Night)": {
    "canvas_bg": INDIGO_CANVAS_BG,
    "image_bg":  "#09354A",
    "message_bg":INDIGO_MESSAGE_BG,
    "text_fg":   "#FFFFFF",
    "splitter":  "#39C0ED",
    "accent":    "#FF5A4F",
},
# =========================================================
# 5) AUTUMN LEAVES
# =========================================================
"Autumn Leaves (Wine / Ember / Gold)": {
    "canvas_bg": INDIGO_CANVAS_BG,   # derived darker (optional)
    "image_bg":  "#7C2C47",
    "message_bg":INDIGO_MESSAGE_BG,
    "text_fg":   "#FFFFFF",
    "splitter":  "#FFD447",
    "accent":    "#FF8A3D",
},
# =========================================================
# 6) FLOWER POP
# =========================================================
"Flower Pop (Pink / Teal / Mango / Magenta / Green)": {
    "swatches": ["#FF4D6B", "#3395A2", "#F1AB38", "#C20259", "#01A75B"],
    "canvas_bg":  INDIGO_CANVAS_BG,
    "image_bg":   "#3395A2",
    "message_bg": INDIGO_MESSAGE_BG,
    "text_fg":    "#FFFFFF",
    "title_fg":   "#F1AB38",
    "splitter":   "#01A75B",
    "border":     "#C20259",
    "accent":     "#FF4D6B",
},
# =========================================================
# 6B) PRIMROSE POP (alias of Flower Pop)
# =========================================================
"Primrose Pop (Pink / Teal / Mango / Magenta / Green)": {
    "swatches": ["#FF4D6B", "#3395A2", "#F1AB38", "#C20259", "#01A75B"],
    "canvas_bg":  INDIGO_CANVAS_BG,
    "image_bg":   "#3395A2",
    "message_bg": INDIGO_MESSAGE_BG,
    "text_fg":    "#FFFFFF",
    "title_fg":   "#F1AB38",
    "splitter":   "#01A75B",
    "border":     "#C20259",
    "accent":     "#FF4D6B",
},
# =========================================================
# 7) BLUE TEAL LIME
# =========================================================
"Blue Teal Lime (Navy / Teal / Lime)": {
    "swatches": ["#182A7F", "#008080", "#92BE30"],
    "canvas_bg":  INDIGO_CANVAS_BG,
    "image_bg":   "#008080",
    "message_bg": INDIGO_MESSAGE_BG,
    "text_fg":    "#FFFFFF",
    "title_fg":   "#92BE30",
    "splitter":   "#92BE30",
    "border":     "#182A7F",
    "accent":     "#008080",
},
# =========================================================
# 7B) SEAL AND LIME (alias of Blue Teal Lime)
# =========================================================
"Seal and Lime (Navy / Teal / Lime)": {
    "swatches": ["#182A7F", "#008080", "#92BE30"],
    "canvas_bg":  INDIGO_CANVAS_BG,
    "image_bg":   "#008080",
    "message_bg": INDIGO_MESSAGE_BG,
    "text_fg":    "#FFFFFF",
    "title_fg":   "#92BE30",
    "splitter":   "#92BE30",
    "border":     "#182A7F",
    "accent":     "#008080",
},
# =========================================================
# 8) WISTERIA OLIVINE
# =========================================================
"Wisteria Olivine (Lilac / Purple / Green)": {
    "swatches": ["#C3ACEA", "#A866BE", "#801F82", "#9FB98E", "#334E29"],
    "canvas_bg":  INDIGO_CANVAS_BG,
    "image_bg":   "#334E29",
    "message_bg": INDIGO_MESSAGE_BG,
    "text_fg":    "#FFFFFF",
    "title_fg":   "#C3ACEA",
    "splitter":   "#9FB98E",
    "border":     "#801F82",
    "accent":     "#A866BE",
},
# =========================================================
# 9) TROPICAL PATTERN
# =========================================================
"Tropical Pattern (Blue / Yellow / Pink / Orange / Teal / Plum)": {
    "swatches": ["#1E3487", "#FCBE07", "#FE3169", "#FE842E", "#04B485", "#540147"],
    "canvas_bg":  INDIGO_CANVAS_BG,
    "image_bg":   "#1E3487",
    "message_bg": INDIGO_MESSAGE_BG,
    "text_fg":    "#FFFFFF",
    "title_fg":   "#FCBE07",
    "splitter":   "#04B485",
    "border":     "#540147",
    "accent":     "#FE3169",
},
# =========================================================
# 10) BOUGAINVILLEA GREENS
# =========================================================
"Bougainvillea Greens (Magenta / Deep Green)": {
    "swatches": ["#8F0A52", "#450821", "#425B23", "#1F5C21", "#0A2C0D"],
    "canvas_bg":  INDIGO_CANVAS_BG,
    "image_bg":   "#1F5C21",
    "message_bg": INDIGO_MESSAGE_BG,
    "text_fg":    "#FFFFFF",
    "title_fg":   "#8F0A52",
    "splitter":   "#425B23",
    "border":     "#450821",
    "accent":     "#8F0A52",
},
# =========================================================
# 11) NEON SWIRL
# =========================================================
"Neon Swirl (Orange / Hot Pink / Purple / Blue / Lime)": {
    "swatches": ["#FF3C00", "#FF007F", "#9B00FF", "#008CFF", "#B8FF00"],
    "canvas_bg":  INDIGO_CANVAS_BG,
    "image_bg":   "#008CFF",
    "message_bg": INDIGO_MESSAGE_BG,
    "text_fg":    "#FFFFFF",
    "title_fg":   "#B8FF00",
    "splitter":   "#B8FF00",
    "border":     "#9B00FF",
    "accent":     "#FF007F",
},
# =========================================================
# 12) BRUME MENTHE
# =========================================================
"Brume Menthe (Mint / Lemon / Verbena)": {
    "swatches": ["#C2F2E4", "#35C8B4", "#EDF7BE", "#A4CF4A"],
    "canvas_bg":  INDIGO_CANVAS_BG,
    "image_bg":   "#14AFA0",
    "message_bg": INDIGO_MESSAGE_BG,
    "text_fg":    "#FFFFFF",
    "title_fg":   "#EDF7BE",
    "splitter":   "#A4CF4A",
    "border":     "#35C8B4",
    "accent":     "#A4CF4A",
},
# =========================================================
# 13) HONEYCOMB GLOW
# =========================================================
"Honeycomb Glow (Amber / Purple / Ember)": {
    "swatches": ["#E79742", "#873B79", "#481C4D", "#CF6742", "#512A6D"],
    "canvas_bg":  INDIGO_CANVAS_BG,
    "image_bg":   "#512A6D",
    "message_bg": INDIGO_MESSAGE_BG,
    "text_fg":    "#FFFFFF",
    "title_fg":   "#E79742",
    "splitter":   "#873B79",
    "border":     "#CF6742",
    "accent":     "#E79742",
},
# =========================================================
# 14) FLORAL SUNSET
# =========================================================
"Floral Sunset (Deep Purple / Orchid / Orange / Blush)": {
    "swatches": ["#361938", "#811C62", "#A8396C", "#FA7D29", "#F5948D"],
    "canvas_bg":  INDIGO_CANVAS_BG,
    "image_bg":   "#811C62",
    "message_bg": INDIGO_MESSAGE_BG,
    "text_fg":    "#FFFFFF",
    "title_fg":   "#F5948D",
    "splitter":   "#F5948D",
    "border":     "#A8396C",
    "accent":     "#FA7D29",
},
# =========================================================
# 15) CRYSTALS LUX
# =========================================================
"Crystals Luxe (Deep Blue / Sand / Wine / Violet)": {
    "swatches": ["#143F62", "#D8C09C", "#6F073A", "#61105C", "#410D4B"],
    "canvas_bg":  INDIGO_CANVAS_BG,
    "image_bg":   "#143F62",
    "message_bg": INDIGO_MESSAGE_BG,
    "text_fg":    "#FFFFFF",
    "title_fg":   "#D8C09C",
    "splitter":   "#6F073A",
    "border":     "#61105C",
    "accent":     "#D8C09C",
},
# =========================================================
# 16) SEEALPSEE WINTER
# =========================================================
"Seealpsee Winter (Deep Navy / Ice / Silver)": {
    "canvas_bg": INDIGO_CANVAS_BG,
    "image_bg": "#0B1020",
    "message_bg": INDIGO_MESSAGE_BG,
    "text_fg": "#F2F5FA",
    "splitter": "#DDE6F7",
    "accent": "#7DEBFF",
},
# =========================================================
# 17) OCEAN CALM
# =========================================================
"Ocean Calm (Midnight / Teal / Pearl)": {
    "canvas_bg": INDIGO_CANVAS_BG,
    "image_bg": "#06202A",
    "message_bg": INDIGO_MESSAGE_BG,
    "text_fg": "#EAF6FF",
    "splitter": "#2EE6D6",
    "accent": "#66FFF2",
},
# =========================================================
# 18) COZY BIRTHDAY
# =========================================================
"Cozy Birthday (Plum / Cream / Rose Gold)": {
    "canvas_bg": INDIGO_CANVAS_BG,
    "image_bg": "#160B1B",
    "message_bg": INDIGO_MESSAGE_BG,
    "text_fg": "#FFF6EF",
    "splitter": "#FFD0C4",
    "accent": "#FFC8D6",
},
# =========================================================
# 19) WARM CANDLELIGHT
# =========================================================
"Warm Candlelight (Espresso / Honey / Cream)": {
    "canvas_bg": INDIGO_CANVAS_BG,
    "image_bg": "#100B09",
    "message_bg": INDIGO_MESSAGE_BG,
    "text_fg": "#FFF4E8",
    "splitter": "#FFD761",
    "accent": "#FFE29C",
},
# =========================================================
# 20) FEATHER NIGHT
# =========================================================
"Feather Night (Violet / Steel / Navy)": {
    "swatches": ["#B25DBA", "#4D7B93", "#8351A8", "#1A2C54", "#2F0E39"],
    "canvas_bg":  INDIGO_CANVAS_BG,
    "image_bg":   "#1A2C54",
    "message_bg": INDIGO_MESSAGE_BG,
    "text_fg":    "#FFFFFF",
    "title_fg":   "#B25DBA",
    "splitter":   "#4D7B93",
    "border":     "#8351A8",
    "accent":     "#B25DBA",
},
# =========================================================
# 21) NEON PUNCH
# =========================================================
"Neon Punch (Orange / Hot Pink / Purple / Blue / Lime)": {
    "swatches": ["#D75329", "#FF017E", "#9B00FE", "#008CFF", "#97D75A"],
    "canvas_bg":  INDIGO_CANVAS_BG,
    "image_bg":   "#008CFF",
    "message_bg": INDIGO_MESSAGE_BG,
    "text_fg":    "#FFFFFF",
    "title_fg":   "#97D75A",
    "splitter":   "#97D75A",
    "border":     "#9B00FE",
    "accent":     "#FF017E",
},
# =========================================================
# 22) ZEBRA NEON
# =========================================================
"Zebra Neon (Purple / Magenta / Yellow / Aqua / Indigo)": {
    "swatches": ["#B700CC", "#F600AF", "#FFEB01", "#42C3D0", "#513AEE"],
    "canvas_bg":  INDIGO_CANVAS_BG,
    "image_bg":   "#513AEE",
    "message_bg": INDIGO_MESSAGE_BG,
    "text_fg":    "#FFFFFF",
    "title_fg":   "#FFEB01",
    "splitter":   "#42C3D0",
    "border":     "#B700CC",
    "accent":     "#F600AF",
},
# =========================================================
# 23) NEON WAVE
# =========================================================
"Neon Wave (Lime / Cyan / Blue / Violet / Magenta)": {
    "swatches": ["#37F04E", "#00E5FF", "#0147FF", "#8A2BE1", "#DC12E7"],
    "canvas_bg":  INDIGO_CANVAS_BG,
    "image_bg":   "#0147FF",
    "message_bg": INDIGO_MESSAGE_BG,
    "text_fg":    "#FFFFFF",
    "title_fg":   "#00E5FF",
    "splitter":   "#37F04E",
    "border":     "#8A2BE1",
    "accent":     "#DC12E7",
},
# =========================================================
# 24) ARCHWAY GLOW
# =========================================================
"Archway Glow (Indigo / Lilac / Rose / Wine)": {
    "swatches": ["#4525A2", "#A677CA", "#ABA7E3", "#890C50", "#EB5F7A"],
    "canvas_bg":  INDIGO_CANVAS_BG,
    "image_bg":   "#4525A2",
    "message_bg": INDIGO_MESSAGE_BG,
    "text_fg":    "#FFFFFF",
    "title_fg":   "#ABA7E3",
    "splitter":   "#EB5F7A",
    "border":     "#890C50",
    "accent":     "#A677CA",
},
}

DEFAULT_PALETTE_NAME: str = "Archway Glow (Indigo / Lilac / Rose / Wine)"


# =============================================================================
# SECTION 3 — DATA MODELS
# =============================================================================

@dataclass
class PaletteSelection:
    name: str
    canvas_bg: str
    image_bg: str
    message_bg: str
    text_fg: str
    splitter: str
    accent: str


@dataclass
class CardRuntimeOptions:
    orientation: str = "horizontal"
    use_unified_canvas_color: bool = False
    palette_name: str = DEFAULT_PALETTE_NAME
    image_fit_mode: str = DEFAULT_IMAGE_FIT_MODE
    image_panel_ratio: float = DEFAULT_IMAGE_PANEL_RATIO
    image_path: Optional[str] = None
    birthday_message: Optional[str] = BIRTHDAY_MESSAGE
    message_font_pt: Optional[int] = DEFAULT_MESSAGE_FONT_PT
    # Slideshow options
    enable_slideshow: bool = False
    slideshow_pause_seconds: float = 7.0
    slideshow_max_images: int = 5
    image_folder: Optional[str] = None

def get_palette_names() -> List[str]:
    return list(FARBKOMBINATIONEN_PALETTES.keys())


def palette_from_name(palette_name: str) -> PaletteSelection:
    if palette_name not in FARBKOMBINATIONEN_PALETTES:
        palette_name = DEFAULT_PALETTE_NAME
    data = FARBKOMBINATIONEN_PALETTES[palette_name]
    return PaletteSelection(
        name=palette_name,
        canvas_bg=data["canvas_bg"],
        image_bg=data["image_bg"],
        message_bg=data["message_bg"],
        text_fg=data["text_fg"],
        splitter=data["splitter"],
        accent=data.get("accent", data["text_fg"]),
    )


# =============================================================================
# SECTION 4 — EXPORTS DIRECTORY (THIS IS WHAT FIXES YOUR ERROR)
# =============================================================================

def _script_dir() -> str:
    """
    Folder where this file lives.
    """
    return os.path.dirname(os.path.abspath(__file__))


def get_exports_dir() -> str:
    """
    Public function used by GUI to show export folder path.
    """
    return os.path.join(_script_dir(), EXPORTS_DIR_NAME)


def ensure_exports_dir_exists() -> None:
    """
    Creates exports folder if missing.
    """
    os.makedirs(get_exports_dir(), exist_ok=True)


# =============================================================================
# SECTION 5 — TERMINAL INPUT HELPERS (PYCHARM FRIENDLY)
# =============================================================================

def _safe_input(prompt: str, default: str = "") -> str:
    """
    Always TRY to prompt, even inside PyCharm.
    If stdin doesn't work, we fall back to default.

    This avoids the 'isatty() == False' problem.
    """
    try:
        value = input(prompt)
        value = value.strip()
        return value if value else default
    except EOFError:
        return default
    except Exception:
        return default


def _parse_float_in_range(raw_value: str, default_value: float, min_value: float, max_value: float) -> float:
    """Parse a float without relying on exceptions for normal control flow."""
    s = (raw_value or "").strip()
    if not s:
        return float(default_value)

    # Allow simple floats like: 0.55, .55, 1, 1.0
    normalized = s
    if normalized.startswith("."):
        normalized = "0" + normalized

    # Validate characters (digits + at most one dot)
    if normalized.count(".") > 1:
        return float(default_value)

    candidate = normalized.replace(".", "", 1)
    if not candidate.isdigit():
        return float(default_value)

    value = float(normalized)
    if value < min_value:
        return float(min_value)
    if value > max_value:
        return float(max_value)
    return float(value)



def prompt_user_for_runtime_options() -> CardRuntimeOptions:
    runtime = CardRuntimeOptions()

    print("\n" + "=" * 72)
    print("B-DAY E-CARD TEMPLATE — Terminal Setup")
    print("=" * 72)

    # 1) Orientation
    o = _safe_input("1) Orientation: [H]orizontal or [V]ertical [H]: ", default="H").lower()
    runtime.orientation = "vertical" if o.startswith("v") else "horizontal"

    # 2) Background mode
    b = _safe_input("2) Background: Use ONE canvas color for both panels? [y/N]: ", default="n").lower()
    runtime.use_unified_canvas_color = b.startswith("y")

    # 3) Palette choice
    names = get_palette_names()
    print("\n3) Choose a palette:")
    for idx, name in enumerate(names, start=1):
        print(f"   {idx:>2}. {name}")
    default_idx = str(names.index(DEFAULT_PALETTE_NAME) + 1)
    p = _safe_input(f"Enter palette number [default {default_idx}]: ", default=default_idx)

    try:
        chosen_index = int(p)
        if 1 <= chosen_index <= len(names):
            runtime.palette_name = names[chosen_index - 1]
        else:
            runtime.palette_name = DEFAULT_PALETTE_NAME
    except Exception:
        runtime.palette_name = DEFAULT_PALETTE_NAME

    # 4) Image fit (clearer options)
    #     T  -> Top-Contain (fit inside, NO crop, aligned toward TOP)
    #     C  -> Contain     (fit inside, NO crop, centered)
    #     V  -> Cover       (fills panel, MAY crop edges)
    f = _safe_input(
        "4) Image fit: [T]op-contain (recommended), [C]ontain (center), or co[V]er (crop) [T]: ",
        default="T",
    ).lower()

    if f.startswith("v"):
        runtime.image_fit_mode = "cover"
    elif f.startswith("c"):
        runtime.image_fit_mode = "contain"
    else:
        runtime.image_fit_mode = "t_contain"

    # 5) Slideshow
    s = _safe_input("5) Slideshow in image panel (rotate through images)? [Y/n]: ", default="Y").lower()
    runtime.enable_slideshow = not s.startswith("n")

    if runtime.enable_slideshow:
        # Slideshow pause seconds
        pause_input = _safe_input("   Slideshow pause seconds (1.0–20.0) [7.0]: ", default="7.0")
        runtime.slideshow_pause_seconds = _parse_float_in_range(pause_input, 7.0, 1.0, 20.0)

        # Max images
        max_img_input = _safe_input("   How many slideshow images (1–25) [5]: ", default="5")
        try:
            runtime.slideshow_max_images = max(1, min(25, int(max_img_input)))
        except:
            runtime.slideshow_max_images = 5

        # Image folder
        default_folder = os.path.join(os.path.dirname(__file__), "CARD IMAGES")
        use_default = _safe_input(f"6) Use default image folder?\n   {default_folder} [Y/n]: ", default="Y").lower()
        if use_default.startswith("n"):
            runtime.image_folder = _safe_input("   Enter image folder path: ", default=default_folder)
        else:
            runtime.image_folder = default_folder
    else:
        # Single image path
        ip = _safe_input(f"6) Image path (ENTER for default: {DEFAULT_IMAGE_PATH}): ", default=DEFAULT_IMAGE_PATH)
        runtime.image_path = ip

    # 7) Image panel size (share of the card)
    recommended_default = 0.55 if runtime.orientation == "horizontal" else 0.60
    r = _safe_input(
        f"7) Image panel size (0.30–0.80). Example: 0.55 = 55% of the card {'width' if runtime.orientation == 'horizontal' else 'height'} (image panel) [{recommended_default}]: ",
        default=str(recommended_default),
    )
    runtime.image_panel_ratio = _parse_float_in_range(r, recommended_default, 0.30, 0.80)

    # 8) Message font size
    fs = _safe_input(f"8) Message font size (pt) [default {DEFAULT_MESSAGE_FONT_PT}]: ", default=str(DEFAULT_MESSAGE_FONT_PT))
    try:
        runtime.message_font_pt = max(10, int(fs))
    except Exception:
        runtime.message_font_pt = DEFAULT_MESSAGE_FONT_PT

    # 9) Message text
    cm = _safe_input("9) Use default message text? [Y/n]: ", default="Y").lower()
    if cm.startswith("n"):
        print("\nPaste your message. Finish with a single line containing only: END")
        lines: List[str] = []
        while True:
            line = _safe_input("", default="")
            if line.strip() == "END":
                break
            lines.append(line)
        runtime.birthday_message = "\n".join(lines).strip() if lines else BIRTHDAY_MESSAGE
    else:
        runtime.birthday_message = BIRTHDAY_MESSAGE

    ensure_exports_dir_exists()

    print("\nSetup complete. The card window will open now.")
    print("=" * 72 + "\n")
    return runtime


def print_terminal_runtime_help() -> None:
    print("\nTerminal commands while the window is open:")
    print("  g  -> generate/export card (PNG) to the exports folder")
    print("  i  -> load a different image (opens file dialog)")
    print("  p  -> print current settings")
    print("  h  -> show this help")
    print("  q  -> quit")
    print("\nBackup keyboard shortcuts:")
    print("  Ctrl+G export   Ctrl+I load image   Ctrl+P settings   Ctrl+H help   Ctrl+Q quit\n")


# =============================================================================
# SECTION 6 — STYLESHEET BUILDERS
# =============================================================================

def build_app_stylesheet(palette: PaletteSelection, use_unified_canvas_color: bool) -> str:
    if use_unified_canvas_color:
        canvas_bg = palette.canvas_bg
        image_bg = palette.canvas_bg
        message_bg = palette.canvas_bg
    else:
        canvas_bg = palette.canvas_bg
        image_bg = palette.image_bg
        message_bg = palette.message_bg

    return f"""
    QMainWindow {{
        background: {canvas_bg};
    }}

    QFrame#ImagePanelFrame {{
        background: {image_bg};
        border-radius: 22px;
        border: 1px solid rgba(255,255,255,0.10);
    }}
    QFrame#MessagePanelFrame {{
        background: {message_bg};
        border-radius: 22px;
        border: 1px solid rgba(255,255,255,0.10);
    }}

    QLabel#PanelTitleLabel {{
        font-size: 20px;
        font-weight: 800;
        padding: 6px 6px;
        color: {palette.accent};
    }}

    QLabel#ImageDisplayLabel {{
        border: none;
        border-radius: 18px;
        background: rgba(0,0,0,0.10);
        color: rgba(255,255,255,0.85);
    }}

    QToolBar {{
        background: rgba(0,0,0,0.20);
        border: 1px solid rgba(255,255,255,0.08);
    }}
    """


def build_splitter_stylesheet(splitter_color_hex: str) -> str:
    return f"""
    QSplitter::handle {{
        background: {splitter_color_hex};
        border: 1px solid rgba(0,0,0,0.35);
        border-radius: 4px;
    }}
    """


def apply_readable_text_style(text_edit: QTextEdit, text_color_hex: str, font_point_size: int) -> None:
    font = QFont()
    font.setFamilies(["Century Gothic", "Roboto", "Arial", "Verdana"])
    font.setPointSize(int(font_point_size))
    text_edit.setFont(font)

    text_edit.setStyleSheet(
        f"""
        QTextEdit {{
            background: rgba(255,255,255,0.08);
            color: {text_color_hex};
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 18px;
            padding: 18px;
        }}
        """
    )


# =============================================================================
# SECTION 7 — IMAGE LOADING + SCALING
# =============================================================================

def try_load_pixmap(image_path: str) -> Optional[QPixmap]:
    if not image_path:
        return None
    if not os.path.isfile(image_path):
        return None
    pixmap = QPixmap(image_path)
    return None if pixmap.isNull() else pixmap


def _label_target_size(label: QLabel) -> Optional[tuple[int, int]]:
    if label.width() <= 2 or label.height() <= 2:
        return None
    return max(1, label.width() - 6), max(1, label.height() - 6)


def scale_pixmap_to_label_contain(pixmap: QPixmap, label: QLabel) -> Optional[QPixmap]:
    target = _label_target_size(label)
    if target is None:
        return None
    tw, th = target
    return pixmap.scaled(tw, th, Qt.KeepAspectRatio, Qt.SmoothTransformation)


def scale_pixmap_to_label_cover(pixmap: QPixmap, label: QLabel) -> Optional[QPixmap]:
    target = _label_target_size(label)
    if target is None:
        return None
    tw, th = target

    scaled = pixmap.scaled(tw, th, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

    x = max(0, (scaled.width() - tw) // 2)
    y = max(0, (scaled.height() - th) // 2)
    return scaled.copy(x, y, tw, th)


# =============================================================================
# SECTION 8 — EXPORT HELPERS
# =============================================================================

def default_export_filename() -> str:
    """
    Windows-safe timestamp.
    NOTE: "%-M" is not portable on Windows, so we use "%H-%M-%S".
    """
    ensure_exports_dir_exists()
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return os.path.join(get_exports_dir(), f"birthday_card_{ts}.png")


def export_widget_to_png(widget: QWidget, output_path: str) -> bool:
    try:
        ensure_exports_dir_exists()
        if not output_path.lower().endswith(".png"):
            output_path += ".png"
        pix = widget.grab()
        return pix.save(output_path, "PNG")
    except Exception:
        return False
