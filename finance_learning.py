import streamlit as st
import pandas as pd
import numpy as np
import re as _re

st.set_page_config(page_title="Financial Modeling School", layout="wide", page_icon="📈")

if "current_page" not in st.session_state:
    st.session_state.current_page = "overview"

# ── Practice companies ─────────────────────────────────────────────────────────
COMPANIES = [
    {"name":"NovaTech Industries",    "sector":"Technology",
     "revenue":"$500M",  "ebitda":"$120M", "ni":"$52.5M","price":"$45.00","shares":"20M",
     "rev_n":500, "ebitda_n":120, "ni_n":52.5, "price_n":45.00, "shares_n":20,
     "rev_growth":0.05, "wacc":0.0935, "terminal_g":0.025},
    {"name":"Meridian Capital Group", "sector":"Financial Services",
     "revenue":"$320M",  "ebitda":"$85M",  "ni":"$38M",  "price":"$28.00","shares":"15M",
     "rev_n":320, "ebitda_n":85,  "ni_n":38,   "price_n":28.00, "shares_n":15,
     "rev_growth":0.04, "wacc":0.0850, "terminal_g":0.020},
    {"name":"Apex Consumer Brands",   "sector":"Consumer Staples",
     "revenue":"$1.2B",  "ebitda":"$210M", "ni":"$95M",  "price":"$62.00","shares":"40M",
     "rev_n":1200,"ebitda_n":210, "ni_n":95,   "price_n":62.00, "shares_n":40,
     "rev_growth":0.03, "wacc":0.0750, "terminal_g":0.020},
    {"name":"Frontier Energy",        "sector":"Energy",
     "revenue":"$780M",  "ebitda":"$165M", "ni":"$72M",  "price":"$38.50","shares":"25M",
     "rev_n":780, "ebitda_n":165, "ni_n":72,   "price_n":38.50, "shares_n":25,
     "rev_growth":0.06, "wacc":0.1000, "terminal_g":0.020},
    {"name":"Cascade Logistics",      "sector":"Industrials",
     "revenue":"$440M",  "ebitda":"$95M",  "ni":"$41M",  "price":"$33.00","shares":"18M",
     "rev_n":440, "ebitda_n":95,  "ni_n":41,   "price_n":33.00, "shares_n":18,
     "rev_growth":0.05, "wacc":0.0875, "terminal_g":0.020},
]


def _co_inputs(co):
    """Compute per-page given-inputs from a company's numeric fields.
    IS, BS, and CFS figures are derived so they are internally consistent.
    Balance sheet always ties: Total Assets == Total L&E.
    """
    R, E, N, P, S = co["rev_n"], co["ebitda_n"], co["ni_n"], co["price_n"], co["shares_n"]
    TAX = 0.30

    # Income statement line items
    cogs     = round(R * 0.60, 1)
    sga      = round(R * 0.40 - E, 1)
    da       = round(R * 0.06, 1)
    ebit     = E - da
    interest = round(ebit - N / (1 - TAX), 1)
    capex    = round(R * 0.07, 1)
    divs     = round(N * 0.25, 1)

    # Net debt ~1.05× EBITDA, rounded to nearest $5M
    net_debt = round(E * 1.05 / 5) * 5

    # Balance sheet — built so Total Assets == Total L&E exactly
    cash   = round(R * 0.15, 1)
    ar     = round(R * 0.12, 1)
    inv    = round(R * 0.08, 1)
    ppe    = round(R * 0.40, 1)
    intang = round(R * 0.10, 1)
    ap     = round(R * 0.06, 1)
    st_debt = round(net_debt * 0.15 / 5) * 5        # ~15% of net debt, rounded to $5M
    lt_debt = net_debt + cash - st_debt              # ensures net_debt = LTD + STD − Cash
    total_assets = cash + ar + inv + ppe + intang
    total_liab   = ap + st_debt + lt_debt
    equity       = total_assets - total_liab
    com_stock    = round(equity * 0.50, 1)
    ret_earn     = round(equity - com_stock, 1)

    def fm(v):
        if abs(v) >= 1000:
            return f"${v/1000:.1f}B"
        return f"${int(v)}M" if v == int(v) else f"${v}M"

    ebitda_margin = E / R
    rev_growth = co.get("rev_growth", 0.05)
    wacc       = co.get("wacc", 0.0935)
    terminal_g = co.get("terminal_g", 0.025)

    # Budget vs. Actual — Q1 figures (~24% of annual)
    # Keep unit count constant (12,000 budget / 11,500 actual); price per unit scales with revenue.
    Q1_UNITS_B, Q1_UNITS_A = 12_000, 11_500
    q1_rev_b   = round(R * 0.24, 1)
    q1_rev_a   = round(q1_rev_b * 0.942, 1)
    q1_cogs_b  = round(cogs * 0.24, 1)
    q1_cogs_a  = round(q1_cogs_b * 0.976, 1)
    q1_sga_b   = round(sga * 0.25, 1)
    q1_sga_a   = round(q1_sga_b * 1.075, 1)
    q1_price_b = round(q1_rev_b * 1e6 / Q1_UNITS_B)
    q1_price_a = round(q1_rev_a * 1e6 / Q1_UNITS_A)

    # Merger target (always ~60% of acquirer size)
    tgt_price   = round(P * 0.60, 2)
    tgt_shares  = round(S * 0.40, 1)
    tgt_ni      = round(N * 0.35, 1)
    synergies   = round(N * 0.08, 1)
    intang_amort = round(N * 0.04, 1)

    return {
        "3stmt": [
            ("Revenue", fm(R)), ("COGS", fm(cogs)), ("SG&A", fm(sga)),
            ("D&A", fm(da)), ("Interest Exp.", fm(interest)), ("Tax Rate", "30%"),
            ("Beg. Cash", fm(cash)), ("Beg. AR", fm(ar)), ("Beg. Inventory", fm(inv)),
            ("Beg. PP&E", fm(ppe)), ("Beg. Intangibles", fm(intang)),
            ("Beg. AP", fm(ap)), ("Beg. ST Debt", fm(st_debt)), ("Beg. LT Debt", fm(lt_debt)),
            ("Beg. Com. Stock", fm(com_stock)), ("Beg. Ret. Earn.", fm(ret_earn)),
            ("Capex", fm(capex)), ("Dividends", fm(divs)),
        ],
        "dcf": [
            ("Base Revenue", fm(R)), ("Rev. Growth", f"{rev_growth*100:.1f}%"),
            ("EBITDA Margin", f"{ebitda_margin*100:.1f}%"), ("D&A % Rev.", "6.0%"),
            ("Capex % Rev.", "7.0%"), ("Tax Rate", "30%"),
            ("WACC", f"{wacc*100:.2f}%"), ("Terminal g", f"{terminal_g*100:.1f}%"),
            ("Net Debt", fm(net_debt)), ("Shares Out.", f"{int(S)}M"),
        ],
        "comps": [
            ("LTM EBITDA", fm(E)), ("Net Debt", fm(net_debt)), ("Shares Out.", f"{int(S)}M"),
        ],
        "precedent": [
            ("LTM EBITDA", fm(E)), ("Net Debt", fm(net_debt)),
            ("Shares Out.", f"{int(S)}M"), ("Current Price", f"${P:.2f}"),
        ],
        "lbo": [
            ("LTM EBITDA", fm(E)), ("Entry EV/EBITDA", "9.0×"),
            ("Debt / EV", "60%"), ("Interest Rate", "7.0%"),
            ("EBITDA Growth", "5% / yr"), ("D&A", fm(da)),
            ("Capex", fm(capex)), ("Tax Rate", "30%"), ("Exit EV/EBITDA", "9.0×"),
        ],
        "merger": [
            ("Target Price", f"${tgt_price:.2f}"), ("Acq. Premium", "25%"),
            ("Target Shares", f"{tgt_shares}M"), ("Target NI", fm(tgt_ni)),
            ("Acquirer NI", fm(N)), ("Acquirer Shares", f"{int(S)}M"),
            ("After-tax Synergies", fm(synergies)), ("Intangibles Amort.", f"${intang_amort}M/yr"),
        ],
        "budget": [
            ("Budg. Revenue", fm(q1_rev_b)), ("Act. Revenue", fm(q1_rev_a)),
            ("Budg. COGS", fm(q1_cogs_b)), ("Act. COGS", fm(q1_cogs_a)),
            ("Budg. SG&A", fm(q1_sga_b)), ("Act. SG&A", fm(q1_sga_a)),
            ("Budg. Units", f"{Q1_UNITS_B:,}"), ("Budg. Price/Unit", f"${q1_price_b:,}"),
            ("Act. Units", f"{Q1_UNITS_A:,}"), ("Act. Price/Unit", f"${q1_price_a:,}"),
        ],
    }
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
/* ── Collapse Streamlit top bar to zero height (preserves sidebar toggle) ── */
header[data-testid="stHeader"] {
    height:0 !important; min-height:0 !important;
    padding:0 !important; margin:0 !important;
    overflow:visible !important;
}
/* Always keep the sidebar expand button reachable */
[data-testid="collapsedControl"] {
    display:flex !important; visibility:visible !important;
    opacity:1 !important; pointer-events:auto !important;
    z-index:999999 !important;
}

/* ── Global background & text ── */
.stApp { background:#F8FAFC; }
.stApp p, .stApp li, .stMarkdown p, .stMarkdown li { color:#374151; font-size:.93rem; line-height:1.72; }
.stApp h1 { color:#111827; font-size:1.65rem; font-weight:700; letter-spacing:-.01em; }
.stApp h2 { color:#111827; font-size:1.15rem; font-weight:700; margin-top:1.8rem; }
.stApp h3 { color:#1F2937; font-size:1rem; font-weight:600; }
.stApp strong, .stMarkdown strong { color:#111827; }
.block-container { padding-top:0 !important; padding-bottom:2.5rem; max-width:1100px; }

/* ── Page header ── */
.page-hdr-title { font-size:1.08rem; font-weight:800; color:#111827; letter-spacing:-.01em; line-height:1.25; }
.page-hdr-sub   { font-size:.72rem; color:#9CA3AF; margin-top:2px; }
.page-hdr-co    {
    display:inline-flex; align-items:center; gap:6px;
    padding:5px 12px; background:#EFF6FF;
    border:1px solid #BFDBFE; border-radius:5px;
}
.page-hdr-co-name   { font-size:.78rem; font-weight:700; color:#1D4ED8; }
.page-hdr-co-sector { font-size:.65rem; color:#64748B; }
.page-hdr-inputs-lbl {
    font-size:.57rem; font-weight:700; letter-spacing:.14em;
    text-transform:uppercase; color:#94A3B8; margin-bottom:5px;
}

/* ── Input chips ── */
.input-chip {
    display:inline-flex; align-items:baseline; gap:4px;
    font-size:.71rem; color:#111827; font-weight:600;
    background:#F8FAFC; padding:2px 8px;
    border:1px solid #E2E8F0; border-radius:3px;
    margin:2px 3px 2px 0; white-space:nowrap;
}
.input-chip-lbl {
    font-size:.57rem; color:#94A3B8; font-weight:500;
    letter-spacing:.03em; text-transform:uppercase;
}

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

/* ── Guide panel for Build tabs ── */
.guide-panel {
    background:#F8FAFC; border:1px solid #E5E7EB;
    border-left:3px solid #2563EB;
    padding:12px 14px; margin-bottom:8px;
}
.guide-line {
    font-size:.79rem; color:#374151; line-height:1.85;
    padding:3px 0; border-bottom:1px solid #F3F4F6;
}
.guide-line:last-child { border-bottom:none; }

/* ── Sidebar — grey ladder ── */
section[data-testid="stSidebar"],
[data-testid="stSidebar"] {
    background:#F9FAFB !important;
    border-right:1px solid #E5E7EB !important;
}
section[data-testid="stSidebar"] > div { padding-top:0 !important; }

.nav-wordmark {
    background:#F3F4F6; border-bottom:1px solid #E5E7EB;
    padding:15px 16px; margin-bottom:4px;
    font-size:.68rem; font-weight:800; letter-spacing:.22em;
    text-transform:uppercase; color:#374151;
}
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
    width:100% !important; text-align:left !important;
    border-radius:0 !important;
    border-top:none !important; border-right:none !important;
    border-bottom:1px solid #E5E7EB !important;
    border-left:3px solid #C9CDD4 !important;
    outline:none !important; box-shadow:none !important;
    font-size:.82rem !important; font-weight:500 !important;
    padding:9px 12px 9px 14px !important; margin:0 !important;
    background-color:#EAECEF !important; color:#1E3A5F !important;
}
[data-testid="stSidebar"] .stButton > button *,
[data-testid="stSidebar"] .stButton > button p,
[data-testid="stSidebar"] .stButton > button span,
[data-testid="stSidebar"] .stButton > button div { color:#1E3A5F !important; }
[data-testid="stSidebar"] .stButton > button:hover {
    background-color:#D9DCE0 !important; border-left-color:#6B7280 !important; color:#111827 !important;
}
[data-testid="stSidebar"] .stButton > button:hover * { color:#111827 !important; }
[data-testid="stSidebar"] .stButton > button[kind="primary"],
[data-testid="stSidebar"] .stButton > button[kind="primary"]:focus,
[data-testid="stSidebar"] .stButton > button[kind="primary"]:active {
    background-color:#D1D5DB !important; border-left-color:#1E3A5F !important;
    color:#111827 !important; font-weight:700 !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] * {
    color:#111827 !important; font-weight:700 !important;
}

/* ── Excel formula bar ── */
.xl-fbar-label {
    display:flex; align-items:center; gap:8px;
    background:#F1F5F9; border:1px solid #CBD5E1;
    border-radius:4px 4px 0 0; padding:3px 8px;
    font-size:.59rem; font-weight:700; letter-spacing:.1em;
    text-transform:uppercase; color:#64748B; margin-bottom:0;
}
.xl-ref-chip {
    display:inline-block; font-size:.64rem; font-weight:700;
    font-family:'SF Mono','Fira Code',monospace;
    background:#EFF6FF; color:#1D4ED8;
    border:1px solid #BFDBFE; border-radius:2px;
    padding:1px 5px; margin:1px 2px; cursor:pointer;
}

/* ── Hint rows ── */
.hint-row { font-size:.8rem; color:#4B5563; padding:6px 0; border-bottom:1px solid #F3F4F6; }
.hint-num { display:inline-block; width:54px; font-family:monospace; color:#9CA3AF; font-size:.71rem; }

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

# ── Formula engine ─────────────────────────────────────────────────────────────

def _eval_formula(raw, cell_vals, cross=None):
    """Evaluate one cell. cross = {SheetName: {ref: val}} for cross-section refs."""
    if cross is None:
        cross = {}
    s = str(raw).strip()
    if not s or s.lower() == "nan":
        return ""
    if not s.startswith("="):
        clean = s.replace("$", "").replace(",", "")
        try:
            return float(clean)
        except:
            return s

    expr = s[1:]

    # Strip $ from refs: $B$2 → B2
    expr = _re.sub(r'\$([A-Z])\$(\d+)', r'\1\2', expr)
    expr = _re.sub(r'\$([A-Z])(\d+)', r'\1\2', expr)
    expr = _re.sub(r'([A-Z])\$(\d+)', r'\1\2', expr)

    # Cross-sheet: IS!B12 → value from cross["IS"]["B12"]
    def _xr(m):
        sheet = m.group(1).upper()
        ref = m.group(2).upper()
        v = cross.get(sheet, {}).get(ref, 0)
        return str(float(v)) if isinstance(v, (int, float)) else "0"
    expr = _re.sub(r'([A-Za-z_]\w*)!([A-Z]\d+)', _xr, expr)

    # SUM(A1:A5)
    def _sum(m):
        col, r1, r2 = m.group(1).upper(), int(m.group(2)), int(m.group(4))
        total = sum(float(cell_vals.get(f"{col}{r}", 0) or 0)
                    for r in range(r1, r2+1)
                    if isinstance(cell_vals.get(f"{col}{r}", 0), (int, float)))
        return str(total)
    expr = _re.sub(r'SUM\(([A-Z])(\d+):([A-Z])(\d+)\)', _sum, expr, flags=_re.I)

    # Aggregate functions
    for fn_name, fn_np in [("MEDIAN", np.median), ("AVERAGE", np.mean), ("MAX", np.max), ("MIN", np.min)]:
        def _agg(m, fn=fn_np):
            col, r1, r2 = m.group(1).upper(), int(m.group(2)), int(m.group(4))
            vs = [float(cell_vals.get(f"{col}{r}", 0) or 0)
                  for r in range(r1, r2+1)
                  if isinstance(cell_vals.get(f"{col}{r}", 0), (int, float))]
            return str(round(float(fn(vs)), 8)) if vs else "0"
        expr = _re.sub(fr'{fn_name}\(([A-Z])(\d+):([A-Z])(\d+)\)', _agg, expr, flags=_re.I)

    # PERCENTILE(A1:A5, 0.25)
    def _pct(m):
        col, r1, r2, p = m.group(1).upper(), int(m.group(2)), int(m.group(4)), float(m.group(5))
        vs = [float(cell_vals.get(f"{col}{r}", 0) or 0)
              for r in range(r1, r2+1)
              if isinstance(cell_vals.get(f"{col}{r}", 0), (int, float))]
        return str(round(np.percentile(vs, p * 100), 8)) if vs else "0"
    expr = _re.sub(r'PERCENTILE\(([A-Z])(\d+):([A-Z])(\d+),\s*([0-9.]+)\)', _pct, expr, flags=_re.I)

    # IF(cond, true, false) — simple, no nesting
    def _if(m):
        cond_s, tv, fv = m.group(1).strip(), m.group(2).strip().strip('"\''), m.group(3).strip().strip('"\'')
        ce = _re.sub(r'[A-Z]\d+', lambda mc: str(float(cell_vals.get(mc.group(0).upper(), 0) or 0)), cond_s)
        try:
            return f'"{tv}"' if bool(eval(ce, {"__builtins__": {}}, {})) else f'"{fv}"'
        except:
            return f'"{fv}"'
    expr = _re.sub(r'IF\(([^,]+),([^,]+),([^)]+)\)', _if, expr, flags=_re.I)

    # IRR(B0:F0) — Newton-Raphson
    def _irr(m):
        col1, row, col2 = m.group(1).upper(), int(m.group(2)), m.group(3).upper()
        cols = [chr(c) for c in range(ord(col1), ord(col2)+1)]
        flows = [float(cell_vals.get(f"{c}{row}", 0) or 0) for c in cols]
        rate = 0.1
        for _ in range(200):
            try:
                npv = sum(f / (1+rate)**i for i, f in enumerate(flows))
                dnpv = -sum(i*f / (1+rate)**(i+1) for i, f in enumerate(flows) if i > 0)
                if abs(dnpv) < 1e-12:
                    break
                rate = max(rate - npv/dnpv, -0.9999)
            except:
                return "#IRR"
        return str(round(rate, 6))
    expr = _re.sub(r'IRR\(([A-Z])(\d+):([A-Z])(\d+)\)', _irr, expr, flags=_re.I)

    # Cell references
    def _ref(m):
        v = cell_vals.get(m.group(0).upper(), 0)
        return str(float(v)) if isinstance(v, (int, float)) else "0"
    expr = _re.sub(r'[A-Z]\d+', _ref, expr)

    expr = expr.replace("^", "**")
    try:
        result = eval(expr, {"__builtins__": {}}, {})
        if isinstance(result, str):
            return result.strip('"\'')
        return round(float(result), 6)
    except:
        return "#ERR"


def _compute_grid(b_vals, cross=None, seed=None):
    """Evaluate all B-column cells; seed = extra {ref: val} to pre-populate."""
    cell_vals = dict(seed or {})
    bs = list(b_vals)
    # Literals first
    for i, b in enumerate(bs):
        s = str(b).strip()
        if s and s.lower() != "nan" and not s.startswith("="):
            try:
                cell_vals[f"B{i+1}"] = float(s.replace("$","").replace(",",""))
            except:
                cell_vals[f"B{i+1}"] = s
    # Multi-pass formulas
    for _ in range(8):
        for i, b in enumerate(bs):
            if str(b).strip().startswith("="):
                cell_vals[f"B{i+1}"] = _eval_formula(b, cell_vals, cross)
    return cell_vals


def _compute_multicol(col_data, cross=None, seed=None):
    """
    col_data: dict {col_letter: [val_list]} e.g. {"B": [...], "C": [...]}
    Returns merged cell_vals dict with B1, B2, C1, C2, etc.
    """
    cell_vals = dict(seed or {})
    # Literals
    for col, vals in col_data.items():
        for i, v in enumerate(vals):
            s = str(v).strip()
            if s and s.lower() != "nan" and not s.startswith("="):
                try:
                    cell_vals[f"{col.upper()}{i+1}"] = float(s.replace("$","").replace(",",""))
                except:
                    cell_vals[f"{col.upper()}{i+1}"] = s
    # Multi-pass formulas
    for _ in range(8):
        for col, vals in col_data.items():
            for i, v in enumerate(vals):
                if str(v).strip().startswith("="):
                    cell_vals[f"{col.upper()}{i+1}"] = _eval_formula(v, cell_vals, cross)
    return cell_vals


def _fmt(v):
    if isinstance(v, float):
        if v == int(v) and abs(v) < 1e10:
            return f"{int(v):,}"
        if abs(v) < 1:
            return f"{v:.4f}".rstrip('0').rstrip('.')
        return f"{v:,.2f}"
    return str(v) if (v is not None and str(v) not in ("", "nan")) else ""


def _get_all_cells():
    if "_all_cells" not in st.session_state:
        st.session_state._all_cells = {}
    return st.session_state._all_cells


_FN_TEMPLATES = {
    "—  insert function  —": None,
    "SUM(range)":        "=SUM(B1:B5)",
    "AVERAGE(range)":    "=AVERAGE(B1:B5)",
    "MEDIAN(range)":     "=MEDIAN(B1:B5)",
    "IF(cond,T,F)":      "=IF(B1>0,1,0)",
    "MAX(range)":        "=MAX(B1:B5)",
    "MIN(range)":        "=MIN(B1:B5)",
    "PERCENTILE(r,p)":   "=PERCENTILE(B1:B5,0.25)",
    "SUM(B+C range)":    "=SUM(B2:B10)",
}


def formula_grid_section(section_key, title, guidance_lines, n_rows=12,
                          cross=None, seed=None, section_name=None, reveal_lines=None):
    """
    Two-column guided grid: left = guidance, right = Excel-like formula grid.
    Formula bar: name-box (cell selector) + fx input + apply button.
    Function dropdown inserts template into active cell.
    Cell-ref chips insert reference into active cell formula.
    reveal_lines: optional parallel list; per-row "show answer" button reveals this text.
    """
    sk = f"fgs_{section_key}"
    if sk not in st.session_state:
        st.session_state[sk] = {"a": [""] * n_rows, "b": [""] * n_rows, "ver": 0, "active": 1}
    s = st.session_state[sk]
    while len(s["a"]) < n_rows: s["a"].append("")
    while len(s["b"]) < n_rows: s["b"].append("")
    if "active" not in s: s["active"] = 1

    cell_vals = _compute_grid(s["b"], cross=cross, seed=seed)
    if section_name:
        _get_all_cells()[section_name] = cell_vals

    st.markdown(f'<div class="sec">{title}</div>', unsafe_allow_html=True)

    hints_on = st.session_state.get("hints_on", True)
    active = s["active"]

    if hints_on:
        col_g, col_grid = st.columns([5, 8])
        with col_g:
            for idx, line in enumerate(guidance_lines):
                rn = idx + 1
                is_act = (rn == active)
                bg = "background:#EFF6FF;" if is_act else ""
                bl = "border-left:3px solid #2563EB;" if is_act else "border-left:3px solid #E5E7EB;"
                bc = "#1D4ED8" if is_act else "#94A3B8"
                badge = (f'<span style="font-family:monospace;font-weight:700;font-size:.59rem;'
                         f'color:{bc};min-width:26px;display:inline-block;flex-shrink:0;'
                         f'padding-top:1px;">B{rn}</span>')
                st.markdown(
                    f'<div class="guide-line" style="{bg}{bl}padding:4px 6px;'
                    f'display:flex;align-items:flex-start;gap:5px;border-bottom:1px solid #F3F4F6;">'
                    f'{badge}<span style="font-size:.74rem;">{line}</span></div>',
                    unsafe_allow_html=True)
                if reveal_lines and idx < len(reveal_lines):
                    rk = f"rev_{section_key}_r{rn}"
                    is_rev = st.session_state.get(rk, False)
                    if st.button("▼ hide answer" if is_rev else "▶ show answer",
                                 key=f"revbtn_{section_key}_r{rn}",
                                 use_container_width=False):
                        st.session_state[rk] = not is_rev
                        st.rerun()
                    if is_rev:
                        st.markdown(
                            f'<div style="background:#FEFCE8;border-left:3px solid #CA8A04;'
                            f'border-radius:0 3px 3px 0;padding:5px 8px;font-size:.73rem;'
                            f'color:#713F12;margin-bottom:3px;">{reveal_lines[idx]}</div>',
                            unsafe_allow_html=True)
    else:
        col_grid = st.container()

    with col_grid:
        ver = s["ver"]
        active = s["active"]   # 1-based row index
        cur_b = s["b"][active - 1] if active <= len(s["b"]) else ""

        # ── Formula bar label ───────────────────────────
        st.markdown('<div class="xl-fbar-label">▣ Formula Bar</div>', unsafe_allow_html=True)

        # ── Name-box | fx | formula input | ↵ | ↺ ──────
        c_cell, c_fxlbl, c_fbar, c_apply, c_clr = st.columns([1, 0.25, 5.5, 0.7, 0.7])

        with c_cell:
            cell_opts = [f"B{i+1}" for i in range(n_rows)]
            sel_cell = st.selectbox("cell", cell_opts, index=active - 1,
                                    key=f"xlcell_{section_key}_v{ver}",
                                    label_visibility="collapsed")
            new_active = int(sel_cell[1:])
            if new_active != active:
                s["active"] = new_active
                st.rerun()

        with c_fxlbl:
            st.markdown('<div style="padding-top:6px;text-align:center;font-family:monospace;'
                        'font-size:.78rem;color:#64748B;font-style:italic;">fx</div>',
                        unsafe_allow_html=True)

        with c_fbar:
            formula_input = st.text_input(
                "formula", value=cur_b,
                key=f"xlfbar_{section_key}_v{ver}_r{active}",
                placeholder="Enter value or =formula (e.g. =B1+B2)",
                label_visibility="collapsed")

        with c_apply:
            if st.button("↵", key=f"xlapply_{section_key}_v{ver}",
                         use_container_width=True, help="Apply formula to selected cell"):
                s["b"][active - 1] = formula_input
                s["ver"] += 1
                st.rerun()

        with c_clr:
            if st.button("↺", key=f"xlclr_{section_key}_v{ver}",
                         use_container_width=True, help="Clear and reset this sheet"):
                s["a"] = [""] * n_rows
                s["b"] = [""] * n_rows
                s["ver"] += 1
                s["active"] = 1
                st.rerun()

        # ── Function dropdown ────────────────────────────
        fn_col, _ = st.columns([4, 4])
        with fn_col:
            fn_list = list(_FN_TEMPLATES.keys())
            sel_fn = st.selectbox("ƒx function", fn_list,
                                  key=f"fnsel_{section_key}_v{ver}",
                                  label_visibility="collapsed",
                                  help="Select a function to insert into the active cell")
            tpl = _FN_TEMPLATES.get(sel_fn)
            if tpl is not None:
                s["b"][active - 1] = tpl
                s["ver"] += 1
                st.rerun()

        # ── Cell-ref chips (populated cells) ────────────
        nonempty = [(f"B{i+1}", s["b"][i]) for i in range(n_rows)
                    if s["b"][i] and str(s["b"][i]).strip() and i + 1 != active]
        if nonempty:
            st.markdown(
                f'<div style="font-size:.59rem;color:#94A3B8;margin:2px 0 1px;">Click ref to insert into active cell:</div>',
                unsafe_allow_html=True)
            ref_cols = st.columns(min(len(nonempty), 8))
            for i, (ref, val) in enumerate(nonempty[:8]):
                with ref_cols[i]:
                    label = ref
                    if st.button(label, key=f"xlref_{ref}_{section_key}_v{ver}",
                                 use_container_width=True,
                                 help=f"{ref} = {_fmt(cell_vals.get(ref, val))}"):
                        cur = s["b"][active - 1]
                        if not cur or not str(cur).strip().startswith("="):
                            s["b"][active - 1] = f"={ref}"
                        else:
                            s["b"][active - 1] = cur + ref
                        s["ver"] += 1
                        st.rerun()

        # ── Grid ────────────────────────────────────────
        rows = []
        for i in range(n_rows):
            b = s["b"][i]; a = s["a"][i]
            v = cell_vals.get(f"B{i+1}", "")
            result = _fmt(v) if (b and str(b).strip() and str(b).strip().lower() != "nan") else ""
            row_num = f"▶{i+1}" if (i + 1 == active) else str(i + 1)
            rows.append({" ": row_num, "A": a or "", "B": b or "", "→ Result": result})

        df = pd.DataFrame(rows)
        ek = f"de_{section_key}_v{ver}"
        edited = st.data_editor(df, key=ek, hide_index=True, use_container_width=True,
            num_rows="fixed",
            column_config={
                " ":          st.column_config.TextColumn(" ", disabled=True, width=32),
                "A":          st.column_config.TextColumn("A  ·  Label", width=148),
                "B":          st.column_config.TextColumn("B  ·  Value / Formula", width=218),
                "→ Result":   st.column_config.TextColumn("→ Result", disabled=True, width=90),
            })

        na = [("" if str(x) in ("nan","None","") else str(x)) for x in edited["A"]]
        nb = [("" if str(x) in ("nan","None","") else str(x)) for x in edited["B"]]
        if na != s["a"] or nb != s["b"]:
            s["a"] = na; s["b"] = nb; s["ver"] += 1
            st.rerun()


def formula_grid_multicol(section_key, title, guidance_lines, n_rows, col_labels,
                           cross=None, seed=None, section_name=None, reveal_lines=None):
    """
    Multi-column formula grid (e.g. Year 1–5 projections).
    col_labels: list of column header strings (one per value column, max 6).
    """
    cols = list("BCDEFG")[:len(col_labels)]
    sk = f"fgsm_{section_key}"
    if sk not in st.session_state:
        st.session_state[sk] = {
            "a": [""] * n_rows,
            "cols": {c: [""] * n_rows for c in cols},
            "ver": 0
        }
    s = st.session_state[sk]
    while len(s["a"]) < n_rows: s["a"].append("")
    for c in cols:
        if c not in s["cols"]: s["cols"][c] = [""] * n_rows
        while len(s["cols"][c]) < n_rows: s["cols"][c].append("")

    cell_vals = _compute_multicol(s["cols"], cross=cross, seed=seed)
    if section_name:
        _get_all_cells()[section_name] = cell_vals

    st.markdown(f'<div class="sec">{title}</div>', unsafe_allow_html=True)

    hints_on_mc = st.session_state.get("hints_on", True)

    if hints_on_mc:
        col_g, col_grid = st.columns([5, 8])
        with col_g:
            for idx, line in enumerate(guidance_lines):
                rn = idx + 1
                bg = "background:#EFF6FF;" if rn == 1 else ""
                bl = "border-left:3px solid #2563EB;" if rn == 1 else "border-left:3px solid #E5E7EB;"
                bc = "#1D4ED8" if rn == 1 else "#94A3B8"
                badge = (f'<span style="font-family:monospace;font-weight:700;font-size:.59rem;'
                         f'color:{bc};min-width:26px;display:inline-block;flex-shrink:0;'
                         f'padding-top:1px;">R{rn}</span>')
                st.markdown(
                    f'<div class="guide-line" style="{bg}{bl}padding:4px 6px;'
                    f'display:flex;align-items:flex-start;gap:5px;border-bottom:1px solid #F3F4F6;">'
                    f'{badge}<span style="font-size:.74rem;">{line}</span></div>',
                    unsafe_allow_html=True)
                if reveal_lines and idx < len(reveal_lines):
                    rk = f"rev_{section_key}_r{rn}"
                    is_rev = st.session_state.get(rk, False)
                    if st.button("▼ hide answer" if is_rev else "▶ show answer",
                                 key=f"revbtn_{section_key}_r{rn}",
                                 use_container_width=False):
                        st.session_state[rk] = not is_rev
                        st.rerun()
                    if is_rev:
                        st.markdown(
                            f'<div style="background:#FEFCE8;border-left:3px solid #CA8A04;'
                            f'border-radius:0 3px 3px 0;padding:5px 8px;font-size:.73rem;'
                            f'color:#713F12;margin-bottom:3px;">{reveal_lines[idx]}</div>',
                            unsafe_allow_html=True)
    else:
        col_grid = st.container()

    with col_grid:
        rows = []
        for i in range(n_rows):
            row = {"#": str(i+1), "Label (A)": s["a"][i] or ""}
            for c, lbl in zip(cols, col_labels):
                row[lbl] = s["cols"][c][i] or ""
            rows.append(row)
        df = pd.DataFrame(rows)

        col_cfg = {
            "#": st.column_config.TextColumn("#", disabled=True, width=32),
            "Label (A)": st.column_config.TextColumn("Label (A)", width=130),
        }
        for lbl in col_labels:
            col_cfg[lbl] = st.column_config.TextColumn(lbl, width=130)

        ek = f"dem_{section_key}_v{s['ver']}"
        edited = st.data_editor(df, key=ek, hide_index=True, use_container_width=True,
                                num_rows="fixed", column_config=col_cfg)

        # Show computed results below
        result_rows = []
        na = [("" if str(x) in ("nan","None","") else str(x)) for x in edited["Label (A)"]]
        for i in range(n_rows):
            label = na[i]
            if not label:
                continue
            row_data = {"Row label": label}
            for c, lbl in zip(cols, col_labels):
                v = cell_vals.get(f"{c}{i+1}", "")
                row_data[lbl] = _fmt(v) if v != "" else ""
            result_rows.append(row_data)

        if any(any(v for k, v in r.items() if k != "Row label") for r in result_rows):
            st.caption("↓ Computed results")
            st.dataframe(pd.DataFrame(result_rows), hide_index=True, use_container_width=True)

        # Detect changes
        changed = na != s["a"]
        new_cols = {}
        for c, lbl in zip(cols, col_labels):
            nc = [("" if str(x) in ("nan","None","") else str(x)) for x in edited[lbl]]
            new_cols[c] = nc
            if nc != s["cols"][c]:
                changed = True

        if changed:
            s["a"] = na
            for c in cols:
                s["cols"][c] = new_cols[c]
            s["ver"] += 1
            st.rerun()


# ── Module header ──────────────────────────────────────────────────────────────
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

def page_header(page):
    title, subtitle = _PAGE_META.get(page, ("", ""))
    co = current_company()
    inputs = _co_inputs(co).get(page)

    # ── Row 1: title (left) + company badge (centre-right) + button (far right) ──
    c_title, c_co, c_btn = st.columns([5, 4, 1])
    with c_title:
        st.markdown(
            f'<div style="padding:6px 0 4px;">'
            f'<div class="page-hdr-title">{title}</div>'
            f'<div class="page-hdr-sub">{subtitle}</div></div>',
            unsafe_allow_html=True)
    with c_co:
        st.markdown(
            f'<div style="padding:8px 0 4px;text-align:right;">'
            f'<div class="page-hdr-co">'
            f'<span class="page-hdr-co-name">{co["name"]}</span>'
            f'<span style="color:#CBD5E1;font-size:.7rem;">|</span>'
            f'<span class="page-hdr-co-sector">{co["sector"]}</span>'
            f'</div></div>',
            unsafe_allow_html=True)
    with c_btn:
        st.markdown('<div style="padding-top:9px;"></div>', unsafe_allow_html=True)
        if st.button("↻", key="reroll_btn", help="Next practice company",
                     use_container_width=True):
            st.session_state.company_idx = (st.session_state.company_idx + 1) % len(COMPANIES)
            st.rerun()

    # ── Row 2: given inputs strip ──
    if inputs is None:
        inputs_list = [("Rev", co["revenue"]), ("EBITDA", co["ebitda"]),
                       ("NI", co["ni"]), ("Price", co["price"]), ("Shares", co["shares"])]
    else:
        inputs_list = inputs
    chips_html = "".join(
        f'<span class="input-chip"><span class="input-chip-lbl">{lbl}</span>{val}</span>'
        for lbl, val in inputs_list
    )
    st.markdown(
        f'<div style="padding:6px 0 14px;border-bottom:1px solid #E5E7EB;margin-bottom:18px;">'
        f'<div class="page-hdr-inputs-lbl">Given Inputs — use these values, do not re-derive</div>'
        f'<div>{chips_html}</div></div>',
        unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
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
        '<span style="display:inline-block;width:9px;height:9px;background:#2563EB;margin-right:8px;vertical-align:middle;"></span>Blue — hardcoded input<br>'
        '<span style="display:inline-block;width:9px;height:9px;background:#374151;margin-right:8px;vertical-align:middle;"></span>Black — formula<br>'
        '<span style="display:inline-block;width:9px;height:9px;background:#16A34A;margin-right:8px;vertical-align:middle;"></span>Green — cross-sheet link<br>'
        '<span style="font-family:monospace;font-size:.7rem;background:#E5E7EB;color:#374151;padding:1px 5px;margin-right:6px;">Ctrl+`</span>toggle formula view'
        '</div>'
        f'<div style="margin-top:14px;padding-top:12px;border-top:1px solid #E5E7EB;">'
        f'<div style="font-size:.53rem;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:#9CA3AF;margin-bottom:6px;">Practice Company</div>'
        f'<div style="font-size:.77rem;color:#4B5563;line-height:1.85;">'
        f'<span style="color:#111827;font-weight:700;display:block;margin-bottom:3px;">{current_company()["name"]}</span>'
        f'{current_company()["sector"]}<br>'
        f'Rev {current_company()["revenue"]} · EBITDA {current_company()["ebitda"]}<br>'
        f'NI {current_company()["ni"]} · {current_company()["price"]} / {current_company()["shares"]} sh'
        '</div></div></div>',
        unsafe_allow_html=True)
    st.markdown('<div style="margin:12px 16px 0;padding-top:12px;border-top:1px solid #E5E7EB;">'
                '<div style="font-size:.53rem;font-weight:700;letter-spacing:.2em;text-transform:uppercase;'
                'color:#9CA3AF;margin-bottom:8px;">Build Options</div></div>',
                unsafe_allow_html=True)
    hints_on = st.session_state.get("hints_on", True)
    if st.button(("💡 Hints: ON  — click to hide" if hints_on else "💡 Hints: OFF — click to show"),
                 key="hint_toggle_sb", use_container_width=True):
        st.session_state.hints_on = not hints_on
        st.rerun()

page_header(page)

# ══════════════════════════════════════════════════════════════════════════════
# OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "overview":
    st.markdown("# Financial Modeling School")
    st.markdown("Build the seven core Excel models used in investment banking and private equity — from a completely blank spreadsheet. Each module teaches you how professional analysts actually construct these models: the logic, the structure, the conventions, and the formulas.")
    concept("How each module works",
        "<b>Learn tab</b> — Read deeply about how the model is constructed: why each section exists, "
        "how the pieces connect, what bankers actually use each line for, and the thinking behind each formula.<br><br>"
        "<b>Build tab</b> — An interactive spreadsheet with guided sections. Type row labels in col A and "
        "values or formulas in col B. Formulas starting with <b>=</b> are evaluated live — just like Excel. "
        "Guidance on the left of each section directs your thinking without giving answers away.")
    pro_tip("The only way to learn financial modeling is to build models. Reading is essential but not enough — "
            "you need your hands on the keyboard, typing formulas, making mistakes, and fixing them. "
            "Every module here is a build exercise, not a reading exercise.")
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

**COGS vs. SG&A — a critical distinction.** COGS (Cost of Goods Sold) are variable costs that scale with revenue: raw materials, direct labor, manufacturing overhead. SG&A (Selling, General & Administrative) are largely fixed: office rent, executive salaries, software subscriptions. COGS is modeled as a % of revenue; SG&A is often modeled as a fixed or slowly growing dollar amount.

**D&A — non-cash but real.** Depreciation & Amortization represents the accounting recognition of an asset losing value over time. It reduces reported profit (and thus taxes) but does NOT reduce cash. This is why we add it back in the Cash Flow Statement.
""")
        st.markdown("## Building the Balance Sheet")
        st.markdown("""
The Balance Sheet rests on one identity that must always hold: **Assets = Liabilities + Equity.** If it doesn't balance, you have an error somewhere — and no banker will use a model that doesn't balance.

**Assets** are organized by liquidity — current assets (cash, receivables, inventory) come first because they convert within a year. Then long-term assets (PP&E, intangibles), which represent the company's productive capacity.

**The balance check cell.** Every professional model has a dedicated check cell: =Total Assets − Total L&E. If this cell is not zero, something is broken. Build it immediately and watch it.

**Retained Earnings is the link from the Income Statement.** Each period's Net Income increases Retained Earnings (less any dividends paid). This is one of the key connections between the IS and BS.
""")
        st.markdown("## Building the Cash Flow Statement and Linking the Model")
        st.markdown("""
The CFS is structured in three sections: Operating Activities, Investing Activities, and Financing Activities.

**Operating Activities** starts with Net Income from the IS (cross-sheet link: =IS!B12). Then it makes two types of adjustments:
1. *Add back non-cash charges:* D&A is subtracted on the IS to reduce taxable income, but no cash left the company. So we add it back here.
2. *Adjust for working capital changes:* If Accounts Receivable increased, you recognized revenue but haven't collected the cash yet — that's a negative adjustment. If Accounts Payable increased, you're holding onto cash longer — that's positive.

**Investing Activities** is primarily Capex — spending on PP&E, always entered as a negative number.

**Financing Activities** captures dividends paid, debt raised/repaid, and share buybacks.

**Sheet referencing syntax.** To link between tabs, type =IS!B12 in another tab. This syntax is the backbone of every three-statement model.
""")
        warning("The most common beginner mistake: hard-coding numbers on the CFS instead of linking them from the IS. If you type 52.5 for Net Income instead of =IS!B12, the model breaks as soon as you change any revenue assumption.")
        pro_tip("Build the IS first, then BS, then CFS. Use Ctrl+` to toggle formula view in Excel and verify every non-blue cell is a formula — no exceptions.")

    with build_tab:
        st.markdown("## Build the Three Statement Model")
        st.markdown("Three sections — one per statement. Type labels in col A, values or formulas in col B. "
                    "Formulas starting with **=** evaluate live. The guidance panel on the left of each section gives you hints without giving away the answer.")

        # ── IS ──
        formula_grid_section("3s_is", "Income Statement (IS tab)", [
            "What is the very first number on any income statement — the amount a company earns from its core business before any costs are subtracted? Find it in the given inputs.",
            "What is the direct cost of producing what the company sold? Unlike overhead, this scales with sales volume. Find it in the inputs.",
            "After subtracting production costs from the top line, what remains? This is your first profitability subtotal — the spread between what you charge and what it costs to make.",
            "What are the fixed operating costs that run the business day-to-day — rent, executive salaries, marketing — separate from production costs? Find this in the inputs.",
            "After subtracting those fixed overhead costs from your first subtotal, what remains? This is the operating metric private equity firms and bankers focus on most — before non-cash charges, financing, and taxes.",
            "There is a non-cash charge that reduces taxable income on paper but involves no actual cash outflow — it represents assets 'aging' over time. Enter it from inputs. Note this row number; the cash flow section will reference it.",
            "After deducting that non-cash aging charge from the previous subtotal, what is the true operating profit? This is the last subtotal before financing costs and taxes enter the picture.",
            "The company borrowed money. What is the annual cost of carrying that debt? This is a financing decision, not an operating one — and the sign matters.",
            "After paying interest to lenders, what profit remains before the government's share is deducted? This is your pre-tax subtotal.",
            "Enter this percentage as a decimal and store it in its own dedicated cell. Why is it dangerous to embed a rate directly inside a formula instead of referencing a standalone cell?",
            "Apply the rate from the row above to the pre-tax profit. Are you referencing the rate cell, or did you accidentally type the number again?",
            "After taxes, what remains? This is the final bottom line. Note its row number — the cash flow statement will link here using a cross-sheet reference.",
            "Express the bottom line as a percentage of the top line. Is your result in the single-digit-to-low-teens range? If it is far off, check the formulas in the rows above.",
        ], n_rows=13, section_name="IS", reveal_lines=[
            "<b>Label:</b> Revenue &nbsp;|&nbsp; <b>Enter:</b> hard-code the revenue figure from inputs",
            "<b>Label:</b> COGS &nbsp;|&nbsp; <b>Enter:</b> hard-code cost of goods sold from inputs",
            "<b>Label:</b> Gross Profit &nbsp;|&nbsp; <b>Formula:</b> =B1−B2 &nbsp;(Revenue minus COGS)",
            "<b>Label:</b> SG&amp;A &nbsp;|&nbsp; <b>Enter:</b> hard-code selling, general &amp; admin costs from inputs",
            "<b>Label:</b> EBITDA &nbsp;|&nbsp; <b>Formula:</b> =B3−B4 &nbsp;(Gross Profit minus SG&amp;A)",
            "<b>Label:</b> D&amp;A &nbsp;|&nbsp; <b>Enter:</b> hard-code depreciation &amp; amortization from inputs",
            "<b>Label:</b> EBIT &nbsp;|&nbsp; <b>Formula:</b> =B5−B6 &nbsp;(EBITDA minus D&amp;A)",
            "<b>Label:</b> Interest Expense &nbsp;|&nbsp; <b>Enter:</b> hard-code interest expense from inputs",
            "<b>Label:</b> EBT &nbsp;|&nbsp; <b>Formula:</b> =B7−B8 &nbsp;(EBIT minus Interest Expense)",
            "<b>Label:</b> Tax Rate &nbsp;|&nbsp; <b>Enter:</b> hard-code as decimal (e.g. 0.30)",
            "<b>Label:</b> Tax Expense &nbsp;|&nbsp; <b>Formula:</b> =B9*B10 &nbsp;(EBT × Tax Rate)",
            "<b>Label:</b> Net Income &nbsp;|&nbsp; <b>Formula:</b> =B9−B11 &nbsp;(EBT minus Tax Expense)",
            "<b>Label:</b> NI Margin &nbsp;|&nbsp; <b>Formula:</b> =B12/B1 &nbsp;(Net Income ÷ Revenue)",
        ])

        # ── BS ──
        formula_grid_section("3s_bs", "Balance Sheet (BS tab)", [
            "The most liquid asset goes first — it is immediately available to spend. Enter the opening balance from the given inputs.",
            "The company recognized revenue but customers have not paid yet — the cash is still owed to the company. What do you call money customers owe? Enter from inputs. Why is this listed as an asset despite no cash arriving?",
            "Goods were produced but have not been sold yet. What do you call unsold goods sitting in storage? Enter from inputs. How does this eventually convert to cash?",
            "You now have three short-term asset rows. What is the umbrella term for assets that convert to cash within a year? Sum the three rows above.",
            "The physical machinery and buildings that run the business, reduced by the depreciation charged against them over time. Enter from inputs.",
            "Non-physical, long-lived assets: patents, trademarks, brand names, goodwill from acquisitions. Enter from inputs.",
            "Sum every asset the company owns — both the short-term bucket and the two long-term lines. Note this row number: it must tie exactly to the total of the liabilities and equity section below.",
            "— Leave blank as a visual separator between assets and liabilities.",
            "The company received goods from suppliers but has not paid for them yet. What is the name for money owed to suppliers? Enter from inputs. Why is delaying payment beneficial for cash?",
            "Debt that must be repaid within the next 12 months. Enter from inputs.",
            "Debt that does not mature for more than a year. Enter from inputs.",
            "Add everything the company owes — to suppliers, to short-term lenders, and to long-term lenders. Which rows above make up this total?",
            "— Leave blank as a visual separator.",
            "Capital raised by issuing shares to investors. This goes in the equity section — the residual claim shareholders hold after all liabilities are settled. Enter from inputs.",
            "Profits earned over the company's life that were kept rather than paid as dividends. Each period's bottom-line earnings flow into this line. Enter from inputs.",
            "Sum the two equity components above. This is the shareholders' total stake in the business.",
            "Combine your two subtotals — everything owed and everything owned by shareholders. This must equal the total assets figure calculated above. Does it?",
            "— Leave blank.",
            "Write a formula that produces zero only when the model is correct. Subtract one major subtotal from the other — if the result is not zero, there is an error somewhere that must be found before this model can be used.",
        ], n_rows=19, section_name="BS", reveal_lines=[
            "<b>Label:</b> Cash &nbsp;|&nbsp; <b>Enter:</b> hard-code from inputs",
            "<b>Label:</b> Accounts Receivable &nbsp;|&nbsp; <b>Enter:</b> hard-code from inputs",
            "<b>Label:</b> Inventory &nbsp;|&nbsp; <b>Enter:</b> hard-code from inputs",
            "<b>Label:</b> Current Assets &nbsp;|&nbsp; <b>Formula:</b> =B1+B2+B3 &nbsp;(Cash + AR + Inventory)",
            "<b>Label:</b> PP&amp;E, net &nbsp;|&nbsp; <b>Enter:</b> hard-code from inputs",
            "<b>Label:</b> Intangibles &nbsp;|&nbsp; <b>Enter:</b> hard-code from inputs",
            "<b>Label:</b> Total Assets &nbsp;|&nbsp; <b>Formula:</b> =B4+B5+B6 &nbsp;(Current Assets + PP&amp;E + Intangibles)",
            "<i>Blank separator row — leave A and B empty</i>",
            "<b>Label:</b> Accounts Payable &nbsp;|&nbsp; <b>Enter:</b> hard-code from inputs",
            "<b>Label:</b> Short-term Debt &nbsp;|&nbsp; <b>Enter:</b> hard-code from inputs",
            "<b>Label:</b> Long-term Debt &nbsp;|&nbsp; <b>Enter:</b> hard-code from inputs",
            "<b>Label:</b> Total Liabilities &nbsp;|&nbsp; <b>Formula:</b> =B9+B10+B11",
            "<i>Blank separator row — leave A and B empty</i>",
            "<b>Label:</b> Common Stock &nbsp;|&nbsp; <b>Enter:</b> hard-code from inputs",
            "<b>Label:</b> Retained Earnings &nbsp;|&nbsp; <b>Enter:</b> hard-code from inputs",
            "<b>Label:</b> Total Equity &nbsp;|&nbsp; <b>Formula:</b> =B14+B15",
            "<b>Label:</b> Total L&amp;E &nbsp;|&nbsp; <b>Formula:</b> =B12+B16 &nbsp;(Total Liabilities + Total Equity)",
            "<i>Blank separator row — leave A and B empty</i>",
            "<b>Label:</b> Balance Check &nbsp;|&nbsp; <b>Formula:</b> =B7−B17 &nbsp;(must equal 0)",
        ])

        # ── CFS ── (reads from IS and BS via cross-section refs)
        all_cells = _get_all_cells()
        cfs_cross = {k: v for k, v in all_cells.items() if k in ("IS", "BS")}
        formula_grid_section("3s_cfs", "Cash Flow Statement (CFS tab)", [
            "The cash flow statement always starts with a figure pulled from a different statement. Which row on the income statement holds the final bottom line? Use a cross-sheet reference rather than typing the number.",
            "One of the income statement charges reduced taxable income without any cash actually leaving the company. Since no cash went out, what must you do to reconcile income to cash? What sign does that adjustment carry here?",
            "If money owed by customers grows from one period to the next, does that represent cash collected or cash still outstanding? Think: revenue recognized but not yet received — does that help or hurt your cash balance?",
            "If unsold goods build up in the warehouse, cash was spent producing them. Does building up that stock help or hurt your cash position? What sign does growth in that asset carry on the cash flow statement?",
            "If the company is paying suppliers more slowly — holding onto cash longer — is that favorable or unfavorable for cash? Which direction does growing supplier balances move this line?",
            "You have five operating rows above this one. What function totals a range of cells? This subtotal is the single most important health metric in the model — a negative number here is a serious warning sign.",
            "— Leave blank as a visual separator.",
            "Buying equipment and property always flows cash out — it is never income. What is the specific term for this type of capital spending? What sign does an outflow carry?",
            "For this model, capital spending is the only investing activity. Rather than repeating the number, how do you reference the row directly above this one?",
            "— Leave blank as a visual separator.",
            "Cash returned to shareholders always flows out. What sign does it carry in the model?",
            "For this model, shareholder distributions are the only financing activity. Reference the row above rather than hardcoding the number.",
            "— Leave blank.",
            "Start from the opening cash balance and add the three section subtotals. Which three rows above combine with the beginning cash figure? And where does the ending balance appear on the balance sheet?",
        ], n_rows=14, cross=cfs_cross, section_name="CFS", reveal_lines=[
            "<b>Label:</b> Net Income &nbsp;|&nbsp; <b>Formula:</b> =IS!B12 &nbsp;(cross-sheet link from IS)",
            "<b>Label:</b> Add: D&amp;A &nbsp;|&nbsp; <b>Formula:</b> =IS!B6 &nbsp;(add back; positive sign — no cash left)",
            "<b>Label:</b> Δ Accounts Receivable &nbsp;|&nbsp; <b>Enter:</b> change in AR; growing AR is negative (cash not collected)",
            "<b>Label:</b> Δ Inventory &nbsp;|&nbsp; <b>Enter:</b> change in Inventory; growing inventory is negative (cash spent)",
            "<b>Label:</b> Δ Accounts Payable &nbsp;|&nbsp; <b>Enter:</b> change in AP; growing AP is positive (holding onto cash longer)",
            "<b>Label:</b> Cash from Operations &nbsp;|&nbsp; <b>Formula:</b> =SUM(B1:B5)",
            "<i>Blank separator — leave A and B empty</i>",
            "<b>Label:</b> Capex &nbsp;|&nbsp; <b>Enter:</b> from inputs as a <i>negative</i> number (cash outflow)",
            "<b>Label:</b> Cash from Investing &nbsp;|&nbsp; <b>Formula:</b> =B8 &nbsp;(reference Capex row)",
            "<i>Blank separator — leave A and B empty</i>",
            "<b>Label:</b> Dividends Paid &nbsp;|&nbsp; <b>Enter:</b> from inputs as a <i>negative</i> number",
            "<b>Label:</b> Cash from Financing &nbsp;|&nbsp; <b>Formula:</b> =B11 &nbsp;(reference Dividends row)",
            "<i>Blank separator — leave A and B empty</i>",
            "<b>Label:</b> Ending Cash &nbsp;|&nbsp; <b>Formula:</b> =BS!B1+B6+B9+B12 &nbsp;(Beginning Cash + Ops + Investing + Financing)",
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

DCFs are never presented as a single number. Every assumption — growth rate, margins, WACC, terminal growth — is uncertain. Bankers always pair a DCF with a sensitivity table showing how the implied share price changes as assumptions vary.
""")
        st.markdown("## Constructing the Projection Period")
        st.markdown("""
The projection period is typically 5 years. Revenue projections are built from a growth rate assumption. In Excel, you anchor the base-year revenue with an absolute reference ($B$2) and apply compound growth: =$B$2*(1+$B$3)^1 for Year 1, ^2 for Year 2, etc. The dollar signs are essential — they prevent the reference from shifting when you drag the formula right.

**Free Cash Flow** is the number being discounted: FCF = EBITDA × (1 − tax rate) − Capex. This shorthand approximation is common in simplified DCFs.

**Discounting each year's FCF** uses: PV = FCF ÷ (1 + WACC)^n, where n is the year number.
""")
        st.markdown("## Building WACC From First Principles")
        st.markdown("""
**Cost of Equity (CAPM):** Ke = Risk-Free Rate + Beta × Equity Risk Premium. For NovaTech: Ke = 4.5% + 1.1 × 5.5% = 10.55%.

**After-tax Cost of Debt:** Kd × (1 − tax rate). For NovaTech: 6% × (1 − 30%) = 4.2% after-tax.

**Weighting:** WACC = (E/V) × Ke + (D/V) × Kd × (1−T), where V = E + D. Use *market value* weights. For NovaTech: market cap = $900M, debt = $125M, V = $1,025M. WACC ≈ 9.35%.
""")
        st.markdown("## Terminal Value and the Enterprise Value Bridge")
        st.markdown("""
**Gordon Growth Model** (most common): TV = FCF(Y5) × (1 + g) / (WACC − g). The formula assumes FCF grows at g forever. g should be close to long-run nominal GDP growth (2–3%) and MUST be less than WACC or the model produces infinite value.

The TV must then be discounted to present value: PV of TV = TV / (1 + WACC)^5. TV typically represents 60–80% of total DCF value — this is why WACC and g are so sensitive.

**Bridge to share price:**
1. Enterprise Value = Sum of PV(FCFs) + PV(Terminal Value)
2. Equity Value = Enterprise Value − Net Debt
3. Implied Share Price = Equity Value ÷ Shares Outstanding
""")
        warning("Never present a single DCF price as the answer. Always build and present a sensitivity table with WACC on one axis and terminal growth rate on the other.")
        pro_tip("When building the projection block, put Year 1 in col D and Year 5 in col H. Lock assumption references with $ (=$B$3) before dragging — this is the most common formula error in DCF models.")

    with build_tab:
        st.markdown("## Build the DCF Model")
        st.markdown("Three sections: assumptions (col B), 5-year projections (cols B–F per year), then terminal value and the bridge to share price.")

        # ── Assumptions ──
        formula_grid_section("dcf_assum", "Assumption Inputs", [
            "The anchor for every projection formula below. Enter from inputs and note the row number — you will lock this reference with $ signs so it does not drift when formulas are dragged across columns.",
            "Enter as a decimal. This is the annual compound rate applied to the base figure each year. Note the row — projections will reference it with a locked $ reference.",
            "What fraction of each year's revenue becomes operating profit? Enter as a decimal. This margin multiplies against each projected year's revenue.",
            "This non-cash charge scales with revenue in this simplified model. Enter as a decimal.",
            "Capital expenditure as a fraction of revenue each year. Enter as a decimal. This reduces the free cash flow available for distribution.",
            "The government's claim on pre-tax income. Enter as a decimal. Applied inside the free cash flow formula. Note this row.",
            "The rate at which every future cash flow is discounted back to today's value. Enter as a decimal. Why does a higher rate here produce a lower implied valuation?",
            "Long-run growth assumed after the projection period ends. Enter as a decimal. There is a hard mathematical constraint on how large this can be relative to another assumption — can you figure out what it is and why?",
            "The company's total debt minus its cash on hand. Enter from inputs. This bridges from total business value down to what shareholders actually receive.",
            "The last divisor in the model — it converts total equity value into a per-share price. Enter in millions.",
        ], n_rows=10, section_name="DCF_ASSUM", reveal_lines=[
            "<b>Label:</b> Base Revenue &nbsp;|&nbsp; <b>Enter:</b> hard-code revenue from inputs",
            "<b>Label:</b> Revenue Growth Rate &nbsp;|&nbsp; <b>Enter:</b> hard-code as decimal (e.g. 0.08)",
            "<b>Label:</b> EBITDA Margin &nbsp;|&nbsp; <b>Enter:</b> hard-code as decimal (e.g. 0.22)",
            "<b>Label:</b> D&amp;A % of Revenue &nbsp;|&nbsp; <b>Enter:</b> hard-code as decimal",
            "<b>Label:</b> Capex % of Revenue &nbsp;|&nbsp; <b>Enter:</b> hard-code as decimal",
            "<b>Label:</b> Tax Rate &nbsp;|&nbsp; <b>Enter:</b> hard-code as decimal (e.g. 0.30)",
            "<b>Label:</b> WACC &nbsp;|&nbsp; <b>Enter:</b> hard-code as decimal (e.g. 0.0935)",
            "<b>Label:</b> Terminal Growth Rate &nbsp;|&nbsp; <b>Enter:</b> hard-code as decimal; <i>must be less than WACC</i>",
            "<b>Label:</b> Net Debt &nbsp;|&nbsp; <b>Enter:</b> hard-code from inputs",
            "<b>Label:</b> Shares Outstanding &nbsp;|&nbsp; <b>Enter:</b> hard-code in millions from inputs",
        ])

        # ── Projections ──
        dcf_assum_cells = _get_all_cells().get("DCF_ASSUM", {})
        formula_grid_multicol("dcf_proj", "Five-Year Projections (Years 1 – 5)", [
            "What grows at a compound rate from the base year? Each year's figure applies the growth assumption once more than the prior year. Think: base × (1 + rate) raised to which power for Year 1, for Year 2, and so on?",
            "Each year's operating profit is a fixed percentage of that year's revenue. Which assumption row holds that margin? How do you multiply this year's revenue figure by it?",
            "Simplified free cash flow: operating profit after taxes, minus capital spending. Which assumption rows hold the tax rate and capex percentage? How do they combine with this year's operating profit?",
            "This factor converts a future dollar to today's value using the discount rate. How does the exponent change from Year 1 to Year 5? Think: one divided by (1 + rate) raised to what power for each year?",
            "Bring the free cash flow to present value using two numbers from the same column. Which row holds the cash flow, and which row holds the discount factor? How do they combine?",
        ], n_rows=5, col_labels=["Yr 1 (B)","Yr 2 (C)","Yr 3 (D)","Yr 4 (E)","Yr 5 (F)"],
        seed=dcf_assum_cells, section_name="DCF_PROJ", reveal_lines=[
            "<b>Label:</b> Revenue &nbsp;|&nbsp; <b>Formula (Yr n):</b> =$B$1*(1+$B$2)^n &nbsp;(lock base &amp; rate with $)",
            "<b>Label:</b> EBITDA &nbsp;|&nbsp; <b>Formula:</b> =Revenue_this_year * $B$3",
            "<b>Label:</b> Free Cash Flow &nbsp;|&nbsp; <b>Formula:</b> =EBITDA*(1−$B$6) − (Revenue*$B$5)",
            "<b>Label:</b> Discount Factor &nbsp;|&nbsp; <b>Formula (Yr n):</b> =1/(1+$B$7)^n",
            "<b>Label:</b> PV of FCF &nbsp;|&nbsp; <b>Formula:</b> =FCF_this_col * DiscountFactor_this_col",
        ])

        # ── TV & Bridge ──
        dcf_proj_cells = _get_all_cells().get("DCF_PROJ", {})
        dcf_seed = {**dcf_assum_cells, **dcf_proj_cells}
        formula_grid_section("dcf_bridge", "Terminal Value & Share Price Bridge", [
            "Pull the final year's free cash flow from your projections. Which row and which column (Year 5) holds this figure?",
            "This valuation component assumes the final year's cash flow grows at the long-run rate forever. The formula has three ingredients. Which two rates create the denominator, and why must one be strictly larger than the other?",
            "The terminal value occurs at the end of Year 5, so it must be brought back to today's dollars. How many years do you discount it for, and which formula accomplishes that?",
            "You have five years of discounted cash flows in the projections section. What function sums a range of cells?",
            "Two components together make up the total business value from this model. What are they, and how do they combine?",
            "Enter or reference from your assumptions. This is what goes to lenders before shareholders receive anything — why does that make it a subtraction from business value?",
            "After debtholders are paid in full, what remains belongs to shareholders. Which two rows above combine to give you this?",
            "The model's final output: value per share. Divide the equity value by what? Compare your answer to the current stock price in the given inputs — is it above or below?",
        ], n_rows=8, seed=dcf_seed, reveal_lines=[
            "<b>Label:</b> Year 5 FCF &nbsp;|&nbsp; <b>Enter:</b> reference FCF row, Year 5 column from projections",
            "<b>Label:</b> Terminal Value &nbsp;|&nbsp; <b>Formula:</b> =B1*(1+g)/(WACC−g) &nbsp;where g = terminal growth rate",
            "<b>Label:</b> PV of Terminal Value &nbsp;|&nbsp; <b>Formula:</b> =B2/(1+WACC)^5",
            "<b>Label:</b> Sum of PV(FCFs) &nbsp;|&nbsp; <b>Formula:</b> =SUM of the 5 PV of FCF cells from projections",
            "<b>Label:</b> Enterprise Value &nbsp;|&nbsp; <b>Formula:</b> =B3+B4 &nbsp;(PV of TV + Sum of PV FCFs)",
            "<b>Label:</b> Net Debt &nbsp;|&nbsp; <b>Enter:</b> hard-code or reference from assumptions",
            "<b>Label:</b> Equity Value &nbsp;|&nbsp; <b>Formula:</b> =B5−B6",
            "<b>Label:</b> Implied Share Price &nbsp;|&nbsp; <b>Formula:</b> =B7/Shares_Outstanding",
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
""")
        st.markdown("## Understanding the Multiples")
        st.markdown("""
**EV/EBITDA** is the most commonly used multiple in investment banking. Enterprise Value (market cap + net debt) divided by EBITDA gives you a measure of how many years of operating earnings you're paying for the whole business. It's capital-structure neutral — both EV and EBITDA are unaffected by whether a company uses debt or equity.

**EV/Revenue** is used when EBITDA is negative or unreliable — early-stage companies, high-growth SaaS, or businesses with deliberately low margins.

**P/E (Price-to-Earnings)** uses market cap (equity value, after debt) divided by net income (also after interest). Two identical businesses with different debt levels will have very different P/Es. Bankers prefer EV-based multiples for cross-company comparisons.

**Why median rather than mean?** One outlier peer trading at 25× in a group that otherwise trades at 9–10× would distort the mean dramatically. The median is robust to outliers.
""")
        st.markdown("## Building the Comps Table in Excel")
        st.markdown("""
One row per comparable company, with metric columns on the right. Col A = company name. Then input columns for raw data (EV, EBITDA, Revenue, Net Income, Market Cap). Then formula columns for the derived multiples.

The summary block uses Excel statistical functions: =MEDIAN(range) and =PERCENTILE(range, 0.25). Apply median EV/EBITDA × NovaTech EBITDA to get implied EV → subtract net debt → divide by shares → implied share price.
""")
        warning("Comps are only as good as your peer selection. Including a company with 40% revenue growth alongside companies growing at 5% will distort the multiple.")

    with build_tab:
        st.markdown("## Build the Comps Table")
        st.markdown("Peer data (all $M): **TechAlpha** EV 1,104 · EBITDA 120 · Rev 480 · NI 65 · MktCap 1,202 | "
                    "**DataCore** EV 810 · EBITDA 100 · Rev 420 · NI 50 · MktCap 810 | "
                    "**CloudSystems** EV 1,260 · EBITDA 120 · Rev 400 · NI 59 · MktCap 1,239 | "
                    "**InfoPro** EV 858 · EBITDA 110 · Rev 510 · NI 54 · MktCap 853")

        formula_grid_section("comps_peers", "Peer Table — Raw Data & Multiples", [
            "Before entering any data, think about what this table needs to show. You are tracking company names, key financial metrics, and derived ratios. What ratios do bankers use most commonly to compare total business value to earnings power and to revenue? Think about what the numerator and denominator of each ratio represent.",
            "Enter all raw data for the first peer. Multiples are always derived — never typed. If you know a company's total business value and what it earns before interest, taxes, D&A — how do you turn those two numbers into a ratio?",
            "Same structure as the row above. Once the ratio formulas in the first data row are correct, what is the most efficient way to apply the same logic to this peer without rewriting the formulas?",
            "Third peer, same structure. Notice that some companies trade at higher ratios. What fundamental business characteristics — margins, growth, competitive position — might explain a premium?",
            "Last peer. You now have four data points for each metric. What patterns do you notice in how the ratios compare across the group?",
            "— Leave blank as a visual separator before the summary statistics.",
            "The low end of the peer distribution. There is an Excel function that returns a value at a specific rank in a range. What argument do you pass to get the 25th percentile, expressed as a decimal?",
            "The midpoint of the peer set. Why is this statistic preferred over the average when summarizing valuation ratios? What problem does it avoid?",
            "The high end of the range. Together with the low end and midpoint, these three rows give a valuation range — not a single point. Why is a range more useful to a banker than a single number?",
            "Apply the midpoint logic to the ratio that relates market price to per-share earnings. This gives a separate equity-value check using the net income line.",
        ], n_rows=10, section_name="COMPS_PEERS", reveal_lines=[
            "<b>Header row</b> — labels: Company | EV | EBITDA | Revenue | Net Income | Mkt Cap | EV/EBITDA | EV/Revenue | P/E",
            "<b>Label:</b> TechAlpha &nbsp;|&nbsp; raw data from above; <b>EV/EBITDA</b> =EV÷EBITDA; <b>EV/Rev</b> =EV÷Revenue; <b>P/E</b> =MktCap÷NI",
            "<b>Label:</b> DataCore &nbsp;|&nbsp; same structure — copy ratio formulas from the row above",
            "<b>Label:</b> CloudSystems &nbsp;|&nbsp; same structure",
            "<b>Label:</b> InfoPro &nbsp;|&nbsp; same structure",
            "<i>Blank separator — leave A and B empty</i>",
            "<b>Label:</b> 25th Percentile &nbsp;|&nbsp; <b>Formula:</b> =PERCENTILE(EV/EBITDA range, 0.25) &nbsp;repeat for each multiple",
            "<b>Label:</b> Median &nbsp;|&nbsp; <b>Formula:</b> =MEDIAN(EV/EBITDA range) &nbsp;repeat for each multiple",
            "<b>Label:</b> 75th Percentile &nbsp;|&nbsp; <b>Formula:</b> =PERCENTILE(EV/EBITDA range, 0.75)",
            "<b>Label:</b> Median P/E &nbsp;|&nbsp; <b>Formula:</b> =MEDIAN(P/E range)",
        ])

        formula_grid_section("comps_val", "NovaTech Implied Valuation", [
            "Enter from the given inputs — this is the financial metric you are applying the peer ratio to.",
            "Do not retype this — reference it from the peer table you just built. Which row holds the midpoint of the peer ratios?",
            "You know what the peer set pays per dollar of this earnings metric, and you know NovaTech's figure. How do you work backward to an implied total business value?",
            "Enter from the given inputs. Why does subtracting this convert a total business value into what shareholders actually receive?",
            "After paying off lenders, what remains belongs to shareholders. Which two rows above combine to give you this?",
            "Divide the equity value into a per-share amount. By what divisor? Is NovaTech cheap or expensive relative to peers based on this implied price?",
        ], n_rows=6, seed=_get_all_cells().get("COMPS_PEERS", {}), reveal_lines=[
            "<b>Label:</b> NovaTech EBITDA &nbsp;|&nbsp; <b>Enter:</b> hard-code from inputs",
            "<b>Label:</b> Median EV/EBITDA &nbsp;|&nbsp; <b>Enter:</b> reference the Median row from the peer table above",
            "<b>Label:</b> Implied EV &nbsp;|&nbsp; <b>Formula:</b> =B1*B2 &nbsp;(EBITDA × Median Multiple)",
            "<b>Label:</b> Net Debt &nbsp;|&nbsp; <b>Enter:</b> hard-code from inputs",
            "<b>Label:</b> Equity Value &nbsp;|&nbsp; <b>Formula:</b> =B3−B4",
            "<b>Label:</b> Implied Share Price &nbsp;|&nbsp; <b>Formula:</b> =B5÷Shares Outstanding",
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

When an acquirer buys a company, they're buying control of the entire enterprise — the ability to install management, cut costs, redirect capital. Shareholders won't sell without receiving a premium above the current stock price. Typical control premiums run 20–40%.
""")
        st.markdown("## Construction Differences from Comps")
        st.markdown("""
**Unaffected stock price.** This is the target's stock price 30 days before any deal rumors. You use it because by announcement, the stock has already jumped. Using the post-announcement price would understate the control premium.

**Control premium column.** Calculated as: (Deal EV − Unaffected Market Cap) ÷ Unaffected Market Cap. Apply the average premium to NovaTech's current price to estimate a minimum acquisition price.

**LTM EBITDA at time of deal, not current.** When looking at the multiple an acquirer paid, use the EBITDA that existed at deal time — not today's figure.
""")
        warning("Precedents go stale quickly. A 2015 deal multiple reflects 2015 market conditions. Weight recent transactions more heavily and exclude deals from unusually hot or distressed markets.")

    with build_tab:
        st.markdown("## Build the Precedent Transactions Table")
        st.markdown("Deal data (all $M): **AcquireCo/TechAlpha '22** Deal EV 1,320 · LTM EBITDA 120 · Pre-deal MktCap 975 | "
                    "**MegaCorp/DataCore '21** Deal EV 980 · LTM EBITDA 100 · Pre-deal MktCap 809 | "
                    "**GlobalTech/InfoPro '23** Deal EV 1,045 · LTM EBITDA 110 · Pre-deal MktCap 856")

        formula_grid_section("prec_deals", "Deal Table — Raw Data & Derived Metrics", [
            "Before entering any data, think about what columns this table needs. You are tracking completed acquisitions, not just stock prices. What extra information does a deal table capture that a trading comps table does not? Think about what a buyer paid versus what the target's shares were trading at before the deal.",
            "Enter the raw deal data for the first transaction. The earnings multiple is always derived. The second derived column captures how much above the pre-deal market value the buyer paid — how do you express that difference as a percentage?",
            "Same structure. Once the formulas in the row above are correct, how do you efficiently apply the same logic to this deal?",
            "Third deal. Compare the derived multiples to those in your trading comps. Do you observe a consistent pattern? What economic concept explains the difference?",
            "— Leave blank as a separator before summary statistics.",
            "Find the midpoint of the three deal multiples. Why should this be higher than the trading comps midpoint? What premium does it reflect?",
            "Find the average premium across all three deals. What does the typical acquisition premium range tell you about why buyers must pay more than the current market price?",
            "Apply the average premium to NovaTech's current stock price. This is the minimum offer price any acquirer must put on the table to convince shareholders to sell. How do you calculate it?",
            "— Leave blank.",
        ], n_rows=9, section_name="PREC_DEALS", reveal_lines=[
            "<b>Header row</b> — labels: Deal | Year | Deal EV | LTM EBITDA | EV/EBITDA | Pre-deal Mkt Cap | Control Premium %",
            "<b>Label:</b> AcquireCo/TechAlpha '22 &nbsp;|&nbsp; <b>EV/EBITDA</b> =Deal EV÷LTM EBITDA; <b>Premium</b> =(Deal EV−Pre-deal Cap)÷Pre-deal Cap",
            "<b>Label:</b> MegaCorp/DataCore '21 &nbsp;|&nbsp; same formulas — copy from row above",
            "<b>Label:</b> GlobalTech/InfoPro '23 &nbsp;|&nbsp; same formulas",
            "<i>Blank separator — leave A and B empty</i>",
            "<b>Label:</b> Median EV/EBITDA &nbsp;|&nbsp; <b>Formula:</b> =MEDIAN(EV/EBITDA range)",
            "<b>Label:</b> Avg Control Premium &nbsp;|&nbsp; <b>Formula:</b> =AVERAGE(premium range)",
            "<b>Label:</b> NovaTech Floor Price &nbsp;|&nbsp; <b>Formula:</b> =Current price × (1 + Avg Premium)",
            "<i>Blank separator — leave A and B empty</i>",
        ])

        formula_grid_section("prec_val", "NovaTech Implied EV Valuation", [
            "Enter from the given inputs. An acquirer is effectively paying a multiple of this earnings figure for the entire business.",
            "Reference the midpoint from your deal table — do not retype it. It should be higher than the trading comps midpoint. Do you understand why?",
            "If you know what acquirers historically paid per unit of this earnings metric, and you know NovaTech's figure, how do you calculate the implied total business value?",
            "Subtract net borrowings from the total business value. Who gets paid before shareholders in any acquisition — and why does that make this a subtraction?",
            "Divide equity value by shares outstanding. Is your answer higher than the comps-implied price? Can you explain the difference?",
        ], n_rows=5, seed=_get_all_cells().get("PREC_DEALS", {}), reveal_lines=[
            "<b>Label:</b> NovaTech EBITDA &nbsp;|&nbsp; <b>Enter:</b> hard-code from inputs",
            "<b>Label:</b> Median Deal Multiple &nbsp;|&nbsp; <b>Enter:</b> reference from deal table",
            "<b>Label:</b> Implied EV &nbsp;|&nbsp; <b>Formula:</b> =B1*B2",
            "<b>Label:</b> Equity Value &nbsp;|&nbsp; <b>Formula:</b> =B3−Net Debt (from inputs)",
            "<b>Label:</b> Implied Per-Share Price &nbsp;|&nbsp; <b>Formula:</b> =B4÷Shares Outstanding",
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

Why leverage? Because it amplifies returns on equity invested. If you buy a $1,080M company with $432M equity and $648M debt, and the business generates enough cash flow to pay down debt over five years, the equity at exit is worth far more than the $432M invested — even if the exit multiple stays the same.
""")
        st.markdown("## The Three Sources of PE Return")
        st.markdown("""
**1. EBITDA Growth.** The company becomes more profitable — through revenue growth, cost cuts, or add-on acquisitions.

**2. Deleveraging.** Every dollar of cash flow used to pay down debt increases equity value by a dollar (Equity = EV − Debt). A company that pays down $200M of debt over five years creates $200M of additional equity value even if EV stays flat.

**3. Multiple Expansion.** Buying at 9× and selling at 11× captures the difference. This is the least reliable source — it depends on market conditions at exit — so conservative models assume entry multiple = exit multiple.
""")
        st.markdown("## Building the Model: Three Sections")
        st.markdown("""
**Section 1 — Sources & Uses.** Purchase price = entry multiple × LTM EBITDA. Structure: 60% debt, 40% PE equity. Sources must equal Uses.

**Section 2 — Debt Schedule.** Tracks the loan balance year by year. Each year: Beginning Debt → subtract cash available for paydown → Ending Debt → feeds next year's Beginning Debt. This rolling structure is the core of the model.

**Section 3 — Exit & Returns.** Exit EV = Year 5 EBITDA × exit multiple. Exit Equity = Exit EV − remaining debt. MOIC = Exit Equity ÷ Entry Equity. IRR uses Excel's =IRR() function on a cash flow row: −entry equity at year 0, exit equity at year 5, zeros in between.
""")
        warning("The exit multiple assumption is the single biggest variable in an LBO. Always assume exit = entry in your base case. Multiple expansion is a bonus, not a plan.")
        pro_tip("Build the debt schedule as a rolling structure: Ending Debt in Yr1 = Beginning Debt − paydown, and Beginning Debt in Yr2 = Yr1 Ending Debt. This is more robust than a one-line formula.")

    with build_tab:
        st.markdown("## Build the LBO Model")

        formula_grid_section("lbo_su", "Sources & Uses", [
            "Enter from the given inputs — this single earnings figure drives every other number in the deal. Why do LBO models start with this metric rather than revenue or net income?",
            "Enter from the given inputs. The PE firm is paying this many times the earnings figure for the whole business. Why do LBO deals use this type of multiple rather than a price-to-earnings ratio?",
            "The total purchase price for the business. Multiply the two rows above. This is the amount that must be financed.",
            "Most of the purchase price is borrowed money. At 60%, how much of the total deal value does that represent? Why does leverage amplify equity returns if the business performs well?",
            "The PE firm contributes the remaining 40% from its own capital. MOIC and IRR measure returns against this number — not the full purchase price. Why does that matter?",
            "The two funding sources must add up to exactly the total cost. Does the sum of debt and equity equal the purchase price? If not, find the error.",
            "— Leave blank.",
        ], n_rows=7, section_name="LBO_SU", reveal_lines=[
            "<b>Label:</b> LTM EBITDA &nbsp;|&nbsp; <b>Enter:</b> hard-code from inputs",
            "<b>Label:</b> Entry Multiple &nbsp;|&nbsp; <b>Enter:</b> hard-code from inputs",
            "<b>Label:</b> Entry EV &nbsp;|&nbsp; <b>Formula:</b> =B1*B2",
            "<b>Label:</b> Debt (60%) &nbsp;|&nbsp; <b>Formula:</b> =B3*0.60",
            "<b>Label:</b> PE Equity (40%) &nbsp;|&nbsp; <b>Formula:</b> =B3*0.40",
            "<b>Label:</b> Sources Check &nbsp;|&nbsp; <b>Formula:</b> =B4+B5 &nbsp;(should equal B3)",
            "<i>Blank separator — leave A and B empty</i>",
        ])

        lbo_su_cells = _get_all_cells().get("LBO_SU", {})
        formula_grid_multicol("lbo_debt", "Debt Schedule (Years 1 – 5)", [
            "Year 1 links from the financing section you built. Years 2 through 5 each take their opening balance from where the prior year ended. Why is this rolling structure important for tracking how debt falls over time?",
            "The annual cost of carrying the outstanding loan. Apply the interest rate from inputs to the balance at the start of the year. Should you use the opening or closing balance — and why?",
            "The company's earnings grow at a fixed annual rate. How do you express compound growth mathematically? What is the formula for Year 3 if you start at a base and grow at rate r each year?",
            "Simplified available cash after tax and capital costs — this is what goes toward repaying the lender each year. Which inputs determine how much tax and capex eat into operating earnings?",
            "After applying available cash to the outstanding loan, what balance remains? Watch this number fall each year — that decline is the deleveraging that drives private equity returns.",
            "If exit value is based on a multiple of Year 5 earnings, and debt has been substantially paid down, how does equity value change? What is the formula if you were to compute it for each year?",
        ], n_rows=6, col_labels=["Yr 1 (B)","Yr 2 (C)","Yr 3 (D)","Yr 4 (E)","Yr 5 (F)"],
        seed=lbo_su_cells, section_name="LBO_DEBT", reveal_lines=[
            "<b>Label:</b> Beginning Debt &nbsp;|&nbsp; Yr1: reference PE Debt from S&amp;U; Yr2+: =prior year's Ending Debt",
            "<b>Label:</b> Interest Expense &nbsp;|&nbsp; <b>Formula:</b> =Beginning Debt × Interest Rate (from inputs)",
            "<b>Label:</b> EBITDA &nbsp;|&nbsp; <b>Formula (Yr n):</b> =Entry EBITDA × (1+growth rate)^n",
            "<b>Label:</b> FCF for Paydown &nbsp;|&nbsp; <b>Formula:</b> =EBITDA*(1−tax rate) − Capex (from inputs)",
            "<b>Label:</b> Ending Debt &nbsp;|&nbsp; <b>Formula:</b> =Beginning Debt − FCF for Paydown",
            "<b>Label:</b> Equity Value Preview &nbsp;|&nbsp; <b>Formula:</b> =(Exit Multiple × EBITDA) − Ending Debt",
        ])

        lbo_debt_cells = _get_all_cells().get("LBO_DEBT", {})
        lbo_seed = {**lbo_su_cells, **lbo_debt_cells}
        formula_grid_section("lbo_exit", "Exit & Returns", [
            "Conservative base case: set this equal to what was paid at entry. Why do bankers resist assuming the exit ratio will be higher — and what does that constraint imply about where returns must actually come from?",
            "Compound the entry earnings figure at the given growth rate for 5 years. What exponent do you use? How does compounding for 5 periods differ from simply multiplying by 5?",
            "Multiply the two rows above. This is the implied sale price when the fund exits. Which rows, and what operation?",
            "Pull from your debt schedule — the balance at the end of Year 5. How much of the original loan is still outstanding after 5 years of paydown?",
            "After paying off lenders at exit, what remains for the fund? Sale proceeds minus what?",
            "Reference from your financing section — do not retype. Why does retyping a number from another section create model risk?",
            "How much did the fund multiply its money? Express as a ratio: what you receive divided by what you invested. What is the typical target for an institutional PE fund?",
            "To calculate annualized return, you need a cash flow timeline: negative investment at Year 0, no cash flows in between, and positive exit proceeds at Year 5. Build that row now.",
            "Apply the IRR function to the cash flow row above. What annualized rate does the fund earn? Is it above the 20% institutional benchmark?",
        ], n_rows=9, seed=lbo_seed, reveal_lines=[
            "<b>Label:</b> Exit Multiple &nbsp;|&nbsp; <b>Enter:</b> same as entry multiple (base case = no expansion)",
            "<b>Label:</b> Year 5 EBITDA &nbsp;|&nbsp; <b>Formula:</b> =Entry EBITDA*(1+growth rate)^5",
            "<b>Label:</b> Exit EV &nbsp;|&nbsp; <b>Formula:</b> =B1*B2 &nbsp;(Exit Multiple × Year 5 EBITDA)",
            "<b>Label:</b> Remaining Debt &nbsp;|&nbsp; <b>Enter:</b> reference Year 5 Ending Debt from debt schedule",
            "<b>Label:</b> Exit Equity &nbsp;|&nbsp; <b>Formula:</b> =B3−B4",
            "<b>Label:</b> Entry Equity &nbsp;|&nbsp; <b>Enter:</b> reference PE Equity from S&amp;U section",
            "<b>Label:</b> MOIC &nbsp;|&nbsp; <b>Formula:</b> =B5/B6 &nbsp;(Exit Equity ÷ Entry Equity)",
            "<b>Label:</b> IRR Cash Flow Row &nbsp;|&nbsp; build row: [−Entry Equity, 0, 0, 0, 0, Exit Equity]",
            "<b>Label:</b> IRR &nbsp;|&nbsp; <b>Formula:</b> =IRR(cash flow row above)",
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

**Accretive** means the deal increases EPS. **Dilutive** means the deal decreases EPS. Boards and public investors focus intensely on this metric because EPS drives stock price. A dilutive deal — especially one without a compelling strategic rationale — invites shareholder criticism and activist pressure.
""")
        st.markdown("## Why All-Stock Deals Are More Complex")
        st.markdown("""
In a cash deal, the acquirer simply pays cash and the target's shareholders disappear. No new shares are issued.

In an all-stock deal, the acquirer issues new shares to pay for the target. This increases the share count, which dilutes EPS unless the earnings contribution from the acquired business more than compensates. Fewer new shares = less dilution. A higher acquirer stock price means fewer new shares need to be issued for the same deal value.
""")
        st.markdown("## Building the Pro Forma Income Statement")
        st.markdown("""
**Synergies (positive).** Cost synergies from eliminating duplicate functions. Enter as a positive number — they increase combined earnings.

**Amortization of Acquired Intangibles (negative).** When you acquire a company, accounting rules require you to step up intangible assets to fair value. These are then amortized — a recurring non-cash expense that hits reported EPS. Enter as negative.

**The EPS test.** Pro Forma EPS = Pro Forma Net Income ÷ Pro Forma Shares. Compare to standalone EPS = Acquirer NI ÷ Acquirer Shares. % change = (PF EPS − Standalone EPS) ÷ Standalone EPS.
""")
        warning("Synergies are almost always overstated by management. Use conservative estimates in base case and show a sensitivity for break-even synergies — the minimum needed for the deal to be EPS-neutral.")

    with build_tab:
        st.markdown("## Build the Merger Model")

        formula_grid_section("merger_deal", "Deal Assumptions", [
            "Enter from the given inputs — this is the target's stock price before any deal rumors reached the market. Why is the pre-rumor price used rather than today's price?",
            "Enter from the given inputs as a decimal. Why must acquirers pay above market price — what are shareholders giving up by selling control?",
            "What does each target shareholder actually receive per share? Work out the formula using the market price and the premium rate from the two rows above.",
            "Enter from the given inputs. Combined with the per-share offer, this gives the total cost of acquiring the company.",
            "The total consideration paid to target shareholders. Which two rows above multiply together to give you this?",
            "Enter from the given inputs. In an all-stock deal, this is the currency NovaTech uses to pay — the higher it is, the fewer new shares must be created. Why does that matter?",
            "In an all-stock deal, NovaTech issues its own shares to pay for the target. Total consideration divided by what price gives the number of new shares created?",
            "How much do existing NovaTech shareholders get diluted? Express the new shares as a fraction of total shares after the deal closes.",
        ], n_rows=8, section_name="MERGER_DEAL", reveal_lines=[
            "<b>Label:</b> Target Market Price &nbsp;|&nbsp; <b>Enter:</b> hard-code from inputs",
            "<b>Label:</b> Acquisition Premium &nbsp;|&nbsp; <b>Enter:</b> hard-code as decimal (e.g. 0.25)",
            "<b>Label:</b> Offer Price Per Share &nbsp;|&nbsp; <b>Formula:</b> =B1*(1+B2)",
            "<b>Label:</b> Target Shares Outstanding &nbsp;|&nbsp; <b>Enter:</b> hard-code from inputs",
            "<b>Label:</b> Total Deal Value &nbsp;|&nbsp; <b>Formula:</b> =B3*B4",
            "<b>Label:</b> NovaTech Share Price &nbsp;|&nbsp; <b>Enter:</b> hard-code from inputs",
            "<b>Label:</b> New Shares Issued &nbsp;|&nbsp; <b>Formula:</b> =B5/B6",
            "<b>Label:</b> Dilution % &nbsp;|&nbsp; <b>Formula:</b> =B7/(Existing Shares+B7)",
        ])

        formula_grid_section("merger_pf", "Pro Forma Income Statement", [
            "Enter NovaTech's standalone bottom-line earnings from inputs — the baseline before any deal impact is considered.",
            "Enter the target's standalone bottom-line earnings from inputs. Adding this is the primary financial benefit of combining the two companies.",
            "Cost savings from eliminating duplicate operations, already net of taxes. Should this add to or subtract from combined earnings? Enter from inputs.",
            "An accounting charge that arises when acquired intangible assets are written up to fair value and then amortized. Does this increase or decrease reported earnings? What sign does it carry? Enter from inputs.",
            "Combine all four components — some add to earnings, some subtract. Which function handles a mix of positive and negative items across a range?",
        ], n_rows=5, seed=_get_all_cells().get("MERGER_DEAL", {}), section_name="MERGER_PF", reveal_lines=[
            "<b>Label:</b> Acquirer NI &nbsp;|&nbsp; <b>Enter:</b> NovaTech's net income from inputs (positive)",
            "<b>Label:</b> Target NI &nbsp;|&nbsp; <b>Enter:</b> TargetCo's net income from inputs (positive)",
            "<b>Label:</b> After-tax Synergies &nbsp;|&nbsp; <b>Enter:</b> from inputs as a positive number",
            "<b>Label:</b> Intangibles Amortization &nbsp;|&nbsp; <b>Enter:</b> from inputs as a <i>negative</i> number",
            "<b>Label:</b> Pro Forma NI &nbsp;|&nbsp; <b>Formula:</b> =SUM(B1:B4)",
        ])

        merger_seed = {**_get_all_cells().get("MERGER_DEAL", {}), **_get_all_cells().get("MERGER_PF", {})}
        formula_grid_section("merger_eps", "EPS & Accretion / Dilution Test", [
            "NovaTech's share count before any new shares are issued. Enter from inputs.",
            "Reference from your deal assumptions section — do not retype it. Why does retyping a number from another section create model risk?",
            "After the deal closes, total shares outstanding increases. Which two rows above combine to give you the new share count?",
            "NovaTech's per-share earnings before the deal. Divide standalone earnings by standalone shares — this is the benchmark you are testing against.",
            "The combined entity's per-share earnings after the deal. Divide combined earnings by combined shares. Compare carefully to the benchmark above.",
            "Express the change in per-share earnings as a percentage. A positive result means the deal improved earnings per share. What do you call each outcome — and which outcome do boards prefer?",
        ], n_rows=6, seed=merger_seed, reveal_lines=[
            "<b>Label:</b> Standalone Shares &nbsp;|&nbsp; <b>Enter:</b> hard-code from inputs",
            "<b>Label:</b> New Shares Issued &nbsp;|&nbsp; <b>Enter:</b> reference from Deal Assumptions section",
            "<b>Label:</b> Pro Forma Shares &nbsp;|&nbsp; <b>Formula:</b> =B1+B2",
            "<b>Label:</b> Standalone EPS &nbsp;|&nbsp; <b>Formula:</b> =Acquirer NI / B1",
            "<b>Label:</b> Pro Forma EPS &nbsp;|&nbsp; <b>Formula:</b> =Pro Forma NI / B3",
            "<b>Label:</b> Accretion/(Dilution) &nbsp;|&nbsp; <b>Formula:</b> =(B5−B4)/B4 &nbsp;(positive = accretive, negative = dilutive)",
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
Budget vs. Actual (BvA) is the core rhythm of corporate finance. Every month, the FP&A team publishes a report comparing what was planned (the budget) against what actually happened (the actuals). The result is a variance report.

The skill is in the interpretation. A $7M revenue miss sounds bad. But is it because the sales team sold fewer units (a volume problem)? Or because they sold the right number at lower prices (a pricing problem)? These require completely different responses. The BvA model's job is to separate them.
""")
        st.markdown("## Building the Variance Table")
        st.markdown("""
The table architecture: one row per P&L line item (Revenue, COGS, Gross Profit, SG&A, EBITDA), with columns for Budget, Actual, Variance $, Variance %, and a Favorable/Unfavorable flag.

**Variance $ = Actual − Budget.** For revenue, positive is good. For costs, positive means you overspent.

**Gross Profit and EBITDA are derived, not input.** Budget GP = =B2-B3. Actual GP = =C2-C3. If a line is a formula in budget, it must also be a formula in actual.

**F/U flag:** for revenue =IF(Variance>=0,"F","U"). For cost rows, the logic reverses.
""")
        st.markdown("## Volume / Price Decomposition")
        st.markdown("""
**Volume Effect = (Actual Units − Budget Units) × Budget Price.** Isolates the impact of selling fewer units, holding price constant.

**Price Effect = Actual Units × (Actual Price − Budget Price).** Isolates pricing impact at actual volume.

Volume Effect + Price Effect = Total Revenue Variance. This is your built-in check.
""")
        warning("A revenue miss almost always creates a disproportionately larger EBITDA miss. If revenue misses by 5%, EBITDA might miss by 25% — because many costs are fixed.")
        pro_tip("Apply conditional formatting to the Variance $ column: red for negative values, green for positive. This makes the table instantly scannable in a CFO presentation.")

    with build_tab:
        st.markdown("## Build the Budget vs. Actual Model")
        st.markdown("Q1 data: Budget revenue $120M, actual $113M · Budget COGS $72M, actual $70.3M · Budget SG&A $20M, actual $21.5M")

        formula_grid_section("bva_main", "Main Variance Table (cols A – F)", [
            "Before entering any data, think about what a variance report must communicate. A manager needs to see what was planned, what actually happened, the gap in dollar terms, the gap in percentage terms, and whether each line is good or bad news. What columns does that imply — and does the ordering matter?",
            "Enter planned and actual amounts for the top line from inputs. The dollar gap is always actual minus plan. For a revenue line, is a positive gap good or bad news? How would you encode that judgment in an IF formula?",
            "Enter planned and actual for this cost line from inputs. Same dollar gap formula — but does the good/bad logic flip for a cost versus a revenue line? Why?",
            "This line must never be typed — it must always be derived from the rows above. Budget column: subtract the cost from the revenue figure. Actual column: same operation using actual figures. Why does hardcoding this number break the model?",
            "Enter planned and actual for this overhead line from inputs. Apply the same variance formula and the good/bad flag. You overspent here — what does the flag show?",
            "Same rule as before — always a formula, never typed. Subtract the overhead line from the previous subtotal in each column. Notice: if revenue misses by about 6%, this subtotal misses by a much larger percentage. What causes that amplification?",
            "Express this subtotal as a percentage of the top line for each column. What does the margin percentage reveal that the raw dollar variance alone does not show?",
        ], n_rows=7, section_name="BVA_MAIN", reveal_lines=[
            "<b>Header row</b> — labels: Line Item | Budget | Actual | Variance $ | Variance % | F/U",
            "<b>Label:</b> Revenue &nbsp;|&nbsp; Budget &amp; Actual from inputs; <b>Var$</b> =Actual−Budget; <b>F/U</b> =IF(Var$≥0,\"F\",\"U\")",
            "<b>Label:</b> COGS &nbsp;|&nbsp; Budget &amp; Actual from inputs; <b>F/U flips</b> =IF(Var$≤0,\"F\",\"U\") &nbsp;(lower cost = Favorable)",
            "<b>Label:</b> Gross Profit &nbsp;|&nbsp; <i>Never type</i>; <b>Budget col</b> =Revenue_budget−COGS_budget; <b>Actual col</b> same",
            "<b>Label:</b> SG&amp;A &nbsp;|&nbsp; Budget &amp; Actual from inputs; same F/U logic as COGS",
            "<b>Label:</b> EBITDA &nbsp;|&nbsp; <i>Never type</i>; <b>Formula each col:</b> =GrossProfit_col−SGA_col",
            "<b>Label:</b> EBITDA Margin &nbsp;|&nbsp; <b>Formula each col:</b> =EBITDA_col/Revenue_col",
        ])

        formula_grid_section("bva_decomp", "Volume / Price Revenue Decomposition", [
            "Enter the planned unit volume from inputs.",
            "Enter the actual unit volume from inputs. How many fewer units were sold than planned?",
            "Enter the planned price per unit from inputs.",
            "Enter the realized price per unit from inputs. Was the revenue miss driven by volume, price, or both?",
            "Isolate the revenue impact of selling fewer units, holding price constant at the planned rate. If you sold fewer units than planned and value those lost units at the planned price — what is the formula?",
            "Isolate the revenue impact of lower pricing, holding volume constant at actual. Every unit actually sold came in at a lower price than planned — how much revenue did that price difference cost?",
            "Add the two effects above. This sum must exactly equal the total revenue variance from your main table. If it does not match, which formula is wrong?",
        ], n_rows=7, reveal_lines=[
            "<b>Label:</b> Budget Units &nbsp;|&nbsp; <b>Enter:</b> hard-code from inputs",
            "<b>Label:</b> Actual Units &nbsp;|&nbsp; <b>Enter:</b> hard-code from inputs",
            "<b>Label:</b> Budget Price/Unit &nbsp;|&nbsp; <b>Enter:</b> hard-code from inputs",
            "<b>Label:</b> Actual Price/Unit &nbsp;|&nbsp; <b>Enter:</b> hard-code from inputs",
            "<b>Label:</b> Volume Effect &nbsp;|&nbsp; <b>Formula:</b> =(Actual Units − Budget Units) × Budget Price",
            "<b>Label:</b> Price Effect &nbsp;|&nbsp; <b>Formula:</b> =Actual Units × (Actual Price − Budget Price)",
            "<b>Label:</b> Check &nbsp;|&nbsp; <b>Formula:</b> =Volume Effect + Price Effect &nbsp;(must tie to Revenue Variance in main table)",
        ])
