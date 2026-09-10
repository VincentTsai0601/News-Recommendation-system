"""British newspaper-inspired presentation, using local CSS and SVG."""
import streamlit as st
import base64
from functools import lru_cache
from pathlib import Path

STYLE = """
<style>
:root { color-scheme: light; --british-wall: url("__BRITISH_WALL__"); }
 .stApp {
 background-color:#d8cbb7;
 background-image:linear-gradient(rgba(244,237,224,.20),rgba(244,237,224,.20)),var(--british-wall);
 background-size:cover; background-position:center top; background-attachment:fixed;
}
[data-testid="stHeader"] { background:rgba(248,244,235,.94); }
[data-testid="stMainBlockContainer"] {
 max-width:1180px; padding:2rem 2.5rem 3rem;
 background:rgba(250,247,240,.94); margin-top:1.5rem; margin-bottom:2rem;
 border:1px solid rgba(108,85,61,.28); box-shadow:0 12px 48px rgba(40,29,18,.18);
 border-radius:6px;
}
.world-masthead { border-top:4px solid #18324f; border-bottom:1px solid #8e8b7d;
 display:flex; align-items:center; justify-content:space-between; gap:20px; padding:20px 0; }
.world-brand { font-family:Georgia,'Times New Roman',serif; font-size:36px; font-weight:700; color:#18324f; letter-spacing:-1px; }
.world-brand span { color:#a12732; }
.world-edition { color:#625f54; font-size:10px; letter-spacing:2px; text-align:right; line-height:1.9; }
.world-hero { position:relative; overflow:hidden; min-height:360px; padding:42px 28px 28px;
 margin:20px 0; border:1px solid #c4b69f; border-radius:3px;
 background-image:linear-gradient(90deg,rgba(250,247,240,.98) 0%,rgba(250,247,240,.94) 38%,rgba(250,247,240,.12) 78%),var(--british-wall);
 background-size:cover; background-position:center;
}
.world-hero .eyebrow { font-size:10px; letter-spacing:3px; color:#a12732; font-weight:700; margin-bottom:20px; }
.world-hero h1, .world-hero h1 * { font-family:Georgia,'Times New Roman',serif!important; font-weight:400; }
.world-hero h1 { color:#18324f; font-size:57px; line-height:1.12; letter-spacing:-2px; max-width:640px; position:relative; z-index:1; margin:0 0 25px; padding:0; }
.world-hero h1 em { color:#a12732; }
.world-hero p { color:#56594e; line-height:1.8; font-size:14px; position:relative; z-index:1; max-width:560px; }
.westminster { position:absolute; width:510px; height:330px; right:-20px; bottom:0; opacity:.28; pointer-events:none; }
.world-strip { display:flex; flex-wrap:wrap; gap:24px; border-top:1px solid #969385; border-bottom:3px double #969385;
 padding:14px 0; margin-bottom:24px; font-size:10px; letter-spacing:1.5px; color:#56594e; }
.world-strip b { color:#a12732; }
[data-testid="stForm"] { background:#eee8da; border:1px solid #cbc3b2; border-radius:3px; }
.story-tag { color:#a12732; font-size:10px; letter-spacing:2px; font-weight:700; padding:4px 0 8px; }
[data-testid="stColumn"] h3 { font-family:Georgia,'Times New Roman',serif!important; font-size:28px; font-weight:400; line-height:1.25; color:#18324f; }
[data-testid="stColumn"] [data-testid="stVerticalBlock"] { border-radius:3px; }
[data-testid="stText"] { color:#45483f; line-height:1.8; font-size:13px; }
[data-testid="stCaptionContainer"] p { color:#64665c; }
[data-testid="stLinkButton"] a { color:#a12732; border:1px solid #bca9a3; background:transparent; border-radius:3px; font-size:12px; }
[data-testid="stButton"] button, [data-testid="stFormSubmitButton"] button {
 background:#18324f; color:#fffaf0; border:1px solid #18324f; border-radius:3px; }
[data-testid="stButton"] button:hover, [data-testid="stFormSubmitButton"] button:hover { background:#294967; color:#fffaf0; }
.world-footer { border-top:3px double #969385; margin-top:30px; padding:22px 0; font-family:Georgia,serif; color:#625f54; font-size:12px; }
@media(max-width:700px) {
.world-brand { font-size:27px; }
.world-edition { font-size:8px; max-width:120px; }
.stApp { background-attachment:scroll; }
.world-hero { min-height:290px; padding:26px 18px;
 background-image:linear-gradient(90deg,rgba(250,247,240,.96),rgba(250,247,240,.80)),var(--british-wall);
 background-position:center; }
.world-hero h1 { font-size:38px; letter-spacing:-1px; }
.world-hero p { max-width:100%; }
.westminster { right:-180px; opacity:.15; }
.world-strip { gap:12px; font-size:9px; }
[data-testid="stMainBlockContainer"] { padding:1rem; margin-top:.5rem; border-radius:0; }
}
.article-open { display:inline-flex; align-items:center; justify-content:center;
 min-height:48px; padding:10px 20px; box-sizing:border-box;
 background:#18324f; color:#fffaf0!important; text-decoration:none!important;
 border-radius:3px; font-size:15px; font-weight:600; touch-action:manipulation; }
.article-open:hover { background:#294967; }
.article-open:focus-visible { outline:3px solid #a12732; outline-offset:3px; }
@media(max-width:700px) { .article-open { width:100%; } }
</style>
"""

HERO = """
<div class="world-masthead">
 <div class="world-brand">World <span>/</span> Brief</div>
 <div class="world-edition">THE INTERNATIONAL EDITION<br>BRITISH STYLE · GLOBAL PERSPECTIVE</div>
</div>
<div class="world-hero">
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

@lru_cache(maxsize=1)
def background_style():
    image = Path(__file__).resolve().parent / "assets" / "british-wall.jpg"
    encoded = base64.b64encode(image.read_bytes()).decode("ascii")
    return STYLE.replace("__BRITISH_WALL__", "data:image/jpeg;base64," + encoded)


def render_header():
    st.markdown(background_style(), unsafe_allow_html=True)
    st.markdown(HERO, unsafe_allow_html=True)
