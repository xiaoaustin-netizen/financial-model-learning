import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Financial Modeling School", layout="wide", page_icon="📈")

if "current_page" not in st.session_state:
    st.session_state.current_page = "overview"

# ── Practice companies ─────────────────────────────────────────────────────────
COMPANIES = [
    {"name":"NovaTech Industries",    "sector":"Technology",         "revenue":"$500M",  "ebitda":"$120M", "ni":"$52.5M","price":"$45.00","shares":"20M"},
    {"name":"Meridian Capital Group", "sector":"Financial Services", "revenue":"$320M",  "ebitda":"$85M",  "ni":"$38M",  "price":"$28.00","shares":"15M"},
    {"name":"Apex Consumer Brands",   "sector":"Consumer Staples",   "revenue":"$1.2B",  "ebitda":"$210M", "ni":"$95M",  "price":"$62.00","shares":"40M"},
    {"name":"Frontier Energy",        "sector":"Energy",             "revenue":"$780M",  "ebitda":"$165M", "ni":"$72M",  "price":"$38.50","shares":"25M"},
    {"name":"Cascade Logistics",      "sector":"Industrials",        "revenue":"$440M",  "ebitda":"$95M",  "ni":"$41M",  "price":"$33.00","shares":"18M"},
]
if "company_idx" not in st.session_state:
    st.session_state.company_idx = 0

def current_company():
    return COMPANIES[st.session_state.company_idx]

def nav_btn(label, key):
    active = st.session_state.current_page == key
    btn_type = "primary" if active else "secondary"
    if st.button(label, key=f"nav_{key}", use_container_width=True, type=btn_type):
        st.session_state.current_page = key
        st.rerun()

st.markdown("""<style>
/* ── Hide Streamlit default top bar ── */
header[data-testid="stHeader"] { display:none !important; }

/* ── Global background & text ── */
.stApp { background:#F8FAFC; }
.stApp p, .stApp li, .stMarkdown p, .stMarkdown li { color:#374151; font-size:.93rem; line-height:1.72; }
.stApp h1 { color:#111827; font-size:1.65rem; font-weight:700; letter-spacing:-.01em; }
.stApp h2 { color:#111827; font-size:1.15rem; font-weight:700; margin-top:1.8rem; }
.stApp h3 { color:#1F2937; font-size:1rem; font-weight:600; }
.stApp strong, .stMarkdown strong { color:#111827; }
.block-container { padding-top:0 !important; padding-bottom:2.5rem; max-width:1100px; }

/* ── Module header bar ── */
.mod-header {
    background:#FFFFFF; border-bottom:1px solid #E5E7EB;
    padding:13px 0 11px; margin-bottom:24px;
    display:flex; justify-content:space-between; align-items:flex-start;
}

/* ── Input chips for model pages ── */
.input-chip {
    display:inline-flex; align-items:baseline; gap:5px;
    font-size:.70rem; color:#1E293B;
    background:#F3F4F6; padding:3px 8px;
    border:1px solid #E5E7EB; margin:2px 2px 0 0;
}
.input-chip-lbl {
    font-size:.60rem; color:#9CA3AF;
    font-weight:600; letter-spacing:.02em; white-space:nowrap;
}
.mod-header-title  { font-size:.98rem; font-weight:700; color:#111827; }
.mod-header-sub    { font-size:.73rem; color:#9CA3AF; margin-top:2px; }
.mod-stat {
    font-size:.71rem; color:#4B5563;
    background:#F3F4F6; padding:4px 9px;
    border:1px solid #E5E7EB; margin-left:6px;
    display:inline-block; white-space:nowrap;
}
.mod-stat-label { font-size:.62rem; color:#9CA3AF; display:block; line-height:1; margin-bottom:1px; }

/* ── Section labels ── */
.sec {
    font-size:.58rem; font-weight:700; letter-spacing:.16em;
    text-transform:uppercase; color:#9CA3AF;
    border-bottom:1px solid #E5E7EB; padding-bottom:6px; margin-bottom:14px;
}

/* ── Cards ── */
.card {
    border-radius:6px; padding:16px 22px; margin-bottom:14px;
    border-left:3px solid; box-shadow:0 1px 2px rgba(0,0,0,.05);
    color:#1F2937; font-size:.88rem; line-height:1.65;
}
.card-concept { background:#EFF6FF; border-color:#2563EB; }
.card-formula { background:#F5F3FF; border-color:#7C3AED; }
.card-warning { background:#FFFBEB; border-color:#D97706; }
.card-pro     { background:#F9FAFB; border-color:#D1D5DB; }
.card b, .card strong { color:#111827; }

.card-title {
    font-size:.58rem; font-weight:700; letter-spacing:.14em;
    text-transform:uppercase; margin-bottom:8px;
}
.ct-concept { color:#1D4ED8; }
.ct-formula { color:#6D28D9; }
.ct-warning { color:#B45309; }
.ct-pro     { color:#6B7280; }

.formula-text {
    font-family:'SF Mono','Fira Code','Cascadia Code',monospace;
    font-size:.92rem; color:#1F2937; font-weight:600;
    background:#FFFFFF; border:1px solid #E5E7EB;
    padding:8px 12px; display:block; margin-top:4px;
}

/* ── Overview landing cards ── */
.lp-card {
    background:#FFFFFF; border:1px solid #E5E7EB;
    border-radius:6px; padding:18px 22px; margin-bottom:8px; border-top:3px solid;
    box-shadow:0 1px 3px rgba(0,0,0,.04);
}
.lp-title { font-size:.93rem; font-weight:700; color:#111827; }
.lp-desc  { font-size:.82rem; color:#4B5563; margin-top:7px; line-height:1.6; }

/* ── Sidebar — grey ladder ── */
section[data-testid="stSidebar"],
[data-testid="stSidebar"] {
    background:#F9FAFB !important;
    border-right:1px solid #E5E7EB !important;
}
section[data-testid="stSidebar"] > div { padding-top:0 !important; }

/* Wordmark strip */
.nav-wordmark {
    background:#F3F4F6; border-bottom:1px solid #E5E7EB;
    padding:15px 16px; margin-bottom:4px;
    font-size:.68rem; font-weight:800; letter-spacing:.22em;
    text-transform:uppercase; color:#374151;
}

/* Section group labels */
.nav-group-hdr {
    font-size:.53rem; font-weight:700; letter-spacing:.2em;
    text-transform:uppercase; color:#9CA3AF;
    padding:14px 16px 3px; margin:0; border:none;
}

/* ── Sidebar buttons: nuclear override ── */
[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] .stButton > button:focus,
[data-testid="stSidebar"] .stButton > button:active,
[data-testid="stSidebar"] .stButton > button:focus-visible,
[data-testid="stSidebar"] .stButton > button:focus:not(:active) {
    width:100% !important;
    text-align:left !important;
    border-radius:0 !important;
    border-top:none !important;
    border-right:none !important;
    border-bottom:1px solid #E5E7EB !important;
    border-left:3px solid #C9CDD4 !important;
    outline:none !important;
    box-shadow:none !important;
    font-size:.82rem !important;
    font-weight:500 !important;
    padding:9px 12px 9px 14px !important;
    margin:0 !important;
    line-height:1.3 !important;
    background-color:#EAECEF !important;
    color:#1E3A5F !important;
}
[data-testid="stSidebar"] .stButton > button *,
[data-testid="stSidebar"] .stButton > button p,
[data-testid="stSidebar"] .stButton > button span,
[data-testid="stSidebar"] .stButton > button div {
    color:#1E3A5F !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color:#D9DCE0 !important;
    border-left-color:#6B7280 !important;
    color:#111827 !important;
}
[data-testid="stSidebar"] .stButton > button:hover * {
    color:#111827 !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"],
[data-testid="stSidebar"] .stButton > button[kind="primary"]:focus,
[data-testid="stSidebar"] .stButton > button[kind="primary"]:active {
    background-color:#D1D5DB !important;
    border-left-color:#1E3A5F !important;
    border-left-width:3px !important;
    color:#111827 !important;
    font-weight:700 !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] * {
    color:#111827 !important;
    font-weight:700 !important;
}

/* ── Reroll button ── */
div[data-testid="stHorizontalBlock"] .stButton.reroll button,
button[kind="secondary"].reroll-btn {
    border-radius:4px; font-size:.78rem; font-weight:600;
    padding:6px 14px; border:1px solid #D1D5DB;
    background:#FFFFFF; color:#374151;
}
button[kind="secondary"].reroll-btn:hover {
    background:#F3F4F6; border-color:#9CA3AF; color:#111827;
}

/* ── Hint rows ── */
.hint-row {
    font-size:.8rem; color:#4B5563; padding:6px 0;
    border-bottom:1px solid #F3F4F6; line-height:1.6;
}
.hint-num {
    display:inline-block; width:54px; font-family:monospace;
    color:#9CA3AF; font-size:.71rem;
}

/* ── Tabs ── */
button[data-baseweb="tab"] { font-size:.82rem; font-weight:600; color:#4B5563; }
</style>""", unsafe_allow_html=True)

# ── Card helpers ───────────────────────────────────────────────────────────────
def concept(title, body):
    st.markdown(f'<div class="card card-concept"><div class="card-title ct-concept">Concept — {title}</div>{body}</div>', unsafe_allow_html=True)

def formula_card(expr, note=""):
    note_html = f'<div style="font-size:.78rem;color:#6D28D9;margin-top:8px;">{note}</div>' if note else ""
    st.markdown(f'<div class="card card-formula"><div class="card-title ct-formula">Formula</div><div class="formula-text">{expr}</div>{note_html}</div>', unsafe_allow_html=True)

def warning(body):
    st.markdown(f'<div class="card card-warning"><div class="card-title ct-warning">Common Mistake</div>{body}</div>', unsafe_allow_html=True)

def pro_tip(body):
    st.markdown(f'<div class="card card-pro"><div class="card-title ct-pro">Analyst Note</div>{body}</div>', unsafe_allow_html=True)

def given_inputs(_items, _note=""):
    pass

def xl_sheet(title, rows):
    html = (f'<div style="margin:12px 0 20px;">'
            f'<div style="font-size:.58rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase;'
            f'color:#94A3B8;margin-bottom:10px;padding-bottom:5px;border-bottom:1px solid #E2E8F0;">'
            f'Reference Layout — {title}</div>')
    html += ('<table style="border-collapse:collapse;width:100%;font-size:.82rem;'
             'border:1px solid #E2E8F0;border-radius:8px;overflow:hidden;">')
    html += '<thead><tr>'
    html += '<th style="background:#F1F5F9;color:#64748B;padding:7px 12px;text-align:left;width:7%;font-size:.72rem;font-weight:600;letter-spacing:.06em;border-bottom:1px solid #E2E8F0;">Row</th>'
    html += '<th style="background:#F1F5F9;color:#64748B;padding:7px 12px;text-align:left;width:30%;font-size:.72rem;font-weight:600;letter-spacing:.06em;border-bottom:1px solid #E2E8F0;">Col A — Label</th>'
    html += '<th style="background:#F1F5F9;color:#64748B;padding:7px 12px;text-align:left;width:37%;font-size:.72rem;font-weight:600;letter-spacing:.06em;border-bottom:1px solid #E2E8F0;">Col B — Value / Formula</th>'
    html += '<th style="background:#F1F5F9;color:#64748B;padding:7px 12px;text-align:left;width:26%;font-size:.72rem;font-weight:600;letter-spacing:.06em;border-bottom:1px solid #E2E8F0;">Notes</th>'
    html += '</tr></thead><tbody>'
    for r in rows:
        t = r.get("type", "formula")
        if t == "section":
            html += (f'<tr><td colspan="4" style="background:#F8FAFC;color:#94A3B8;font-style:italic;'
                     f'padding:5px 12px;border-bottom:1px solid #E2E8F0;font-size:.73rem;'
                     f'letter-spacing:.05em;">{r.get("label","")}</td></tr>')
            continue
        bg  = {"input":"#EFF6FF","formula":"#FFFFFF","link":"#F0FDF4"}.get(t,"#FFFFFF")
        fg  = {"input":"#1D4ED8","formula":"#1E293B","link":"#15803D"}.get(t,"#1E293B")
        bdg = {
            "input":   '<span style="font-size:.58rem;background:#DBEAFE;color:#1D4ED8;padding:1px 6px;border-radius:3px;margin-left:6px;letter-spacing:.04em;">INPUT</span>',
            "formula": '<span style="font-size:.58rem;background:#F1F5F9;color:#64748B;padding:1px 6px;border-radius:3px;margin-left:6px;letter-spacing:.04em;">FORMULA</span>',
            "link":    '<span style="font-size:.58rem;background:#DCFCE7;color:#15803D;padding:1px 6px;border-radius:3px;margin-left:6px;letter-spacing:.04em;">LINKED</span>',
        }.get(t,"")
        html += (f'<tr>'
                 f'<td style="background:#F8FAFC;color:#94A3B8;font-family:monospace;padding:5px 12px;border-bottom:1px solid #F1F5F9;">{r.get("row","")}</td>'
                 f'<td style="background:#FFFFFF;color:#1E293B;padding:5px 12px;border-bottom:1px solid #F1F5F9;">{r.get("label","")}</td>'
                 f'<td style="background:{bg};color:{fg};font-family:monospace;padding:5px 12px;border-bottom:1px solid #F1F5F9;">{r.get("value","")}{bdg}</td>'
                 f'<td style="background:#F8FAFC;color:#64748B;font-size:.73rem;padding:5px 12px;border-bottom:1px solid #F1F5F9;">{r.get("note","")}</td>'
                 f'</tr>')
    html += '</tbody></table></div>'
    st.markdown(html, unsafe_allow_html=True)

# ── Module header bar ─────────────────────────────────────────────────────────
_PAGE_META = {
    "overview":  ("Financial Modeling School",       "Seven core Excel models — IB & PE curriculum"),
    "3stmt":     ("① Three Statement Model",          "Foundation · Income Statement · Balance Sheet · Cash Flow"),
    "dcf":       ("② DCF Model",                     "Valuation · Discounted Cash Flow · WACC · Terminal Value"),
    "comps":     ("③ Comparable Company Analysis",    "Valuation · Public Market Multiples · Peer Benchmarking"),
    "precedent": ("④ Precedent Transactions",         "Valuation · M&A Deal Multiples · Control Premium"),
    "lbo":       ("⑤ LBO Model",                     "Advanced · Sources & Uses · Debt Schedule · MOIC / IRR"),
    "merger":    ("⑥ Merger Model",                  "Advanced · Accretion / Dilution · EPS Impact"),
    "budget":    ("⑦ Budget vs. Actual",              "FP&A · Variance Analysis · Volume / Price Decomposition"),
}

_PAGE_INPUTS = {
    # Non-derivable inputs per model — peer/deal data lives in the page body, not the top bar
    "3stmt": [
        ("Revenue","$500M"),("COGS","$300M"),("SG&A","$80M"),
        ("D&A","$30M"),("Interest Exp.","$15M"),("Tax Rate","30%"),
        ("Beg. Cash","$75M"),("Beg. AR","$60M"),("Beg. Inventory","$40M"),
        ("Beg. PP&E","$200M"),("Beg. Intangibles","$50M"),
        ("Beg. AP","$30M"),("Beg. ST Debt","$25M"),("Beg. LT Debt","$175M"),
        ("Beg. Com. Stock","$100M"),("Beg. Ret. Earn.","$95M"),
        ("Capex","$35M"),("Dividends","$15M"),
    ],
    "dcf": [
        ("Base Revenue","$500M"),("Rev. Growth","5.0%"),
        ("EBITDA Margin","24.0%"),("D&A % Rev.","6.0%"),
        ("Capex % Rev.","7.0%"),("Tax Rate","30%"),
        ("WACC","9.35%"),("Terminal g","2.5%"),
        ("Net Debt","$125M"),("Shares Out.","20M"),
    ],
    # Comps/Precedents: only target company values in top bar; peer table is in the page body
    "comps": [
        ("LTM EBITDA","$120M"),("Net Debt","$125M"),("Shares Out.","20M"),
    ],
    "precedent": [
        ("LTM EBITDA","$120M"),("Net Debt","$125M"),
        ("Shares Out.","20M"),("Current Price","$45.00"),
    ],
    "lbo": [
        ("LTM EBITDA","$120M"),("Entry EV/EBITDA","9.0×"),
        ("Debt / EV","60%"),("Interest Rate","7.0%"),
        ("EBITDA Growth","5% / yr"),("D&A","$30M"),
        ("Capex","$35M"),("Tax Rate","30%"),("Exit EV/EBITDA","9.0×"),
    ],
    "merger": [
        ("Target Price","$30.00"),("Acq. Premium","25%"),
        ("Target Shares","10M"),("Target NI","$20M"),
        ("Acquirer NI","$52.5M"),("Acquirer Shares","20M"),
        ("After-tax Synergies","$5M"),("Intangibles Amort.","$2M/yr"),
    ],
    "budget": [
        ("Budg. Revenue","$120M"),("Act. Revenue","$113M"),
        ("Budg. COGS","$72M"),("Act. COGS","$70.3M"),
        ("Budg. SG&A","$20M"),("Act. SG&A","$21.5M"),
        ("Budg. Units","12,000"),("Budg. Price/Unit","$10,000"),
        ("Act. Units","11,500"),("Act. Price/Unit","$9,826"),
    ],
}

def page_header(page):
    title, subtitle = _PAGE_META.get(page, ("", ""))
    co = current_company()
    inputs = _PAGE_INPUTS.get(page)
    col_hdr, col_btn = st.columns([10, 1])
    with col_hdr:
        # Company name badge — always shown
        co_badge = (
            f'<span style="display:inline-flex;align-items:center;gap:6px;'
            f'background:#EFF6FF;border:1px solid #BFDBFE;'
            f'padding:3px 10px;margin-right:10px;white-space:nowrap;">'
            f'<span style="font-size:.65rem;font-weight:700;color:#1D4ED8;">{co["name"]}</span>'
            f'<span style="font-size:.60rem;color:#93C5FD;">{co["sector"]}</span>'
            f'</span>'
        )
        if inputs is None:
            # Overview: show generic company stats
            chips_html = "".join(
                f'<span class="input-chip"><span class="input-chip-lbl">{lbl}</span>{val}</span>'
                for lbl, val in [("Revenue", co["revenue"]), ("EBITDA", co["ebitda"]),
                                 ("Net Income", co["ni"]), ("Price", co["price"]), ("Shares", co["shares"])]
            )
        else:
            # Model pages: show only non-derivable inputs
            chips_html = "".join(
                f'<span class="input-chip"><span class="input-chip-lbl">{lbl}</span>{val}</span>'
                for lbl, val in inputs
            )
        st.markdown(
            f'<div class="mod-header">'
            f'<div style="flex-shrink:0;margin-right:16px;padding-top:2px;">'
            f'<div class="mod-header-title">{title}</div>'
            f'<div class="mod-header-sub">{subtitle}</div>'
            f'</div>'
            f'<div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:flex-end;gap:0;">'
            f'{co_badge}{chips_html}</div></div>',
            unsafe_allow_html=True)
    with col_btn:
        st.markdown('<div style="padding-top:8px;"></div>', unsafe_allow_html=True)
        if st.button("New Co.", key="reroll_btn", help="Cycle to next practice company",
                     use_container_width=True):
            st.session_state.company_idx = (st.session_state.company_idx + 1) % len(COMPANIES)
            st.rerun()

# ── blank_grid: fully empty spreadsheet with reveal + hints expander ──────────
def blank_grid(key, n_rows, col_a_width=220, col_b_label="B", extra_cols=None,
               answers=None, hints=None):
    """
    Renders a blank Excel-like grid (row # | A | B | ...).
    answers: list of dicts, one per row, keys = column names.
    hints:   list of (row_label, hint_text) tuples, shown in an expander below.
    """
    reveal_key = f"reveal_{key}"
    if reveal_key not in st.session_state:
        st.session_state[reveal_key] = False

    col_names = ["A", col_b_label] + (extra_cols or [])

    c_info, c_btn = st.columns([7, 1])
    with c_btn:
        lbl = "Hide" if st.session_state[reveal_key] else "Reveal"
        if st.button(lbl, key=f"btn_{reveal_key}"):
            st.session_state[reveal_key] = not st.session_state[reveal_key]
            st.rerun()
    with c_info:
        st.caption("Col A — row labels   |   Col B — values or formulas (prefix formulas with =)   |   Cross-sheet links: =SheetName!CellRef")

    data = []
    for i in range(n_rows):
        row = {"#": str(i + 1)}
        for c in col_names:
            if st.session_state[reveal_key] and answers and i < len(answers):
                row[c] = answers[i].get(c, "")
            else:
                row[c] = ""
        data.append(row)

    df = pd.DataFrame(data)
    disabled = ["#"] + (col_names if st.session_state[reveal_key] else [])

    cfg = {"#": st.column_config.TextColumn("#", disabled=True, width=36)}
    cfg["A"] = st.column_config.TextColumn("A  (row label)", width=col_a_width)
    cfg[col_b_label] = st.column_config.TextColumn(f"{col_b_label}  (value / formula)", width=260)
    for ec in (extra_cols or []):
        cfg[ec] = st.column_config.TextColumn(ec, width=130)

    st.data_editor(df, column_config=cfg, hide_index=True,
                   key=key, use_container_width=True,
                   num_rows="fixed", disabled=disabled)

    if hints:
        with st.expander("Row hints — expand when stuck"):
            html = ""
            for row_label, hint_text in hints:
                html += (f'<div class="hint-row">'
                         f'<span class="hint-num">Row {row_label}</span>{hint_text}</div>')
            st.markdown(html, unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="nav-wordmark">FM School</div>', unsafe_allow_html=True)

    nav_btn("Overview", "overview")
    st.markdown('<div class="nav-group-hdr">Foundation</div>', unsafe_allow_html=True)
    nav_btn("①  Three Statement", "3stmt")
    st.markdown('<div class="nav-group-hdr">Valuation</div>', unsafe_allow_html=True)
    nav_btn("②  DCF Model", "dcf")
    nav_btn("③  Comps", "comps")
    nav_btn("④  Precedent Txns", "precedent")
    st.markdown('<div class="nav-group-hdr">Advanced</div>', unsafe_allow_html=True)
    nav_btn("⑤  LBO Model", "lbo")
    nav_btn("⑥  Merger Model", "merger")
    st.markdown('<div class="nav-group-hdr">FP&amp;A</div>', unsafe_allow_html=True)
    nav_btn("⑦  Budget vs Actual", "budget")
    page = st.session_state.current_page

    st.markdown(
        '<div style="margin:20px 16px 0;padding-top:14px;border-top:1px solid #E5E7EB;">'
        '<div style="font-size:.53rem;font-weight:700;letter-spacing:.2em;text-transform:uppercase;'
        'color:#9CA3AF;margin-bottom:10px;">Excel Convention</div>'
        '<div style="font-size:.77rem;color:#4B5563;line-height:2.1;">'
        '<span style="display:inline-block;width:9px;height:9px;background:#2563EB;'
        'margin-right:8px;vertical-align:middle;"></span>Blue — hardcoded input<br>'
        '<span style="display:inline-block;width:9px;height:9px;background:#374151;'
        'margin-right:8px;vertical-align:middle;"></span>Black — formula<br>'
        '<span style="display:inline-block;width:9px;height:9px;background:#16A34A;'
        'margin-right:8px;vertical-align:middle;"></span>Green — cross-sheet link<br>'
        '<span style="font-family:monospace;font-size:.7rem;background:#E5E7EB;'
        'color:#374151;padding:1px 5px;margin-right:6px;">Ctrl+`</span>'
        'toggle formula view'
        '</div>'
        '<div style="margin-top:14px;padding-top:12px;border-top:1px solid #E5E7EB;">'
        '<div style="font-size:.53rem;font-weight:700;letter-spacing:.2em;text-transform:uppercase;'
        f'color:#9CA3AF;margin-bottom:6px;">Practice Company</div>'
        f'<div style="font-size:.77rem;color:#4B5563;line-height:1.85;">'
        f'<span style="color:#111827;font-weight:700;display:block;margin-bottom:3px;">'
        f'{current_company()["name"]}</span>'
        f'{current_company()["sector"]}<br>'
        f'Rev {current_company()["revenue"]} · EBITDA {current_company()["ebitda"]}<br>'
        f'NI {current_company()["ni"]} · {current_company()["price"]} / {current_company()["shares"]} sh'
        '</div></div></div>',
        unsafe_allow_html=True)

page_header(page)

# ══════════════════════════════════════════════════════════════════════════════
# OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "overview":
    st.markdown("# Financial Modeling School")
    st.markdown("Build the seven core Excel models used in investment banking and private equity — from a completely blank spreadsheet. Each module teaches you how professional analysts actually construct these models: the logic, the structure, the conventions, and the formulas.")
    concept("How each module works",
        "<b>Learn tab</b> — Read about how the model is constructed: why each section exists, "
        "how the pieces connect, what bankers actually use each line for, and the thinking behind "
        "each formula. A completed reference layout is included so you can study the finished product.<br><br>"
        "<b>Build tab</b> — Open a blank Excel workbook and build the model alongside this page. "
        "Both columns — labels (col A) and values/formulas (col B) — are blank. Fill them in yourself. "
        "Expand the row hints if you get stuck. Hit Reveal only after a genuine attempt.")
    pro_tip("The only way to learn financial modeling is to actually build models. "
            "Reading is essential but insufficient — you need your hands on the keyboard in Excel, "
            "typing formulas, making mistakes, and fixing them. Treat every module as a build exercise, not a reading exercise.")
    st.markdown("---")
    st.markdown('<div class="sec">Build Order</div>', unsafe_allow_html=True)
    for key, num, name, cat, time, color, desc in [
        ("3stmt","①","Three Statement Model","Foundation","~50 min","#3B82F6",
         "The non-negotiable starting point. Three linked tabs (IS, BS, CFS) in one workbook. Every other model either embeds this or assumes you can read it fluently."),
        ("dcf","②","DCF Model","Valuation","~45 min","#8B5CF6",
         "Project free cash flows, calculate WACC from first principles, build a terminal value, and discount everything to a share price. Add a sensitivity table."),
        ("comps","③","Comparable Company Analysis","Valuation","~30 min","#10B981",
         "Pull public market multiples for 4–6 peers, compute medians, and apply them to NovaTech. The fastest model to build; always paired with DCF."),
        ("precedent","④","Precedent Transactions","Valuation","~25 min","#F59E0B",
         "Same architecture as comps but using M&A deal data. Adds control premium columns. Gives a higher valuation range because acquirers pay to gain control."),
        ("lbo","⑤","LBO Model","Advanced","~55 min","#EF4444",
         "Sources & Uses → debt schedule → five-year hold → exit. MOIC and IRR outputs. The core private equity interview model."),
        ("merger","⑥","Merger Model","Advanced","~40 min","#EC4899",
         "Combine two income statements, issue shares, add synergies, and test whether the deal increases or decreases the acquirer's EPS."),
        ("budget","⑦","Budget vs. Actual","FP&A","~25 min","#14B8A6",
         "Side-by-side variance table with F/U flags, then a volume/price decomposition of the revenue miss. The monthly rhythm of corporate finance."),
    ]:
        st.markdown(
            f'<div class="lp-card" style="border-top-color:{color};">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
            f'<div class="lp-title">{num} {name}</div>'
            f'<div style="font-size:.74rem;color:#9CA3AF;">{cat} · {time}</div></div>'
            f'<div class="lp-desc">{desc}</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# THREE STATEMENT MODEL
# ══════════════════════════════════════════════════════════════════════════════
elif page == "3stmt":
    st.markdown("# ① Three Statement Model")
    learn_tab, build_tab = st.tabs(["Learn the Model", "Build It in Excel"])

    with learn_tab:
        st.markdown("## Why Three Statements?")
        st.markdown("""
Every public company must publish three financial statements. Individually, each tells only part of the story. Together, they give a complete picture of a business's financial reality — and linking them in one Excel workbook is the fundamental skill every financial analyst builds first.

**The Income Statement** answers: was the company profitable over this period? It runs from revenue down to net income across a quarter or year, deducting each category of cost in sequence.

**The Balance Sheet** answers: what does the company own and owe at this exact moment? It is a snapshot — assets on one side, liabilities plus equity on the other — and it must always balance by accounting law.

**The Cash Flow Statement** answers: how did cash actually move? This is the most important statement for understanding business health, because a company can show strong net income while simultaneously running out of cash.

The three-statement *model* links these with live Excel formulas so that changing one assumption — say, raising revenue growth by 2% — automatically ripples through all three statements. That dynamic linkage is what makes it a model rather than three separate spreadsheets.
""")
        st.markdown("## Building the Income Statement")
        st.markdown("""
The Income Statement is built top-down. You always start with **Revenue** — every dollar the company earned from its core operations. Then you deduct costs in a specific order that reveals different profit margins at each level.

**Why this order matters:** Each subtotal tells you something different. Gross Profit isolates the profitability of production. EBITDA isolates operating cash generation. EBIT incorporates asset aging costs. EBT incorporates financing costs. Net Income incorporates taxes. Bankers move up and down this stack constantly — an LBO analyst cares about EBITDA, an equity investor cares about EPS, a credit analyst cares about interest coverage.

**COGS vs. SG&A — a critical distinction.** COGS (Cost of Goods Sold) are variable costs that scale with revenue: raw materials, direct labor, manufacturing overhead. When revenue doubles, COGS roughly doubles. SG&A (Selling, General & Administrative) are largely fixed: office rent, executive salaries, software subscriptions. They don't scale with revenue the same way. This distinction matters enormously for forecasting — COGS is modeled as a % of revenue, SG&A is often modeled as a fixed or slowly growing dollar amount.

**D&A — non-cash but real.** Depreciation & Amortization represents the accounting recognition of an asset losing value over time. A factory bought for $200M is worth less each year as it ages — D&A captures this. Critically, it reduces reported profit (and thus taxes) but does NOT reduce cash. This is why we add it back in the Cash Flow Statement. The line between EBITDA and EBIT exists precisely to isolate this non-cash charge.

**The tax line.** Tax = EBT × tax rate. Importantly, interest expense is deducted before calculating taxes (interest is tax-deductible), which is why it matters whether a company uses debt. A company with $100M EBIT and $20M interest pays taxes on $80M, not $100M — the "tax shield" on debt is a central concept in capital structure and LBO modeling.
""")
        st.markdown("## Building the Balance Sheet")
        st.markdown("""
The Balance Sheet rests on one identity that must always hold: **Assets = Liabilities + Equity.** If it doesn't balance, you have an error somewhere — and no banker will use a model that doesn't balance.

**Assets** are organized by liquidity — how quickly they can be converted to cash. Current assets (cash, receivables, inventory) come first because they'll convert within a year. Then long-term assets (PP&E, intangibles), which represent the company's productive capacity.

**Liabilities** mirror this structure: current liabilities (payables, short-term debt) due within a year, then long-term liabilities (bonds, term loans). Together they represent what the company owes to lenders, suppliers, and other creditors.

**Equity** is what's left for shareholders after all obligations: contributed capital (what investors paid in) plus accumulated retained earnings (profits the company kept rather than paying out as dividends). In a sense, equity is the accounting "plug" — it absorbs everything that doesn't fit in liabilities.

**The balance check cell.** Every professional model has a dedicated check cell: =Total Assets − Total L&E. If this cell is not zero, something is broken. Build it immediately and watch it. In real work, a non-zero balance check triggers an urgent audit of every formula in the model.

**Retained Earnings is the link from the Income Statement.** Each period's Net Income increases Retained Earnings (less any dividends paid). This is one of the key connections between the IS and BS — but in a linked model, you update Retained Earnings each year using a roll-forward formula rather than hard-coding it.
""")
        st.markdown("## Building the Cash Flow Statement and Linking the Model")
        st.markdown("""
The CFS is structured in three sections: Operating Activities, Investing Activities, and Financing Activities. Each section captures a different category of cash movement.

**Operating Activities** starts with Net Income from the IS (cross-sheet link: =IS!B12). Then it makes two types of adjustments:

1. *Add back non-cash charges:* D&A is subtracted on the IS to reduce taxable income, but no cash left the company. So we add it back here (=IS!B7).
2. *Adjust for working capital changes:* If Accounts Receivable increased, you recognized revenue but haven't collected the cash yet — that's a negative adjustment. If Accounts Payable increased, you received goods but haven't paid yet — that's a positive adjustment (you're holding onto cash longer). Working capital dynamics are often where the model gets nuanced.

The result is **Cash from Operations** — the cleanest measure of how much cash the core business generates.

**Investing Activities** is primarily Capex (capital expenditures — spending on PP&E). This is entered as a negative number because it's a cash outflow. In a simple model, CFI = Capex. In more complex models you'd include acquisitions, asset sales, etc.

**Financing Activities** captures cash flows between the company and its capital providers: dividends paid to shareholders (negative), debt raised (positive), debt repaid (negative), share buybacks (negative). The sum of all three sections is the **Net Change in Cash**.

**Closing the loop — the circular link.** The ending cash on the CFS feeds back into the Balance Sheet cash line for next year. In Excel: if your CFS ending cash is in CFS!B14, then next year's BS cash = =CFS!B14. This creates the "circular" linkage that makes the model fully integrated. Change any assumption and all three statements update simultaneously.

**Sheet referencing syntax.** To link between tabs, type =IS!B12 in another tab to pull a value from cell B12 of the IS tab. If the tab name has spaces, wrap it in single quotes: ='Income Statement'!B12. This syntax is the backbone of every three-statement model.
""")
        warning("The most common beginner mistake: hard-coding numbers on the CFS instead of linking them from the IS. If you type 52.5 for Net Income in the CFS instead of =IS!B12, the model breaks as soon as you change any revenue assumption. Every number that appears on more than one sheet must be a formula referencing the original source.")
        pro_tip("Build the IS first, then BS, then CFS. This is the professional order because the IS generates the numbers the other two statements need. Use Ctrl+` to toggle formula view in Excel and verify every non-blue cell is a formula — no exceptions.")
        st.markdown("---")
        st.markdown("## Completed Reference Layout")
        st.markdown("Study this before building. Understand why each cell is an input vs. formula.")
        xl_sheet("IS Tab", [
            {"row":"B1","label":"NovaTech — Income Statement (FY)","value":"(title row)","note":"Header — no formula","type":"input"},
            {"row":"B2","label":"Revenue","value":"500","note":"Hardcoded input","type":"input"},
            {"row":"B3","label":"COGS","value":"300","note":"Hardcoded input","type":"input"},
            {"row":"B4","label":"Gross Profit","value":"=B2-B3","note":"Formula","type":"formula"},
            {"row":"B5","label":"SG&A","value":"80","note":"Hardcoded input","type":"input"},
            {"row":"B6","label":"EBITDA","value":"=B4-B5","note":"Formula","type":"formula"},
            {"row":"B7","label":"D&A","value":"30","note":"Hardcoded input","type":"input"},
            {"row":"B8","label":"EBIT","value":"=B6-B7","note":"Formula","type":"formula"},
            {"row":"B9","label":"Interest Expense","value":"15","note":"Hardcoded input","type":"input"},
            {"row":"B10","label":"EBT","value":"=B8-B9","note":"Formula","type":"formula"},
            {"row":"B11","label":"Tax (30%)","value":"=B10*0.30","note":"Formula","type":"formula"},
            {"row":"B12","label":"Net Income","value":"=B10-B11","note":"Formula — feeds CFS","type":"formula"},
        ])
        xl_sheet("BS Tab", [
            {"type":"section","label":"ASSETS"},
            {"row":"B2","label":"Cash","value":"75","note":"Will later = CFS ending cash","type":"input"},
            {"row":"B3","label":"Accounts Receivable","value":"60","note":"Input","type":"input"},
            {"row":"B4","label":"Inventory","value":"40","note":"Input","type":"input"},
            {"row":"B5","label":"Total Current Assets","value":"=SUM(B2:B4)","note":"Formula","type":"formula"},
            {"row":"B6","label":"PP&E","value":"200","note":"Input","type":"input"},
            {"row":"B7","label":"Intangibles","value":"50","note":"Input","type":"input"},
            {"row":"B8","label":"Total Assets","value":"=B5+B6+B7","note":"Formula","type":"formula"},
            {"type":"section","label":"LIABILITIES & EQUITY"},
            {"row":"B10","label":"Accounts Payable","value":"30","note":"Input","type":"input"},
            {"row":"B11","label":"Short-term Debt","value":"25","note":"Input","type":"input"},
            {"row":"B12","label":"Total Current Liabilities","value":"=B10+B11","note":"Formula","type":"formula"},
            {"row":"B13","label":"Long-term Debt","value":"175","note":"Input","type":"input"},
            {"row":"B14","label":"Total Liabilities","value":"=B12+B13","note":"Formula","type":"formula"},
            {"row":"B15","label":"Common Stock","value":"100","note":"Input","type":"input"},
            {"row":"B16","label":"Retained Earnings","value":"95","note":"Input","type":"input"},
            {"row":"B17","label":"Total Equity","value":"=B15+B16","note":"Formula","type":"formula"},
            {"row":"B18","label":"Total Liabilities & Equity","value":"=B14+B17","note":"Formula","type":"formula"},
            {"row":"B19","label":"Balance Check","value":"=B8-B18","note":"Must = 0","type":"formula"},
        ])
        xl_sheet("CFS Tab", [
            {"type":"section","label":"OPERATING ACTIVITIES"},
            {"row":"B2","label":"Net Income","value":"=IS!B12","note":"Cross-sheet link","type":"link"},
            {"row":"B3","label":"+ D&A","value":"=IS!B7","note":"Cross-sheet link","type":"link"},
            {"row":"B4","label":"Δ Accounts Receivable","value":"-5","note":"Negative = AR grew (cash tied up)","type":"input"},
            {"row":"B5","label":"Δ Inventory","value":"-3","note":"Negative = inventory built","type":"input"},
            {"row":"B6","label":"Δ Accounts Payable","value":"2","note":"Positive = paid later (cash held)","type":"input"},
            {"row":"B7","label":"Cash from Operations","value":"=SUM(B2:B6)","note":"Formula","type":"formula"},
            {"type":"section","label":"INVESTING ACTIVITIES"},
            {"row":"B8","label":"Capex","value":"-35","note":"Negative = cash out","type":"input"},
            {"row":"B9","label":"Cash from Investing","value":"=B8","note":"Formula","type":"formula"},
            {"type":"section","label":"FINANCING ACTIVITIES"},
            {"row":"B10","label":"Dividends Paid","value":"-15","note":"Negative = cash out","type":"input"},
            {"row":"B11","label":"Cash from Financing","value":"=B10","note":"Formula","type":"formula"},
            {"type":"section","label":"NET CHANGE"},
            {"row":"B12","label":"Net Change in Cash","value":"=B7+B9+B11","note":"Sum of three sections","type":"formula"},
            {"row":"B13","label":"Beginning Cash","value":"=BS!B2","note":"Links from BS","type":"link"},
            {"row":"B14","label":"Ending Cash","value":"=B13+B12","note":"Feeds back into BS next period","type":"formula"},
        ])

    with build_tab:
        st.markdown("## Build the Three Statement Model From Scratch")
        st.markdown("Open a blank Excel workbook. Create three tabs named **IS**, **BS**, and **CFS**. Work through each grid below — fill in both the row label (col A) and the value or formula (col B). Expand hints only when genuinely stuck.")

        st.markdown("### Income Statement (IS tab)")
        blank_grid("3s_is", 12,
            answers=[
                {"A":"NovaTech Industries — Income Statement","B":""},
                {"A":"Revenue","B":"500"},
                {"A":"COGS","B":"300"},
                {"A":"Gross Profit","B":"=B2-B3"},
                {"A":"SG&A","B":"80"},
                {"A":"EBITDA","B":"=B4-B5"},
                {"A":"D&A","B":"30"},
                {"A":"EBIT","B":"=B6-B7"},
                {"A":"Interest Expense","B":"15"},
                {"A":"EBT","B":"=B8-B9"},
                {"A":"Tax","B":"=B10*0.30"},
                {"A":"Net Income","B":"=B10-B11"},
            ],
            hints=[
                ("1","Header row. Company name, statement name, fiscal year. Nothing in col B."),
                ("2","The top line of any P&L. Every dollar earned from core business operations this year."),
                ("3","Direct costs that scale with production — materials, direct labor. Subtracted from revenue."),
                ("4","Write a formula. What profit remains after subtracting production costs from revenue? This margin tells you how scalable the business is."),
                ("5","Overhead costs that are largely fixed — office rent, executive salaries, sales team. Subtracted from gross profit."),
                ("6","Write a formula: gross profit minus SG&A. This is the banker's preferred operating metric because it excludes financing (interest) and non-cash (D&A) noise."),
                ("7","Depreciation & Amortization. A non-cash charge for aging assets — reduces reported profit but never leaves the bank account."),
                ("8","Write a formula: EBITDA minus D&A. Operating income after accounting for asset aging."),
                ("9","Cost of outstanding debt paid to lenders this period. Not related to operations — it's a financing cost."),
                ("10","Write a formula: EBIT minus interest. The taxable profit base."),
                ("11","Write a formula: EBT multiplied by the tax rate. NovaTech's rate is 30%."),
                ("12","Write a formula: EBT minus tax. The bottom line. This number will link into your CFS tab."),
            ])

        st.markdown("### Balance Sheet (BS tab)")
        blank_grid("3s_bs", 18,
            answers=[
                {"A":"NovaTech Industries — Balance Sheet","B":""},
                {"A":"Cash","B":"75"},
                {"A":"Accounts Receivable","B":"60"},
                {"A":"Inventory","B":"40"},
                {"A":"Total Current Assets","B":"=SUM(B2:B4)"},
                {"A":"PP&E","B":"200"},
                {"A":"Intangibles","B":"50"},
                {"A":"Total Assets","B":"=B5+B6+B7"},
                {"A":"","B":""},
                {"A":"Accounts Payable","B":"30"},
                {"A":"Short-term Debt","B":"25"},
                {"A":"Total Current Liabilities","B":"=B10+B11"},
                {"A":"Long-term Debt","B":"175"},
                {"A":"Total Liabilities","B":"=B12+B13"},
                {"A":"Common Stock","B":"100"},
                {"A":"Retained Earnings","B":"95"},
                {"A":"Total Equity","B":"=B15+B16"},
                {"A":"Total Liabilities & Equity","B":"=B14+B17"},
            ],
            hints=[
                ("1","Header row."),
                ("2","Most liquid asset — cash on hand. This cell will eventually link from the CFS ending cash line."),
                ("3","Money owed to the company by customers for sales already recognized but not yet collected."),
                ("4","Goods produced or purchased but not yet sold. Another current asset."),
                ("5","Write a SUM formula across the three current assets above."),
                ("6","Property, Plant & Equipment — physical long-term assets (factories, machinery, buildings). Net of accumulated depreciation."),
                ("7","Intangible long-term assets — patents, trademarks, acquired goodwill."),
                ("8","Write a formula: current assets plus PP&E plus intangibles. This is the total of everything the company controls."),
                ("9","Leave blank — a visual separator between assets and liabilities."),
                ("10","Money owed to suppliers for goods/services already received. A current liability."),
                ("11","Debt due within the next 12 months."),
                ("12","Write a formula: AP plus short-term debt."),
                ("13","Debt due beyond one year — bonds, term loans."),
                ("14","Write a formula: current liabilities plus long-term debt."),
                ("15","Paid-in capital from equity investors."),
                ("16","Accumulated profits the company has kept rather than paying as dividends."),
                ("17","Write a formula: common stock plus retained earnings."),
                ("18","Write a formula: total liabilities plus total equity. THIS MUST EQUAL TOTAL ASSETS (row 8). Add a row 19 balance check: =B8-B18 — it must show zero."),
            ])

        st.markdown("### Cash Flow Statement (CFS tab)")
        blank_grid("3s_cfs", 14,
            answers=[
                {"A":"NovaTech Industries — Cash Flow Statement","B":""},
                {"A":"Net Income","B":"=IS!B12"},
                {"A":"+ D&A (add back)","B":"=IS!B7"},
                {"A":"Δ Accounts Receivable","B":"-5"},
                {"A":"Δ Inventory","B":"-3"},
                {"A":"Δ Accounts Payable","B":"2"},
                {"A":"Cash from Operations","B":"=SUM(B2:B6)"},
                {"A":"Capex","B":"-35"},
                {"A":"Cash from Investing","B":"=B8"},
                {"A":"Dividends Paid","B":"-15"},
                {"A":"Cash from Financing","B":"=B10"},
                {"A":"Net Change in Cash","B":"=B7+B9+B11"},
                {"A":"Beginning Cash","B":"=BS!B2"},
                {"A":"Ending Cash","B":"=B13+B12"},
            ],
            hints=[
                ("1","Header row."),
                ("2","Start operating activities with net income — cross-sheet link from IS tab. Syntax: =IS!B12"),
                ("3","D&A was subtracted on the IS to reduce taxes but no cash left. Add it back. Link: =IS!B7"),
                ("4","AR increased by $5M — you billed customers but didn't collect. Cash tied up = negative adjustment. Enter -5."),
                ("5","Inventory grew by $3M — you spent cash building stock you haven't sold. Enter -3."),
                ("6","AP grew by $2M — you received goods but delayed payment. Holding cash longer = positive. Enter 2."),
                ("7","Write a SUM formula across rows 2–6. This is cash generated by operations."),
                ("8","Capital expenditures — spending on equipment. Always a negative number (cash out). Enter -35."),
                ("9","Write a formula referencing only capex for this simple model."),
                ("10","Dividends paid to shareholders. Cash out = negative. Enter -15."),
                ("11","Write a formula referencing the dividends line."),
                ("12","Write a formula: operating + investing + financing cash flows. The net movement in cash this period."),
                ("13","What cash did the company start the period with? Cross-sheet link from BS cash line: =BS!B2"),
                ("14","Write a formula: beginning cash plus net change. This ending cash should feed back into the BS cash cell, closing the loop."),
            ])

# ══════════════════════════════════════════════════════════════════════════════
# DCF MODEL
# ══════════════════════════════════════════════════════════════════════════════
elif page == "dcf":
    st.markdown("# ② DCF Model — Discounted Cash Flow")
    learn_tab, build_tab = st.tabs(["Learn the Model", "Build It in Excel"])

    with learn_tab:
        st.markdown("## What Is a DCF and Why Do Bankers Build It?")
        st.markdown("""
A DCF (Discounted Cash Flow) is an **intrinsic valuation** — it values a company purely on its own fundamentals, independent of what the stock market is currently pricing it at. If the stock is at $45 but your DCF says $60, the company is undervalued. If it says $30, it's overvalued. The DCF is the tool that lets you form that independent view.

The model rests on a single economic principle: a dollar today is worth more than a dollar in the future, because today's dollar can be invested and grow. Therefore, to find what future cash flows are worth *today*, you discount them back at the rate investors require to take on the risk of holding this company's stock and debt. That rate is called WACC.

DCFs are never presented as a single number. Every assumption — growth rate, margins, WACC, terminal growth — is uncertain. Bankers always pair a DCF with a sensitivity table showing how the implied share price changes as assumptions vary. The honest output of a DCF is a *range*, not a point estimate.
""")
        st.markdown("## Constructing the Projection Period")
        st.markdown("""
The projection period is typically 5 years — long enough to capture the company's strategic trajectory, short enough that your forecasts have some credibility. Beyond 5 years, uncertainty compounds so dramatically that explicit year-by-year projections become meaningless. That's what the terminal value handles.

**Revenue projections** are built from a growth rate assumption. In Excel, you anchor the base-year revenue with an absolute reference ($B$2) and apply compound growth: =$B$2*(1+$B$3)^1 for Year 1, ^2 for Year 2, etc. The dollar signs are essential — they prevent the reference from shifting when you drag the formula right across year columns.

**EBITDA** is projected as a margin percentage of revenue: =Revenue × EBITDA Margin%. Bankers often hold margins flat or let them expand slightly over the projection period, depending on the company's competitive dynamics.

**Free Cash Flow** is the number being discounted. In a simplified projection, FCF = EBITDA × (1 − tax rate) − Capex. This shorthand strips out the D&A add-back and working capital changes that appear in the full CFS. In a more rigorous model (like the LBO), you'd build a full income statement and CFS to derive FCF from first principles.

**Discounting each year's FCF** uses the formula PV = FCF ÷ (1 + WACC)^n, where n is the year number. Year 1's FCF is divided by (1+WACC)^1, Year 5's by (1+WACC)^5. You can also split this into a "discount factor" row (=1/(1+WACC)^n) and a "PV of FCF" row (=FCF × discount factor) — the two-row approach makes auditing easier.
""")
        st.markdown("## Building WACC From First Principles")
        st.markdown("""
WACC is not a single number you look up — you calculate it from component inputs. Understanding each piece is essential because WACC is the biggest driver of DCF valuation.

**Cost of Equity (CAPM):** Ke = Risk-Free Rate + Beta × Equity Risk Premium. The risk-free rate is typically the 10-year Treasury yield (currently ~4.5%). Beta measures how volatile the stock is relative to the market — a beta of 1.1 means the stock moves 10% more than the market in either direction. The Equity Risk Premium (~5–6%) is the historical excess return of stocks over risk-free assets. For NovaTech: Ke = 4.5% + 1.1 × 5.5% = 10.55%.

**After-tax Cost of Debt:** Kd × (1 − tax rate). Debt is cheaper than equity for two reasons: lenders have priority in bankruptcy (less risk), and interest is tax-deductible (the government subsidizes debt). For NovaTech: 6% × (1 − 30%) = 4.2% after-tax.

**Weighting:** WACC = (E/V) × Ke + (D/V) × Kd × (1−T), where V = E + D (total firm value). Use *market value* weights, not book value — book equity can be wildly different from what investors are actually paying. For NovaTech: market cap = $900M, debt = $125M, V = $1,025M. WACC ≈ 9.35%.
""")
        st.markdown("## Terminal Value and the Enterprise Value Bridge")
        st.markdown("""
The terminal value captures everything beyond year 5 — theoretically, all cash flows to infinity. Two methods exist:

**Gordon Growth Model** (most common in DCF): TV = FCF(Y5) × (1 + g) / (WACC − g). Here g is the long-run sustainable growth rate, usually close to nominal GDP growth (2–3%). The formula assumes FCF grows at g forever. This is the approach used in most IB DCFs.

**Exit Multiple Method:** TV = Year 5 EBITDA × assumed exit EV/EBITDA multiple. This is conceptually closer to a comps analysis — you're assuming the company will sell at a market multiple in year 5. Many practitioners prefer this method because it avoids making heroic assumptions about infinite growth.

The TV must then be **discounted to present value**: PV of TV = TV / (1 + WACC)^5. This is the single largest number in your model — TV typically represents 60–80% of total DCF value. This is why WACC and g are so sensitive: a 0.5% change in either can move the implied share price by 20%+.

**Enterprise Value to Share Price bridge:**
1. Enterprise Value = Sum of PV(FCFs) + PV(Terminal Value)
2. Equity Value = Enterprise Value − Net Debt (EV is for all capital providers; subtracting debt gives what belongs to equity holders)
3. Implied Share Price = Equity Value ÷ Shares Outstanding

**The sensitivity table** is built using Excel's Data Table feature (Data → What-If Analysis → Data Table). Set up a grid with WACC values across the top row and g values down the left column. The output cell is your implied share price. Row input = WACC cell, Column input = g cell. This is the most important output of the model — it replaces a false precision single number with an honest range.
""")
        warning("Never present a single DCF price as the answer. The assumptions are too uncertain. Always build and present the sensitivity table. A DCF that doesn't have a sensitivity analysis is incomplete.")
        pro_tip("When building the projection block, put Year 1 in col D and Year 5 in col H. The assumption inputs stay in col B. Lock assumption references with $ (=$B$3) before dragging — this is the most common formula error in DCF models.")
        st.markdown("---")
        st.markdown("## Completed Reference Layout")
        xl_sheet("DCF Tab — Assumptions in Col B, Projections in Cols D–H", [
            {"type":"section","label":"ASSUMPTION INPUTS (col B) — all hardcoded"},
            {"row":"B2","label":"Base Revenue ($M)","value":"500","note":"Input","type":"input"},
            {"row":"B3","label":"Revenue Growth","value":"0.05","note":"Input","type":"input"},
            {"row":"B4","label":"EBITDA Margin","value":"0.24","note":"Input","type":"input"},
            {"row":"B5","label":"Tax Rate","value":"0.30","note":"Input","type":"input"},
            {"row":"B6","label":"Capex % of Revenue","value":"0.07","note":"Input","type":"input"},
            {"row":"B7","label":"WACC","value":"0.0935","note":"Calculated — see WACC block","type":"formula"},
            {"row":"B8","label":"Terminal Growth Rate","value":"0.025","note":"Input","type":"input"},
            {"type":"section","label":"PROJECTIONS — col D = Yr1, E = Yr2, F = Yr3, G = Yr4, H = Yr5"},
            {"row":"D11","label":"Revenue","value":"=$B$2*(1+$B$3)^1","note":"Drag right — change ^1 to ^2 etc.","type":"formula"},
            {"row":"D12","label":"EBITDA","value":"=D11*$B$4","note":"Drag right","type":"formula"},
            {"row":"D13","label":"Free Cash Flow","value":"=D12*(1-$B$5)-D11*$B$6","note":"Drag right","type":"formula"},
            {"row":"D14","label":"Discount Factor","value":"=1/(1+$B$7)^1","note":"Change ^1 per year","type":"formula"},
            {"row":"D15","label":"PV of FCF","value":"=D13*D14","note":"Drag right","type":"formula"},
            {"type":"section","label":"TERMINAL VALUE & EV BRIDGE"},
            {"row":"B17","label":"Terminal Value","value":"=H13*(1+$B$8)/($B$7-$B$8)","note":"Gordon Growth on Y5 FCF","type":"formula"},
            {"row":"B18","label":"PV of Terminal Value","value":"=B17/(1+$B$7)^5","note":"Discount TV back 5 years","type":"formula"},
            {"row":"B19","label":"Sum PV(FCFs)","value":"=SUM(D15:H15)","note":"Sum all 5 discounted FCFs","type":"formula"},
            {"row":"B20","label":"Enterprise Value","value":"=B18+B19","note":"Formula","type":"formula"},
            {"row":"B21","label":"Net Debt","value":"125","note":"Input","type":"input"},
            {"row":"B22","label":"Equity Value","value":"=B20-B21","note":"Formula","type":"formula"},
            {"row":"B23","label":"Shares Outstanding","value":"20","note":"Input","type":"input"},
            {"row":"B24","label":"Implied Share Price","value":"=B22/B23","note":"Formula","type":"formula"},
        ])

    with build_tab:
        st.markdown("## Build the DCF Model")
        st.markdown("One tab, three sections: assumptions block (col B), 5-year projections (cols D–H), then the terminal value and share price bridge below the projections.")

        st.markdown("### Section 1: Assumption Inputs (col B, rows 1–10)")
        st.markdown("These are all hardcoded blue inputs. Give each row a label in col A and its value in col B.")
        blank_grid("dcf_assum", 8,
            answers=[
                {"A":"DCF Model — NovaTech Industries","B":""},
                {"A":"Base Revenue ($M)","B":"500"},
                {"A":"Revenue Growth Rate","B":"0.05"},
                {"A":"EBITDA Margin","B":"0.24"},
                {"A":"Tax Rate","B":"0.30"},
                {"A":"Capex % of Revenue","B":"0.07"},
                {"A":"WACC","B":"0.0935"},
                {"A":"Terminal Growth Rate (g)","B":"0.025"},
            ],
            hints=[
                ("1","Header row — title and company name."),
                ("2","Starting revenue before any growth is applied. The anchor for all projections."),
                ("3","Annual revenue growth assumption — enter as a decimal."),
                ("4","EBITDA as a fraction of revenue each year — enter as a decimal."),
                ("5","Effective tax rate applied to pre-tax income — enter as a decimal."),
                ("6","Capital expenditures as a fraction of revenue — enter as a decimal."),
                ("7","Weighted Average Cost of Capital — the discount rate. Calculated in a separate block (see Learn tab). Enter 0.0935 for now."),
                ("8","Long-run terminal growth rate — roughly GDP growth. Enter as a decimal."),
            ])

        st.markdown("### Section 2: 5-Year Projections (cols D–H, rows 11–15)")
        st.markdown("Year 1 = col D, Year 5 = col H. Col A holds row labels. Use **$ signs** to lock assumption cell references so formulas can be dragged right.")
        blank_grid("dcf_proj", 5, col_b_label="D (Yr 1)",
            extra_cols=["E (Yr 2)", "F (Yr 3)", "G (Yr 4)", "H (Yr 5)"],
            answers=[
                {"A":"Revenue","D (Yr 1)":"=$B$2*(1+$B$3)^1","E (Yr 2)":"=$B$2*(1+$B$3)^2","F (Yr 3)":"=$B$2*(1+$B$3)^3","G (Yr 4)":"=$B$2*(1+$B$3)^4","H (Yr 5)":"=$B$2*(1+$B$3)^5"},
                {"A":"EBITDA","D (Yr 1)":"=D11*$B$4","E (Yr 2)":"=E11*$B$4","F (Yr 3)":"=F11*$B$4","G (Yr 4)":"=G11*$B$4","H (Yr 5)":"=H11*$B$4"},
                {"A":"Free Cash Flow","D (Yr 1)":"=D12*(1-$B$5)-D11*$B$6","E (Yr 2)":"=E12*(1-$B$5)-E11*$B$6","F (Yr 3)":"=F12*(1-$B$5)-F11*$B$6","G (Yr 4)":"=G12*(1-$B$5)-G11*$B$6","H (Yr 5)":"=H12*(1-$B$5)-H11*$B$6"},
                {"A":"Discount Factor","D (Yr 1)":"=1/(1+$B$7)^1","E (Yr 2)":"=1/(1+$B$7)^2","F (Yr 3)":"=1/(1+$B$7)^3","G (Yr 4)":"=1/(1+$B$7)^4","H (Yr 5)":"=1/(1+$B$7)^5"},
                {"A":"PV of FCF","D (Yr 1)":"=D13*D14","E (Yr 2)":"=E13*E14","F (Yr 3)":"=F13*F14","G (Yr 4)":"=G13*G14","H (Yr 5)":"=H13*H14"},
            ],
            hints=[
                ("11","Revenue. Formula: base revenue × (1 + growth rate) raised to the year number. Lock B2 and B3 with $ so you can drag right."),
                ("12","EBITDA. Formula: that year's revenue × EBITDA margin assumption. Lock the margin reference."),
                ("13","Free Cash Flow. Formula: EBITDA × (1 − tax rate) − (revenue × capex%). Lock all assumption references."),
                ("14","Discount Factor. Formula: 1 ÷ (1 + WACC) raised to the year number. Lock WACC reference. This converts future cash to present value."),
                ("15","PV of FCF. Formula: FCF × discount factor — both from the same year column."),
            ])

        st.markdown("### Section 3: Terminal Value & Share Price Bridge (col B, rows 17–24)")
        blank_grid("dcf_bridge", 8,
            answers=[
                {"A":"Terminal Value","B":"=H13*(1+$B$8)/($B$7-$B$8)"},
                {"A":"PV of Terminal Value","B":"=B17/(1+$B$7)^5"},
                {"A":"Sum of PV(FCFs)","B":"=SUM(D15:H15)"},
                {"A":"Enterprise Value","B":"=B18+B19"},
                {"A":"Net Debt","B":"125"},
                {"A":"Equity Value","B":"=B20-B21"},
                {"A":"Shares Outstanding (M)","B":"20"},
                {"A":"Implied Share Price","B":"=B22/B23"},
            ],
            hints=[
                ("17","Terminal Value using Gordon Growth. Formula: Year 5 FCF × (1+g) ÷ (WACC−g). Reference H13 for Y5 FCF, B8 for g, B7 for WACC."),
                ("18","PV of Terminal Value. Discount TV back 5 years: TV ÷ (1+WACC)^5."),
                ("19","Sum all five discounted FCFs using =SUM(D15:H15)."),
                ("20","Enterprise Value = PV(TV) + Sum PV(FCFs). Add rows 18 and 19."),
                ("21","Net Debt is an input: $125M. Enter as a hardcoded number."),
                ("22","Equity Value = Enterprise Value − Net Debt. This represents what belongs to shareholders."),
                ("23","Shares outstanding: 20M. Hardcoded input."),
                ("24","Implied Share Price = Equity Value ÷ Shares. Compare to $45 current market price to form a view."),
            ])

# ══════════════════════════════════════════════════════════════════════════════
# COMPS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "comps":
    st.markdown("# ③ Comparable Company Analysis")
    learn_tab, build_tab = st.tabs(["Learn the Model", "Build It in Excel"])

    with learn_tab:
        st.markdown("## The Logic of Relative Valuation")
        st.markdown("""
Comps (Comparable Company Analysis) is built on a simple market principle: similar assets should trade at similar prices. If four technology companies with similar growth rates and margins trade at a median of 9.5× EV/EBITDA, a fifth similar company should also trade near 9.5× — unless there's a specific reason it deserves a premium or discount.

This makes comps fast, defensible, and grounded in real market data. Unlike a DCF, it doesn't require you to forecast cash flows — it just asks what the market is currently paying. The challenge is in the peer selection: pick the wrong comparables and your valuation is meaningless.

Good peer selection requires companies with similar: business model, industry vertical, end markets, size (revenue range), growth profile, and margin structure. You typically run a screen in Bloomberg or CapIQ to find candidates, then manually review each one to confirm comparability. A five-company peer set is usually sufficient; going beyond eight or ten dilutes the analysis.
""")
        st.markdown("## Understanding the Multiples")
        st.markdown("""
**EV/EBITDA** is the most commonly used multiple in investment banking. Enterprise Value (market cap + net debt) divided by EBITDA gives you a measure of how many years of operating earnings you're paying for the whole business. It's capital-structure neutral — both EV and EBITDA are unaffected by whether a company uses debt or equity, making it comparable across peers with different leverage levels.

**EV/Revenue** is used when EBITDA is negative or unreliable — early-stage companies, high-growth SaaS, or businesses with deliberately low margins (e.g., Amazon in its growth phase). It's a rougher metric but sometimes the only one available.

**P/E (Price-to-Earnings)** is the most recognizable multiple, but the least useful for cross-company comparisons in IB. P/E uses market cap (equity value, after debt) divided by net income (also after interest). This means two identical businesses with different debt levels will have very different P/Es. Bankers prefer EV-based multiples for precisely this reason.

**Why median rather than mean?** One outlier peer — a company trading at 25× in a group that otherwise trades at 9–10× — would distort the mean dramatically. The median is robust to outliers. You also present the 25th and 75th percentiles to show the spread of the range.
""")
        st.markdown("## Building the Comps Table in Excel")
        st.markdown("""
The architecture is straightforward: one row per comparable company, with metric columns on the right. Col A = company name. Then input columns for the raw data (EV, EBITDA, Revenue, Net Income, Market Cap). Then formula columns for the derived multiples.

**Sourcing the data:** In real work, EV and market cap come from Bloomberg or CapIQ as of the analysis date. EBITDA and revenue are LTM (Last Twelve Months) figures — you pull the most recent four quarters of financials and add them up. Net income is also LTM.

**The summary block** sits below the peer rows and uses Excel statistical functions: =MEDIAN(range) and =PERCENTILE(range, 0.25) and =PERCENTILE(range, 0.75). These are drag-and-drop across multiple multiple columns once you've set them up for one.

**The NovaTech valuation block** sits below the summary. Take the median EV/EBITDA multiple, multiply by NovaTech's EBITDA, get an implied EV. Subtract net debt to get implied equity value. Divide by shares to get implied share price. Compare to the $45 market price and interpret: is the stock cheap or expensive relative to peers?
""")
        warning("Comps are only as good as your peer selection. Including a company with 40% revenue growth alongside companies growing at 5% will distort the multiple and make your valuation meaningless. Screen carefully and be prepared to explain why each peer belongs in the set.")
        st.markdown("---")
        st.markdown("## Completed Reference Layout")
        xl_sheet("COMPS Tab", [
            {"type":"section","label":"PEER TABLE — Row 1 = headers, rows 2–5 = companies"},
            {"row":"A2","label":"TechAlpha Inc.","value":"company name","note":"Text","type":"input"},
            {"row":"B2","label":"Enterprise Value ($M)","value":"1104","note":"From Bloomberg / CapIQ","type":"input"},
            {"row":"C2","label":"EBITDA ($M)","value":"120","note":"LTM input","type":"input"},
            {"row":"D2","label":"Revenue ($M)","value":"480","note":"Input","type":"input"},
            {"row":"E2","label":"Net Income ($M)","value":"65","note":"Input","type":"input"},
            {"row":"F2","label":"Market Cap ($M)","value":"1202","note":"Input","type":"input"},
            {"row":"G2","label":"EV/EBITDA","value":"=B2/C2","note":"Drag down all peers","type":"formula"},
            {"row":"H2","label":"EV/Revenue","value":"=B2/D2","note":"Drag down","type":"formula"},
            {"row":"I2","label":"P/E","value":"=F2/E2","note":"Drag down","type":"formula"},
            {"type":"section","label":"SUMMARY ROWS (e.g. rows 7–9)"},
            {"row":"G7","label":"25th Percentile","value":"=PERCENTILE(G2:G5,0.25)","note":"Formula","type":"formula"},
            {"row":"G8","label":"Median","value":"=MEDIAN(G2:G5)","note":"Apply to NovaTech","type":"formula"},
            {"row":"G9","label":"75th Percentile","value":"=PERCENTILE(G2:G5,0.75)","note":"Formula","type":"formula"},
            {"type":"section","label":"NOVATECH VALUATION (rows 12–17)"},
            {"row":"B12","label":"NovaTech EBITDA","value":"120","note":"Input","type":"input"},
            {"row":"B13","label":"Implied EV","value":"=G8*B12","note":"Median × EBITDA","type":"formula"},
            {"row":"B14","label":"Net Debt","value":"125","note":"Input","type":"input"},
            {"row":"B15","label":"Implied Equity Value","value":"=B13-B14","note":"Formula","type":"formula"},
            {"row":"B16","label":"Shares Outstanding","value":"20","note":"Input","type":"input"},
            {"row":"B17","label":"Implied Share Price","value":"=B15/B16","note":"Formula","type":"formula"},
        ])

    with build_tab:
        st.markdown("## Build the Comps Table")
        st.markdown("Peer data — TechAlpha: EV 1104, EBITDA 120, Rev 480, NI 65, MktCap 1202 | DataCore: 810, 100, 420, 50, 810 | CloudSystems: 1260, 120, 400, 59, 1239 | InfoPro: 858, 110, 510, 54, 853")

        st.markdown("### Peer Table (rows 1–5, cols A–I)")
        st.markdown("Row 1 = column headers. Rows 2–5 = one company each. Build all input columns first, then write the multiple formulas.")
        blank_grid("comps_peers", 10,
            answers=[
                {"A":"Company","B":"EV ($M)"},
                {"A":"TechAlpha Inc.","B":"1104"},
                {"A":"DataCore Corp.","B":"810"},
                {"A":"CloudSystems","B":"1260"},
                {"A":"InfoPro Group","B":"858"},
                {"A":"","B":""},
                {"A":"25th Percentile EV/EBITDA","B":"=PERCENTILE(G2:G5,0.25)"},
                {"A":"Median EV/EBITDA","B":"=MEDIAN(G2:G5)"},
                {"A":"75th Percentile EV/EBITDA","B":"=PERCENTILE(G2:G5,0.75)"},
                {"A":"Median P/E","B":"=MEDIAN(I2:I5)"},
            ],
            hints=[
                ("1","Header row. Col A = Company, then label each metric column: EV, EBITDA, Revenue, Net Income, Market Cap, EV/EBITDA, EV/Revenue, P/E — across cols B through I."),
                ("2","TechAlpha. Enter all five raw data inputs (EV, EBITDA, Rev, NI, MktCap) in cols B–F. Then write EV/EBITDA =B2/C2 in col G, EV/Rev =B2/D2 in col H, P/E =F2/E2 in col I."),
                ("3","DataCore. Same structure as row 2 — enter data in cols B–F, formulas in G–I."),
                ("4","CloudSystems. Same structure."),
                ("5","InfoPro. Same structure. After completing rows 2–5, you should be able to drag row 2's G–I formulas down."),
                ("6","Leave blank as a visual separator."),
                ("7","25th percentile of EV/EBITDA across all four peers. PERCENTILE function, range G2:G5, quartile 0.25."),
                ("8","Median EV/EBITDA — this is what you'll apply to NovaTech."),
                ("9","75th percentile. Same structure."),
                ("10","Median P/E across the I column range."),
            ])

        st.markdown("### NovaTech Valuation Block (rows 12–17)")
        blank_grid("comps_val", 6,
            answers=[
                {"A":"NovaTech EBITDA ($M)","B":"120"},
                {"A":"Implied EV (median multiple)","B":"=G8*B12"},
                {"A":"Net Debt ($M)","B":"125"},
                {"A":"Implied Equity Value","B":"=B13-B14"},
                {"A":"Shares Outstanding (M)","B":"20"},
                {"A":"Implied Share Price","B":"=B15/B16"},
            ],
            hints=[
                ("12","NovaTech's EBITDA — hardcoded input."),
                ("13","Implied Enterprise Value: median EV/EBITDA multiple (from summary block) multiplied by NovaTech's EBITDA."),
                ("14","Net Debt: what NovaTech owes lenders net of cash. Hardcoded input."),
                ("15","Equity Value = Implied EV minus Net Debt. This is what belongs to shareholders."),
                ("16","NovaTech's shares outstanding. Input."),
                ("17","Implied Share Price = Equity Value ÷ Shares. Compare to current $45 market price."),
            ])

# ══════════════════════════════════════════════════════════════════════════════
# PRECEDENT TRANSACTIONS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "precedent":
    st.markdown("# ④ Precedent Transaction Analysis")
    learn_tab, build_tab = st.tabs(["Learn the Model", "Build It in Excel"])

    with learn_tab:
        st.markdown("## Why Precedent Transactions Give Higher Valuations Than Comps")
        st.markdown("""
Precedent transaction analysis uses the same multiple framework as comps — but instead of trading multiples (what the market pays for a minority stake today), it uses acquisition multiples (what acquirers paid to buy entire companies in completed M&A deals). These are almost always higher for one reason: **the control premium**.

When an acquirer buys a company, they're not buying a few shares on the open market — they're buying control of the entire enterprise. That control has value: the ability to install a new management team, cut costs, merge operations, redirect capital. Shareholders know this, which is why they won't sell unless they receive a premium above the current stock price. Typical control premiums run 20–40%.

For a sell-side banker advising a company being acquired, precedent transactions are invaluable because they establish a floor for what the acquirer should pay. For a buy-side banker trying to keep the price low, comps are more useful because they reflect a lower baseline. In a pitch book, both analyses appear side by side.
""")
        st.markdown("## Construction Differences from Comps")
        st.markdown("""
The table structure is almost identical to comps, with two important additions:

**Unaffected stock price.** This is the target company's stock price before any deal rumors emerged — usually 30 days before announcement. You use the unaffected price because by the time the deal is announced, the stock has already jumped on speculation. Using the post-announcement price would understate the control premium.

**Control premium column.** Calculated as: (Deal EV − Unaffected Market Cap) ÷ Unaffected Market Cap. This percentage tells you how much above the pre-deal price the acquirer paid. You take the average across all transactions and apply it to NovaTech's current stock price to estimate a minimum acquisition price.

**LTM EBITDA at time of deal, not current.** When you look at what multiple an acquirer paid, you must use the EBITDA that existed at the time of the deal — not today's EBITDA. Using current figures would distort the multiple because years may have passed and the company's financials have changed.

**Deal data sourcing.** In practice, you find precedent transactions through SEC filings (13D, S-4, Schedule TO), Bloomberg's M&A database, CapIQ, or financial news databases. The data you need for each deal: announcement date, closing date, deal EV, target LTM EBITDA, and unaffected stock price (pull from Bloomberg the price 30 days before announcement).
""")
        warning("Precedents go stale quickly. A 2015 deal multiple reflects 2015 market conditions, interest rates, and valuation sentiment — all of which may be dramatically different today. Weight recent transactions more heavily and exclude deals from unusually hot or distressed markets.")
        st.markdown("---")
        st.markdown("## Completed Reference Layout")
        xl_sheet("PRECEDENTS Tab", [
            {"type":"section","label":"DEAL TABLE — same structure as comps + control premium columns"},
            {"row":"A2","label":"AcquireCo / TechAlpha","value":"deal label","note":"Text","type":"input"},
            {"row":"B2","label":"Year","value":"2022","note":"Input","type":"input"},
            {"row":"C2","label":"Deal EV ($M)","value":"1320","note":"From deal filing","type":"input"},
            {"row":"D2","label":"Target LTM EBITDA","value":"120","note":"EBITDA at time of deal","type":"input"},
            {"row":"E2","label":"Transaction EV/EBITDA","value":"=C2/D2","note":"Drag down","type":"formula"},
            {"row":"F2","label":"Unaffected Mkt Cap ($M)","value":"975","note":"30 days pre-announcement","type":"input"},
            {"row":"G2","label":"Control Premium","value":"=(C2-F2)/F2","note":"Drag down","type":"formula"},
            {"type":"section","label":"SUMMARY"},
            {"row":"E6","label":"Median Transaction Multiple","value":"=MEDIAN(E2:E4)","note":"Formula","type":"formula"},
            {"row":"G6","label":"Average Control Premium","value":"=AVERAGE(G2:G4)","note":"Formula","type":"formula"},
            {"type":"section","label":"NOVATECH VALUATION"},
            {"row":"C9","label":"NovaTech EBITDA","value":"120","note":"Input","type":"input"},
            {"row":"C10","label":"Implied EV","value":"=E6*C9","note":"Formula","type":"formula"},
            {"row":"C11","label":"Net Debt","value":"125","note":"Input","type":"input"},
            {"row":"C12","label":"Implied Equity Value","value":"=C10-C11","note":"Formula","type":"formula"},
            {"row":"C13","label":"Shares","value":"20","note":"Input","type":"input"},
            {"row":"C14","label":"Implied Price (deal multiples)","value":"=C12/C13","note":"Formula","type":"formula"},
            {"row":"C15","label":"Implied Acquisition Price","value":"=45*(1+G6)","note":"Current price × (1+premium)","type":"formula"},
        ])

    with build_tab:
        st.markdown("## Build the Precedent Transactions Table")
        st.markdown("Deals: AcquireCo/TechAlpha 2022 (EV 1320, EBITDA 120, unaffected mkt cap 975) | MegaCorp/DataCore 2021 (EV 980, EBITDA 100, unaffected 809) | GlobalTech/InfoPro 2023 (EV 1045, EBITDA 110, unaffected 856)")

        st.markdown("### Deal Table + Summary")
        blank_grid("prec_deals", 9,
            answers=[
                {"A":"Deal (Acquirer / Target)","B":"Year"},
                {"A":"AcquireCo / TechAlpha","B":"2022"},
                {"A":"MegaCorp / DataCore","B":"2021"},
                {"A":"GlobalTech / InfoPro","B":"2023"},
                {"A":"","B":""},
                {"A":"Median Transaction EV/EBITDA","B":"=MEDIAN(E2:E4)"},
                {"A":"Average Control Premium","B":"=AVERAGE(G2:G4)"},
                {"A":"","B":""},
                {"A":"NovaTech — Implied Acquisition Price/Share","B":"=45*(1+G6)"},
            ],
            hints=[
                ("1","Header row. Label each column: Deal, Year, Deal EV, LTM EBITDA, EV/EBITDA (formula), Unaffected Mkt Cap, Control Premium (formula)."),
                ("2","First deal. Enter Deal EV in col C (1320), EBITDA in col D (120). EV/EBITDA in col E = =C2/D2. Unaffected mkt cap in col F (975). Control premium in col G = =(C2-F2)/F2."),
                ("3","Same structure as row 2. DataCore: EV 980, EBITDA 100, unaffected mkt cap 809."),
                ("4","Same structure. InfoPro: EV 1045, EBITDA 110, unaffected mkt cap 856."),
                ("5","Leave blank as separator."),
                ("6","Median of the EV/EBITDA column across all three deals. Reference col E rows 2–4."),
                ("7","Average control premium. Reference col G rows 2–4 using =AVERAGE()."),
                ("8","Leave blank."),
                ("9","Implied acquisition price per NovaTech share: current price ($45) × (1 + average control premium). This is the floor an acquirer would need to offer."),
            ])

        st.markdown("### NovaTech Implied EV Valuation")
        blank_grid("prec_val", 5,
            answers=[
                {"A":"NovaTech EBITDA ($M)","B":"120"},
                {"A":"Implied EV (deal multiple)","B":"=E6*C9"},
                {"A":"Net Debt ($M)","B":"125"},
                {"A":"Implied Equity Value","B":"=C10-C11"},
                {"A":"Implied Share Price","B":"=C12/20"},
            ],
            hints=[
                ("1","NovaTech's EBITDA. Hardcoded input."),
                ("2","Implied EV: median deal multiple × NovaTech EBITDA. Reference the median cell from your summary block."),
                ("3","Net Debt. Hardcoded."),
                ("4","Equity Value = Implied EV − Net Debt."),
                ("5","Implied share price. Divide equity value by shares (20M)."),
            ])

# ══════════════════════════════════════════════════════════════════════════════
# LBO
# ══════════════════════════════════════════════════════════════════════════════
elif page == "lbo":
    st.markdown("# ⑤ LBO Model — Leveraged Buyout")
    learn_tab, build_tab = st.tabs(["Learn the Model", "Build It in Excel"])

    with learn_tab:
        st.markdown("## What Is an LBO and Why Does Leverage Drive Returns?")
        st.markdown("""
An LBO (Leveraged Buyout) is an acquisition financed primarily with borrowed money — typically 60% debt, 40% equity. A private equity firm provides the equity and uses the acquisition target's own cash flows to service and pay down the debt over a 3–7 year hold period. At exit (a sale or IPO), the firm collects the remaining equity value.

Why leverage? Because it amplifies returns on the equity invested. If you buy a $1,000 company with $400 equity and $600 debt, and it grows to $1,200, the debt is still $600 (assuming no paydown) and the equity is worth $600 — a 50% gain on $400 invested. If you'd bought it with 100% equity at $1,000, a $1,200 exit is only a 20% gain. The leverage magnified the return from 20% to 50%.

This amplification is only beneficial if the business generates enough cash flow to service the debt. LBO targets are therefore selected for predictable, stable cash flows — not growth. A cyclical or rapidly evolving business makes a poor LBO candidate because a cash flow shortfall triggers covenant violations and potentially bankruptcy.
""")
        st.markdown("## The Three Sources of PE Return")
        st.markdown("""
PE firms generate returns from three levers, and understanding which lever drives a specific deal matters for analysis:

**1. EBITDA Growth.** The company becomes more profitable under PE ownership — through revenue growth, cost cuts, operational improvements, or add-on acquisitions. If entry EBITDA was $120M and exit EBITDA is $160M, the company is simply worth more at the same multiple.

**2. Deleveraging.** Every dollar of cash flow used to pay down debt increases equity value by a dollar (since Equity = EV − Debt). A company that starts with $648M debt and pays it down to $400M over five years has created $248M of additional equity value, even if EV stays flat.

**3. Multiple Expansion.** If the company is bought at 9× EBITDA and sold at 11× EBITDA, the equity captures the difference. This is the least reliable source of return — it depends on market conditions at exit, not operating performance — so conservative LBO models assume entry multiple = exit multiple.
""")
        st.markdown("## Building the Model: Three Sections")
        st.markdown("""
**Section 1 — Sources & Uses.** This is the first thing every LBO model starts with. Uses = what you're buying (purchase price) plus transaction fees. Sources = how you're funding it (debt + PE equity). They must balance: Sources = Uses, always.

Purchase price = entry EV/EBITDA multiple × LTM EBITDA. If the PE firm buys at 9× and EBITDA = $120M, purchase price = $1,080M. Structure: 60% debt = $648M, 40% PE equity = $432M. Every entry assumption flows from here.

**Section 2 — Debt Schedule.** The debt schedule tracks the outstanding balance year by year across the 5-year hold. Each year: Beginning Debt → Interest Expense (= Beginning Debt × rate) → Ending Debt (= Beginning − Cash Available for Paydown). The Ending Debt in Year 1 becomes the Beginning Debt in Year 2. This rolling structure is the core of the model.

In a full model, "Cash Available for Paydown" comes from a mini income statement: EBITDA → subtract D&A → subtract interest → calculate taxes on EBIT → add D&A back → subtract capex = FCF. For simplicity here, we use a direct FCF approximation.

**Section 3 — Exit & Returns.** Exit EV = Year 5 EBITDA × exit multiple. Exit Equity = Exit EV − Remaining Debt. MOIC = Exit Equity ÷ Entry Equity.

IRR is computed using Excel's =IRR() function on a cash flow row: negative entry equity at year 0, $0 for years 1–4 (no distributions), positive exit equity at year 5. =IRR() solves for the discount rate that makes the NPV of this cash flow stream equal zero — that discount rate is the annualized return.
""")
        warning("The exit multiple assumption is the single biggest variable in an LBO model. Assuming you can exit at a higher multiple than you entered is multiple expansion — a bonus return, not a guaranteed one. Base case models always assume exit multiple = entry multiple. Downside cases use a lower exit multiple.")
        pro_tip("Build the debt schedule as a rolling structure: Ending Debt in col D (Yr 1) = =D13-D17, and Beginning Debt in col E (Yr 2) = =D18. Each year's beginning debt links from the prior year's ending debt. This is more robust than a formula that computes remaining debt as Entry Debt minus (paydown × years).")
        st.markdown("---")
        st.markdown("## Completed Reference Layout")
        xl_sheet("LBO Tab", [
            {"type":"section","label":"SOURCES & USES"},
            {"row":"B3","label":"Entry EV/EBITDA Multiple","value":"9.0","note":"Input","type":"input"},
            {"row":"B4","label":"LTM EBITDA ($M)","value":"120","note":"Input","type":"input"},
            {"row":"B5","label":"Entry EV","value":"=B3*B4","note":"Formula","type":"formula"},
            {"row":"B6","label":"Debt (60%)","value":"=B5*0.60","note":"Formula","type":"formula"},
            {"row":"B7","label":"PE Equity (40%)","value":"=B5*0.40","note":"Formula","type":"formula"},
            {"type":"section","label":"DEBT SCHEDULE — col D=Yr1, col E=Yr2 … col H=Yr5"},
            {"row":"D13","label":"Beginning Debt","value":"=B6","note":"Yr1 links from S&U; Yr2+ = prior ending debt","type":"link"},
            {"row":"D14","label":"Interest Rate","value":"0.07","note":"Input","type":"input"},
            {"row":"D15","label":"Interest Expense","value":"=D13*D14","note":"Formula — drag right","type":"formula"},
            {"row":"D16","label":"EBITDA (growing 5%/yr)","value":"=B4*1.05^1","note":"^1, ^2 … ^5 per year","type":"formula"},
            {"row":"D17","label":"Cash for Paydown","value":"=D16*0.70-30-35","note":"Simplified FCF","type":"formula"},
            {"row":"D18","label":"Ending Debt","value":"=D13-D17","note":"Next yr beginning debt","type":"formula"},
            {"type":"section","label":"EXIT & RETURNS"},
            {"row":"B25","label":"Exit Multiple","value":"9.0","note":"Input","type":"input"},
            {"row":"B26","label":"Year 5 EBITDA","value":"=B4*1.05^5","note":"Formula","type":"formula"},
            {"row":"B27","label":"Exit EV","value":"=B25*B26","note":"Formula","type":"formula"},
            {"row":"B28","label":"Remaining Debt at Exit","value":"=H18","note":"Yr5 ending debt","type":"link"},
            {"row":"B29","label":"Exit Equity","value":"=B27-B28","note":"Formula","type":"formula"},
            {"row":"B30","label":"MOIC","value":"=B29/B7","note":"Formula","type":"formula"},
            {"row":"B32","label":"IRR Cash Flow — Yr0","value":"=-B7","note":"Negative entry equity","type":"formula"},
            {"row":"F32","label":"IRR Cash Flow — Yr5","value":"=B29","note":"Exit equity in year 5 col","type":"link"},
            {"row":"B33","label":"IRR","value":"=IRR(B32:G32)","note":"=IRR() on the cash flow row","type":"formula"},
        ])

    with build_tab:
        st.markdown("## Build the LBO Model")

        st.markdown("### Section 1: Sources & Uses")
        blank_grid("lbo_su", 7,
            answers=[
                {"A":"LBO Model — NovaTech Industries","B":""},
                {"A":"","B":""},
                {"A":"Entry EV/EBITDA Multiple","B":"9.0"},
                {"A":"LTM EBITDA ($M)","B":"120"},
                {"A":"Entry EV (Purchase Price)","B":"=B3*B4"},
                {"A":"Debt (60% of EV)","B":"=B5*0.60"},
                {"A":"PE Equity (40% of EV)","B":"=B5*0.40"},
            ],
            hints=[
                ("1","Header row."),
                ("2","Leave blank — visual separator."),
                ("3","Entry multiple — the EV/EBITDA at which the PE firm acquires NovaTech. Hardcoded input."),
                ("4","NovaTech's Last Twelve Months EBITDA at the time of acquisition. Hardcoded input."),
                ("5","Purchase price formula: entry multiple × LTM EBITDA."),
                ("6","Debt portion of the capital structure: 60% of entry EV. This is what lenders provide."),
                ("7","Equity portion: 40% of entry EV. This is the PE firm's cash-out-of-pocket. It's what MOIC and IRR are measured against."),
            ])

        st.markdown("### Section 2: Debt Schedule (col D = Yr 1 through col H = Yr 5)")
        st.markdown("Fill in Year 1 formulas, then extend them across columns. The beginning debt in each year links from the ending debt of the prior year.")
        blank_grid("lbo_debt", 6, col_b_label="D (Yr 1)",
            extra_cols=["E (Yr 2)", "F (Yr 3)", "G (Yr 4)", "H (Yr 5)"],
            answers=[
                {"A":"Beginning Debt","D (Yr 1)":"=B6","E (Yr 2)":"=D18","F (Yr 3)":"=E18","G (Yr 4)":"=F18","H (Yr 5)":"=G18"},
                {"A":"Interest Rate","D (Yr 1)":"0.07","E (Yr 2)":"0.07","F (Yr 3)":"0.07","G (Yr 4)":"0.07","H (Yr 5)":"0.07"},
                {"A":"Interest Expense","D (Yr 1)":"=D13*D14","E (Yr 2)":"=E13*E14","F (Yr 3)":"=F13*F14","G (Yr 4)":"=G13*G14","H (Yr 5)":"=H13*H14"},
                {"A":"EBITDA (5% growth)","D (Yr 1)":"=B4*1.05^1","E (Yr 2)":"=B4*1.05^2","F (Yr 3)":"=B4*1.05^3","G (Yr 4)":"=B4*1.05^4","H (Yr 5)":"=B4*1.05^5"},
                {"A":"Cash for Debt Paydown","D (Yr 1)":"=D16*0.70-30-35","E (Yr 2)":"=E16*0.70-30-35","F (Yr 3)":"=F16*0.70-30-35","G (Yr 4)":"=G16*0.70-30-35","H (Yr 5)":"=H16*0.70-30-35"},
                {"A":"Ending Debt","D (Yr 1)":"=D13-D17","E (Yr 2)":"=E13-E17","F (Yr 3)":"=F13-F17","G (Yr 4)":"=G13-G17","H (Yr 5)":"=H13-H17"},
            ],
            hints=[
                ("13","Beginning Debt. Year 1 links from your Sources & Uses debt cell (=B6). Each subsequent year links from the prior year's Ending Debt row."),
                ("14","Interest rate — hardcoded in each column. NovaTech's debt carries 7% interest."),
                ("15","Interest Expense = Beginning Debt × interest rate. This reduces pre-tax income (interest is tax-deductible)."),
                ("16","EBITDA in each year. Formula: entry EBITDA × 1.05 raised to the year number. Lock the B4 reference."),
                ("17","Cash available for debt paydown. Simplified formula: EBITDA × (1−30% tax) − D&A ($30M) − Capex ($35M)."),
                ("18","Ending Debt = Beginning Debt minus cash paydown. This is the remaining balance at year end. Link it to the next year's Beginning Debt row."),
            ])

        st.markdown("### Section 3: Exit & Returns")
        blank_grid("lbo_exit", 9,
            answers=[
                {"A":"Exit EV/EBITDA Multiple","B":"9.0"},
                {"A":"Year 5 EBITDA ($M)","B":"=B4*1.05^5"},
                {"A":"Exit EV ($M)","B":"=B25*B26"},
                {"A":"Remaining Debt at Exit","B":"=H18"},
                {"A":"Exit Equity ($M)","B":"=B27-B28"},
                {"A":"MOIC","B":"=B29/B7"},
                {"A":"","B":""},
                {"A":"IRR Cash Flow Row: [-entry eq, 0, 0, 0, 0, +exit eq]","B":"=-B7"},
                {"A":"IRR","B":"=IRR(B32:G32)"},
            ],
            hints=[
                ("1","Exit multiple — assume same as entry for base case. Hardcoded input."),
                ("2","Year 5 EBITDA: entry EBITDA compounded at 5% for 5 years. Formula links from S&U section."),
                ("3","Exit EV = exit multiple × Year 5 EBITDA."),
                ("4","Remaining debt at year 5: link from your debt schedule Ending Debt in the Year 5 column."),
                ("5","Exit Equity = Exit EV − Remaining Debt. This is what the PE firm receives at exit."),
                ("6","MOIC = Exit Equity ÷ Entry Equity. Entry equity is in your Sources & Uses block."),
                ("7","Leave blank."),
                ("8","IRR cash flow row: Col B = negative entry equity (cash out at year 0). Cols C–F = 0 (no cash flows during hold). Col G = positive exit equity (cash in at year 5). Then put =IRR(B32:G32) in a cell below."),
                ("9","IRR: =IRR() on the full cash flow row from year 0 through year 5. This is the annualized return on the PE firm's equity."),
            ])

# ══════════════════════════════════════════════════════════════════════════════
# MERGER MODEL
# ══════════════════════════════════════════════════════════════════════════════
elif page == "merger":
    st.markdown("# ⑥ Merger Model — M&A Accretion / Dilution")
    learn_tab, build_tab = st.tabs(["Learn the Model", "Build It in Excel"])

    with learn_tab:
        st.markdown("## What Is Accretion and Why Do Boards Care?")
        st.markdown("""
A merger model answers one question: if Company A acquires Company B, does the combined company's Earnings Per Share (EPS) go up or down relative to Company A's standalone EPS?

**Accretive** means the deal increases EPS. The combined earnings power divided by the combined share count produces a higher per-share number than Company A had before.

**Dilutive** means the deal decreases EPS. The share count grew faster than earnings, reducing the per-share figure.

Boards and public investors focus intensely on this metric because EPS drives stock price over time. A dilutive deal — especially one without a compelling strategic rationale — invites shareholder criticism and activist pressure. CEOs can lose their jobs over significant EPS dilution without a credible synergy story.

But EPS accretion/dilution can be gamed. A company with a high P/E can acquire a company with a low P/E in an all-stock deal and mechanically produce accretion even with zero synergies. The real question is whether the deal creates economic value, which requires a DCF alongside the accretion/dilution analysis.
""")
        st.markdown("## Why All-Stock Deals Are More Complex")
        st.markdown("""
In a cash deal, the acquirer simply pays cash and the target's shareholders disappear. No new shares are issued. The only effect on EPS is that the acquirer's net income increases (by the target's NI + synergies − financing cost of the cash) while share count stays the same.

In an all-stock deal, the acquirer issues new shares to pay for the target. This increases the share count, which dilutes EPS unless the earnings contribution from the acquired business more than compensates. The dilution effect depends on three variables:

1. **Deal value** — how much the acquirer is paying (offer price × target shares)
2. **New shares issued** — deal value ÷ acquirer stock price (at a higher stock price, fewer new shares need to be issued)
3. **Earnings contribution** — target NI + synergies − amortization of acquired intangibles

If the target's P/E is higher than the acquirer's P/E, the deal is mechanically dilutive in all-stock (you're issuing expensive currency for expensive earnings). If the target's P/E is lower, the deal tends to be accretive.
""")
        st.markdown("## Building the Pro Forma Income Statement")
        st.markdown("""
The core of the merger model is the pro forma income statement — a combined view of the two companies after the deal closes. It has three adjustments versus simply adding the two income statements together:

**Synergies (positive).** Cost synergies come from eliminating duplicate functions — redundant corporate offices, overlapping sales forces, shared IT systems. Revenue synergies (cross-selling, expanded customer reach) are harder to model and less certain. Bankers typically haircut management's synergy estimates by 20–50% and phase them in over 2–3 years. Enter synergies as a positive number (they increase combined earnings).

**Amortization of Acquired Intangibles (negative).** When you acquire a company, accounting rules (purchase price allocation) require you to step up the value of intangible assets — brands, customer relationships, technology — to fair value. These stepped-up intangibles are then amortized over their useful lives, creating a recurring expense that reduces reported earnings. This is purely a non-cash accounting charge, but it hits reported EPS and must be modeled.

**Interest on Acquisition Debt (if cash deal).** In a cash deal, the acquirer may borrow to fund the acquisition. The interest on that debt (net of tax) reduces pro forma earnings. In an all-stock deal, no new debt is incurred.

**The EPS test.** Pro Forma EPS = Pro Forma Net Income ÷ Pro Forma Shares. Compare to standalone EPS = Acquirer NI ÷ Acquirer Shares. The % change = (PF EPS − Standalone EPS) ÷ Standalone EPS. Positive = accretive; negative = dilutive.
""")
        warning("Synergies are almost always overstated by management. When modeling, use conservative (low) synergy estimates in your base case and run a sensitivity showing how EPS changes as synergies vary from zero to full management estimates. Break-even synergies — the minimum needed for the deal to be EPS-neutral — is the most useful single output.")
        st.markdown("---")
        st.markdown("## Completed Reference Layout")
        xl_sheet("MERGER Tab", [
            {"type":"section","label":"DEAL ASSUMPTIONS"},
            {"row":"B2","label":"Target Stock Price","value":"30","note":"Input","type":"input"},
            {"row":"B3","label":"Acquisition Premium","value":"0.25","note":"Input","type":"input"},
            {"row":"B4","label":"Offer Price/Share","value":"=B2*(1+B3)","note":"Formula","type":"formula"},
            {"row":"B5","label":"Target Shares (M)","value":"10","note":"Input","type":"input"},
            {"row":"B6","label":"Total Deal Value ($M)","value":"=B4*B5","note":"Formula","type":"formula"},
            {"row":"B7","label":"Acquirer Stock Price","value":"45","note":"Input","type":"input"},
            {"row":"B8","label":"New Shares Issued (M)","value":"=B6/B7","note":"Formula","type":"formula"},
            {"type":"section","label":"PRO FORMA INCOME STATEMENT"},
            {"row":"B13","label":"Acquirer Net Income","value":"52.5","note":"Input","type":"input"},
            {"row":"B14","label":"Target Net Income","value":"20","note":"Input","type":"input"},
            {"row":"B15","label":"Synergies (after-tax)","value":"5","note":"Input","type":"input"},
            {"row":"B16","label":"Amortization of Intangibles","value":"-2","note":"Input (negative)","type":"input"},
            {"row":"B17","label":"Pro Forma Net Income","value":"=SUM(B13:B16)","note":"Formula","type":"formula"},
            {"type":"section","label":"EPS & ACCRETION/DILUTION"},
            {"row":"B20","label":"Acquirer Shares Standalone","value":"20","note":"Input","type":"input"},
            {"row":"B21","label":"New Shares Issued","value":"=B8","note":"Link from deal section","type":"link"},
            {"row":"B22","label":"Pro Forma Shares","value":"=B20+B21","note":"Formula","type":"formula"},
            {"row":"B23","label":"Standalone EPS","value":"=B13/B20","note":"Formula","type":"formula"},
            {"row":"B24","label":"Pro Forma EPS","value":"=B17/B22","note":"Formula","type":"formula"},
            {"row":"B25","label":"Accretion/(Dilution) %","value":"=(B24-B23)/B23","note":"Format as %","type":"formula"},
        ])

    with build_tab:
        st.markdown("## Build the Merger Model")

        st.markdown("### Section 1: Deal Assumptions")
        blank_grid("merger_deal", 8,
            answers=[
                {"A":"Merger Model — NovaTech acquires TargetCo","B":""},
                {"A":"Target Current Stock Price","B":"30"},
                {"A":"Acquisition Premium","B":"0.25"},
                {"A":"Offer Price per Share","B":"=B2*(1+B3)"},
                {"A":"Target Shares Outstanding (M)","B":"10"},
                {"A":"Total Deal Value ($M)","B":"=B4*B5"},
                {"A":"Acquirer (NovaTech) Stock Price","B":"45"},
                {"A":"New NovaTech Shares Issued (M)","B":"=B6/B7"},
            ],
            hints=[
                ("1","Header row."),
                ("2","What TargetCo's stock is currently trading at in the market before any deal. Hardcoded input."),
                ("3","The premium above market price that NovaTech is offering. 25% is typical. Enter as a decimal."),
                ("4","Offer price formula: current price × (1 + premium). What each TargetCo shareholder receives per share."),
                ("5","Total TargetCo shares outstanding. Hardcoded input."),
                ("6","Total deal value formula: offer price × target shares. This is what NovaTech needs to pay in total."),
                ("7","NovaTech's current stock price — the 'currency' being used in an all-stock deal. Hardcoded input."),
                ("8","New shares NovaTech must issue: total deal value ÷ NovaTech's stock price. More expensive NovaTech stock = fewer new shares = less dilution."),
            ])

        st.markdown("### Section 2: Pro Forma Income Statement")
        blank_grid("merger_pf", 5,
            answers=[
                {"A":"NovaTech Standalone Net Income ($M)","B":"52.5"},
                {"A":"TargetCo Net Income ($M)","B":"20"},
                {"A":"Cost Synergies (after-tax, $M)","B":"5"},
                {"A":"Amortization of Acquired Intangibles ($M)","B":"-2"},
                {"A":"Pro Forma Net Income ($M)","B":"=SUM(B13:B16)"},
            ],
            hints=[
                ("13","NovaTech's standalone net income. Hardcoded input."),
                ("14","TargetCo's net income that comes along with the acquisition. Hardcoded input."),
                ("15","Expected cost savings from combining the two companies. Entered as a positive number. After-tax means the synergy number is already net of the tax impact."),
                ("16","Non-cash accounting charge from stepping up acquired intangibles to fair value. Enter as a negative number — it reduces earnings."),
                ("17","Pro Forma Net Income: sum all four rows above. This is combined earnings after deal adjustments."),
            ])

        st.markdown("### Section 3: EPS & Accretion/Dilution Test")
        blank_grid("merger_eps", 6,
            answers=[
                {"A":"NovaTech Standalone Shares (M)","B":"20"},
                {"A":"New Shares Issued (M)","B":"=B8"},
                {"A":"Pro Forma Total Shares (M)","B":"=B20+B21"},
                {"A":"NovaTech Standalone EPS","B":"=B13/B20"},
                {"A":"Pro Forma EPS","B":"=B17/B22"},
                {"A":"Accretion / (Dilution) %","B":"=(B24-B23)/B23"},
            ],
            hints=[
                ("20","NovaTech's current shares before the deal. Hardcoded input."),
                ("21","New shares from the deal — link from your deal assumptions section using =B8."),
                ("22","Combined share count post-deal: standalone + new shares issued."),
                ("23","NovaTech's standalone EPS before the deal: Net Income ÷ Standalone Shares."),
                ("24","Pro Forma EPS post-deal: Pro Forma Net Income ÷ Pro Forma Shares."),
                ("25","Accretion/(Dilution): (PF EPS − Standalone EPS) ÷ Standalone EPS. Format this cell as a percentage in Excel. Positive = accretive. Negative = dilutive."),
            ])

# ══════════════════════════════════════════════════════════════════════════════
# BUDGET VS. ACTUAL
# ══════════════════════════════════════════════════════════════════════════════
elif page == "budget":
    st.markdown("# ⑦ Budget vs. Actual Model")
    learn_tab, build_tab = st.tabs(["Learn the Model", "Build It in Excel"])

    with learn_tab:
        st.markdown("## What BvA Is and Why It Matters")
        st.markdown("""
Budget vs. Actual (BvA) is the core rhythm of corporate finance. Every month, the FP&A (Financial Planning & Analysis) team publishes a report comparing what was planned (the budget, set at the beginning of the year) against what actually happened (the actuals, pulled from the accounting system). The result is a variance report.

This sounds simple, but the skill is in the interpretation. A $7M revenue miss sounds bad. But is it because the sales team sold fewer units (a volume problem — fix the pipeline)? Or because they sold the budgeted number of units at lower prices (a pricing problem — fix the discount policy)? These are completely different business problems requiring completely different responses. The BvA model's job is to separate them.

CFOs and boards live in this model. Every monthly business review starts with a BvA — which lines missed, by how much, why, and what's being done. The analyst who builds it needs to be able to explain every variance, not just compute it.
""")
        st.markdown("## Building the Variance Table")
        st.markdown("""
The table architecture is straightforward: one row per P&L line item (Revenue, COGS, Gross Profit, SG&A, EBITDA), with columns for Budget, Actual, Variance $, Variance %, and a Favorable/Unfavorable flag.

**Variance $ = Actual − Budget.** For revenue, a positive variance is good (you beat). For costs, a positive variance is bad (you overspent). This is the most common source of confusion in BvA — the sign convention flips between revenue and cost lines.

**Favorable/Unfavorable (F/U) flag.** Use an IF formula: for revenue rows, =IF(Variance>=0, "F", "U"). For cost rows, the logic reverses: =IF(Variance<=0, "F", "U"). In practice, many teams just use a single rule (positive = favorable for revenue, negative = favorable for costs) and build the flag into a lookup or IF-AND formula.

**Gross Profit and EBITDA are derived, not input.** You don't enter actual gross profit directly — you calculate it from actual revenue minus actual COGS (=C2-C3). This is important: if a line is a formula in the budget column, it must also be a formula in the actual column.

**Conditional formatting** makes the table readable at a glance. Select the Variance $ column → Home → Conditional Formatting → Highlight Cell Rules → set red for negative numbers, green for positive. In a management review, a CFO needs to see at a glance which lines are red without reading every number.
""")
        st.markdown("## Volume / Price Decomposition")
        st.markdown("""
When revenue misses budget, the first question is: did we sell fewer units, or did we sell them at a lower price? These require different responses.

**Volume Effect = (Actual Units − Budget Units) × Budget Price.** This isolates the impact of unit volume on revenue, holding price constant at the budgeted level. If you sold 500 fewer units than budgeted at $10,000 each, the volume effect is −$5M.

**Price Effect = Actual Units × (Actual Price − Budget Price).** This isolates the pricing impact, holding volume at the actual level. If prices were $174 lower than budgeted across 11,500 actual units, the price effect is −$2M.

The two effects sum to the total revenue variance: Volume Effect + Price Effect = Revenue Variance $. This is a built-in check on your work.

Why hold price constant in the volume effect and use actual units in the price effect? This is the standard "Laspeyres" decomposition — volume comes first, price second. The alternative (price first) gives slightly different numbers but the choice is conventional and should be consistent throughout your analysis.

The business response differs: a volume miss means you need more leads, better conversion, or more sales reps. A price miss means your discounting is out of control, you're facing more competitive pressure, or you have a mix shift toward lower-margin products. The CEO and board need to know which it is.
""")
        warning("A revenue miss almost always creates a disproportionately larger EBITDA miss. If revenue misses by 5%, EBITDA might miss by 25% — because many costs are fixed. The fixed-cost operating leverage that helps EBITDA margins expand in good times works against you in bad times. Always compute and explain the EBITDA variance % alongside the revenue variance %.")
        pro_tip("Select the variance column and apply two conditional formatting rules: cells less than zero → red fill, cells greater than zero → green fill. For cost rows you may want to invert this (red for positive variance since overspending is bad). This visual layer makes the table instantly scannable in a CFO presentation.")
        st.markdown("---")
        st.markdown("## Completed Reference Layout")
        xl_sheet("BVA Tab", [
            {"type":"section","label":"MAIN TABLE — Col A=Label, B=Budget, C=Actual, D=Variance $, E=Variance %, F=F/U"},
            {"row":"B2","label":"Revenue (Budget)","value":"120","note":"Input","type":"input"},
            {"row":"C2","label":"Revenue (Actual)","value":"113","note":"Input","type":"input"},
            {"row":"D2","label":"Revenue Variance $","value":"=C2-B2","note":"Formula","type":"formula"},
            {"row":"E2","label":"Revenue Variance %","value":"=D2/B2","note":"Format as %","type":"formula"},
            {"row":"F2","label":"Revenue F/U","value":"=IF(D2>=0,\"F\",\"U\")","note":"Formula","type":"formula"},
            {"type":"section","label":"REPEAT FOR COGS (row 3), GROSS PROFIT (row 4 — derived), SG&A (row 5), EBITDA (row 6)"},
            {"row":"B4","label":"Gross Profit (Budget)","value":"=B2-B3","note":"Derived — not a hardcoded input","type":"formula"},
            {"row":"C4","label":"Gross Profit (Actual)","value":"=C2-C3","note":"Derived","type":"formula"},
            {"row":"D4","label":"Gross Profit Variance","value":"=C4-B4","note":"Formula","type":"formula"},
            {"type":"section","label":"VOLUME / PRICE DECOMPOSITION"},
            {"row":"B12","label":"Budget Units","value":"12000","note":"Input","type":"input"},
            {"row":"B13","label":"Budget Price/Unit ($)","value":"10000","note":"Input","type":"input"},
            {"row":"B14","label":"Actual Units","value":"11500","note":"Input","type":"input"},
            {"row":"B15","label":"Actual Price/Unit ($)","value":"9826","note":"Input","type":"input"},
            {"row":"B16","label":"Volume Effect ($M)","value":"=(B14-B12)*B13/1000000","note":"Formula","type":"formula"},
            {"row":"B17","label":"Price Effect ($M)","value":"=B14*(B15-B13)/1000000","note":"Formula","type":"formula"},
            {"row":"B18","label":"Check (= Revenue Variance)","value":"=B16+B17","note":"Must equal D2","type":"formula"},
        ])

    with build_tab:
        st.markdown("## Build the Budget vs. Actual Model")
        st.markdown("Q1 data: Budget revenue $120M, actual $113M. Budget COGS $72M, actual $70.3M. Budget SG&A $20M, actual $21.5M. Budget EBITDA $28M, actual $21.2M.")

        st.markdown("### Main Variance Table (cols A–F, rows 1–6)")
        st.markdown("Build the header row first, then each P&L line. Gross Profit and EBITDA rows should use formulas, not hardcoded actuals.")
        blank_grid("bva_main", 7,
            answers=[
                {"A":"Line Item","B":"Budget ($M)"},
                {"A":"Revenue","B":"120"},
                {"A":"COGS","B":"72"},
                {"A":"Gross Profit","B":"=B2-B3"},
                {"A":"SG&A","B":"20"},
                {"A":"EBITDA","B":"=B4-B5"},
                {"A":"","B":""},
            ],
            hints=[
                ("1","Header row. Col A = Line Item, Col B = Budget, Col C = Actual, Col D = Variance $, Col E = Variance %, Col F = F/U flag. Label all columns."),
                ("2","Revenue row. Enter budget in col B (120), actual in col C (113). Variance in col D = Actual − Budget. Variance % in col E = Variance ÷ Budget. F/U in col F: =IF(D2>=0,\"F\",\"U\")."),
                ("3","COGS row. Same structure. Budget 72, actual 70.3. For COGS: a negative variance is favorable (spent less than planned). Adjust your F/U formula accordingly."),
                ("4","Gross Profit row. Do NOT hardcode actuals. Budget = =B2-B3, Actual = =C2-C3. Variance = Actual − Budget. This ensures consistency with the revenue and COGS rows."),
                ("5","SG&A row. Budget 20, actual 21.5. Same structure as COGS."),
                ("6","EBITDA row. Budget = =B4-B5, Actual = =C4-C5. This cascades from all the rows above automatically."),
                ("7","Leave blank or use as a totals check row."),
            ])

        st.markdown("### Volume / Price Decomposition")
        blank_grid("bva_decomp", 7,
            answers=[
                {"A":"Volume / Price Revenue Decomposition","B":""},
                {"A":"Budget Units Sold","B":"12000"},
                {"A":"Budget Price per Unit ($)","B":"10000"},
                {"A":"Actual Units Sold","B":"11500"},
                {"A":"Actual Price per Unit ($)","B":"9826"},
                {"A":"Volume Effect ($M)","B":"=(B14-B12)*B13/1000000"},
                {"A":"Price Effect ($M)","B":"=B14*(B15-B13)/1000000"},
            ],
            hints=[
                ("1","Section header."),
                ("2","Budget units: how many units the company planned to sell this quarter."),
                ("3","Budget price per unit: the average selling price assumed in the plan."),
                ("4","Actual units: how many were actually sold."),
                ("5","Actual price per unit: average realized price across actual sales."),
                ("6","Volume Effect formula: (Actual Units − Budget Units) × Budget Price, divided by 1,000,000 to convert to $M. This isolates how much of the miss was from selling fewer units."),
                ("7","Price Effect formula: Actual Units × (Actual Price − Budget Price), divided by 1,000,000. This isolates the pricing component. Add a row 8 check: =B16+B17. It must equal your revenue variance $ from the main table."),
            ])
