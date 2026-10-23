"""Writes data.js from the list below: sizes and years are read from the files.
Edit PROJECTS here (titles, stories, groups, order), then run:  py tools/build_data.py"""
import json, os, subprocess, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets", "img")

# (id, title, category, one line, the story (panel), tools, [files]) -- the first file is the cover
PROJECTS = [
    ("emerald", "Emerald Ring", "3D Product", "A cut emerald in a worn silver band, lit low across an oak table.",
     "Made to be something mildly special for someone. Modelled and lit in Blender; the textures come from BlenderKit.",
     "Blender, BlenderKit", ["0979.png"]),
    ("ryder", "Ryder", "Character", "A post-apocalyptic scavenger, drawn years ago and finally built in 3D.",
     "Ryder started as a drawing from a long time ago. This is him in 3D: goggles, a scarf that never sits still, and a turnaround to show him off.",
     "Blender", ["rotation.mp4", "BestCharacter Desgin44.jpg", "BestCharacter Desgin44phone.jpg", "Test Pre design.mp4"]),
    ("metal", "Metal Sonic", "Character", "Built entirely by me, in a cel-shaded look.",
     "Everything here, model, shading and the title card, was made from scratch in Blender. The goal was the full character in a clean cel-shaded style.",
     "Blender", ["part 3.mp4", "Gem metal.mp4"]),
    ("speed", "Ryder's Ride", "3D Scene", "The vehicle I designed for Ryder, flat out.",
     "The shape is inspired by the game Surge, where you drive sector to sector and it keeps getting faster. Everything is made in Blender with no outside textures. The ground blasting past is just noise textures stretched out, blue, yellow and red, layered on a bluish-black plane.",
     "Blender", ["neon racecarHD.jpg", "lopite.mp4"]),
    ("rewrite", "Rewrite", "Animation", "Janky, wild and still playful, like a 90s rubber-hose cartoon.",
     "Built 100% in Blender, after the Rewrite character from the game. What drew me in is how the animation feels: not balanced, a bit crazy, but smooth and relatable. He can swap into other characters; Lord X is the one other form I've made so far.",
     "Blender", ["rewrite.mp4", "567.mp4", "hemmock.mp4", "Lord X.mp4", "XX (1) (1).jpg"]),
    ("malware", "Malware", "Character", "A female character made in response to Rewrite.",
     "A static model for now; the eyes don't move yet. The short clip is voiced by my girlfriend.",
     "Blender", ["SaYY.mp4"]),
    ("rey", "Rey", "Character", "The red guy with glasses, made for a comic I haven't finished.",
     "Rey is an older character of mine; the E is the one with a flick on top, moving forward. A few months ago I started a comic with him. It isn't finished yet.",
     "Blender", ["0000-0200.mp4", "you.jpg", "khekee.jpg", "jskfnjf.png"]),
    ("night", "Night Run", "Illustration", "My cel-shaded character on a silhouette city.",
     "Building a whole 3D city wasn't going to happen, so I did what Vector and Shadow Fight did: silhouettes for the background. That leaves the detail for the character and still sells the idea.",
     "Blender", ["Refined.jpg"]),
    ("noir", "NOIR Technologies", "Branding", "Identity, social posts and motion for a software studio.",
     "Motion graphics, video editing and Blender work together.",
     "Blender, Figma, video editing", ["v4.mp4", "1000582694.png", "Frame 656.png", "Frame 658.png", "Frame 660.png", "Frame 648.png", "better.mp4", "1000582695.png", "ChatGPT Image Sep 16, 2026, 02_32_03 PM.png"]),
    ("breeze", "Breeze", "Motion", "Animation and a light edit for Breeze.",
     "I animated the shop scene and did the small edit around it.",
     "Blender, video editing", ["biopass-ad.mp4"]),
    ("hardsurface", "Hardsurface", "Web Design", "A place to build 3D models and show them online.",
     "Made for my lecturer: a space where people design their 3D models and anyone can view them online. We planned to build it together but went our separate ways, so only the front page exists. The wooden planet is a Blender model of mine; the space, the light beam and the glare were put together in Figma.",
     "Figma, Blender", ["MacBook Pro 14_ (1).jpg", "Klean!!!.jpg"]),
    ("folio", "Portfolio, Click", "Web Design", "An attempt at a more dynamic portfolio.",
     "Designed in Figma, with the hollow black face made in Blender. No reference, straight from my head. It got too complex for me at the time, so it stopped here.",
     "Figma, Blender", ["MacBook Pro 14_ - 1 (3).png"]),
    ("chalce", "CHALCE", "Web Design", "Another portfolio attempt, with the emerald up front.",
     "A second go at a portfolio. The glass was shot for it too: I was chasing caustics in Cycles, but my laptop couldn't get there, so I kept the shot as it was.",
     "Figma, Blender", ["MacBook Pro 14_ - 12 (1).png", "metallic.png", "i878u.png"]),
    ("music", "Music Note", "Branding", "A button from an older portfolio.",
     "That portfolio paired an image with each section. This was the graphic for the music section, and the note also became its play button. The background track was C418's Aria Math.",
     "Blender", ["note1.jpg"]),
    ("yale", "Yale School of Art", "Web Design", "A loud, patterned redesign, for a 30-day design challenge.",
     "One of my entries for Gary Simon's 30-day design challenge on LinkedIn.",
     "Figma", ["MacBook Pro 14_ - 17.png", "Frame 348 (1).png"]),
    ("everyflaw", "Every Flaw, Seen.", "Web Design", "Built from the challenge's own Figma brief, desktop and mobile.",
     "A 30-day design challenge (Gary Simon): we had to make something from the Figma project he shared.",
     "Figma", ["MacBook Pro 14_ - 14.png", "iPhone 16 & 17 Pro Max - 1.png"]),
    ("assurance", "Assurance", "Web Design", "BH's famously plain website, redesigned.",
     "A 30-day design challenge entry: could I make one of the plainest sites online look good? Desktop and mobile.",
     "Figma", ["MacBook Pro 14_ - 10 (2).png", "iPhone 16 - 4.png"]),
    ("itemtogo", "Item To Go", "App Design", "An app redesign that keeps the brand's feel.",
     "I saw a redesign of this app that got the UX right but lost the brand: nothing popped. This is my attempt to keep their look and vibe.",
     "Figma", ["Home (1).jpg"]),
    ("smart", "Smart Home Brochure", "Print", "A brochure built in 3D.",
     "The brochure itself was made in Blender, with some real photos placed on planes, which gave more interesting results than a flat layout. I only finished this one page.",
     "Blender", ["PROPOSALD 2.jpg"]),
    ("lughole", "Lughole", "Motion", "The intro for an animated series with my friend.",
     "The plan: we talk about something interesting, I animate just our faces to our voices, plus a few random moments. Animation is slow, so that keeps it doable. So far only the intro exists.",
     "Blender", ["My Video-2.mp4"]),
    ("teddy", "Teddy", "3D Product", "A client job: a teddy copied from a reference, fur and all.",
     "Someone asked for a teddy matched exactly to a reference, with fur, animated across scenes: on a plane, on the beach. Back then I couldn't do all of it yet, so this render and the beach shot are what came out of it.",
     "Blender", ["VERSION 3.jpg", "pic 1.jpg"]),
    ("controllers", "Controllers", "3D Product", "A PlayStation pad from years ago, and the one on my desk.",
     "The white one was a PlayStation controller attempt from 3 or 4 years ago. The dark one is my current controller, close to the real thing, red and blue lights included.",
     "Blender", ["dez.png", "wew.png", "gamepad.mp4", "number 22222222.mp4", "keyboadddd.211jpg.jpg", "keyboadddd.111jpg.jpg", "keyboadddd.png", "shy-devilsss.jpg"]),
    ("squid", "Squidward's House", "3D Product", "Squidward's house, 100% Blender.", "", "Blender", ["squid3.jpg"]),
    ("piano", "Concert Grand", "3D Product", "A piano, made entirely in Blender.", "", "Blender", ["Composed.jpg"]),
    ("bottles", "Bottles", "3D Product", "A bottle my family actually had, modelled from scratch.",
     "Modelled from nothing in Blender. Only the pattern on the side comes from BlenderKit.",
     "Blender, BlenderKit", ["bottotol3.jpg", "bottotol2.jpg"]),
    ("cups", "Cups", "3D Product", "Old, simple, and the depth of field does a lot.", "", "Blender", ["cuos.jpg", "cup.jpg"]),
    ("rust", "Rusted Vessel", "Lookdev", "Gritty, rusted orange metal.", "Made following a tutorial.", "Blender", ["PBallwall2.jpg"]),
    ("materials", "Material Studies", "Lookdev", "Jade, wood and lacquer.", "", "Blender", ["PEBBLE2.jpg", "Orb.jpg", "Cooool.jpg"]),
    ("arches", "Arches", "3D Scene", "Three arches on a mirror floor.",
     "The sky is a stock photo (Freepik, I think); the floor is a low-roughness reflective plane. A colour ramp on the background is what made it start looking like an anime.",
     "Blender", ["Not anime.jpg", "back.jpg", "bigger a.jpg", "Houseeee.jpg"]),
    ("sunrise", "ThatNewGuy23", "3D Scene", "A knot in a field with the sun behind it.",
     "I was learning volumetrics. It came out good, so I kept it.",
     "Blender", ["blending3.jpg", "phonewallp2.jpg", "redfff.jpg"]),
    ("monolith", "Monolith", "3D Scene", "A tower in grass under a brown-to-blue sky.", "Just design.", "Blender", ["unlcuk.jpg", "raacer.jpg"]),
    ("redcube", "Red Cube", "3D Scene", "A red cube with bulging spheres and a blue torus.", "Just design.", "Blender", ["pUTY.jpg"]),
    ("cactus", "Cactus", "Illustration", "My first try at a toon shader.", "Made in Blender, straight from my head with no reference.", "Blender", ["chimp.jpg"]),
    ("gamejolt", "Game Jolt Friend", "Character", "Someone's Game Jolt design, built in 3D as a gift.", "They liked it. Simple as that.", "Blender", ["0001-0080.mp4"]),
    ("marks", "Marks", "Branding", "Logos and app icons.", "", "Blender", ["icon-light.jpg", "5050.jpg"]),
    ("flat", "Flat Studies", "Illustration", "Small flat pieces.", "", "Blender", ["iuihhyth.png", "jhjh.jpg", "qwfqwd.png", "blue.jpg"]),
    ("loops", "Short Loops", "Animation", "Little animations that loop.", "", "Blender", ["0001-0200 (2).mp4", "Pose1.mp4", "Skull face.mp4", "intro.mp4"]),
]
FEATURED = ["emerald", "ryder", "metal"]


def size(f):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                          "-of", "csv=p=0", os.path.join(IMG, f)], capture_output=True, text=True).stdout.strip()
    w, h = out.split("\n")[0].split(",")[:2]
    return int(w), int(h)


used, out = set(), []
for pid, title, cat, line, story, tools, files in PROJECTS:
    items = []
    for f in files:
        assert os.path.exists(os.path.join(IMG, f)), f
        used.add(f)
        w, h = size(f)
        items.append({"src": "assets/img/" + f, "thumb": "assets/thumbs/" + os.path.splitext(f)[0] + ".jpg",
                      "type": "video" if f.lower().endswith(".mp4") else "image", "w": w, "h": h})
    year = max(time.localtime(os.path.getmtime(os.path.join(IMG, f))).tm_year for f in files)
    out.append({"id": pid, "title": title, "cat": cat, "line": line, "story": story, "tools": tools, "year": year, "items": items})
left = sorted(set(os.listdir(IMG)) - used)
print("not shown:", left)
with open(os.path.join(ROOT, "data.js"), "w", encoding="utf-8") as fh:
    fh.write("// Made by tools/build_data.py -- edit the list there, not here.\n")
    fh.write("const FEATURED = " + json.dumps(FEATURED) + ";\n")
    fh.write("const PROJECTS = " + json.dumps(out, indent=1, ensure_ascii=False) + ";\n")
print(len(out), "projects,", len(used), "files")
