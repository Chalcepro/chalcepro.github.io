"""Writes data.js from the list below: sizes and years are read from the files.
Edit PROJECTS here (titles, groups, order), then run:  py tools/build_data.py"""
import json, os, subprocess, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets", "img")

# (id, title, category, one line, tools, [files]) -- the first file is the cover
PROJECTS = [
    ("emerald", "Emerald Ring", "3D Product", "A cut emerald in a worn silver band, lit low across an oak table.", "Blender, Cycles", ["0979.png"]),
    ("goggle", "Goggle Head", "Character", "An original mascot: aviator goggles, a scarf that never sits still, and a lot of attitude for a face with no mouth.", "Blender", ["rotation.mp4", "BestCharacter Desgin44.jpg", "BestCharacter Desgin44phone.jpg", "Test Pre design.mp4"]),
    ("metal", "Metal Sonic", "Character", "Fan model on a showroom plinth, with a chrome pass and a neon title card.", "Blender", ["part 3.mp4", "Gem metal.mp4"]),
    ("sonic", "Sonic, Rewrite", "Animation", "Low-poly Sonic in a Green Hill loop, then the Rewrite version of the same shot.", "Blender", ["rewrite.mp4", "567.mp4"]),
    ("hammock", "Hammock", "Animation", "Sonic doing nothing, beautifully.", "Blender", ["hemmock.mp4"]),
    ("sayy", "Pink", "Character", "A stylised hedgehog, posed and lit like a toy.", "Blender", ["SaYY.mp4"]),
    ("exe", ".EXE", "Illustration", "Lord X: a flat illustration and the animated title card built from it.", "Blender, Photoshop", ["Lord X.mp4", "XX (1) (1).jpg"]),
    ("agent", "Red Agent", "Character", "A one-colour stick agent, animated, then posed in stills.", "Blender", ["0000-0200.mp4", "you.jpg", "khekee.jpg", "jskfnjf.png"]),
    ("noir", "NOIR Technologies", "Branding", "Identity, social posts and motion for a software studio.", "Figma, Blender, After Effects", ["v4.mp4", "1000582694.png", "Frame 656.png", "Frame 658.png", "Frame 660.png", "Frame 648.png", "better.mp4", "1000582695.png", "ChatGPT Image Sep 16, 2026, 02_32_03 PM.png"]),
    ("biopass", "Biopass", "Motion", "Shop scene and edit for a product ad.", "Blender, Premiere", ["biopass-ad.mp4"]),
    ("controllers", "Controller Studies", "3D Product", "Pads and a keyboard, re-lit until the plastic read right.", "Blender, Cycles", ["keyboadddd.211jpg.jpg", "keyboadddd.111jpg.jpg", "dez.png", "wew.png", "gamepad.mp4", "number 22222222.mp4", "keyboadddd.png", "shy-devilsss.jpg"]),
    ("hardsurface", "Hardsurface", "Web Design", "Landing page for a 3D asset community.", "Figma, Blender", ["MacBook Pro 14_ (1).jpg"]),
    ("chalce", "CHALCE", "Web Design", "A luxury brand site where the product does the talking.", "Figma, Blender", ["MacBook Pro 14_ - 12 (1).png", "metallic.png"]),
    ("everyflaw", "Every Flaw, Seen.", "Web Design", "Inspection software, desktop and mobile.", "Figma", ["MacBook Pro 14_ - 14.png", "iPhone 16 & 17 Pro Max - 1.png"]),
    ("assurance", "Assurance", "Web Design", "A deliberately old-web investor page, desktop and mobile.", "Figma", ["MacBook Pro 14_ - 10 (2).png", "iPhone 16 - 4.png"]),
    ("yale", "Yale School of Art", "Web Design", "A loud, patterned redesign of the school's wiki.", "Figma", ["MacBook Pro 14_ - 17.png", "Frame 348 (1).png"]),
    ("folio", "Portfolio, Early", "Web Design", "An earlier version of this site.", "Figma", ["MacBook Pro 14_ - 1 (3).png"]),
    ("food", "Easy Pickup", "App Design", "Food ordering app, home screen.", "Figma", ["Home (1).jpg"]),
    ("smart", "Smart Home Brochure", "Print", "Tri-fold for a home automation company.", "Photoshop", ["PROPOSALD 2.jpg"]),
    ("sunrise", "ThatNewGuy23", "Branding", "Channel art: one sunrise, three crops.", "Blender", ["phonewallp2.jpg", "redfff.jpg", "blending3.jpg"]),
    ("lughole", "Lughole", "Motion", "Channel intro.", "After Effects", ["My Video-2.mp4"]),
    ("materials", "Material Studies", "Lookdev", "Copper, jade, wood and lacquer, one object at a time.", "Blender, Cycles", ["PBallwall2.jpg", "PEBBLE2.jpg", "Orb.jpg", "Klean!!!.jpg", "Cooool.jpg"]),
    ("arches", "Quiet Architecture", "3D Scene", "Arches, doorways and white rooms.", "Blender", ["Not anime.jpg", "back.jpg", "bigger a.jpg", "Houseeee.jpg"]),
    ("monolith", "Monolith", "3D Scene", "A slab in a field, then a slab in the dark.", "Blender", ["unlcuk.jpg", "raacer.jpg"]),
    ("speed", "Speed", "3D Scene", "Two vehicles, both late for something.", "Blender", ["neon racecarHD.jpg", "lopite.mp4"]),
    ("teddy", "Teddy", "3D Product", "Fur and a cold marble floor.", "Blender, Cycles", ["VERSION 3.jpg"]),
    ("piano", "Concert Grand", "3D Product", "Keys at a low angle.", "Blender", ["Composed.jpg"]),
    ("glass", "Glass on a Ledge", "3D Product", "Pressed glass, warm light.", "Blender, Cycles", ["i878u.png"]),
    ("beach", "Beach Ball", "3D Scene", "Sand, wind lines, one ball.", "Blender", ["pic 1.jpg"]),
    ("cups", "Cups", "3D Product", "Matte tumblers, then one cup drawn flat.", "Blender", ["cuos.jpg", "cup.jpg"]),
    ("bottles", "Bottles", "3D Product", "One bottle, two colourways.", "Blender", ["bottotol3.jpg", "bottotol2.jpg"]),
    ("squid", "Tiki House", "3D Product", "A pencil pot that is also a house.", "Blender", ["squid3.jpg"]),
    ("tread", "Tread", "3D Product", "Rubber and red bricks.", "Blender", ["pUTY.jpg"]),
    ("marks", "Marks", "Branding", "Logos and app icons.", "Illustrator, Blender", ["note1.jpg", "icon-light.jpg", "5050.jpg"]),
    ("night", "Night Run", "Illustration", "Rooftops after dark.", "Photoshop", ["Refined.jpg"]),
    ("flat", "Flat Studies", "Illustration", "Small flat pieces.", "Illustrator", ["chimp.jpg", "iuihhyth.png", "jhjh.jpg", "qwfqwd.png", "blue.jpg"]),
    ("loops", "Short Loops", "Animation", "Little animations that loop.", "Blender", ["0001-0080.mp4", "0001-0200 (2).mp4", "Pose1.mp4", "Skull face.mp4", "intro.mp4"]),
]
FEATURED = ["emerald", "goggle", "metal"]


def size(f):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                          "-of", "csv=p=0", os.path.join(IMG, f)], capture_output=True, text=True).stdout.strip()
    w, h = out.split("\n")[0].split(",")[:2]
    return int(w), int(h)


used, out = set(), []
for pid, title, cat, line, tools, files in PROJECTS:
    items = []
    for f in files:
        assert os.path.exists(os.path.join(IMG, f)), f
        used.add(f)
        w, h = size(f)
        items.append({"src": "assets/img/" + f, "thumb": "assets/thumbs/" + os.path.splitext(f)[0] + ".jpg",
                      "type": "video" if f.lower().endswith(".mp4") else "image", "w": w, "h": h})
    year = max(time.localtime(os.path.getmtime(os.path.join(IMG, f))).tm_year for f in files)
    out.append({"id": pid, "title": title, "cat": cat, "line": line, "tools": tools, "year": year, "items": items})
left = sorted(set(os.listdir(IMG)) - used)
print("not shown:", left)
with open(os.path.join(ROOT, "data.js"), "w", encoding="utf-8") as fh:
    fh.write("// Made by tools/build_data.py -- edit the list there, not here.\n")
    fh.write("const FEATURED = " + json.dumps(FEATURED) + ";\n")
    fh.write("const PROJECTS = " + json.dumps(out, indent=1, ensure_ascii=False) + ";\n")
print(len(out), "projects,", len(used), "files")
