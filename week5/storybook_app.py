
import json
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="AI Storybook", layout="wide")
st.title("AI Multimodal Storybook: Pip Finds a Daycare")
st.caption("Generated with GPT-4o (story), SDXL (images) and Bark (narration)")

story = json.loads(Path("story.json").read_text()) if Path("story.json").exists() else {"scenes": []}
titles = {s["id"]: s.get("title", "") for s in story.get("scenes", [])}

for i in range(1, 4):
    st.subheader(f"Scene {i}: {titles.get(i, '')}")
    col1, col2 = st.columns([1, 1])
    with col1:
        img_path = f"scene{i}_image.png"
        if Path(img_path).exists():
            st.image(img_path, use_container_width=True)
        else:
            st.warning(f"scene{i}_image.png not found")
    with col2:
        audio_path = f"scene{i}_audio.wav"
        if Path(audio_path).exists():
            st.audio(audio_path)
        else:
            st.warning(f"scene{i}_audio.wav not found")
    st.divider()
