from pathlib import Path

ROOT = Path('.')
main_path = ROOT / 'src' / 'main.js'
style_path = ROOT / 'src' / 'style.css'
html_path = ROOT / 'index.html'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    count = text.count(old)
    if count != 1:
        print(f'Patch mismatch: {label}; found {count}. Nearby source:')
        for i, line in enumerate(text.splitlines(), 1):
            if any(term in line for term in ('roadMaterial', 'mapRoads.push', 'yellowLine', 'isRoadSurface', 'mobile-look', 'pointerup')):
                print(f'{i}: {line[:500]}')
        raise SystemExit(f'Patch stopped: expected one match for {label}, found {count}')
    return text.replace(old, new, 1)


main = main_path.read_text(encoding='utf-8')
replacements = [
    ("addBox(7,.018,.16,mats.line,x,.015,center-5.4,scene,false);", "addBox(7,.018,.16,mats.line,x,-.045,center-5.4,scene,false);", "east-west lane marking 1"),
    ("addBox(7,.018,.16,mats.line,x,.015,center+5.4,scene,false);", "addBox(7,.018,.16,mats.line,x,-.045,center+5.4,scene,false);", "east-west lane marking 2"),
    ("addBox(len,.022,.2,mats.yellowLine,0,.02,center-.12,scene,false);", "addBox(len,.022,.2,mats.yellowLine,0,-.04,center-.12,scene,false);", "east-west center line 1"),
    ("addBox(len,.022,.2,mats.yellowLine,0,.02,center+.12,scene,false);", "addBox(len,.022,.2,mats.yellowLine,0,-.04,center+.12,scene,false);", "east-west center line 2"),
    ("const m = addGround(w, len, roadMaterial, center, 0); m.position.y = -0.05; mapRoads.push({x:center,z:0,w,d:len});", "const m = addGround(w, len, roadMaterial, center, 0); m.position.y = -0.035; mapRoads.push({x:center,z:0,w,d:len});", "north-south road height"),
    ("addBox(.16,.018,7,mats.line,center-5.4,.015,z,scene,false);", "addBox(.16,.018,7,mats.line,center-5.4,-.025,z,scene,false);", "north-south lane marking 1"),
    ("addBox(.16,.018,7,mats.line,center+5.4,.015,z,scene,false);", "addBox(.16,.018,7,mats.line,center+5.4,-.025,z,scene,false);", "north-south lane marking 2"),
    ("addBox(.2,.022,len,mats.yellowLine,center-.12,.02,0,scene,false);", "addBox(.2,.022,len,mats.yellowLine,center-.12,-.02,0,scene,false);", "north-south center line 1"),
    ("addBox(.2,.022,len,mats.yellowLine,center+.12,.02,0,scene,false);", "addBox(.2,.022,len,mats.yellowLine,center+.12,-.02,0,scene,false);", "north-south center line 2"),
    ("addBox(1.3,.025,5.8,mats.line,cross+i*1.9,.025,v-7,scene,false);", "addBox(1.3,.025,5.8,mats.line,cross+i*1.9,-.037,v-7,scene,false);", "horizontal crosswalk"),
    ("addBox(5.8,.025,1.3,mats.line,v-7,.025,cross+i*1.9,scene,false);", "addBox(5.8,.025,1.3,mats.line,v-7,-.017,cross+i*1.9,scene,false);", "vertical crosswalk"),
    ("function isRoadSurface(x,z,buffer=11.5){", "function isRoadSurface(x,z,buffer=14.5){", "tree road exclusion"),
]
for old, new, label in replacements:
    main = replace_once(main, old, new, label)

main = replace_once(main,
    "$('mobile-look').addEventListener('pointerdown',e=>{e.preventDefault();toast('Проводи пальцем по свободной части экрана, чтобы вращать камеру');});",
    "$('mobile-look').addEventListener('pointerdown',e=>{e.preventDefault();toast('Проводи пальцем по свободной части экрана, чтобы вращать камеру');});\n"
    "$('mobile-map').addEventListener('pointerdown',e=>{e.preventDefault();if(started&&!dead&&!paused){$('map-screen').classList.remove('hidden');paused=true;drawMap($('bigmap'),true);}});\n"
    "$('mobile-pause').addEventListener('pointerdown',e=>{e.preventDefault();if(!started||dead)return;paused=!paused;$('pause-screen').classList.toggle('hidden',!paused);});",
    "mobile map/pause handlers")
main = replace_once(main,
    "renderer.domElement.addEventListener('pointerup',e=>{if(touchLook&&e.pointerId===touchLook.id)touchLook=null;});",
    "renderer.domElement.addEventListener('pointerup',e=>{if(touchLook&&e.pointerId===touchLook.id)touchLook=null;});\nrenderer.domElement.addEventListener('pointercancel',e=>{if(touchLook&&e.pointerId===touchLook.id)touchLook=null;});",
    "touch camera cancel")
main_path.write_text(main, encoding='utf-8')

html = html_path.read_text(encoding='utf-8')
if 'id="mobile-map"' not in html:
    html = replace_once(html,
        '<div id="mobile-controls" class="mobile-controls">',
        '<div id="mobile-controls" class="mobile-controls">\n      <div class="mobile-top-actions"><button id="mobile-map" class="mobile-top-btn">КАРТА</button><button id="mobile-pause" class="mobile-top-btn">Ⅱ</button></div>',
        'mobile top buttons')
html = html.replace('id="mobile-jump" class="mobile-btn"', 'id="mobile-jump" class="mobile-btn jump-btn"')
html = html.replace('id="mobile-run" class="mobile-btn"', 'id="mobile-run" class="mobile-btn run-btn"')
html = html.replace('WASD — движение&nbsp; • &nbsp;F — транспорт&nbsp; • &nbsp;M — карта', 'ДЖОЙСТИК — движение&nbsp; • &nbsp;ПРАВАЯ ЧАСТЬ — камера')
html_path.write_text(html, encoding='utf-8')

style = style_path.read_text(encoding='utf-8')
marker = '/* Mobile controls: separated touch targets, no overlap with the HUD. */'
if marker not in style:
    style += '''
/* Mobile controls: separated touch targets, no overlap with the HUD. */
.mobile-top-actions{position:absolute;right:12px;top:76px;display:flex;gap:8px;pointer-events:auto}
.mobile-top-btn{min-width:54px;height:38px;padding:0 12px;border:1px solid #ffffff70;border-radius:12px;background:rgba(8,17,24,.78);color:#fff;font-size:10px;font-weight:900;letter-spacing:1px;backdrop-filter:blur(8px);touch-action:none}
.mobile-top-btn:active{background:#e9b45c;color:#111}
.jump-btn{right:0;bottom:0}
.run-btn{right:82px;bottom:12px}
.brake-btn{right:82px!important;bottom:88px!important}
@media(max-width:760px){
  .bottom-left{left:10px;bottom:164px;gap:5px}
  .map-wrap{width:66px;height:66px}
  .map-label{font-size:6px;bottom:5px;letter-spacing:1px}
  .player-bars{width:104px;padding:6px 7px}
  .joystick{left:18px;bottom:18px;width:126px;height:126px}
  .stick{width:54px;height:54px;margin:-27px}
  .mobile-actions{right:12px;bottom:16px;width:174px;height:196px}
  .mobile-btn{width:56px;height:56px;font-size:7px}
  .attack-btn{width:66px;height:66px;right:0;top:48px}
  .car-btn{width:58px;height:58px;right:76px;top:0}
  .look-btn{width:46px;height:46px;right:78px;top:82px}
  .run-btn{right:76px;bottom:8px}
  .brake-btn{right:76px!important;bottom:82px!important}
  .jump-btn{right:0;bottom:0}
  .mobile-top-actions{top:72px;right:10px}
}
@media(max-width:380px){
  .mobile-actions{right:8px;transform:scale(.92);transform-origin:bottom right}
  .joystick{left:12px;transform:scale(.94);transform-origin:bottom left}
  .bottom-left{bottom:150px}
  .player-bars{width:92px}
}
'''
    style_path.write_text(style, encoding='utf-8')
print('Applied road and mobile-control fixes.')
