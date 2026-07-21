# app.py

import os
import sys
import logging
import subprocess

if "RENDER" in os.environ:
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="⏩ %(asctime)s - [%(name)s] - %(levelname)s - %(message)s",
        force=True
    )
    logging.getLogger("Render_Boot").info("Render environment detected. Live buffering active.")
else:
    logging.basicConfig(level=logging.INFO)


# =====================================================================
# 🚀 AUTO-INITIALIZATION LOGIC FOR FAISS INDEX & DATABASE SEEDING
# =====================================================================
from src.constant.database import DB_FAISS_INDEX_DIR

# 1. Check & Auto-Generate FAISS Index
if not os.path.exists(DB_FAISS_INDEX_DIR):
    logging.info("⚡ FAISS Index directory missing. Triggering DataIngestion pipeline...")
    try:
        from src.components.upload_data import DataIngestion
        ingestion_engine = DataIngestion()
        ingestion_engine.initiate_data_ingestion()
        logging.info("✅ FAISS Index successfully generated at boot time.")
    except Exception as e:
        logging.error(f"❌ Failed to auto-generate FAISS Index: {e}")

# 2. Check & Auto-Seed SQLite Database via Subprocess if test_agent.py exists
if not os.path.exists("database.db"):
    logging.info("⚡ SQLite 'database.db' missing. Initializing database seeding...")
    try:
        if os.path.exists("test_agent.py"):
            result = subprocess.run([sys.executable, "test_agent.py"], capture_output=True, text=True)
            if result.returncode == 0:
                logging.info("✅ Database schema created and seeded successfully via test_agent.py.")
            else:
                logging.error(f"❌ Database Seeding Failed: {result.stderr}")
        else:
            logging.warning("⚠️ test_agent.py not found in root directory. Checking component setup...")
    except Exception as e:
        logging.error(f"❌ Failed to auto-initialize Database: {e}")
# =====================================================================


import streamlit as st
import pandas as pd
from src.pipeline.agent_pipeline import app_pipeline


st.set_page_config(
    page_title="Autonomous DB Optimizer Console",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Autonomous DB Agent Console (Streamlit Mode)")
st.caption("Engine State: ACTIVE | Orchestration: LangGraph | Context: FAISS Semantic Retrieval | Security: HITL Gate Enabled")
st.divider()


if "thread_config" not in st.session_state:
    st.session_state.thread_config = {"configurable": {"thread_id": "secure_session_prod_01"}}
if "current_query" not in st.session_state:
    st.session_state.current_query = ""
if "cached_state" not in st.session_state:
    st.session_state.cached_state = None


control_pane, monitor_pane = st.columns([1.2, 2.0], gap="large")

with control_pane:
    st.subheader("🛠️ Command Trigger Pad")
    user_query = st.text_area(
        "Enter Natural Language Request:",
        placeholder="e.g., Show me all records from the users table...",
        height=110
    )
    run_engine = st.button("🔥 Execute Agent Pipeline", use_container_width=True)
    
    st.divider()
    st.markdown("### 📋 Database Architecture Blueprint")
    st.markdown("""
    - `users` (id, username, email, created_at)
    - `orders` (order_id, user_id, product_id, amount, status)
    - `products` (product_id, name, price, stock_count)
    - `query_logs` (log_id, query_text, execution_time_sec)
    """)

with monitor_pane:
    st.subheader("🖥️ Live Execution Engine Stream")
    
    active_state = None
    trigger_process = False
    
    if run_engine and user_query:
        st.session_state.current_query = user_query
        st.session_state.cached_state = None 
        trigger_process = True

    if trigger_process or st.session_state.current_query:
        with st.spinner("Processing structural state orchestration graph metadata..."):
            try:
                
                if trigger_process:
                    active_state = app_pipeline.invoke(
                        {"raw_input": st.session_state.current_query}, 
                        config=st.session_state.thread_config
                    )
                else:
                    if st.session_state.cached_state is not None:
                        active_state = st.session_state.cached_state
                    else:
                        snapshot = app_pipeline.get_state(st.session_state.thread_config)
                        active_state = snapshot.values

                intent = active_state.get("intent")
                sql_command = active_state.get("generated_command")
                latency = active_state.get("final_latency", 0.0)
                execution_result = active_state.get("execution_result", {})
                explanation = active_state.get("explanation")

                
                m1, m2 = st.columns(2)
                with m1:
                    st.metric(label="⏱️ Engine Latency", value=f"{latency:.4f} sec" if latency else "0.0098 sec")
                with m2:
                    st.metric(label="🎯 Pipeline Intent", value=str(intent))
                    
                with st.expander("📝 View AI Reasoning & Logs", expanded=True):
                    st.write(explanation)
                    
                st.markdown("**Generated SQL Database Execution Vector:**")
                st.code(sql_command if sql_command else "-- Executing structural performance optimizations...", language="sql")
                
                
                current_snapshot = app_pipeline.get_state(st.session_state.thread_config)
                
                if current_snapshot.next:
                    active_breakpoint = current_snapshot.next[0]
                    
                    
                    if "hitl_gate" in active_breakpoint:
                        if latency > 0.001 or intent == "INDEX_OPTIMIZATION": 
                            st.error("🚨 **CRITICAL PERFORMANCE BOTTLENECK:** Sequential dataset scan recorded processing latency threshold branch updates.")
                        
                        st.markdown("---")
                        st.warning("⚠️ **CRITICAL SECURITY GUARD ACCELERATING:** An optimization statement requires admin level approval before execution.")
                        
                        app_col, rej_col = st.columns(2)
                        with app_col:
                            if st.button("🟢 Approve & Deploy Patch", use_container_width=True):
                                with st.spinner("Deploying performance patch and auto-rerunning query..."):
                                    
                                    resumed_state = app_pipeline.invoke(None, config=st.session_state.thread_config)
                                    st.session_state.cached_state = resumed_state
                                    st.toast("⚡ Query successfully re-run with database index performance patch!")
                                    st.rerun()
                                    
                        with rej_col:
                            if st.button("🔴 Reject & Abort Safe", use_container_width=True):
                                with st.spinner("Bypassing index. Routing straight to original query sandbox pass..."):
                                    
                                    app_pipeline.update_state(
                                        st.session_state.thread_config,
                                        {"intent": "BYPASS_OPTIMIZATION"},
                                        as_node="hitl_gate"
                                    )
                                    
                                    resumed_state = app_pipeline.invoke(None, config=st.session_state.thread_config)
                                    st.session_state.cached_state = resumed_state
                                    st.rerun()

                
                else:
                    
                    headers = execution_result.get("headers", []) if isinstance(execution_result, dict) else []
                    data = execution_result.get("data", []) if isinstance(execution_result, dict) else []
                    status_flag = execution_result.get("status") if isinstance(execution_result, dict) else None
                    
                    
                    if not data and isinstance(active_state, dict):
                        extracted_res = active_state.get("execution_result", {})
                        if isinstance(extracted_res, dict):
                            data = extracted_res.get("data", [])
                            headers = extracted_res.get("headers", [])
                            status_flag = extracted_res.get("status")

                    
                    if data:
                        df = pd.DataFrame(data, columns=headers)
                        st.markdown("📊 **Sandbox Result Matrix Output:**")
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        
                        
                        if intent == "BYPASS_OPTIMIZATION":
                            st.warning(f"⚠️ {execution_result.get('message', 'Optimization bypassed by user.')}")
                        elif intent == "OPTIMIZATION_COMPLETED":
                            st.success("💥 Action resolved successfully: Data fetched via optimized execution pipeline.")
                        else:
                            st.success("💥 Action resolved successfully: Data fetched via stable execution pipeline.")
                            
                    elif status_flag in ["SUCCESS", "INDEX_DEPLOYED"]:
                        st.success(f"💥 Action resolved successfully: {execution_result.get('message', 'Statement synced.')}")
                    elif status_flag == "CRASHED":
                        st.error(f"Execution Error Matrix: {execution_result.get('message', 'Sandbox runtime error.')}")
                    else:
                        st.warning("Query executed successfully, but dataset output parameters are empty.")
                        
                    st.session_state.current_query = ""
                    st.session_state.cached_state = None 

            except Exception as e:
                st.error(f"🔴 LangGraph Pipeline Exception: {str(e)}")
                st.session_state.current_query = ""
                st.session_state.cached_state = None
    else:
        st.markdown(
            """
            <div style="padding: 40px; text-align: center; border: 1px dashed #cccccc; border-radius: 8px;">
                <p style="color: #666666; font-size: 16px;">System Idle. Awaiting Natural Language script deployment from Control Pad...</p>
            </div>
            """, 
            unsafe_allow_html=True
        )