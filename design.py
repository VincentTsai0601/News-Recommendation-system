"""British newspaper-inspired presentation, using local CSS and SVG."""
import streamlit as st

STYLE = """
<style>
:root { color-scheme: light; }
.stApp {
 background-color:#f5f0e5;
 background-image:repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(86,62,32,.018) 4px),
 radial-gradient(ellipse at top right,#e2dac7,transparent 60%);
}
[data-testid="stHeader"] { background:#f5f0e5ed; }
[data-testid="stMainBlockContainer"] { max-width:1180px; padding-top:2rem; }
.world-masthead { border-top:4px solid #223b35; border-bottom:1px solid #8e8b7d;
 display:flex; align-items:center; justify-content:space-between; gap:20px; padding:20px 0; }
.world-brand { font-family:Georgia,'Times New Roman',serif; font-size:36px; font-weight:700; color:#203831; letter-spacing:-1px; }
.world-brand span { color:#843c43; }
.world-edition { color:#625f54; font-size:10px; letter-spacing:2px; text-align:right; line-height:1.9; }
.world-hero { position:relative; overflow:hidden; min-height:325px; padding:48px 0 32px; }
.world-hero .eyebrow { font-size:10px; letter-spacing:3px; color:#843c43; font-weight:700; margin-bottom:20px; }
.world-hero h1, .world-hero h1 * { font-family:Georgia,'Times New Roman',serif!important; font-weight:400; }
.world-hero h1 { color:#203831; font-size:65px; line-height:1.12; letter-spacing:-2px; max-width:690px; position:relative; z-index:1; margin:0 0 25px; padding:0; }
.world-hero h1 em { color:#843c43; }
.world-hero p { color:#56594e; line-height:1.8; font-size:14px; position:relative; z-index:1; max-width:560px; }
.westminster { position:absolute; width:510px; height:330px; right:-20px; bottom:0; opacity:.28; pointer-events:none; }
.world-strip { display:flex; flex-wrap:wrap; gap:24px; border-top:1px solid #969385; border-bottom:3px double #969385;
 padding:14px 0; margin-bottom:24px; font-size:10px; letter-spacing:1.5px; color:#56594e; }
.world-strip b { color:#843c43; }
[data-testid="stForm"] { background:#eee8da; border:1px solid #cbc3b2; border-radius:3px; }
.story-tag { color:#843c43; font-size:10px; letter-spacing:2px; font-weight:700; padding:4px 0 8px; }
[data-testid="stColumn"] h3 { font-family:Georgia,'Times New Roman',serif!important; font-size:28px; font-weight:400; line-height:1.25; color:#203831; }
[data-testid="stColumn"] [data-testid="stVerticalBlock"] { border-radius:3px; }
[data-testid="stText"] { color:#45483f; line-height:1.8; font-size:13px; }
[data-testid="stCaptionContainer"] p { color:#64665c; }
[data-testid="stLinkButton"] a { color:#843c43; border:1px solid #bca9a3; background:transparent; border-radius:3px; font-size:12px; }
[data-testid="stButton"] button, [data-testid="stFormSubmitButton"] button {
 background:#243e35; color:#fffaf0; border:1px solid #243e35; border-radius:3px; }
[data-testid="stButton"] button:hover, [data-testid="stFormSubmitButton"] button:hover { background:#38594b; color:#fffaf0; }
.world-footer { border-top:3px double #969385; margin-top:30px; padding:22px 0; font-family:Georgia,serif; color:#625f54; font-size:12px; }
@media(max-width:700px) {
.world-brand { font-size:27px; }
.world-edition { font-size:8px; max-width:120px; }
.world-hero { min-height:290px; padding:30px 0; }
.world-hero h1 { font-size:43px; letter-spacing:-1px; }
.world-hero p { max-width:85%; }
.westminster { right:-180px; opacity:.15; }
.world-strip { gap:12px; font-size:9px; }
[data-testid="stMainBlockContainer"] { padding-top:1rem; }
}
</style>
"""

HERO = """
<div class="world-masthead">
 <div class="world-brand">World <span>/</span> Brief</div>
 <div class="world-edition">THE INTERNATIONAL EDITION<br>BRITISH STYLE · GLOBAL PERSPECTIVE</div>
</div>
<div class="world-hero">
 <svg class="westminster" viewBox="0 0 520 340" aria-hidden="true">
 <g fill="none" stroke="#3e5548" stroke-width="1.5">
 <path d="M0 310H520M0 320H520M10 290H80V200H110V290H150V155H175V290H215V185H375V290H420V170H450V290H510"/>
 <path d="M224 185V150L231 142L238 150V185M355 185V150L362 142L369 150V185"/>
 <path d="M270 290V105H325V290M266 105H329V88H266ZM274 88V65H321V88M278 65L298 15L317 65ZM298 15V0"/>
 <path d="M277 160H317M277 170H317M277 265H317M277 275H317M282 177V255M292 177V255M302 177V255M312 177V255"/>
 <circle cx="297" cy="132" r="20" fill="#f5f0e5"/><circle cx="297" cy="132" r="16"/>
 <path d="M297 117V132L309 139M90 214V237M100 214V237M159 171V196M168 171V196M430 187V210M439 187V210"/>
 <path d="M225 210V260M237 210V260M249 210V260M337 210V260M349 210V260M361 210V260"/>
 <path d="M0 302Q150 297 260 305T520 300M15 334Q140 327 285 333T510 330" stroke-opacity=".5"/>
 </g></svg>
 <div class="eyebrow">THE WORLD, WITH A DIFFERENT ACCENT</div>
 <h1>A classic outlook.<br><em>A world of voices.</em></h1>
 <p>A British-inspired reading room for international news.<br>Follow the stories that matter, in six original languages.</p>
</div>
<div class="world-strip">
 <span><b>EN</b> ENGLISH</span><span><b>中文</b> CHINESE</span>
 <span><b>DE</b> DEUTSCH</span><span><b>FR</b> FRANÇAIS</span>
 <span><b>IT</b> ITALIANO</span><span><b>ES</b> ESPAÑOL</span>
</div>
"""

def render_header():
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown(HERO, unsafe_allow_html=True)
