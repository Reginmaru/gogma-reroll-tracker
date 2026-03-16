# src/gogma_tracker/app.py
"""
Gogma Reroll Tracker — Very compact horizontal card layout
"""

import streamlit as st
import pandas as pd
import os
from pathlib import Path
import datetime

# ────────────────────────────────────────────────
# PAGE CONFIG (must be first!)
# ────────────────────────────────────────────────
st.set_page_config(page_title="Gogma Tracker", layout="wide")

# ────────────────────────────────────────────────
# CONFIG
# ────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parents[2]
base_path = BASE_DIR / "assets" / "icons"

MAX_ROLLS = 1000

SKILLS =  [
    "Doshaguma's Might",
    "Rey Dau's Voltage",
    "Uth Duna's Cover",
    "Nu Udra's Mutiny",
    "Rathalos's Flare",
    "Ebony Odogaron's Power",
    "Guardian Arkveld's Vitality",
    "Jin Dahaad's Revolt",
    "Gravios's Protection",
    "Blangonga's Spirit",
    "Gore Magala's Tyranny",
    "Arkveld's Hunger",
    "Xu Wu's Vigor",
    "Fulgur Anjanath's Will",
    "Mizutsune's Prowess",
    "Zoh Shia's Pulse",
    "Blossomdance Prayer",
    "Seregios's Tenacity",
    "Leviathan's Fury",
    "Flamefete Prayer",
    "Soul of the Dark Knight",
    "Omega Resonance",
    "Dreamspell Prayer",
    "Gogmapocalypse",
    "Lumenhymn Prayer"
]

group_skills = [
    "Scaling Prowess",           # Activates Master Mounter
    "Fortifying Pelt",           # Activates Fortify
    "Flexible Leathercraft",     # Activates Hunter Gatherer
    "Neopteron Alert",           # Activates Honey Hunter
    "Lord's Favor",              # Activates Inspiration
    "Guardian's Pulse",          # Activates Wylk Burst
    "Neopteron Camouflage",      # Activates Fleetfoot
    "Buttery Leathercraft",      # Activates Affinity Sliding
    "Scale Layering",            # Activates Adrenaline
    "Alluring Pelt",             # Activates Diversion
    "Lord's Fury",               # Activates Resuscitate
    "Guardian's Protection",     # Activates Ward of Wyveria
    "Imparted Wisdom",           # Activates Forager's Luck
    "Glory's Favor",             # Activates Luck
    "Festival Spirit",           # Activates Carving Master
    "Lord's Soul",               # Activates Guts (Tenacity)
    "Master of the Fist"         # Activates Satsui no Hado
]

WEAPON_TYPES = [
    "Great Sword", "Long Sword", "Sword & Shield", "Dual Blades",
    "Hammer", "Hunting Horn", "Lance", "Gunlance",
    "Switch Axe", "Charge Blade", "Insect Glaive",
    "Light Bowgun", "Heavy Bowgun", "Bow"
]

ELEMENTS = [
    "Fire", "Water", "Thunder", "Ice", "Dragon",
    "Poison", "Paralysis", "Sleep", "Blast", "Raw"
]

WEAPON_ICONS = {
    el: os.path.join(base_path, f"MHWilds-{el}blight_Icon.png" if el != "Raw" else os.path.join(base_path, "MHWilds-NonElement_Icon.png"))
    for el in ELEMENTS
}

# ────────────────────────────────────────────────
# SESSION STATE
# ────────────────────────────────────────────────
if "reset_skills" not in st.session_state:
    st.session_state.reset_skills = False
if "weapons" not in st.session_state:
    st.session_state.weapons = []

if "next_id" not in st.session_state:
    st.session_state.next_id = 1

if "global_skill1" not in st.session_state:
    st.session_state.global_skill1 = "—"

if "global_skill2" not in st.session_state:
    st.session_state.global_skill2 = "—"

if st.session_state.reset_skills:
    st.session_state.global_s1 = "—"
    st.session_state.global_s2 = "—"
    st.session_state.reset_skills = False

weapons = st.session_state.weapons
skill1 = st.session_state.global_skill1
skill2 = st.session_state.global_skill2

# ────────────────────────────────────────────────
# MAIN APP
# ────────────────────────────────────────────────

# ── TOP CONTROLS ────────────────────────────────────────────────────────
t1, top_left, top_right = st.columns([5, 2.5, 2.5], vertical_alignment="top")

with t1:
    st.title("🗡️ Gogma Artian Reroll Tracker")
    st.caption(f"max {MAX_ROLLS} rolls per weapon / type • session only")

    # ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
    # NEW: FULL USER GUIDE + EXPLANATION
    # ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
    with st.sidebar:
        # with st.expander("📖 How Gogma Rerolls Work + How to Use This App", expanded=False):
        st.markdown("""
### How Gogma Artian Rerolls Actually Work (Quick Explainer)

In Monster Hunter Wilds (TU4+), **Gogma Artian weapons** (upgraded from Rarity 8 Artian via Gogmazios parts like Tarred Devices) get random **Set Bonus Skill** + **Group Skill** combos when you **reroll** (Amend/Reset) those skills (Upgrading to gogma weapon counts as 1 reroll on element + weapon combo).

**Key mechanic most people miss:**
- The possible skill combos are **predetermined** in a hidden static table / sequence **per weapon type + element**.
- There's **one shared counter / seed** that advances **every time you perform any roll** (initial upgrade or reroll) on **any** weapon of that type/element.
- For every weapon + element combo - you need to go back to title screen without saving as you "record" you god rerolls. Then once you're happy with what you found run through all weapon + element combos rolls (aka at the end all your weapons have the desired skills) and only and only after you are happy with your weapons, save.

**Example**:
- You roll GS-Dragon → gets "Seregios's Tenacity + Lord's Soul"
- You roll GS-Fire → gets "Gore Magala's Tyranny + Lord's Fury" (next in sequence)
- You roll GS-Thunder → gets "Gogmapocalypse + Lord's Favor" (next again)
- You return to title screen without saving
- You go back and roll GS-Dragon and reroll once → You will roll the GS-Thunder "Gogmapocalypse + Lord's Favor" even though you skipped the GS-Fire.

You can't "go back", but you **can** hunt for god rolls by advancing the counter strategically across multiple weapons.

### How to Use This Tracker App

1. **Add the combos you care about**  
   Pick **Weapon** + **Element** → click **➕ Add**.  

2. **Roll in-game & log here**  
   - Reroll/upgrade in MH Wilds.  
   - Click the **Roll #X** button on the matching card. (Roll number on this doesn't actually matter as you are saving the roll count on the table)
   - App auto-resets skill pickers so you can change targets instantly.

3. **Track progress**  
   - Cards show current roll count (max 1000).  
   - Right table shows **only saved hits** (sorted by weapon + roll number).  
   - Spot path to take across your weapons!
                        
4. **Finding good rolls** (optional but recommended)  
   Pick **Skill 1** (main Set Bonus) and/or **Skill 2** (Group Skill).  
   → If either is selected when you click **Roll**, it auto-saves to the table.

5. **If you delete the weapon + element container with the red buttons, the save rerolls on the table for that combo will be removed** 
                      
### Pro Tips from Heavy Rerollers
- ** Alt + Tab **: quick switch between tabs to press Reroll.
- **Fastest method**: Reroll in-game → Alt + Tab, instantly click button here while skills renerating, Alt + Tab → reroll again.  
  The app "pre-rerolls" your selection while the game is loading/animating → saves ~1–2 seconds per roll.
  Quick note - if you are rerolling this way you will have to "save" the good rolls after you have already literalled rerolled, this will not ruin the count as long as you keep to it.

- **Session example**:  
  I rolled 9 different GS element combos for ~50 minutes → hit **2 absolute god rolls** (perfect stats + dream skills) and **~12 strong usable ones**.  
  Totally worth it.

**Whatever order you are counting, stick to it**.

Happy hunting & good luck on those god rolls — may your Tarred Devices be infinite 🗡️
        """)

with top_left:
    st.subheader("Add", divider="gray")
    
    st.selectbox("Weapon", WEAPON_TYPES, key="new_type")
    st.selectbox("Element", ELEMENTS, key="new_elem")
    
    if st.button("➕ Add", type="primary"):
        typ = st.session_state.new_type
        elem = st.session_state.new_elem
        
        # Check if this exact type + element already exists
        exists = any(
            w["type"] == typ and w["element"] == elem
            for w in weapons
        )
        
        if exists:
            st.warning(f"**{typ} – {elem}** is already being tracked.")
            st.toast("Duplicate weapon type + element combination", icon="⚠️")
        else:
            weapons.append({
                "id": st.session_state.next_id,
                "type": typ,
                "element": elem,
                "label": f"{typ}",           # you can also do f"{typ} ({elem})"
                "current_count": 0,
                "snapshots": []
            })
            st.session_state.next_id += 1
            st.success(f"Added **{typ} – {elem}**")
            st.rerun()

with top_right:
    st.subheader("Skills", divider="gray")
    s1 = st.selectbox("Skill 1", ["—"] + SKILLS, key="global_s1")
    st.session_state.global_skill1 = s1 if s1 != "—" else None
    s2 = st.selectbox("Skill 2", ["—"] + group_skills, key="global_s2")
    st.session_state.global_skill2 = s2 if s2 != "—" else None

# ── HORIZONTAL FLEX CARDS ───────────────────────────────────────────────
if weapons:
    st.subheader("Tracking", divider="gray")

    left_col, right_col = st.columns(2, gap="medium")

    with left_col:
        st.markdown("**Instances**")
        
        card_cols = st.columns(5, gap="small")
        
        for i, w in enumerate(weapons):
            with card_cols[i % 5]:
                with st.container(border=True, height=200):
                    st.markdown(f"**{w['label']}**")
                    
                    path = WEAPON_ICONS.get(w["element"])
                    if path and os.path.exists(path):
                        st.image(path, width=64)
                    else:
                        st.caption(w["element"])

                    # ── Roll button ───────────────────────────────────────
                    limit = w["current_count"] >= MAX_ROLLS
                    button_l, col_delete = st.columns([7, 3])

                    with col_delete:
                        if st.button("🗑", key=f"del_{w['id']}", help="Remove this weapon", width="content", type="primary"):
                            st.session_state.weapons = [ww for ww in st.session_state.weapons if ww["id"] != w["id"]]
                            st.rerun()

                    with button_l:
                        btn_label = f"Roll #{w['current_count'] + 1}"
                        if limit:
                            btn_label = f"✓ {w['current_count']} (max)"
                        
                        if st.button(
                            btn_label,
                            disabled=limit,
                            key=f"inc_{w['id']}",
                            width="content",
                            type="secondary" if not limit else "primary"
                        ):
                            w["current_count"] += 1
                            
                            if skill1 or skill2:
                                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                snapshot = {
                                    "weapon_label": w["label"] + " - " + w["element"],
                                    "rolls": w["current_count"],
                                    "S1": skill1,
                                    "S2": skill2,
                                    "Time": now
                                }
                                w["snapshots"].append(snapshot)
                                st.session_state.reset_skills = True
                            st.rerun()

    with right_col:
        st.markdown("**Saved Results**")
        
        all_snaps = []
        for w in weapons:
            for s in w["snapshots"]:
                all_snaps.append({
                    "Weapon": s["weapon_label"],
                    "Rolls": s["rolls"],
                    "S1": s.get("S1", "—"),
                    "S2": s.get("S2", "—"),
                    "Time": s["Time"]
                })

        if all_snaps:
            df = pd.DataFrame(all_snaps).sort_values(["Weapon", "Rolls"]).reset_index(drop=True)
            st.dataframe(
                df,
                hide_index=True,
                width="content",
                column_config={
                    "Weapon": st.column_config.TextColumn(width="medium"),
                    "Rolls": st.column_config.NumberColumn(width="small"),
                    "S1": st.column_config.TextColumn(width="medium"),
                    "S2": st.column_config.TextColumn(width="medium"),
                    "Time": st.column_config.TextColumn(width="medium"),
                }
            )
            st.caption(f"Total saved: **{len(all_snaps)}**")
        else:
            st.info("No rolls saved yet.\nSelect skill(s) and click a weapon's button to start tracking.")

# ── RESET ───────────────────────────────────────────────────────────────
st.markdown("---")
if st.button("🗑️ Reset", type="secondary"):
    for k in ["weapons", "next_id", "global_skill1", "global_skill2"]:
        if k in st.session_state:
            del st.session_state[k]
    st.success("Cleared!")
    st.rerun()

st.caption("happy rerolling!")