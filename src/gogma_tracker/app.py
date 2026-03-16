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
# ── TOP CONTROLS ────────────────────────────────────────────────────────
t1, top_left, top_right = st.columns([5, 2.5, 2.5], vertical_alignment="top")

with t1:
    st.title("")
    st.set_page_config(page_title="Gogma Tracker", layout="wide")
    st.title("🗡️ Gogma Artian Reroll Tracker")
    st.caption(f"max {MAX_ROLLS} rolls per weapon / type • session only")

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
            st.warning("")
            # Only add if it doesn't exist
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
# ── MAIN CONTENT: CARDS + TABLE SIDE BY SIDE ────────────────────────────────
if weapons:
    st.subheader("Tracking", divider="gray")

    # Create two equal-width columns
    left_col, right_col = st.columns(2, gap="medium")

    with left_col:
        st.markdown("**Instances**")
        
        # You can keep 5 cards per row inside the left column
        card_cols = st.columns(5, gap="small")
        
        for i, w in enumerate(weapons):
            with card_cols[i % 5]:
                with st.container(border=True, height=200):  # slightly taller to fit delete
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
                        if st.button("🗑", key=f"del_{w['id']}", help="Remove this weapon", width="content", type = "primary"):
                            # Remove this weapon from the list
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
                                # reset selected skills
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