# src/gogma_tracker/app.py
"""
Gogma Reroll Tracker — Very compact horizontal card layout + Path table
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

SKILLS = [
    "Doshaguma's Might", "Rey Dau's Voltage", "Uth Duna's Cover", "Nu Udra's Mutiny",
    "Rathalos's Flare", "Ebony Odogaron's Power", "Guardian Arkveld's Vitality",
    "Jin Dahaad's Revolt", "Gravios's Protection", "Blangonga's Spirit",
    "Gore Magala's Tyranny", "Arkveld's Hunger", "Xu Wu's Vigor",
    "Fulgur Anjanath's Will", "Mizutsune's Prowess", "Zoh Shia's Pulse",
    "Blossomdance Prayer", "Seregios's Tenacity", "Leviathan's Fury",
    "Flamefete Prayer", "Soul of the Dark Knight", "Omega Resonance",
    "Dreamspell Prayer", "Gogmapocalypse", "Lumenhymn Prayer"
]

group_skills = [
    "Scaling Prowess", "Fortifying Pelt", "Flexible Leathercraft", "Neopteron Alert",
    "Lord's Favor", "Guardian's Pulse", "Neopteron Camouflage", "Buttery Leathercraft",
    "Scale Layering", "Alluring Pelt", "Lord's Fury", "Guardian's Protection",
    "Imparted Wisdom", "Glory's Favor", "Festival Spirit", "Lord's Soul",
    "Master of the Fist"
]

WEAPON_TYPES = [
    "Great Sword", "Long Sword", "Sword & Shield", "Dual Blades",
    "Hammer", "Hunting Horn", "Lance", "Gunlance",
    "Switch Axe", "Charge Blade", "Insect Glaive",
    "Light Bowgun", "Heavy Bowgun", "Bow"
]

ELEMENTS = ["Fire", "Water", "Thunder", "Ice", "Dragon", "Poison", "Paralysis", "Sleep", "Blast", "Raw"]

WEAPON_ICONS = {
    el: os.path.join(base_path, f"MHWilds-{el}blight_Icon.png" if el != "Raw" else os.path.join(base_path, "MHWilds-NonElement_Icon.png"))
    for el in ELEMENTS
}

# ────────────────────────────────────────────────
# SESSION STATE INIT
# ────────────────────────────────────────────────
if "weapons" not in st.session_state:
    st.session_state.weapons = []
if "next_id" not in st.session_state:
    st.session_state.next_id = 1
if "global_skill1" not in st.session_state:
    st.session_state.global_skill1 = "—"
if "global_skill2" not in st.session_state:
    st.session_state.global_skill2 = "—"
if "selected_paths" not in st.session_state:
    st.session_state.selected_paths = set()   # will store tuple keys (Weapon, Rolls, Time)

# Reset helper
if "reset_skills" in st.session_state and st.session_state.reset_skills:
    st.session_state.global_skill1 = "—"
    st.session_state.global_skill2 = "—"
    st.session_state.reset_skills = False

weapons = st.session_state.weapons
skill1 = st.session_state.global_skill1 if st.session_state.global_skill1 != "—" else None
skill2 = st.session_state.global_skill2 if st.session_state.global_skill2 != "—" else None

# ────────────────────────────────────────────────
# MAIN APP
# ────────────────────────────────────────────────

t1, top_left, top_right = st.columns([5, 2.5, 2.5], vertical_alignment="top")

with t1:
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
        exists = any(w["type"] == typ and w["element"] == elem for w in weapons)
        
        if exists:
            st.warning(f"**{typ} – {elem}** is already being tracked.")
            st.toast("Duplicate weapon type + element combination", icon="⚠️")
        else:
            weapons.append({
                "id": st.session_state.next_id,
                "type": typ,
                "element": elem,
                "label": f"{typ}",
                "current_count": 0,
                "snapshots": []
            })
            st.session_state.next_id += 1
            st.success(f"Added **{typ} – {elem}**")
            st.rerun()

with top_right:
    st.subheader("Skills", divider="gray")
    s1 = st.selectbox("Skill 1", ["—"] + SKILLS, key="global_s1")
    st.session_state.global_skill1 = s1
    s2 = st.selectbox("Skill 2", ["—"] + group_skills, key="global_s2")
    st.session_state.global_skill2 = s2

# ── MAIN CONTENT ────────────────────────────────────────────────────────────
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

                    button_l, col_delete = st.columns([7, 3])
                    with col_delete:
                        if st.button("🗑", key=f"del_{w['id']}", help="Remove this weapon", type="primary"):
                            st.session_state.weapons = [ww for ww in weapons if ww["id"] != w["id"]]
                            # Also clean up selections
                            to_remove = {k for k in st.session_state.selected_paths if k[0].startswith(w['label'])}
                            st.session_state.selected_paths -= to_remove
                            st.rerun()

                    with button_l:
                        limit = w["current_count"] >= MAX_ROLLS
                        btn_label = f"Roll #{w['current_count'] + 1}" if not limit else f"✓ {w['current_count']} (max)"
                        if st.button(
                            btn_label,
                            disabled=limit,
                            key=f"inc_{w['id']}",
                            type="secondary" if not limit else "primary"
                        ):
                            w["current_count"] += 1
                            if skill1 or skill2:
                                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                snapshot = {
                                    "weapon_label": f"{w['label']} - {w['element']}",
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

            # Create unique key for each row (used for checkbox persistence)
            df["key"] = df.apply(lambda row: (row["Weapon"], row["Rolls"], row["Time"]), axis=1)

            # Checkbox column
            edited_df = st.data_editor(
                df,
                column_config={
                    "✓": st.column_config.CheckboxColumn(
                        "✓",
                        default=False,
                        required=False
                    ),
                    "Weapon": st.column_config.TextColumn(width="medium"),
                    "Rolls": st.column_config.NumberColumn(width="small"),
                    "S1": st.column_config.TextColumn(width="medium"),
                    "S2": st.column_config.TextColumn(width="medium"),
                    "Time": st.column_config.TextColumn(width="medium"),
                },
                hide_index=True,
                num_rows="fixed",
                key="saved_results_editor",
                column_order=["✓", "Weapon", "Rolls", "S1", "S2", "Time"]
            )

            # Sync selected keys to session state
            selected = set(
                row["key"]
                for _, row in edited_df.iterrows()
                if row["✓"]
            )
            st.session_state.selected_paths = selected

            st.caption(f"Total saved: **{len(df)}** • Path: **{len(selected)}**")

            # ── PATH TABLE ───────────────────────────────────────────────
            if selected:
                st.subheader("Path", divider="orange")
                path_df = df[df["key"].isin(selected)].drop(columns=["key", "✓"]).reset_index(drop=True)
                st.dataframe(
                    path_df,
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "Weapon": st.column_config.TextColumn(width="medium"),
                        "Rolls": st.column_config.NumberColumn(width="small"),
                        "S1": st.column_config.TextColumn(width="medium"),
                        "S2": st.column_config.TextColumn(width="medium"),
                        "Time": st.column_config.TextColumn(width="medium"),
                    }
                )
            else:
                st.info("Tick rows in the table above to build your **Path**")

        else:
            st.info("No rolls saved yet.\nSelect skill(s) and click a weapon's button to start tracking.")

# ── RESET ───────────────────────────────────────────────────────────────
st.markdown("---")
if st.button("🗑️ Reset Everything", type="secondary"):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.success("Session cleared!")
    st.rerun()

st.caption("happy rerolling!")