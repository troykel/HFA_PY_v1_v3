# HFA_ALL_palettes.py
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------------
# Unified Master Palette Library for "Huemanity for ALL" (HfA)
# --------------------------------------------------------------------------------------
# Organized with PEOPLE-FIRST palettes (LGBTQ+, Disability) at the top,
# then all other categories. Each category is sorted ALPHABETICALLY.
#
# Public API:
#   - palette_names_and_map() -> (names, name_to_palette)
#   - get_pack_palettes(pack_name, name_to_palette) -> (pride_palettes, extra_palettes)
#
# Updated: 2026-01-25
# --------------------------------------------------------------------------------------

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


# --------------------------------------------------------------------------------------
# SECTION 1: Data Model
# --------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Palette:
    """
    Represents a single palette / gradient definition.
    """
    name: str
    colors: List[str]
    category: str
    positions: List[float] | None = None


# --------------------------------------------------------------------------------------
# SECTION 2: Constants + Aliases
# --------------------------------------------------------------------------------------

DEFAULT_PALETTE_NAME: str = "RAINBOW - LGBTQ+"

ALIASES: Dict[str, str] = {
    "A Color Story": "A Color Story (Bundle)",
    "ASEXUAL_PRIDE": "Asexual Pride",
    "Autumn Magenta Leaf": "Autumn Magenta Leaf (Bundle)",
    "BISEXUAL_PRIDE": "Bisexual Pride",
    "Dark Lavender Color Palette": "Dark Lavender (Alt)",
    "Enchanted Garden Color Palette": "Enchanted Garden (Alt)",
    "Grey, Black and Purple": "Grey Black Purple Typography (Alt)",
    "LESBIAN_PRIDE": "Lesbian Pride",
    "NON_BINARY_PRIDE": "Non-Binary Pride",
    "Neurodiversity_rainbow": "Neurodiversity Rainbow (Alt)",
    "PANSEXUAL_PRIDE": "Pansexual Pride",
    "Pansy Color Palette": "Pansy (Alt)",
    "Pink Wine Website Palette": "Pink Wine Website (Alt)",
    "RAINBOW": "RAINBOW - LGBTQ+",
    "RAINBOW_PRIDE": "Rainbow Pride (5 Color)",
    "Silver Black Purple": "Silver Black Purple (Bundle)",
    "TRANSGENDER_PRIDE": "Transgender Pride",
    "Tropical Beach Wedding": "Tropical Beach Wedding (Bundle)",
}


def resolve_palette_name(name: str) -> str:
    """Resolve an incoming palette name using ALIASES."""
    key = (name or "").strip()
    return ALIASES.get(key, key)


def _norm_hex_list(colors: List[str]) -> List[str]:
    """Normalize colors to uppercase '#RRGGBB'."""
    out: List[str] = []
    for c in colors:
        c = (c or "").strip().upper()
        if not c.startswith("#"):
            c = "#" + c
        out.append(c)
    return out


# --------------------------------------------------------------------------------------
# SECTION 3: PEOPLE-FIRST Palettes (LGBTQ+, Disability)
# --------------------------------------------------------------------------------------

# LGBTQ+ Pride Palettes (RAINBOW first, then alphabetical)
LGBTQ_PALETTES: List[Palette] = [
    Palette(name="RAINBOW - LGBTQ+", colors=["#FF0000", "#FFA500", "#FFFF00", "#008000", "#0000FF", "#4B0082", "#EE82EE"], category="LGBTQ+"),
    Palette(name="Asexual Pride", colors=["#000000", "#A3A3A3", "#FFFFFF", "#800080"], category="LGBTQ+"),
    Palette(name="Bisexual Pride", colors=["#D60270", "#9B4F96", "#0038A8"], category="LGBTQ+"),
    Palette(name="Lesbian Pride", colors=["#A30262", "#D162A4", "#FF9B55", "#FFFFFF"], category="LGBTQ+"),
    Palette(name="Non-Binary Pride", colors=["#FFF430", "#FFFFFF", "#9C59D1", "#000000"], category="LGBTQ+"),
    Palette(name="Pansexual Pride", colors=["#FF218C", "#FFD800", "#21B1FF"], category="LGBTQ+"),
    Palette(name="Rainbow Pride (5 Color)", colors=["#E40303", "#FFED00", "#008026", "#24408E", "#732982"], category="LGBTQ+"),
    Palette(name="Transgender Pride", colors=["#55CDFC", "#FFFFFF", "#F7A8B8"], category="LGBTQ+"),
]

# Disability / Neurodiversity Palettes (alphabetical)
DISABILITY_PALETTES: List[Palette] = [
    Palette(name="ADHD Awareness", colors=["#FF6B35", "#FF8C42", "#FFA552", "#FFB86B", "#FFC583", "#FFD29C"], category="Disability"),
    Palette(name="Asperger's", colors=["#6A0DAD", "#1E90FF", "#00CED1", "#32CD32", "#FFD700"], category="Disability"),
    Palette(name="Asperger's (Bundle)", colors=["#000000", "#FFFFFF", "#FFD100", "#FFCC00", "#FF9933", "#FF6600"], category="Disability"),
    Palette(name="Autism", colors=["#D92E7F", "#2D5BFF", "#FFD400", "#00B0A8", "#FF6B00"], category="Disability"),
    Palette(name="Autism (Bundle)", colors=["#000000", "#FFFFFF", "#FFD100", "#FFCC00", "#FF9933", "#FF6600"], category="Disability"),
    Palette(name="Bipolar Disorder", colors=["#000000", "#FFFFFF"], category="Disability"),
    Palette(name="Cerebral Palsy Awareness", colors=["#00693E", "#007F4F", "#009B5C", "#00A86B", "#28B779", "#52C68A"], category="Disability"),
    Palette(name="Disability Pride Flag", colors=["#000000", "#E50000", "#FFDD00", "#FFFFFF", "#0000A4", "#008121"], category="Disability"),
    Palette(name="Disability Pride Flag (Bundle)", colors=["#585858", "#CF7280", "#EEDF77", "#E9E9E9", "#7AC1E0"], category="Disability"),
    Palette(name="Down Syndrome Awareness", colors=["#0051BA", "#0066CC", "#FFCD00", "#FFD700", "#FFE135", "#FFEB6B"], category="Disability"),
    Palette(name="Dyslexia", colors=["#F4C2C2", "#C8A2C8", "#87CEEB", "#FFD700", "#98FB98"], category="Disability"),
    Palette(name="Dyslexia (Bundle)", colors=["#FF0000", "#FFFF00", "#00FF00", "#00FFFF", "#FF00FF"], category="Disability"),
    Palette(name="Intellectual Disability Awareness", colors=["#4169E1", "#5B7FE8", "#7595EF", "#8FAAFF", "#A9BFFF", "#C3D4FF"], category="Disability"),
    Palette(name="Neurodiversity Rainbow", colors=["#F5A9B8", "#5BCFFB", "#F6D844", "#6EEB83", "#7D5BA6", "#333333"], category="Disability"),
    Palette(name="Neurodiversity Rainbow (Alt)", colors=["#FF0000", "#FFA500", "#FFFF00", "#008000", "#0000FF", "#4B0082", "#800080"], category="Disability"),
]

# --------------------------------------------------------------------------------------
# SECTION 4: Other Categories (alphabetical within each)
# --------------------------------------------------------------------------------------

# Holiday / Seasonal Palettes (alphabetical)
HOLIDAY_PALETTES: List[Palette] = [
    Palette(name="Classic Christmas", colors=["#C1121F", "#0B3D2E", "#F7F7F7", "#D4AF37", "#4E342E", "#0A1F14"], category="Holiday"),
    Palette(name="Cozy Cabin Christmas", colors=["#8B1E3F", "#1F4D3A", "#FFF1D6", "#8A5A44", "#B87333", "#2B2B2B"], category="Holiday"),
    Palette(name="Modern Icy Christmas", colors=["#0F2D2E", "#BFE7F6", "#EAF7FF", "#C0C0C0", "#D7263D", "#0B1320"], category="Holiday"),
    Palette(name="Thanksgiving Gradient", colors=["#FFFFFF", "#FDA440", "#FD6E42", "#DB437B", "#A41E9F"], category="Holiday"),
]

# Popular Palettes (alphabetical)
POPULAR_PALETTES: List[Palette] = [
    Palette(name="80s", colors=["#FF44CC", "#44FFD1", "#2F2FA2", "#FCEE09", "#0ABDC6"], category="Popular"),
    Palette(name="Campfire", colors=["#4B3E2A", "#FF6F00", "#FFD700", "#2E1A47", "#1A1A1A"], category="Popular"),
    Palette(name="Cotton Candy", colors=["#FFB7D5", "#B0E0E6", "#FFDDEE", "#F0FFFF", "#E6E6FA"], category="Popular"),
    Palette(name="Neon Retro", colors=["#FF6EC7", "#FFD700", "#39FF14", "#00FFFF", "#9400D3"], category="Popular"),
    Palette(name="Steve's 5 Wines", colors=["#4C1C24", "#8B1E3F", "#F2E2C6", "#E8F5C8", "#6B0F1A"], category="Popular"),
]

# Aesthetic / Vibe Palettes (alphabetical)
AESTHETIC_PALETTES: List[Palette] = [
    Palette(name="A Color Story", colors=["#FAD2E1", "#E2ECE9", "#BEE1E6", "#F0EFEB", "#D6E2E9"], category="Soft Pastels"),
    Palette(name="A Color Story (Bundle)", colors=["#FFB7A1", "#EFBC68", "#919F89", "#C8CFD6", "#95A1AE"], category="Pastel / Neutral"),
    Palette(name="Autumn Magenta Leaf", colors=["#5D2A42", "#FB6376", "#FFDCCC", "#FFF9EC", "#6D6875"], category="Autumn"),
    Palette(name="Autumn Magenta Leaf (Bundle)", colors=["#913E7D", "#FB0659", "#82BEAA", "#C3CD62"], category="Autumn / Vibrant"),
    Palette(name="Black White And Lime Fashion", colors=["#0B0B0C", "#2B2B30", "#F5F5F7", "#C7FF3D", "#7AC943"], category="Fashion / Neon"),
    Palette(name="Blue Green Purple", colors=["#2147B5", "#13854B", "#4C318E"], category="Typography / Bold"),
    Palette(name="Bold Boho Color Palette", colors=["#33150F", "#EEB031", "#104756", "#9E550D", "#64766C"], category="Autumn / Bold"),
    Palette(name="Celtic Blue Color Palette", colors=["#2E68BB", "#C6C042", "#AF28AA", "#C382C1", "#E2DAE0"], category="Abstract / Vibrant"),
    Palette(name="Color Harmony Glow - Coral Dahlia", colors=["#7A1E1A", "#C5522A", "#E06A4A", "#F49B52", "#4B2A16"], category="Floral / Warm"),
    Palette(name="Color Palette #322", colors=["#2D4343", "#6F8B8F", "#88A699", "#99B39A", "#B0BCBF"], category="Calm / Nature"),
    Palette(name="Colors That Go With Bright Red", colors=["#C62828", "#F27F33", "#F6C945", "#3C7A4A", "#2F6F6F"], category="Bold / Mexican"),
    Palette(name="Dark Lavender", colors=["#2B193D", "#4A2C6A", "#6E44FF", "#B8B8FF", "#EAE0FF"], category="Purple"),
    Palette(name="Dark Lavender (Alt)", colors=["#826A80", "#5D4755", "#422D35", "#2A1A1B", "#100C06"], category="Floral / Dark"),
    Palette(name="Dee's Tropical Beach Wedding (Bundle)", colors=["#026E81", "#2EB5C0", "#F7C59F", "#F27A7D", "#FFEEDB"], category="Wedding / Tropical"),
    Palette(name="Desert Florals", colors=["#F4E2C8", "#D8943A", "#C7655E", "#9A3C4A", "#5F2C2F"], category="Floral / Desert"),
    Palette(name="Enchanted Garden", colors=["#4B3F72", "#AA4465", "#F58F29", "#55DDE0", "#F0F3BD"], category="Vibrant"),
    Palette(name="Enchanted Garden (Alt)", colors=["#2F4F3E", "#7CA982", "#F2D5E5", "#D0B3E8", "#F5F2E9"], category="Garden / Pastel"),
    Palette(name="Floral Color Scheme - Primrose & Cornflower", colors=["#F7EC8D", "#8B6EC7", "#5E84E2", "#F5F4ED", "#F6A93A"], category="Floral / Spring"),
    Palette(name="Flower Colors Palette", colors=["#D90404", "#9704BF", "#F29F05", "#1C56DE", "#F27405"], category="Floral / Vibrant"),
    Palette(name="Flower Website Palette", colors=["#F7F4F2", "#F9D66F", "#E8B448", "#6C8F6B", "#9B7BB5"], category="Floral / Website"),
    Palette(name="Forest Path Movie Colors", colors=["#69573B", "#79804D", "#3E482A", "#2D2920"], category="Landscape / Forest"),
    Palette(name="Frida Kahlo Inspired", colors=["#C62828", "#F6A529", "#EF6C00", "#2E7D32", "#235C7F"], category="Art / Bold"),
    Palette(name="Grapes", colors=["#ACA7BB", "#7EA683", "#88809E", "#59012D", "#332432"], category="Food / Nature"),
    Palette(name="Green Black Grey Typography", colors=["#4A4A4D", "#6B7A51", "#000000", "#A7B48A", "#BEBEC0"], category="Typography / Minimal"),
    Palette(name="Grey Black Purple Typography", colors=["#0B0C10", "#1F2833", "#C5C6C7", "#66FCF1", "#45A29E"], category="Dark & Moody"),
    Palette(name="Grey Black Purple Typography (Alt)", colors=["#F2F2F4", "#A6A6B0", "#5B5B66", "#2B1B3B", "#6B3FA0"], category="Monochrome / Purple"),
    Palette(name="Grocery Store Color Palette", colors=["#326292", "#9AEA55", "#7DCFCB", "#9E0186", "#DCD7AF"], category="Food / Fresh"),
    Palette(name="Husky Color Palette", colors=["#272A35", "#A1B1CC", "#848B9B", "#0E7EC0", "#D0DBEE"], category="Animals / Cool"),
    Palette(name="Lavender Bee", colors=["#352124", "#796292", "#9B88D9", "#B1B3C9", "#D5B3B2"], category="Nature / Floral"),
    Palette(name="Movie Forest Path", colors=["#1E2A23", "#4A5B3C", "#355B5C", "#6B4A32", "#C1C8B7"], category="Landscape / Forest"),
    Palette(name="Palette Viola", colors=["#064680", "#31245A", "#AC6DBF", "#2A7CA3", "#58BBC2"], category="Abstract / Cool"),
    Palette(name="Pansy", colors=["#4B2C7A", "#7B4BA5", "#B38AD8", "#E6C9FF", "#1B1B1E"], category="Purple"),
    Palette(name="Pansy (Alt)", colors=["#F3E27D", "#D8B5F2", "#A46ACF", "#6A2B84", "#2A102E"], category="Floral / Spring"),
    Palette(name="Pantone Autumn Foliage", colors=["#DB864E", "#8C1C59", "#5F2167", "#34657D", "#83A413"], category="Autumn / Vibrant"),
    Palette(name="Pastel Blue", colors=["#CAF0F8", "#ADE8F4", "#90E0EF", "#48CAE4", "#00B4D8"], category="Soft Pastels"),
    Palette(name="Pink Wine Website", colors=["#2B2D42", "#8D99AE", "#EDF2F4", "#EF233C", "#D90429"], category="Modern"),
    Palette(name="Pink Wine Website (Alt)", colors=["#461D3A", "#502A50", "#7E2A53", "#BA71A2", "#ECD0EC"], category="Website / Pink"),
    Palette(name="Psychedelic Love", colors=["#131210", "#F5034F", "#F4980D", "#A9D10A", "#069F68", "#1BA0DF", "#F105ED", "#FAFAFA"], category="Retro / Psychedelic"),
    Palette(name="Silver Black Purple", colors=["#0F0F0F", "#2A2A2A", "#C0C0C0", "#6A0DAD", "#EAE0FF"], category="Dark & Moody"),
    Palette(name="Silver Black Purple (Bundle)", colors=["#4E2A8B", "#D0D3D8", "#040404"], category="Monochrome / Bold"),
    Palette(name="Teal Green And Brown", colors=["#7F6C53", "#62392E", "#325454", "#3C2F22", "#151412"], category="Interior / Earthy"),
    Palette(name="Teal Green And Charcoal", colors=["#0B4F6C", "#01BAEF", "#FBFBFF", "#757575", "#3B3B3B"], category="Earth & Nature"),
    Palette(name="Tropical Beach Wedding", colors=["#F72585", "#B5179E", "#7209B7", "#3A0CA3", "#4361EE", "#4CC9F0"], category="Vibrant"),
    Palette(name="Viola", colors=["#2D1E2F", "#6B3FA0", "#B8B8FF", "#EAE0FF", "#FFFFFF"], category="Purple"),
]

# Design Palettes (alphabetical)
DESIGN_PALETTES: List[Palette] = [
    Palette(name="Blueberry Mango Bold Combo", colors=["#A0BDF9", "#3974E8", "#182446", "#E9A72F", "#F7D45A"], category="Design"),
    Palette(name="Color Palette #3097", colors=["#2F341F", "#69394F", "#A1688F", "#B99EAB", "#E4E3EA"], category="Design"),
    Palette(name="Dreams Don't Work Blue Florals", colors=["#C8DDF8", "#8493D2", "#214F86", "#1F396A", "#F6F2E7", "#F3D8B1"], category="Design"),
    Palette(name="Spring Floral Inspired", colors=["#F3B651", "#D67155", "#5B6D3D", "#932E50"], category="Design"),
]

# Hippie Palettes (alphabetical)
HIPPIE_PALETTES: List[Palette] = [
    Palette(name="LOVE Icon", colors=["#F9F9F9", "#0F0B09", "#F2054F", "#F59313", "#0AC4F7", "#A94D0F", "#1B6612"], category="Hippie"),
    Palette(name="Peace Sign Pastel", colors=["#C9CBD1", "#2A2525", "#BABCC3", "#544F4E", "#D3E163", "#F25298", "#AEAFB3"], category="Hippie"),
    Palette(name="Peace Sign Pastel Sunset", colors=["#FAFAE5", "#F7C662", "#A3BD87", "#BB5A45", "#294B4D", "#780E17", "#15111E"], category="Hippie"),
    Palette(name="Peace Sign Rainbow", colors=["#09080C", "#FAE711", "#F3F6F1", "#E61306", "#06AC2E", "#045CF7", "#5E1711"], category="Hippie"),
    Palette(name="Peace Sign Retro", colors=["#FEFEFD", "#070507", "#F8EC12", "#F48F0E", "#084DF1", "#DB0708", "#720989"], category="Hippie"),
    Palette(name="Peace Sign Retro Roots", colors=["#C0AF2D", "#1C9C65", "#B4575B", "#0C5A76", "#96255C", "#2A193E", "#092241"], category="Hippie"),
    Palette(name="Psychedelic Cake", colors=["#62A4A6", "#A3CFD2", "#D3E2DE", "#115B62", "#121D1F", "#92A9A5", "#1A9A9A"], category="Hippie"),
    Palette(name="SamHippie420 Cake", colors=["#C77AD8", "#E0459E", "#25A9E0", "#C5E35B", "#FFD43B", "#FF8A2A", "#7A3D9A"], category="Hippie"),
    Palette(name="Scooby", colors=["#926AA6", "#63B547", "#FF8C00", "#A0522D", "#008080"], category="Hippie"),
]

# Nature Palettes (alphabetical)
NATURE_PALETTES: List[Palette] = [
    Palette(name="Autumn Ivy Leaves", colors=["#533024", "#835845", "#444B3C", "#313227"], category="Earth / Nature"),
    Palette(name="Fall Color Palette Aesthetic", colors=["#DCCDC1", "#77818C", "#F99A26", "#A13711", "#152E30"], category="Autumn / City"),
    Palette(name="Fall Colors - Warm Leaves", colors=["#CBAC83", "#AA7640", "#A7542A", "#775129", "#92311A", "#652D18", "#442815", "#2F130B"], category="Seasonal / Autumn"),
    Palette(name="Sunset Palm Beach", colors=["#4C3033", "#29160F", "#FBCF55", "#B7696E", "#4A5FA0", "#5F4871"], category="Landscape / Sunset"),
    Palette(name="Sunset Palm Beach - Deep", colors=["#29160F", "#4C3033", "#4A5FA0", "#5F4871", "#14080A"], category="Landscape / Sunset / Deep"),
    Palette(name="Sunset Palm Beach - Pastel", colors=["#8D6A71", "#6B4A3D", "#FFE5A3", "#EAA0A7", "#8D9BD0", "#9880A5"], category="Landscape / Sunset / Pastel"),
    Palette(name="Vibrant Sunrise", colors=["#FFCA28", "#FF7043", "#EC407A", "#AB47BC", "#7E57C2"], category="Earth / Nature"),
# --- Recovered from OG version - Earth Palettes ---
    Palette(name="Arctic Light", colors=["#0E4C92", "#457B9D", "#A8DADC", "#F1FAEE", "#E63946"], category="Earth / Nature"),
    Palette(name="Canyon Clay", colors=["#E07A5F", "#F2CC8F", "#3D405B", "#81B29A", "#F4F1DE"], category="Earth / Nature"),
    Palette(name="Desert Dusk", colors=["#D2B48C", "#C68642", "#8B5A2B", "#6B4226", "#3B2F2F"], category="Earth / Nature"),
    Palette(name="Forest Floor", colors=["#355E3B", "#6B8F71", "#A4B494", "#CAD2C5", "#2F3E46"], category="Earth / Nature"),
    Palette(name="Meadow Breeze", colors=["#7FB069", "#B7E4C7", "#D8F3DC", "#95D5B2", "#1B4332"], category="Earth / Nature"),
    Palette(name="Mountain Stone", colors=["#4F5B66", "#65737E", "#A7ADBA", "#C0C5CE", "#1F2833"], category="Earth / Nature"),
    Palette(name="Nature", colors=["#556B2F", "#8FBC8F", "#C2B280", "#6B4226", "#A9BA9D"], category="Earth / Nature"),
    Palette(name="Ocean Deep", colors=["#003B6F", "#0077B6", "#00B4D8", "#90E0EF", "#CAF0F8"], category="Earth / Nature"),
    Palette(name="Volcanic Ash", colors=["#2B2D42", "#4B4E6D", "#8D99AE", "#ADB5BD", "#EDF2F4"], category="Earth / Nature"),
]

# Chronic Depression Palettes (alphabetical)
CHRONIC_DEPRESSION_PALETTES: List[Palette] = [
    Palette(name="Arcoíris Oscuro", colors=["#A0BDF9", "#3974E8", "#182446", "#E9A72F", "#F7D45A"], category="Chronic Depression"),
    Palette(name="Finsternis", colors=["#2F341F", "#69394F", "#A1688F", "#B99EAB", "#E4E3EA"], category="Chronic Depression"),
    Palette(name="Niedergeschlagen", colors=["#5A0000", "#993D00", "#7C5B00", "#003300", "#00005A", "#1A0B1E", "#2E003E"], category="Chronic Depression"),
]

# --------------------------------------------------------------------------------------
# SECTION 5: Combined List (People-First, then everything else)
# --------------------------------------------------------------------------------------

ALL_PALETTES: List[Palette] = [
    # PEOPLE-FIRST: LGBTQ+ and Disability communities
    *LGBTQ_PALETTES,
    *DISABILITY_PALETTES,
    # Then all other categories
    *HOLIDAY_PALETTES,
    *POPULAR_PALETTES,
    *AESTHETIC_PALETTES,
    *DESIGN_PALETTES,
    *HIPPIE_PALETTES,
    *NATURE_PALETTES,
    *CHRONIC_DEPRESSION_PALETTES,
]


# --------------------------------------------------------------------------------------
# SECTION 6: Public API
# --------------------------------------------------------------------------------------

def palette_names_and_map(palettes: List[Palette] | None = None) -> Tuple[List[str], Dict[str, Palette]]:
    """
    Build (names, name_to_palette) from palettes.
    - Removes duplicates by palette.name
    - Ensures DEFAULT_PALETTE_NAME is first
    - Adds ALIASES for backward compatibility
    """
    palettes = palettes or ALL_PALETTES

    name_to_palette: Dict[str, Palette] = {}
    names: List[str] = []

    for p in palettes:
        normalized = Palette(name=p.name, colors=_norm_hex_list(p.colors), category=p.category)
        if normalized.name not in name_to_palette:
            name_to_palette[normalized.name] = normalized
            names.append(normalized.name)

    # Ensure default is first
    if DEFAULT_PALETTE_NAME in names:
        names.remove(DEFAULT_PALETTE_NAME)
        names.insert(0, DEFAULT_PALETTE_NAME)

    # Add aliases to mapping (not to names list)
    for alias_name, target_name in ALIASES.items():
        if target_name in name_to_palette and alias_name not in name_to_palette:
            name_to_palette[alias_name] = name_to_palette[target_name]

    return names, name_to_palette


# --------------------------------------------------------------------------------------
# SECTION 7: Curated Packs / Bundles
# --------------------------------------------------------------------------------------

RECOMMENDED_PACKS: Dict[str, Dict[str, List[str]]] = {
    "Ace & Dark Moody": {
        "pride": ["Asexual Pride"],
        "extras": ["Grey Black Purple Typography", "Silver Black Purple", "Teal Green And Charcoal"],
    },
    "Ace & Neurodiverse": {
        "pride": ["Asexual Pride"],
        "extras": ["Grey Black Purple Typography (Alt)", "Silver Black Purple", "Green Black Grey Typography", "Teal Green And Charcoal", "Neurodiversity Rainbow (Alt)"],
    },
    "All Pride Basics": {
        "pride": ["RAINBOW - LGBTQ+", "Rainbow Pride (5 Color)"],
        "extras": ["A Color Story", "Enchanted Garden", "Pansy", "Dark Lavender"],
    },
    "Community Neons & Nightlife": {
        "pride": ["Rainbow Pride (5 Color)", "Non-Binary Pride", "Bisexual Pride"],
        "extras": ["Black White And Lime Fashion", "Blue Green Purple", "Grapes", "Movie Forest Path", "Forest Path Movie Colors"],
    },
    "Disability & Mental Health": {
        "pride": ["Disability Pride Flag", "Dyslexia", "Autism", "Asperger's"],
        "extras": ["Dark Lavender (Alt)", "Color Palette #322", "Desert Florals"],
    },
    "Disability & Neurodiversity": {
        "pride": ["Disability Pride Flag", "Neurodiversity Rainbow", "Dyslexia", "Autism", "Asperger's"],
        "extras": ["Grey Black Purple Typography", "Silver Black Purple", "Teal Green And Charcoal"],
    },
    "Holiday / Seasonal": {
        "pride": [],
        "extras": ["Classic Christmas", "Cozy Cabin Christmas", "Modern Icy Christmas", "Thanksgiving Gradient"],
    },
    "LGBTQ+ Core Pride Flags": {
        "pride": ["RAINBOW - LGBTQ+", "Rainbow Pride (5 Color)"],
        "extras": ["Psychedelic Love", "Bold Boho Color Palette", "Flower Colors Palette", "Color Harmony Glow - Coral Dahlia"],
    },
    "Lesbian, Bi & Pan": {
        "pride": ["Lesbian Pride", "Bisexual Pride", "Pansexual Pride"],
        "extras": ["Autumn Magenta Leaf", "Pink Wine Website", "Pastel Blue", "Viola", "Tropical Beach Wedding", "Pink Wine Website (Alt)", "Celtic Blue Color Palette", "Palette Viola"],
    },
    "Trans & Non-Binary Focus": {
        "pride": ["Transgender Pride", "Non-Binary Pride"],
        "extras": ["A Color Story", "Enchanted Garden", "Pansy", "Dark Lavender", "A Color Story (Alt)", "Enchanted Garden (Alt)", "Pansy (Alt)", "Dark Lavender (Alt)"],
    },
}


def get_pack_palettes(pack_name: str, name_to_palette: Dict[str, Palette]) -> Tuple[List[Palette], List[Palette]]:
    """
    Given a pack name and mapping, return (pride_palettes, extra_palettes).
    """
    pride_palettes: List[Palette] = []
    extra_palettes: List[Palette] = []

    pack = RECOMMENDED_PACKS.get(pack_name)
    if not pack:
        return pride_palettes, extra_palettes

    for raw_name in pack.get("pride", []):
        resolved = resolve_palette_name(raw_name)
        p = name_to_palette.get(resolved) or name_to_palette.get(raw_name)
        if p is not None:
            pride_palettes.append(p)

    for raw_name in pack.get("extras", []):
        resolved = resolve_palette_name(raw_name)
        p = name_to_palette.get(resolved) or name_to_palette.get(raw_name)
        if p is not None:
            extra_palettes.append(p)

    return pride_palettes, extra_palettes


# --------------------------------------------------------------------------------------
# END OF FILE
# --------------------------------------------------------------------------------------
