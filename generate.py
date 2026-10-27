"""Builds dark_mode.svg and light_mode.svg for the GitHub profile README.

Edit the CONTENT section, then run:  python generate.py
"""
import json
import os
import subprocess
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

# ---------------------------------------------------------------- CONTENT ---

HANDLE = "mark@markcole.dev"

LOGO = [
    "███╗   ███╗ ██████╗",
    "████╗ ████║██╔════╝",
    "██╔████╔██║██║     ",
    "██║╚██╔╝██║██║     ",
    "██║ ╚═╝ ██║╚██████╗",
    "╚═╝     ╚═╝ ╚═════╝",
    "",
    "Mukisa Mark Cole",
    "─────────────────",
    "Software Engineer · Co-Founder Kianrover",
    "Creator of the Nevela framework",
    "Business Systems · AI Automation",
    "Uganda 🇺🇬",
    
]

# None = blank spacer row, str = section heading, (key, value) = info row.
ROWS = [
    ("Focus", "business systems + AI automation"),
    ("Backend", "Laravel"),
    ("Frontend", "React"),
    ("Data", "PostgreSQL · MySQL · Redis"),
    ("Deploy", "Laravel Cloud · Vercel · Docker"),
    ("Based", "Uganda · East Africa"),
    None,
    "Roles",
    ("Kianrover", "Co-Founder · kianrover.com"),
    ("Nevela", "Creator · framework documentation"),
    None,
    "Building",
    ("Larex POS", "POS + ecommerce · inventory · sales"),
    ("GETA", "water billing · tenant bills · SMS"),
    ("IKIPS", "savings platform · KYC · analytics"),
    ("Portfolio", "AI knowledge assistant · markcole.dev"),
    None,
    "Services",
    ("Business Systems", "POS · Inventory · CRM · Dashboards"),
    ("AI Automation", "AI assistants · RAG · workflows"),
    ("Integrations", "Payments · SMS · Email · APIs"),
    ("Custom Software", "Internal tools · portals · web apps"),
    None,
    "Contact",
    ("Email", "markcole683@gmail.com"),
    ("Portfolio", "markcole.dev"),
    ("X", "@MarkColeMUKISA"),
    ("GitHub", "MarkColeMukisa"),
    ("Facebook", "MarkColeMukisa"),
    ("Instagram", "MarkColeMukisa"),
    ("LinkedIn", "MarkColeMukisa"),
    ("TikTok", "@markcolemukisa"),
    None,
    "GitHub Stats",
    ("Repos", "{repos}"),
    ("Stars", "{stars}"),
    ("Followers", "{followers}"),
]

GITHUB_USER = "MarkColeMukisa"

MANIFESTO = [
    "// I build software for real business problems —",
    "// business systems, AI automation, and integrations.",
    "// Built for East Africa. Designed to scale beyond it.",
]

PROMPT = ("markcole.dev", "have a business problem? let's build the solution.")

# ------------------------------------------------------------ GITHUB STATS ---

def github_token():
    """GITHUB_TOKEN if set, else the logged-in gh CLI's token (needed to see private repos)."""
    if token := os.environ.get("GITHUB_TOKEN"):
        return token
    try:
        return subprocess.run(["gh", "auth", "token"], capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def github_stats(user):
    """Repo/star/follower counts, including private repos when a token is available.

    Stat rows read "—" if the API is unreachable.
    """
    token = github_token()

    def get(path):
        headers = {"Accept": "application/vnd.github+json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        req = urllib.request.Request(f"https://api.github.com/{path}", headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.load(r)

    # With a token, list every repo the user owns (public + private);
    # without one, only public repos are visible.
    listing = ("user/repos?affiliation=owner&visibility=all" if token
               else f"users/{user}/repos?type=owner")
    try:
        profile = get(f"users/{user}")
        count = stars = 0
        page = 1
        while repos := get(f"{listing}&per_page=100&page={page}"):
            count += len(repos)
            stars += sum(r["stargazers_count"] for r in repos)
            page += 1
        if not token:
            print("warning: no GitHub token found, counting public repos only")
        return dict(repos=count, stars=stars, followers=profile["followers"])
    except Exception as e:
        print(f"warning: GitHub stats unavailable ({e})")
        return dict(repos="—", stars="—", followers="—")


# ----------------------------------------------------------------- THEMES ---

THEMES = {
    "dark": dict(
        bg="#0D1117", key="#FFA657", val="#7EE787", hd="#E6EDF3", dot="#484F58",
        rule="#30363D", accent="#2DD4BF", shine="#CCFBF1", mani="#7EE787",
    ),
    "light": dict(
        bg="#F6F8FA", key="#953800", val="#0A3069", hd="#1F2328", dot="#C2CFDE",
        rule="#D0D7DE", accent="#0F766E", shine="#2DD4BF", mani="#0A3069",
    ),
}

# ----------------------------------------------------------------- LAYOUT ---

WIDTH = 1040
LINE = 20
INFO_X = 400
KEY_WIDTH = 14    # key + dots, so every value starts in the same column
LINE_CHARS = 59   # total width of heading lines (text + ─ rule)
MAX_CHARS = 68    # widest info row that still fits inside the card

BLINK = ('<animate attributeName="opacity" values="1;1;0;0" '
         'keyTimes="0;0.5;0.5;1" dur="1.1s" repeatCount="indefinite"/>')


def heading(label, cursor=False):
    used = len(label) + 1 + (2 if cursor else 0)
    cur = f'<tspan class="cur">▊{BLINK}</tspan> ' if cursor else ""
    return (f'<tspan class="hd">{escape(label)}</tspan> {cur}'
            f'<tspan class="rule">{"─" * (LINE_CHARS - used)}</tspan>')


def info(key, value):
    dots = KEY_WIDTH - len(key)
    width = 2 + len(key) + 2 + dots + 1 + len(value)
    assert width <= MAX_CHARS, f"row too wide ({width} chars): {key}: {value}"
    return (f'<tspan class="dot">. </tspan><tspan class="key">{escape(key)}</tspan>'
            f'<tspan class="col">: </tspan><tspan class="dot">{"." * dots} </tspan>'
            f'<tspan class="val">{escape(value)}</tspan>')


def build(name, t, stats):
    info_lines = [heading(HANDLE, cursor=True)]
    for row in ROWS:
        if isinstance(row, tuple):
            row = (row[0], row[1].format(**stats))
        if row is None:
            info_lines.append("")
        elif isinstance(row, str):
            info_lines.append(heading(row))
        else:
            info_lines.append(info(*row))

    top = 34
    info_bottom = top + LINE * (len(info_lines) - 1)
    logo_top = top + (info_bottom - top - LINE * (len(LOGO) - 1)) // 2
    divider = info_bottom + 34
    mani_top = divider + 16
    prompt_y = mani_top + LINE * (len(MANIFESTO) - 1) + 34
    height = prompt_y + 18

    out = [
        "<?xml version='1.0' encoding='UTF-8'?>",
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}px" height="{height}px" '
        "font-family=\"'JetBrains Mono','Cascadia Code','Consolas','SFMono-Regular',"
        'ui-monospace,monospace" font-size="15px">',
        "<defs>",
        f'<linearGradient id="shine-{name}" x1="0" y1="0" x2="1" y2="0" gradientUnits="objectBoundingBox">',
        f'  <stop offset="0" stop-color="{t["accent"]}"/>',
        f'  <stop offset="0.45" stop-color="{t["accent"]}"/>',
        f'  <stop offset="0.5" stop-color="{t["shine"]}"/>',
        f'  <stop offset="0.55" stop-color="{t["accent"]}"/>',
        f'  <stop offset="1" stop-color="{t["accent"]}"/>',
        '  <animateTransform attributeName="gradientTransform" type="translate" '
        'from="-1 0" to="1 0" dur="4.5s" repeatCount="indefinite"/>',
        "</linearGradient>",
        "</defs>",
        "<style>",
        f'.key{{fill:{t["key"]};font-weight:700}}',
        f'.val{{fill:{t["val"]}}}',
        f'.hd{{fill:{t["hd"]};font-weight:700}}',
        f'.col{{fill:{t["hd"]}}}',
        f'.dot{{fill:{t["dot"]}}}',
        f'.rule{{fill:{t["rule"]}}}',
        f'.cur{{fill:{t["accent"]};font-weight:700}}',
        f'.mani{{fill:{t["mani"]};font-style:italic;opacity:0.92}}',
        f'.ascii{{fill:url(#shine-{name});font-weight:700}}',
        "text,tspan{white-space:pre}",
        "</style>",
        f'<rect width="{WIDTH}px" height="{height}px" fill="{t["bg"]}" rx="12"/>',
        '<text class="ascii">',
    ]
    for i, line in enumerate(LOGO):
        out.append(f'<tspan x="40" y="{logo_top + i * LINE}">{escape(line)}</tspan>')
    out.append("</text>")

    out.append(f'<text fill="{t["hd"]}">')
    for i, line in enumerate(info_lines):
        y = top + i * LINE
        out.append(f'<tspan x="{INFO_X}" y="{y}">{line}</tspan>' if line
                   else f'<tspan x="{INFO_X}" y="{y}" class="dot"> </tspan>')
    out.append("</text>")

    out.append(f'<line x1="24" y1="{divider}" x2="{WIDTH - 24}" y2="{divider}" '
               f'stroke="{t["rule"]}" stroke-width="1"/>')
    for i, line in enumerate(MANIFESTO):
        out.append(f'<text x="24" y="{mani_top + i * LINE}" class="mani">{escape(line)}</text>')
    user, message = PROMPT
    out.append(f'<text x="24" y="{prompt_y}"><tspan class="key">{escape(user)}</tspan>'
               f'<tspan class="col">:~$ </tspan><tspan class="val">{escape(message)}</tspan>'
               f'<tspan class="cur"> ▊{BLINK}</tspan></text>')
    out.append("</svg>")

    path = Path(__file__).with_name(f"{name}_mode.svg")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {path.name} ({WIDTH}x{height})")


if __name__ == "__main__":
    stats = github_stats(GITHUB_USER)
    for theme_name, theme in THEMES.items():
        build(theme_name, theme, stats)
