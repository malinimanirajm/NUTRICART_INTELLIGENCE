import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# --- Page Config ---
st.set_page_config(page_title="NutriCart Intelligence", page_icon="🍎", layout="wide")

# --- UI Styling ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .coach-box { 
        background-color: #e3f2fd; 
        border-left: 5px solid #1976d2; 
        padding: 20px; 
        border-radius: 10px;
        margin: 15px 0;
    }
    .chart-container {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    </style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "data" not in st.session_state:
    st.session_state.data = None

st.title("🍎 NutriCart Intelligence")
st.subheader("Agentic Nutrition Dashboard | V2.1 (Adaptive)")

# --- Sidebar ---
with st.sidebar:
    st.header("🛠️ Audit & Monitoring")
    thread_id = st.text_input("Session ID", value="malini_dev_01")
    show_raw = st.toggle("Show Raw Trace", value=False)
    if st.button("Clear History"):
        st.session_state.data = None
        st.rerun()

# --- Chat Interface ---
prompt = st.chat_input("Ask about products or compare your consumption...")

if prompt:
    with st.status("Agent Executing Nodes...", expanded=show_raw) as status:
        st.write("🔍 Extracting Intent & Entities...")
        try:
            response = requests.post(
                "http://127.0.0.1:8000/ask",
                json={"question": prompt, "thread_id": thread_id}
            )
            # Store data in session state so buttons don't wipe the screen
            st.session_state.data = response.json()
            st.write(f"🧬 Querying Weaviate...")
            st.write("🧠 Reasoning via Coaching Node...")
            status.update(label="Response Generated!", state="complete", expanded=False)
        except Exception as e:
            status.update(label="Execution Failed", state="error")
            st.error(f"Backend Connection Error: {e}")

# --- DISPLAY LOGIC (Uses Session State) ---
if st.session_state.data:
    data = st.session_state.data

    # 1. Display the Primary Answer
    st.markdown(data.get("elaborated_answer", "No answer generated."))

    # 2. Dynamic Visualizations (Graphs)
    matches = data.get("product_matches", [])
    if matches:
        df = pd.DataFrame(matches)
        st.divider()
        st.subheader("📊 Consumption Analytics")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig_prot = px.bar(df, x="product_name", y="protein", title="Protein by Item", color_discrete_sequence=['#4CAF50'])
            st.plotly_chart(fig_prot, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig_eff = px.scatter(df, x="added_sugar", y="protein", text="product_name", title="Efficiency: Sugar vs Protein")
            fig_eff.update_traces(textposition='top center')
            st.plotly_chart(fig_eff, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # 3. Coach's Insight Box + Feedback Loop
    recs = data.get("recommendations", [])
    if recs:
        st.markdown('<div class="coach-box">', unsafe_allow_html=True)
        st.markdown("### 💡 AI Coach's Rescue Plan")
        st.write("I identified a nutritional gap. Add these high-efficiency items to your next cart:")
        
        rec_cols = st.columns(len(recs))
        for i, r in enumerate(recs):
            with rec_cols[i]:
                st.metric(label=r['product_name'], value=f"{r['protein']}g Prot", delta=f"{r['added_sugar']}g Sugar", delta_color="inverse")
                
                # Feedback Buttons
                c1, c2 = st.columns(2)
                if c1.button("👍", key=f"up_{r['product_name']}"):
                    st.toast(f"Saved {r['product_name']} to favorites!")
                
                if c2.button("👎", key=f"down_{r['product_name']}"):
                    requests.post("http://127.0.0.1:8000/feedback", 
                                  json={"product": r['product_name'], "action": "dislike", "thread_id": thread_id})
                    st.error(f"Blacklisted {r['product_name']}.")
                    # Silently remove from local view until next refresh
                    st.session_state.data['recommendations'].pop(i)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # 4. Raw Data Expanders
    with st.expander("📝 View Full Audit Trail", expanded=False):
        st.json(data)

# --- Footer ---
st.divider()
st.caption(f"Trace ID: {thread_id} | Core: Gemini 2.0 Flash-Lite | DB: Weaviate Local")