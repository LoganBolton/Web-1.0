"""A client-side metered paywall.

Only the first paragraph is in the page as text. The rest is base64-encoded
JSON that the page decodes if the reader still has free articles this month
or has signed in. Credentials are checked against a tiny string hash, so the
passwords are not in the page source.
"""
import base64
import json

from .web import esc


def djb2(s):
    h = 5381
    for ch in s:
        h = ((h * 33) ^ ord(ch)) & 0xFFFFFFFF
    return h


def encode(paras):
    return base64.b64encode(json.dumps(paras).encode("utf-8")).decode("ascii")


def block(article_id, lead_html, rest_paras, key, free=3, brand="this paper",
          creds=(), suspended=(), signin_hint="", wall_title=None):
    """Return HTML+JS for the gated article body.

    creds: list of (user, password) that unlock. suspended: list of (user, password)
    that are recognised but refused.
    """
    ok = [djb2(f"{u.lower()}:{p}") for u, p in creds]
    bad = [djb2(f"{u.lower()}:{p}") for u, p in suspended]
    return f"""
<div class="lead">{lead_html}</div>
<div id="pw-rest" data-enc="{encode(rest_paras)}"></div>
<div id="pw-wall" hidden class="paywall">
 <h3>{esc(wall_title or f"You have read your {free} free articles this month")}</h3>
 <p>Subscribe to {esc(brand)} to keep reading, or sign in below.</p>
 <form id="pw-form"><label>Reader name <input id="pw-u" autocomplete="username"></label>
 <label>Pass code <input id="pw-p" type="password" autocomplete="current-password"></label>
 <button>Sign in</button></form><p id="pw-msg" role="alert"></p>
 <p class="pw-hint">{esc(signin_hint)}</p>
</div>
<script>(function(){{
var K='{key}',id='{article_id}',OK={json.dumps(ok)},BAD={json.dumps(bad)},FREE={free};
function h(s){{var x=5381;for(var i=0;i<s.length;i++){{x=(Math.imul(x,33)^s.charCodeAt(i))>>>0;}}return x;}}
function get(k,d){{try{{var v=localStorage.getItem(k);return v===null?d:JSON.parse(v);}}catch(e){{return d;}}}}
function set(k,v){{try{{localStorage.setItem(k,JSON.stringify(v));}}catch(e){{}}}}
function show(){{var el=document.getElementById('pw-rest');
 var b=atob(el.dataset.enc),u=new Uint8Array(b.length);for(var i=0;i<b.length;i++)u[i]=b.charCodeAt(i);
 var ps=JSON.parse(new TextDecoder().decode(u));
 el.innerHTML=ps.map(function(p){{var d=document.createElement('p');d.textContent=p;return d.outerHTML;}}).join('');
 document.getElementById('pw-wall').hidden=true;}}
var seen=get(K+'-seen',[]), sub=get(K+'-sub',false);
if(sub||seen.indexOf(id)>=0||seen.length<FREE){{ if(seen.indexOf(id)<0){{seen.push(id);set(K+'-seen',seen);}} show(); }}
else {{ document.getElementById('pw-wall').hidden=false; }}
document.getElementById('pw-form').addEventListener('submit',function(e){{e.preventDefault();
 var v=h(document.getElementById('pw-u').value.trim().toLowerCase()+':'+document.getElementById('pw-p').value.trim());
 var m=document.getElementById('pw-msg');
 if(OK.indexOf(v)>=0){{set(K+'-sub',true);m.textContent='Signed in. Welcome back.';show();}}
 else if(BAD.indexOf(v)>=0){{m.textContent='This account has been suspended for sharing its pass code. Please contact the circulation desk.';}}
 else {{m.textContent='We do not recognise that reader name and pass code.';}}
}});
}})();</script>"""
