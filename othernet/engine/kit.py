"""Small HTML building blocks shared by site modules.

Sites still style themselves. These helpers only produce plain markup.
"""
from .web import esc


def a(href, label, cls="", title=""):
    c = f' class="{cls}"' if cls else ""
    t = f' title="{esc(title)}"' if title else ""
    return f'<a href="{esc(href)}"{c}{t}>{esc(label)}</a>'


def table(headers, rows, cls="", raw=False, sortable=False, id_=""):
    """rows: list of lists. Cells are escaped unless raw=True (then trusted HTML)."""
    s = ' data-sortable="1"' if sortable else ""
    i = f' id="{id_}"' if id_ else ""
    h = "".join(f"<th>{esc(x)}</th>" for x in headers)
    body = []
    for r in rows:
        cells = "".join(f"<td>{c if raw else esc(c)}</td>" for c in r)
        body.append(f"<tr>{cells}</tr>")
    return f'<table class="{cls}"{s}{i}><thead><tr>{h}</tr></thead><tbody>{"".join(body)}</tbody></table>'


def dl(pairs, cls=""):
    """pairs: (label, html_value)."""
    return f'<dl class="{cls}">' + "".join(f"<dt>{esc(k)}</dt><dd>{v}</dd>" for k, v in pairs) + "</dl>"


def pager(base, page, pages, fmt="{base}page/{n}/", first=None, label="Page"):
    """Links to numbered pages. Page 1 lives at `first` (defaults to base)."""
    if pages <= 1:
        return ""
    first = first or base

    def href(n):
        return first if n == 1 else fmt.format(base=base, n=n)

    out = ['<nav class="pager">']
    if page > 1:
        out.append(f'<a href="{href(page - 1)}" rel="prev">&laquo; Prev</a>')
    for n in range(1, pages + 1):
        if n == page:
            out.append(f"<b>{n}</b>")
        elif n in (1, pages) or abs(n - page) <= 2:
            out.append(f'<a href="{href(n)}">{n}</a>')
        elif abs(n - page) == 3:
            out.append("<span>&hellip;</span>")
    if page < pages:
        out.append(f'<a href="{href(page + 1)}" rel="next">Next &raquo;</a>')
    out.append("</nav>")
    return " ".join(out)


def chunks(items, n):
    return [items[i:i + n] for i in range(0, len(items), n)] or [[]]


def img(site, path, svg, alt, cls="", width=None):
    """Write an SVG under the site and return an <img> tag for it."""
    site.write(path, svg)
    w = f' width="{width}"' if width else ""
    c = f' class="{cls}"' if cls else ""
    return f'<img src="{esc(path)}" alt="{esc(alt)}"{c}{w} loading="lazy">'


def paras(ps):
    return "".join(f"<p>{esc(p)}</p>" for p in ps)


SORTABLE_JS = """
<script>
document.querySelectorAll('table[data-sortable] th').forEach(function(th, i){
  th.style.cursor='pointer'; th.title='Sort';
  th.addEventListener('click', function(){
    var table=th.closest('table'), tb=table.tBodies[0], idx=Array.prototype.indexOf.call(th.parentNode.children, th);
    var rows=Array.prototype.slice.call(tb.rows), asc=th.dataset.dir!=='asc'; th.dataset.dir=asc?'asc':'desc';
    rows.sort(function(a,b){
      var x=a.cells[idx].innerText.replace(/[,%]/g,''), y=b.cells[idx].innerText.replace(/[,%]/g,'');
      var nx=parseFloat(x), ny=parseFloat(y);
      var r=(!isNaN(nx)&&!isNaN(ny))?nx-ny:x.localeCompare(y); return asc?r:-r;});
    rows.forEach(function(r){tb.appendChild(r);});
  });
});
</script>"""

TABS_JS = """
<script>
document.querySelectorAll('[data-tabs]').forEach(function(box){
  var btns=box.querySelectorAll('[data-tab]'), panes=box.querySelectorAll('[data-pane]');
  btns.forEach(function(b){ b.addEventListener('click', function(e){ e.preventDefault();
    btns.forEach(function(x){x.classList.remove('on')}); b.classList.add('on');
    panes.forEach(function(p){ p.hidden = p.dataset.pane !== b.dataset.tab; });
  });});
});
</script>"""


def tabs(items, active=0):
    """items: list of (label, html). Needs TABS_JS on the page."""
    btns = "".join(f'<a href="#" data-tab="t{i}" class="{"on" if i == active else ""}">{esc(lab)}</a>'
                   for i, (lab, _) in enumerate(items))
    panes = "".join(f'<div data-pane="t{i}"{"" if i == active else " hidden"}>{h}</div>'
                    for i, (_, h) in enumerate(items))
    return f'<div class="tabs" data-tabs><div class="tabbar">{btns}</div>{panes}</div>'


COOKIE_WALL_JS = """
<div id="cw" style="position:fixed;inset:0;background:rgba(0,0,0,.55);display:none;z-index:999;align-items:center;justify-content:center">
 <div style="background:#fff;color:#222;max-width:420px;padding:22px;border-radius:8px;font:15px/1.4 system-ui,sans-serif">
  <h3 style="margin-top:0">__TITLE__</h3><p>__TEXT__</p>
  <button id="cw-yes" style="padding:8px 14px">__YES__</button> <button id="cw-no" style="padding:8px 14px">__NO__</button>
 </div></div>
<script>(function(){var k='cw-__KEY__';var ok=null;try{ok=localStorage.getItem(k)}catch(e){}
var el=document.getElementById('cw'); if(!ok){el.style.display='flex';}
function close(v){try{localStorage.setItem(k,v)}catch(e){} el.style.display='none';}
document.getElementById('cw-yes').onclick=function(){close('yes')};
document.getElementById('cw-no').onclick=function(){close('no')};})();</script>"""


def cookie_wall(key, title="We use crumbs", text="This site keeps small crumbs on your loom to "
                "remember you. Is that all right?", yes="Accept crumbs", no="Only the necessary"):
    return (COOKIE_WALL_JS.replace("__KEY__", key).replace("__TITLE__", esc(title))
            .replace("__TEXT__", esc(text)).replace("__YES__", esc(yes)).replace("__NO__", esc(no)))
