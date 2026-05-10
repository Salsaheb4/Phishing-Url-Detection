"""Generate presentation/URL-Project-Presentation.pptx — dark navy + cyan theme."""
from __future__ import annotations
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.oxml.ns import qn
from lxml import etree

ROOT = Path(__file__).resolve().parent.parent
FIGS = ROOT / "outputs" / "figures"
OUT  = Path(__file__).resolve().parent / "URL-Project-Presentation.pptx"

# ── Dimensions ────────────────────────────────────────────────────────────────
SLIDE_W = 12_192_000
SLIDE_H =  6_858_000
IN = 914_400  # 1 inch in EMU

# ── Palette ───────────────────────────────────────────────────────────────────
BG_DARK    = RGBColor(0x0D, 0x1B, 0x2A)
CYAN       = RGBColor(0x00, 0xC8, 0xFF)
SECONDARY  = RGBColor(0x1E, 0x3A, 0x5F)
CARD_DARK  = RGBColor(0x0F, 0x26, 0x3D)
HIGHLIGHT  = RGBColor(0x00, 0x4E, 0x6E)
ROW_ALT    = RGBColor(0x0F, 0x22, 0x33)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
GREY_TEXT  = RGBColor(0xA8, 0xC0, 0xD0)
TAG_LR     = RGBColor(0x1A, 0x6B, 0xAA)
TAG_TREE   = RGBColor(0x2E, 0x7D, 0x32)
TAG_ENS    = RGBColor(0x6A, 0x1E, 0x9A)

TOTAL = 10


# ── Low-level helpers ─────────────────────────────────────────────────────────

def _rgb_hex(rgb: RGBColor) -> str:
    return f"{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"


def add_rect(slide, l, t, w, h, fill: RGBColor, line: RGBColor | None = None, line_w=Pt(1)):
    from pptx.util import Emu as E
    sh = slide.shapes.add_shape(1, int(l), int(t), int(w), int(h))  # 1 = rectangle
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    if line:
        sh.line.color.rgb = line
        sh.line.width = line_w
    else:
        sh.line.fill.background()
    return sh


def add_text(slide, l, t, w, h, text, size, bold=False, color=WHITE,
             align=PP_ALIGN.LEFT, italic=False, wrap=True):
    tb = slide.shapes.add_textbox(int(l), int(t), int(w), int(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.auto_size = None
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = "Calibri"
    return tb


def add_img(slide, filename, l, t, w, h):
    path = FIGS / filename
    if not path.exists():
        return
    slide.shapes.add_picture(str(path), int(l), int(t), int(w), int(h))


def add_background(slide):
    sh = add_rect(slide, 0, 0, SLIDE_W, SLIDE_H, BG_DARK)
    sp_tree = slide.shapes._spTree
    sp_tree.remove(sh._element)
    sp_tree.insert(2, sh._element)


def add_header_bar(slide, title):
    bar_h = int(0.65 * IN)
    add_rect(slide, 0, 0, SLIDE_W, bar_h, SECONDARY)
    add_rect(slide, 0, 0, int(0.12 * IN), bar_h, CYAN)
    add_text(slide, int(0.20 * IN), int(0.05 * IN), SLIDE_W - int(0.4 * IN), bar_h,
             title, 26, bold=True, color=WHITE, align=PP_ALIGN.LEFT)


def add_progress_bar(slide, n):
    bar_h = int(0.07 * IN)
    bar_t = SLIDE_H - bar_h
    add_rect(slide, 0, bar_t, SLIDE_W, bar_h, SECONDARY)
    add_rect(slide, 0, bar_t, int(SLIDE_W * n / TOTAL), bar_h, CYAN)


def set_cell_bg(cell, rgb: RGBColor):
    tc = cell._tc
    tcPr = tc.find(qn('a:tcPr'))
    if tcPr is None:
        tcPr = etree.SubElement(tc, qn('a:tcPr'))
    for old in list(tcPr):
        if old.tag in (qn('a:solidFill'), qn('a:gradFill'), qn('a:noFill')):
            tcPr.remove(old)
    sf = etree.SubElement(tcPr, qn('a:solidFill'))
    sc = etree.SubElement(sf, qn('a:srgbClr'))
    sc.set('val', _rgb_hex(rgb))


def set_cell_text(cell, text, size=13, bold=False, color=WHITE, align=PP_ALIGN.CENTER):
    tf = cell.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = str(text)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "Calibri"


def add_arrow(slide, l, t, w, h):
    from pptx.oxml.ns import nsmap
    sh = slide.shapes.add_shape(13, int(l), int(t), int(w), int(h))  # 13 = RIGHT_ARROW
    sh.fill.solid()
    sh.fill.fore_color.rgb = CYAN
    sh.line.fill.background()
    return sh


def bullet_run(tf, text, size, color, bold=False, first=False):
    if first:
        p = tf.paragraphs[0]
    else:
        p = tf.add_paragraph()
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "Calibri"
    return p


# ── Slide 1: Title ────────────────────────────────────────────────────────────

def slide_01_title(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide)

    # Top thin cyan stripe
    add_rect(slide, 0, 0, SLIDE_W, int(0.025 * IN), CYAN)

    # Centered title block
    cy = int(1.1 * IN)
    add_text(slide, int(0.6 * IN), cy, SLIDE_W - int(1.2 * IN), int(1.5 * IN),
             "Machine Learning-Based Detection of\nPhishing Web Pages Using URL Features",
             36, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    # Cyan accent bar
    bar_y = int(3.05 * IN)
    add_rect(slide, int(0.6 * IN), bar_y, SLIDE_W - int(1.2 * IN), int(0.04 * IN), CYAN)

    # Authors side by side
    auth_y = bar_y + int(0.18 * IN)
    auth_w = int(4.5 * IN)
    for i, (name, sid, email) in enumerate([
        ("Saleh Alsaheb", "20220045", "sal20220045@std.psut.edu.jo"),
        ("Ismael Alhindi", "20220379", "ism20220379@std.psut.edu.jo"),
    ]):
        ax = int(0.6 * IN) + i * (auth_w + int(0.8 * IN))
        add_text(slide, ax, auth_y, auth_w, int(0.45 * IN),
                 name, 20, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_text(slide, ax, auth_y + int(0.45 * IN), auth_w, int(0.32 * IN),
                 sid, 14, color=GREY_TEXT, align=PP_ALIGN.CENTER)
        add_text(slide, ax, auth_y + int(0.77 * IN), auth_w, int(0.30 * IN),
                 email, 12, color=GREY_TEXT, align=PP_ALIGN.CENTER, italic=True)

    # Institution / course
    inst_y = auth_y + int(1.25 * IN)
    add_text(slide, int(0.6 * IN), inst_y, SLIDE_W - int(1.2 * IN), int(0.4 * IN),
             "Networks and Information Security Engineering  ·  Princess Sumaya University for Technology (PSUT)",
             14, color=GREY_TEXT, align=PP_ALIGN.CENTER)
    add_text(slide, int(0.6 * IN), inst_y + int(0.38 * IN), SLIDE_W - int(1.2 * IN), int(0.35 * IN),
             "Artificial Intelligence  ·  Final Project  ·  2026",
             13, color=CYAN, align=PP_ALIGN.CENTER)

    add_progress_bar(slide, 1)


# ── Slide 2: The Problem ──────────────────────────────────────────────────────

def slide_02_problem(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide)
    add_header_bar(slide, "The Problem")
    add_progress_bar(slide, 2)

    content_top = int(0.85 * IN)
    lw = int(6.0 * IN)
    lx = int(0.4 * IN)

    bullets = [
        ("Phishing pages impersonate trusted sites to steal\ncredentials, passwords, and financial data.", CYAN),
        ("Static rule lists and manual review cannot\nscale to millions of new URLs per day.", WHITE),
        ("Automated, lightweight URL-based ML detection\nprovides a fast first line of defense.", WHITE),
    ]
    for i, (text, col) in enumerate(bullets):
        by = content_top + i * int(1.35 * IN)
        add_rect(slide, lx, by, int(0.045 * IN), int(0.9 * IN), col)
        add_text(slide, lx + int(0.15 * IN), by, lw - int(0.2 * IN), int(1.0 * IN),
                 text, 19, color=col, align=PP_ALIGN.LEFT, wrap=True)

    # Goal box
    goal_y = content_top + 3 * int(1.35 * IN) + int(0.1 * IN)
    add_rect(slide, lx, goal_y, lw, int(0.75 * IN), SECONDARY, CYAN, Pt(1.5))
    add_text(slide, lx + int(0.2 * IN), goal_y + int(0.08 * IN), lw - int(0.4 * IN), int(0.6 * IN),
             "Goal: Classify URLs as phishing or legitimate using supervised ML on lexical features only.",
             16, bold=True, color=CYAN, align=PP_ALIGN.LEFT, wrap=True)

    # Figure right
    add_img(slide, "class_distribution.png",
            lx + lw + int(0.25 * IN), content_top,
            int(5.0 * IN), int(3.8 * IN))


# ── Slide 3: Dataset ──────────────────────────────────────────────────────────

def slide_03_dataset(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide)
    add_header_bar(slide, "Dataset")
    add_progress_bar(slide, 3)

    stats = [
        ("100,077", "Raw Rows"),
        ("21,891",  "Unique Rows\n(after dedup)"),
        ("19",      "URL Features"),
        ("72.5%",   "Phishing\nClass Share"),
        ("Kaggle",  "Source"),
    ]

    n = len(stats)
    total_gap = int(0.22 * IN) * (n - 1)
    box_w = int((SLIDE_W - int(0.8 * IN) - total_gap) / n)
    box_h = int(1.85 * IN)
    strip_h = int(0.18 * IN)
    box_top = int(0.9 * IN)

    for i, (val, lbl) in enumerate(stats):
        bx = int(0.4 * IN) + i * (box_w + int(0.22 * IN))
        add_rect(slide, bx, box_top, box_w, box_h, SECONDARY, CYAN, Pt(1))
        add_rect(slide, bx, box_top, box_w, strip_h, CYAN)
        add_text(slide, bx, box_top + strip_h + int(0.18 * IN), box_w, int(0.75 * IN),
                 val, 30, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_text(slide, bx, box_top + strip_h + int(1.0 * IN), box_w, int(0.65 * IN),
                 lbl, 13, color=GREY_TEXT, align=PP_ALIGN.CENTER)

    # Description
    desc_y = box_top + box_h + int(0.25 * IN)
    add_text(slide, int(0.4 * IN), desc_y, SLIDE_W - int(0.8 * IN), int(0.4 * IN),
             "Kaggle Web Page Phishing Dataset  ·  19 numerical URL-derived features  ·  Binary target: phishing (1) / legitimate (0)",
             15, color=GREY_TEXT, align=PP_ALIGN.CENTER)

    # Features sample
    feat_y = desc_y + int(0.5 * IN)
    feats = ["url_length", "n_dots", "n_hypens", "n_slash", "n_questionmark",
             "n_redirection", "n_at", "n_percent", "n_equal", "n_dollar", "…+9 more"]
    feat_text = "  ·  ".join(feats)
    add_text(slide, int(0.4 * IN), feat_y, SLIDE_W - int(0.8 * IN), int(0.35 * IN),
             feat_text, 13, color=CYAN, align=PP_ALIGN.CENTER)

    # Class dist image
    img_y = feat_y + int(0.5 * IN)
    img_w = int(6.5 * IN)
    add_img(slide, "class_distribution.png",
            (SLIDE_W - int(img_w)) // 2, img_y,
            int(img_w), int(2.2 * IN))


# ── Slide 4: Feature Engineering ─────────────────────────────────────────────

def slide_04_features(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide)
    add_header_bar(slide, "Feature Engineering")
    add_progress_bar(slide, 4)

    col_top = int(0.85 * IN)
    col_h   = int(2.8 * IN)
    col_w   = int(5.3 * IN)
    lx, rx  = int(0.4 * IN), int(6.4 * IN)

    # Left — original features
    add_rect(slide, lx, col_top, col_w, col_h, SECONDARY)
    add_rect(slide, lx, col_top, col_w, int(0.32 * IN), CYAN)
    add_text(slide, lx + int(0.15 * IN), col_top + int(0.02 * IN), col_w, int(0.3 * IN),
             "Original Features (19)", 15, bold=True, color=BG_DARK, align=PP_ALIGN.LEFT)

    orig = ["url_length", "n_dots", "n_hypens", "n_underline", "n_slash",
            "n_questionmark", "n_equal", "n_at", "n_and", "n_exclamation",
            "n_space", "n_tilde", "n_comma", "n_plus", "n_asterisk",
            "n_hastag", "n_dollar", "n_percent", "n_redirection"]
    tb = slide.shapes.add_textbox(int(lx + 0.15 * IN), int(col_top + 0.38 * IN),
                                   int(col_w - 0.3 * IN), int(col_h - 0.45 * IN))
    tf = tb.text_frame; tf.word_wrap = True
    for i, f in enumerate(orig):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(1)
        run = p.add_run(); run.text = f"· {f}"
        run.font.size = Pt(13); run.font.color.rgb = GREY_TEXT; run.font.name = "Calibri"

    # Right — engineered features
    eng_colors = [CYAN, CYAN, CYAN, CYAN, CYAN, CYAN]
    eng = [
        ("total_special_chars", "Sum of all special character counts"),
        ("symbol_ratio",        "total_special_chars / (url_length + 1)"),
        ("has_redirect",        "Binary: 1 if n_redirection > 0"),
        ("has_at",              "Binary: 1 if n_at > 0"),
        ("slash_dot_ratio",     "n_slash / (n_dots + 1)"),
        ("url_length_log",      "log(url_length + 1)"),
    ]
    add_rect(slide, rx, col_top, col_w, col_h, SECONDARY)
    add_rect(slide, rx, col_top, col_w, int(0.32 * IN), HIGHLIGHT)
    add_text(slide, rx + int(0.15 * IN), col_top + int(0.02 * IN), col_w, int(0.3 * IN),
             "Engineered Features (+6)", 15, bold=True, color=CYAN, align=PP_ALIGN.LEFT)

    for i, (fname, fdesc) in enumerate(eng):
        ey = int(col_top + 0.42 * IN) + i * int(0.40 * IN)
        add_text(slide, int(rx + 0.15 * IN), ey, int(col_w - 0.3 * IN), int(0.22 * IN),
                 fname, 13, bold=True, color=CYAN, align=PP_ALIGN.LEFT)
        add_text(slide, int(rx + 0.15 * IN), ey + int(0.20 * IN), int(col_w - 0.3 * IN), int(0.18 * IN),
                 fdesc, 11, color=GREY_TEXT, align=PP_ALIGN.LEFT)

    # Correlation figure below
    fig_y = col_top + col_h + int(0.2 * IN)
    fig_w = int(9.5 * IN)
    add_img(slide, "top_correlations.png",
            (SLIDE_W - int(fig_w)) // 2, fig_y,
            int(fig_w), int(2.1 * IN))


# ── Slide 5: Pipeline ─────────────────────────────────────────────────────────

def slide_05_pipeline(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide)
    add_header_bar(slide, "ML Pipeline")
    add_progress_bar(slide, 5)

    steps = [
        ("Load",     "CSV → DataFrame"),
        ("Clean",    "Drop 78K dupes"),
        ("Engineer", "+6 features"),
        ("Split",    "80/20 stratified"),
        ("Scale",    "StandardScaler\n(LR only)"),
        ("CV+Tune",  "GridSearchCV\n5-fold"),
        ("Evaluate", "Test metrics"),
    ]

    n       = len(steps)
    arrow_w = int(0.28 * IN)
    box_h   = int(1.55 * IN)
    total_w = SLIDE_W - int(0.8 * IN)
    box_w   = int((total_w - (n - 1) * arrow_w) / n)
    flow_l  = int(0.4 * IN)
    flow_t  = int(1.25 * IN)
    strip_h = int(0.18 * IN)

    for i, (label, sub) in enumerate(steps):
        bx = flow_l + i * (box_w + arrow_w)
        is_last = (i == n - 1)
        bg = HIGHLIGHT if is_last else SECONDARY
        border = CYAN
        add_rect(slide, bx, flow_t, box_w, box_h, bg, border, Pt(1.5))
        add_rect(slide, bx, flow_t, box_w, strip_h, CYAN)
        # step number
        add_text(slide, bx + int(0.08 * IN), flow_t + strip_h + int(0.02 * IN),
                 int(0.3 * IN), int(0.25 * IN), str(i + 1), 10, color=GREY_TEXT)
        # label
        add_text(slide, bx, flow_t + strip_h + int(0.28 * IN), box_w, int(0.5 * IN),
                 label, 16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        # sub-label
        add_text(slide, bx + int(0.05 * IN), flow_t + strip_h + int(0.78 * IN),
                 box_w - int(0.1 * IN), int(0.7 * IN),
                 sub, 11, color=GREY_TEXT, align=PP_ALIGN.CENTER, wrap=True)

        if not is_last:
            ax = bx + box_w
            ah = int(0.35 * IN)
            at = flow_t + (box_h - ah) // 2
            add_arrow(slide, ax, at, arrow_w, ah)

    # Description row
    desc_y = flow_t + box_h + int(0.35 * IN)
    add_text(slide, flow_l, desc_y, SLIDE_W - int(0.8 * IN), int(0.4 * IN),
             "All four models tuned independently via GridSearchCV · 5-fold stratified CV scored on F1",
             15, color=GREY_TEXT, align=PP_ALIGN.CENTER)

    # Key numbers
    nums_y = desc_y + int(0.55 * IN)
    for i, (val, lbl) in enumerate([
        ("21,891", "unique records"),
        ("5-fold", "cross-validation"),
        ("80 / 20", "train / test split"),
        ("4", "models evaluated"),
    ]):
        nx = flow_l + i * int(2.9 * IN)
        add_rect(slide, nx, nums_y, int(2.5 * IN), int(1.1 * IN), CARD_DARK, SECONDARY, Pt(1))
        add_text(slide, nx, nums_y + int(0.05 * IN), int(2.5 * IN), int(0.5 * IN),
                 val, 22, bold=True, color=CYAN, align=PP_ALIGN.CENTER)
        add_text(slide, nx, nums_y + int(0.55 * IN), int(2.5 * IN), int(0.4 * IN),
                 lbl, 13, color=GREY_TEXT, align=PP_ALIGN.CENTER)


# ── Slide 6: Models ───────────────────────────────────────────────────────────

MODEL_CARDS = [
    {
        "name": "Logistic Regression", "tag": "Linear",
        "tag_color": TAG_LR,
        "desc": "Linear decision boundary via log-odds.\nFast baseline, requires feature scaling.",
        "param": "Best: C=0.01, solver=lbfgs",
        "acc": "0.7753", "f1": "0.8533",
    },
    {
        "name": "Decision Tree", "tag": "Tree",
        "tag_color": TAG_TREE,
        "desc": "Greedy axis-aligned splits.\nInterpretable, no scaling needed.",
        "param": "Best: max_depth=10, min_leaf=1",
        "acc": "0.8022", "f1": "0.8667",
    },
    {
        "name": "Random Forest", "tag": "Ensemble · Bagging",
        "tag_color": TAG_ENS,
        "desc": "200 decorrelated trees.\nAverages predictions to reduce variance.",
        "param": "Best: n_est=200, max_depth=15",
        "acc": "0.8102", "f1": "0.8740",
    },
    {
        "name": "Gradient Boosting", "tag": "Ensemble · Boosting  ★ BEST",
        "tag_color": CYAN,
        "desc": "Sequentially corrects residuals.\nBest balance of precision and recall.",
        "param": "Best: lr=0.1, depth=4, n_est=200",
        "acc": "0.8198", "f1": "0.8801",
    },
]


def draw_model_card(slide, l, t, w, h, data):
    tag_c = data["tag_color"]
    text_on_tag = BG_DARK if tag_c == CYAN else WHITE
    tag_h = int(0.32 * IN)
    px = int(0.15 * IN)

    add_rect(slide, l, t, w, h, CARD_DARK, tag_c, Pt(1.5))
    add_rect(slide, l, t, w, tag_h, tag_c)
    add_text(slide, l, t + int(0.02 * IN), w, tag_h,
             data["tag"], 12, bold=True, color=text_on_tag, align=PP_ALIGN.CENTER)

    add_text(slide, l + px, t + tag_h + int(0.10 * IN), w - 2 * px, int(0.45 * IN),
             data["name"], 19, bold=True, color=WHITE)

    # thin divider
    add_rect(slide, l + px, t + tag_h + int(0.55 * IN), w - 2 * px, int(0.015 * IN), tag_c)

    add_text(slide, l + px, t + tag_h + int(0.60 * IN), w - 2 * px, int(0.75 * IN),
             data["desc"], 13, color=GREY_TEXT, wrap=True)

    add_text(slide, l + px, t + tag_h + int(1.4 * IN), w - 2 * px, int(0.32 * IN),
             data["param"], 12, color=CYAN, italic=True)

    # metric badges
    badge_w = int(1.1 * IN)
    badge_h = int(0.38 * IN)
    badge_t = t + h - badge_h - int(0.12 * IN)
    for bi, (lbl, val) in enumerate([("Acc", data["acc"]), ("F1", data["f1"])]):
        bx = l + w - (2 - bi) * (badge_w + int(0.1 * IN)) - int(0.05 * IN)
        add_rect(slide, bx, badge_t, badge_w, badge_h, SECONDARY)
        add_text(slide, bx, badge_t + int(0.02 * IN), badge_w, badge_h,
                 f"{lbl}: {val}", 12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)


def slide_06_models(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide)
    add_header_bar(slide, "Machine Learning Models")
    add_progress_bar(slide, 6)

    card_w = int(5.55 * IN)
    card_h = int(2.55 * IN)
    h_gap  = int(0.35 * IN)
    v_gap  = int(0.18 * IN)
    top    = int(0.85 * IN)
    lx     = int(0.4 * IN)
    rx     = lx + card_w + h_gap

    positions = [(lx, top), (rx, top),
                 (lx, top + card_h + v_gap), (rx, top + card_h + v_gap)]

    for (cx, cy), data in zip(positions, MODEL_CARDS):
        draw_model_card(slide, cx, cy, card_w, card_h, data)


# ── Slide 7: Results ──────────────────────────────────────────────────────────

RESULTS = [
    ["Model",                "Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC"],
    ["Gradient Boosting",    "0.8198",   "0.8505",    "0.9118", "0.8801",   "0.8873"],
    ["Random Forest",        "0.8102",   "0.8429",    "0.9074", "0.8740",   "0.8793"],
    ["Decision Tree",        "0.8022",   "0.8476",    "0.8866", "0.8667",   "0.8478"],
    ["Logistic Regression",  "0.7753",   "0.8101",    "0.9014", "0.8533",   "0.8329"],
]


def build_results_table(slide, l, t, w, h):
    rows, cols = len(RESULTS), len(RESULTS[0])
    tbl_shape = slide.shapes.add_table(rows, cols, int(l), int(t), int(w), int(h))
    tbl = tbl_shape.table

    col_ws = [int(w * r) for r in [0.295, 0.141, 0.141, 0.141, 0.141, 0.141]]
    for ci, cw in enumerate(col_ws):
        tbl.columns[ci].width = cw

    for ri, row in enumerate(RESULTS):
        for ci, val in enumerate(row):
            cell = tbl.cell(ri, ci)
            is_hdr = ri == 0
            is_gb  = ri == 1
            bg = SECONDARY if is_hdr else (HIGHLIGHT if is_gb else (ROW_ALT if ri % 2 else CARD_DARK))
            set_cell_bg(cell, bg)
            align = PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER
            fc = (BG_DARK if is_hdr else (CYAN if is_gb else (WHITE if is_hdr else GREY_TEXT)))
            if is_hdr:
                fc = WHITE
            elif is_gb:
                fc = WHITE
            set_cell_text(cell, val, size=12, bold=(is_hdr or is_gb), color=fc, align=align)

    # suppress default borders
    for tc in tbl._tbl.iter(qn('a:tc')):
        tcPr = tc.find(qn('a:tcPr'))
        if tcPr is None:
            tcPr = etree.SubElement(tc, qn('a:tcPr'))


def slide_07_results(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide)
    add_header_bar(slide, "Results — All Models")
    add_progress_bar(slide, 7)

    tbl_l = int(0.35 * IN)
    tbl_t = int(0.85 * IN)
    tbl_w = int(6.7 * IN)
    tbl_h = int(2.5 * IN)
    build_results_table(slide, tbl_l, tbl_t, tbl_w, tbl_h)

    # GB callout label
    add_text(slide, tbl_l, tbl_t + tbl_h + int(0.15 * IN), tbl_w, int(0.35 * IN),
             "★  Gradient Boosting: highest accuracy, F1, and AUC across all four models",
             14, color=CYAN, italic=True)

    # F1 chart right
    img_x = tbl_l + tbl_w + int(0.25 * IN)
    img_w = SLIDE_W - img_x - int(0.35 * IN)
    add_img(slide, "model_comparison_f1.png", img_x, tbl_t, img_w, int(2.5 * IN))

    # Recall emphasis note
    note_y = tbl_t + tbl_h + int(0.62 * IN)
    add_rect(slide, tbl_l, note_y, SLIDE_W - int(0.7 * IN), int(0.9 * IN), SECONDARY, HIGHLIGHT, Pt(1))
    add_text(slide, tbl_l + int(0.2 * IN), note_y + int(0.08 * IN),
             SLIDE_W - int(1.1 * IN), int(0.75 * IN),
             "Recall is the primary metric — a missed phishing page is more dangerous than a false alarm.\n"
             "All four models achieve recall above 0.886, demonstrating strong detection capability.",
             14, color=GREY_TEXT, wrap=True)


# ── Slide 8: Best Model ───────────────────────────────────────────────────────

def slide_08_best_model(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide)
    add_header_bar(slide, "Best Model — Gradient Boosting")
    add_progress_bar(slide, 8)

    # Three metric callout boxes
    metrics = [("F1-Score", "0.8801"), ("Recall", "0.9118"), ("ROC-AUC", "0.8873")]
    box_w = int(2.8 * IN)
    box_h = int(1.0 * IN)
    gap   = int((SLIDE_W - 3 * box_w) / 4)
    mt    = int(0.88 * IN)

    for i, (lbl, val) in enumerate(metrics):
        bx = gap + i * (box_w + gap)
        add_rect(slide, bx, mt, box_w, box_h, HIGHLIGHT, CYAN, Pt(1.5))
        add_text(slide, bx, mt + int(0.02 * IN), box_w, int(0.55 * IN),
                 val, 32, bold=True, color=CYAN, align=PP_ALIGN.CENTER)
        add_text(slide, bx, mt + int(0.57 * IN), box_w, int(0.35 * IN),
                 lbl, 14, color=GREY_TEXT, align=PP_ALIGN.CENTER)

    # Confusion matrix + ROC
    img_t = mt + box_h + int(0.25 * IN)
    img_h = SLIDE_H - img_t - int(0.45 * IN)
    half  = (SLIDE_W - int(0.9 * IN)) // 2

    add_img(slide, "confusion_matrix_best_model.png",
            int(0.35 * IN), img_t, half, img_h)
    add_img(slide, "roc_curves.png",
            int(0.35 * IN) + half + int(0.2 * IN), img_t, half, img_h)


# ── Slide 9: Prior Work Comparison ───────────────────────────────────────────

PRIOR = [
    ["Study",                      "Features",                  "Best Model",       "Top Acc."],
    ["Blum et al. [2] (2010)",     "Lexical URL (count-based)", "Online learner",   "N/A"],
    ["Sahingoz et al. [3] (2019)", "NLP + hybrid URL",          "Random Forest",    "97.98%"],
    ["Awasthi & Goel [4] (2022)",  "30 URL-structural",         "Decision Tree",    "95.92%"],
    ["Alnemari et al. [5] (2023)", "30 URL-structural",         "Random Forest",    "97.30%"],
    ["This Work",                  "19 lexical + 6 engineered", "Gradient Boosting","81.98% *"],
]


def slide_09_prior_work(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide)
    add_header_bar(slide, "Comparison with Prior Work")
    add_progress_bar(slide, 9)

    tbl_l = int(0.4 * IN)
    tbl_t = int(0.9 * IN)
    tbl_w = SLIDE_W - int(0.8 * IN)
    tbl_h = int(3.6 * IN)

    rows, cols = len(PRIOR), len(PRIOR[0])
    ts = slide.shapes.add_table(rows, cols, tbl_l, tbl_t, tbl_w, tbl_h)
    tbl = ts.table

    col_ws = [int(tbl_w * r) for r in [0.30, 0.28, 0.24, 0.18]]
    for ci, cw in enumerate(col_ws):
        tbl.columns[ci].width = cw

    for ri, row in enumerate(PRIOR):
        for ci, val in enumerate(row):
            cell = tbl.cell(ri, ci)
            is_hdr = ri == 0
            is_us  = ri == len(PRIOR) - 1
            bg = SECONDARY if is_hdr else (HIGHLIGHT if is_us else (ROW_ALT if ri % 2 else CARD_DARK))
            set_cell_bg(cell, bg)
            fc = WHITE if is_hdr else (CYAN if is_us else GREY_TEXT)
            align = PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER
            set_cell_text(cell, val, size=13, bold=(is_hdr or is_us), color=fc, align=align)

    note_y = tbl_t + tbl_h + int(0.2 * IN)
    add_text(slide, tbl_l, note_y, tbl_w, int(0.8 * IN),
             "* Different datasets and feature sets — not a direct benchmark comparison.\n"
             "Our method uses URL-only lexical features: lighter, no content scraping required.\n"
             "F1-Score = 0.880 and Recall = 0.912 remain competitive for URL-only approaches.",
             13, color=GREY_TEXT, italic=True, wrap=True)


# ── Slide 10: Conclusion ──────────────────────────────────────────────────────

def slide_10_conclusion(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide)
    add_header_bar(slide, "Conclusion")
    add_progress_bar(slide, 10)

    sections = [
        ("Key Takeaways", CYAN, [
            "Gradient Boosting achieved the best results: F1=0.880, Recall=0.912, AUC=0.887.",
            "All four models competitive (F1: 0.853–0.880); hyperparameter tuning lifted Decision Tree F1 from 0.791 to 0.867.",
            "URL lexical features + 6 engineered indicators provide effective, lightweight phishing detection.",
        ]),
        ("Limitations", RGBColor(0xFF, 0xA0, 0x00), [
            "URL-only features miss sophisticated phishing with clean-looking URLs.",
            "Static dataset — 78K of 100K rows were duplicates; model may not generalise to fresh data.",
        ]),
        ("Future Work", GREY_TEXT, [
            "Expand features with host-based, DNS, SSL, and content signals; validate on live phishing feeds.",
        ]),
    ]

    cy = int(0.85 * IN)
    for sec_title, sec_color, items in sections:
        add_rect(slide, int(0.4 * IN), cy, int(0.04 * IN), int(0.32 * IN) * len(items) + int(0.08 * IN), sec_color)
        add_text(slide, int(0.6 * IN), cy, int(9.0 * IN), int(0.32 * IN),
                 sec_title, 16, bold=True, color=sec_color)
        cy += int(0.33 * IN)
        for item in items:
            add_text(slide, int(0.7 * IN), cy, int(9.5 * IN), int(0.32 * IN),
                     f"›  {item}", 14, color=WHITE, wrap=True)
            cy += int(0.34 * IN)
        cy += int(0.15 * IN)

    # Thank you
    ty_w = int(3.5 * IN)
    ty_h = int(0.65 * IN)
    add_rect(slide, SLIDE_W - ty_w - int(0.4 * IN), SLIDE_H - ty_h - int(0.5 * IN),
             ty_w, ty_h, HIGHLIGHT, CYAN, Pt(1.5))
    add_text(slide, SLIDE_W - ty_w - int(0.4 * IN), SLIDE_H - ty_h - int(0.5 * IN),
             ty_w, ty_h, "Thank You", 22, bold=True, color=CYAN, align=PP_ALIGN.CENTER)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    prs = Presentation()
    prs.slide_width  = Emu(SLIDE_W)
    prs.slide_height = Emu(SLIDE_H)

    for fn in [
        slide_01_title,
        slide_02_problem,
        slide_03_dataset,
        slide_04_features,
        slide_05_pipeline,
        slide_06_models,
        slide_07_results,
        slide_08_best_model,
        slide_09_prior_work,
        slide_10_conclusion,
    ]:
        fn(prs)

    prs.save(str(OUT))
    print(f"Saved → {OUT}")


if __name__ == "__main__":
    main()
