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

st.title("🍎 NutriCart Intelligence")
st.subheader("Agentic Nutrition Dashboard | V2.1")

# --- Sidebar ---
with st.sidebar:
    st.header("🛠️ Audit & Monitoring")
    thread_id = st.text_input("Session ID", value="malini_dev_01")
    show_raw = st.toggle("Show Raw Trace", value=False)
    if st.button("Clear History"):
        st.rerun()

# --- Chat Interface ---
prompt = st.chat_input("Ask about products or compare your consumption...")

if prompt:
    # 1. Audit Trail Progress
    with st.status("Agent Executing Nodes...", expanded=show_raw) as status:
        st.write("🔍 Extracting Intent & Entities...")
        try:
            response = requests.post(
                "http://127.0.0.1:8000/ask",
                json={"question": prompt, "thread_id": thread_id}
            )
            data = response.json()
            st.write(f"🧬 Querying Weaviate (Mode: {data.get('mode')})...")
            st.write("🧮 Aggregating Nutrients...")
            st.write("🧠 Reasoning via Coaching Node...")
            status.update(label="Response Generated!", state="complete", expanded=False)
        except Exception as e:
            status.update(label="Execution Failed", state="error")
            st.error(f"Backend Connection Error: {e}")
            st.stop()

    # --- MAIN UI LAYOUT ---
    # 2. Display the Primary Answer
    st.markdown(data["elaborated_answer"])

    # 3. Dynamic Visualizations (Graphs)
    matches = data.get("product_matches", [])
    if matches:
        df = pd.DataFrame(matches)
        
        st.divider()
        st.subheader("📊 Consumption Analytics")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            # Bar Chart for Protein Comparison
            fig_prot = px.bar(
                df, x="product_name", y="protein", 
                title="Protein Content by Item",
                color_discrete_sequence=['#4CAF50']
            )
            st.plotly_chart(fig_prot, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            # Scatter Plot for Efficiency (Protein vs Sugar)
            fig_eff = px.scatter(
                df, x="added_sugar", y="protein", 
                text="product_name",
                title="Efficiency: Low Sugar vs High Protein",
                labels={"added_sugar": "Sugar (g)", "protein": "Protein (g)"}
            )
            fig_eff.update_traces(textposition='top center')
            st.plotly_chart(fig_eff, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # 4. Coach's Insight Box
    recs = data.get("recommendations", [])
    if recs:
        st.markdown('<div class="coach-box">', unsafe_allow_html=True)
        st.markdown("### 💡 AI Coach's Rescue Plan")
        st.write("I identified a nutritional gap. Add these high-efficiency items to your next cart:")
        
        rec_cols = st.columns(len(recs))
        for i, r in enumerate(recs):
            with rec_cols[i]:
                st.metric(
                    label=r['product_name'], 
                    value=f"{r['protein']}g Prot", 
                    delta=f"{r['added_sugar']}g Sugar",
                    delta_color="inverse"
                )
        st.markdown('</div>', unsafe_allow_html=True)

    # 5. Raw Data Expanders
    with st.expander("📝 View Full Audit Trail", expanded=False):
        st.json(data)

# --- Footer ---
st.divider()
st.caption(f"Trace ID: {thread_id} | Core: Gemini 2.0 Flash-Lite | DB: Weaviate Local")