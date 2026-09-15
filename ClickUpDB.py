import streamlit as dt
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- CONFIGURATION ---
CLICKUP_TOKEN = "pk_63097086_RCS1F8Y5W38W0FHXFYWA45346XRZGS0P"[cite: 4]
LIST_ID = "901612921295"  [cite: 4]
REFRESH_INTERVAL = 120  # Smart local cache lifetime (2 minutes)[cite: 4]

headers = {
    "Authorization": CLICKUP_TOKEN,[cite: 4]
    "Content-Type": "application/json"[cite: 4]
}

dt.set_page_config(layout="wide", page_title="Executive Delivery Insights", page_icon="📊")[cite: 4]

# --- ENTERPRISE LUXE DESIGN SYSTEM ---
dt.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 15% 15%, #0F172A 0%, #080D1A 100%);
        color: #F8FAFC;
    }

    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2.5rem;
        max-width: 95%;
    }

    /* Executive Glassmorphic Header */
    .executive-header {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.85) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 22px 30px;
        margin-bottom: 24px;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }

    /* 3D Glassmorphic KPI Cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 16px 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.15);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 16px 28px -6px rgba(0, 0, 0, 0.6);
        border-color: rgba(96, 165, 250, 0.35);
    }
    div[data-testid="stMetricValue"] {
        font-size: 32px !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #FFFFFF 30%, #94A3B8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 11px !important;
        font-weight: 700 !important;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #94A3B8 !important;
    }

    /* 3D Exception Cards with Integrated Footer */
    .insight-wrapper {
        border-radius: 14px;
        padding: 18px 20px 10px 20px;
        margin-bottom: 14px;
        border: 1px solid rgba(255, 255, 255, 0.07);
        box-shadow: 0 12px 24px -6px rgba(0, 0, 0, 0.45);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 125px;
    }
    .insight-crunch {
        background: linear-gradient(135deg, rgba(120, 53, 15, 0.35) 0%, rgba(26, 18, 9, 0.75) 100%);
        border-left: 4px solid #F59E0B;
    }
    .insight-slippage {
        background: linear-gradient(135deg, rgba(127, 29, 29, 0.35) 0%, rgba(30, 10, 10, 0.75) 100%);
        border-left: 4px solid #EF4444;
    }
    .insight-velocity {
        background: linear-gradient(135deg, rgba(30, 58, 138, 0.35) 0%, rgba(10, 18, 38, 0.75) 100%);
        border-left: 4px solid #3B82F6;
    }
    .insight-critical {
        background: linear-gradient(135deg, rgba(153, 27, 27, 0.45) 0%, rgba(40, 10, 10, 0.8) 100%);
        border-left: 4px solid #DC2626;
        box-shadow: 0 0 20px rgba(220, 38, 38, 0.15);
    }
    .insight-healthy {
        background: linear-gradient(135deg, rgba(6, 78, 59, 0.35) 0%, rgba(4, 30, 24, 0.75) 100%);
        border-left: 4px solid #10B981;
    }

    /* Embedded Hyperlink Button Styling */
    div[data-testid*="btn_"] button {
        background: transparent !important;
        border: none !important;
        color: #93C5FD !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        text-decoration: underline !important;
        cursor: pointer !important;
        box-shadow: none !important;
        padding: 0px 4px !important;
        float: right !important;
        margin-top: -24px !important;
        transition: color 0.2s ease !important;
    }
    div[data-testid*="btn_"] button:hover {
        color: #FFFFFF !important;
        text-decoration: underline !important;
        background: transparent !important;
    }

    /* Tables & Theme Tweaks */
    .stDataFrame {
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
    }
    section[data-testid="stSidebar"] {
        background: #090E1A !important;
        border-right: 1px solid rgba(255, 255, 255, 0.07);
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA EXTRACTION WITH PAGINATION ENGINE ---
@dt.cache_data(ttl=REFRESH_INTERVAL)[cite: 4]
def fetch_all_clickup_tasks(list_id):
    all_tasks = [][cite: 4]
    page = 0[cite: 4]
    has_more = True[cite: 4]
    
    while has_more:[cite: 4]
        url = f"https://api.clickup.com/api/v2/list/{list_id}/task?include_closed=true&page={page}"[cite: 4]
        response = requests.get(url, headers=headers)[cite: 4]
        
        if response.status_code != 200:[cite: 4]
            if page == 0:[cite: 4]
                alt_url = f"https://api.clickup.com/api/v2/space/{list_id}/task?include_closed=true&page={page}"[cite: 4]
                response = requests.get(alt_url, headers=headers)[cite: 4]
                if response.status_code != 200:[cite: 4]
                    break[cite: 4]
            else:
                break[cite: 4]
                
        data = response.json()[cite: 4]
        page_tasks = data.get('tasks', [])[cite: 4]
        all_tasks.extend(page_tasks)[cite: 4]
        
        if len(page_tasks) == 20:  [cite: 4]
            page += 1[cite: 4]
        else:
            has_more = False[cite: 4]
            
    return all_tasks[cite: 4]

def transform_and_enrich_data(tasks):
    if not tasks:[cite: 4]
        return pd.DataFrame()[cite: 4]
    
    records = [][cite: 4]
    for t in tasks:[cite: 4]
        raw_due = t.get('due_date')[cite: 4]
        due_dt = datetime.fromtimestamp(int(raw_due) / 1000) if raw_due else None[cite: 4]
        
        if due_dt:[cite: 4]
            task_year = str(due_dt.year)[cite: 4]
            task_month = due_dt.strftime('%B')[cite: 4]
            task_quarter = f"Q{(due_dt.month - 1) // 3 + 1}"[cite: 4]
            task_date = due_dt.date()[cite: 4]
        else:
            task_year = "No Date Allocated"[cite: 4]
            task_month = "No Date Allocated"[cite: 4]
            task_quarter = "No Date Allocated"[cite: 4]
            task_date = None[cite: 4]

        assignees_list = [user.get('username', 'Unassigned') for user in t.get('assignees', [])][cite: 4]
        primary_assignee = assignees_list[0] if assignees_list else "Unassigned"[cite: 4]
        all_team = ", ".join(assignees_list) if assignees_list else "Unassigned"[cite: 4]
        
        p_map = {"1": "1. Urgent 🔴", "2": "2. High 🟡", "3": "3. Normal 🔵", "4": "4. Low ⚪"}[cite: 4]
        p_info = t.get('priority')[cite: 4]
        priority_str = p_map.get(str(p_info.get('id')) if p_info else "", "5. None 📋")[cite: 4]
        
        status_obj = t.get('status', {})[cite: 4]
        raw_status = status_obj.get('status', 'OPEN').upper()[cite: 4]
        is_closed_type = status_obj.get('type') == 'closed'[cite: 4]
        
        if is_closed_type or raw_status in ['CLOSED', 'COMPLETE', 'DONE', 'RESOLVED']:[cite: 4]
            bi_status = 'COMPLETED'[cite: 4]
        elif raw_status in ['ON HOLD', 'HOLD', 'BLOCKED', 'DEFERRED']:[cite: 4]
            bi_status = 'HOLD'[cite: 4]
        elif raw_status in ['OPEN', 'NOT STARTED', 'BACKLOG', 'TO DO']:[cite: 4]
            bi_status = 'NOT STARTED'[cite: 4]
        else:
            bi_status = 'ONGOING'[cite: 4]

        custom_category = "General Initiatives"[cite: 4]
        for cf in t.get('custom_fields', []):[cite: 4]
            if 'category' in cf.get('name', '').lower() and cf.get('value'):[cite: 4]
                if isinstance(cf.get('value'), list):[cite: 4]
                    custom_category = cf['value'][0][cite: 4]
                elif isinstance(cf.get('value'), int) and cf.get('type_config', {}).get('options'):[cite: 4]
                    opts = cf['type_config']['options'][cite: 4]
                    custom_category = next((o['name'] for o in opts if o['orderindex'] == cf['value']), "General Initiatives")[cite: 4]
                else:
                    custom_category = str(cf.get('value'))[cite: 4]

        records.append({
            "Task ID": t.get('id'),[cite: 4]
            "Initiative / Task": t.get('name'),[cite: 4]
            "Raw Status": raw_status,[cite: 4]
            "Category Status": bi_status,[cite: 4]
            "Priority": priority_str,[cite: 4]
            "Owner": primary_assignee,[cite: 4]
            "Full Team Allocated": all_team,[cite: 4]
            "Due Date": task_date,[cite: 4]
            "Year": task_year,[cite: 4]
            "Quarter": task_quarter,[cite: 4]
            "Month": task_month,[cite: 4]
            "Segment": custom_category[cite: 4]
        })[cite: 4]
        
    return pd.DataFrame(records)[cite: 4]

# --- DRILLDOWN MODAL DEFINITIONS ---
COLS_TO_SHOW = ["Task ID", "Initiative / Task", "Owner", "Category Status", "Priority", "Due Date", "Segment"]

@dt.dialog("⚠️ Resource Allocation Drilldown")
def show_resource_drilldown(df, owner):
    dt.markdown(f"#### In-Flight Tasks Assigned to: **{owner}**")
    active_user_tasks = df[(df['Owner'] == owner) & (df['Category Status'] == 'ONGOING')][COLS_TO_SHOW]
    dt.dataframe(active_user_tasks, hide_index=True, use_container_width=True)

@dt.dialog("🚨 Milestone Slippage Exception")
def show_slippage_drilldown(df):
    dt.markdown("#### Delayed Deliverables Requiring Milestone Realignment")
    today_val = datetime.now().date()
    overdue_df = df[(df['Category Status'] != 'COMPLETED') & (df['Due Date'] < today_val) & (df['Due Date'].notnull())][COLS_TO_SHOW]
    dt.dataframe(overdue_df.sort_values(by="Due Date"), hide_index=True, use_container_width=True)

@dt.dialog("📋 Pipeline & Backlog Structure")
def show_backlog_drilldown(df):
    dt.markdown("#### Unstarted Scope / Backlog Queue")
    backlog_df = df[df['Category Status'] == 'NOT STARTED'][COLS_TO_SHOW]
    dt.dataframe(backlog_df, hide_index=True, use_container_width=True)

@dt.dialog("🔥 Critical Path Analysis")
def show_critical_drilldown(df):
    dt.markdown("#### Active Urgent Tasks in Production")
    urgent_df = df[(df['Priority'].str.contains("Urgent")) & (df['Category Status'] == 'ONGOING')][COLS_TO_SHOW]
    dt.dataframe(urgent_df, hide_index=True, use_container_width=True)

# --- RUN BI PIPELINE ---
raw_data = fetch_all_clickup_tasks(LIST_ID)[cite: 4]
master_df = transform_and_enrich_data(raw_data)[cite: 4]

if master_df.empty:[cite: 4]
    dt.info("📡 Connecting to ClickUp data layers... Confirm items populate your workspace list.")[cite: 4]
else:
    # --- EXECUTIVE TOP HERO ---
    dt.markdown(f"""
        <div class="executive-header">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <h1 style="margin: 0; font-size: 27px; font-weight: 800; letter-spacing: -0.02em; color: #FFFFFF;">
                        📊 Strategic Portfolio & Delivery Intelligence
                    </h1>
                    <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 13px; font-weight: 500;">
                        Enterprise Infrastructure Delivery & Capacity Governance
                    </p>
                </div>
                <div style="text-align: right; margin-top: 6px;">
                    <span style="background: rgba(16, 185, 129, 0.15); color: #34D399; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; border: 1px solid rgba(52, 211, 153, 0.3);">
                        ● LIVE STREAM
                    </span>
                    <p style="margin: 4px 0 0 0; color: #64748B; font-size: 11px; font-weight: 500;">
                        System Time: {datetime.now().strftime('%Y-%m-%d %H:%M')} IST
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- ADVANCED DATE & FIELD SLICER SIDEBAR ---
    with dt.sidebar:[cite: 4]
        dt.markdown("### 🎛️ Governance Slicers")
        
        dt.caption("TEMPORAL CONTROLS")
        years_available = sorted(master_df['Year'].unique(), reverse=True)[cite: 4]
        sel_years = dt.multiselect("Select Year", options=years_available, default=years_available)[cite: 4]
        
        quarters_available = sorted(master_df['Quarter'].unique())[cite: 4]
        sel_quarters = dt.multiselect("Select Quarter", options=quarters_available, default=quarters_available)[cite: 4]
        
        months_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "No Date Allocated"][cite: 4]
        months_available = [m for m in months_order if m in master_df['Month'].unique()][cite: 4]
        sel_months = dt.multiselect("Select Month", options=months_available, default=months_available)[cite: 4]
        
        valid_dates = master_df[master_df['Due Date'].notnull()]['Due Date'][cite: 4]
        min_date = valid_dates.min() if not valid_dates.empty else datetime.now().date()[cite: 4]
        max_date = valid_dates.max() if not valid_dates.empty else datetime.now().date() + timedelta(days=90)[cite: 4]
        
        start_date, end_date = dt.date_input("Date Window", [min_date, max_date])[cite: 4]

        dt.markdown("---")[cite: 4]
        dt.caption("STRUCTURAL CONTROLS")
        sel_owners = dt.multiselect("Task Owners", options=sorted(master_df['Owner'].unique()), default=master_df['Owner'].unique())[cite: 4]
        sel_priorities = dt.multiselect("Priority Levels", options=sorted(master_df['Priority'].unique()), default=master_df['Priority'].unique())[cite: 4]
        sel_segments = dt.multiselect("Functional Segments", options=sorted(master_df['Segment'].unique()), default=master_df['Segment'].unique())[cite: 4]

    # --- PROCESS FILTER LOGIC ---
    f_df = master_df[[cite: 4]
        (master_df['Year'].isin(sel_years)) & [cite: 4]
        (master_df['Quarter'].isin(sel_quarters)) & [cite: 4]
        (master_df['Month'].isin(sel_months)) & [cite: 4]
        (master_df['Owner'].isin(sel_owners)) & [cite: 4]
        (master_df['Priority'].isin(sel_priorities)) & [cite: 4]
        (master_df['Segment'].isin(sel_segments))[cite: 4]
    ][cite: 4]
    
    def date_bound_check(row_date):[cite: 4]
        if row_date is None:[cite: 4]
            return True  [cite: 4]
        return start_date <= row_date <= end_date[cite: 4]
        
    if not f_df.empty:[cite: 4]
        f_df = f_df[f_df['Due Date'].apply(date_bound_check)][cite: 4]

    # --- EXECUTIVE SCORECARD METRICS ---
    total_volume = len(f_df)[cite: 4]
    completed_volume = len(f_df[f_df['Category Status'] == 'COMPLETED'])[cite: 4]
    ongoing_volume = len(f_df[f_df['Category Status'] == 'ONGOING'])[cite: 4]
    hold_volume = len(f_df[f_df['Category Status'] == 'HOLD'])[cite: 4]
    unstarted_volume = len(f_df[f_df['Category Status'] == 'NOT STARTED'])[cite: 4]

    effective_denominator = total_volume - hold_volume[cite: 4]
    closure_rate_calc = int((completed_volume / effective_denominator) * 100) if effective_denominator > 0 else 0[cite: 4]

    k1, k2, k3, k4, k5 = dt.columns(5)
    k1.metric("Total Scope", total_volume)
    k2.metric("In Flight", ongoing_volume)
    k3.metric("Delivered", completed_volume, delta=f"{closure_rate_calc}% Closure Velocity")
    k4.metric("On Hold", hold_volume, delta="Excluded", delta_color="off")
    k5.metric("Pipeline Queue", unstarted_volume)

    dt.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # --- AUTOMATED KEY INSIGHTS WITH INLINE BOTTOM-RIGHT HYPERLINKS ---
    dt.markdown("### 💡 Automated Operational Insights & Exception Radar")
    
    if not f_df.empty:[cite: 4]
        c_ins1, c_ins2 = dt.columns(2)
        
        with c_ins1:
            # 1. Resource Workload Insight
            active_only = f_df[f_df['Category Status'] == 'ONGOING'][cite: 4]
            if not active_only.empty:[cite: 4]
                top_owner = active_only['Owner'].value_counts().idxmax()[cite: 4]
                top_owner_count = active_only['Owner'].value_counts().max()[cite: 4]
                if top_owner != "Unassigned" and top_owner_count >= 3:[cite: 4]
                    dt.markdown(f"""
                        <div class="insight-wrapper insight-crunch">
                            <div>
                                <div style="font-weight: 700; color: #FBBF24; margin-bottom: 4px; font-size: 14px;">⚠️ Resource Allocation Crunch</div>
                                <div style="color: #E2E8F0; font-size: 13px; line-height: 1.5;">
                                    <b>{top_owner}</b> is currently spearheading <b>{top_owner_count} concurrent active tasks</b>.
                                </div>
                            </div>
                            <div style="text-align: right; padding-top: 14px; margin-bottom: -2px;">&nbsp;</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if dt.button("Click for details →", key="btn_res", help="Inspect in-flight tasks"):
                        show_resource_drilldown(f_df, top_owner)
                else:
                    dt.markdown("""
                        <div class="insight-wrapper insight-healthy">
                            <div>
                                <div style="font-weight: 700; color: #34D399; margin-bottom: 4px; font-size: 14px;">✅ Balanced Workload Topology</div>
                                <div style="color: #E2E8F0; font-size: 13px;">Active deliverables are evenly distributed across current team capacity.</div>
                            </div>
                            <div style="height: 18px;"></div>
                        </div>
                    """, unsafe_allow_html=True)
            
            # 2. Pipeline Saturation Insight
            if unstarted_volume > (total_volume * 0.40):[cite: 4]
                dt.markdown(f"""
                    <div class="insight-wrapper insight-velocity">
                        <div>
                            <div style="font-weight: 700; color: #60A5FA; margin-bottom: 4px; font-size: 14px;">📋 Pipeline Saturation Notice</div>
                            <div style="color: #E2E8F0; font-size: 13px; line-height: 1.5;">
                                Over 40% of project scope (<b>{unstarted_volume} tasks</b>) remains in unstarted status.
                            </div>
                        </div>
                        <div style="text-align: right; padding-top: 14px; margin-bottom: -2px;">&nbsp;</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                dt.markdown("""
                    <div class="insight-wrapper insight-velocity">
                        <div>
                            <div style="font-weight: 700; color: #60A5FA; margin-bottom: 4px; font-size: 14px;">📋 Controlled Intake Velocity</div>
                            <div style="color: #E2E8F0; font-size: 13px; line-height: 1.5;">Backlog queues align comfortably with planned release schedules.</div>
                        </div>
                        <div style="text-align: right; padding-top: 14px; margin-bottom: -2px;">&nbsp;</div>
                    </div>
                """, unsafe_allow_html=True)
            if dt.button("Click for details →", key="btn_pipe", help="Inspect backlog list"):
                show_backlog_drilldown(f_df)

        with c_ins2:
            # 3. Slippage Exception
            today_date = datetime.now().date()[cite: 4]
            overdue_tasks = f_df[(f_df['Category Status'] != 'COMPLETED') & (f_df['Due Date'] < today_date) & (f_df['Due Date'].notnull())][cite: 4]
            if not overdue_tasks.empty:[cite: 4]
                dt.markdown(f"""
                    <div class="insight-wrapper insight-slippage">
                        <div>
                            <div style="font-weight: 700; color: #F87171; margin-bottom: 4px; font-size: 14px;">🚨 Milestone Slippage Alert</div>
                            <div style="color: #E2E8F0; font-size: 13px; line-height: 1.5;">
                                Identified <b>{len(overdue_tasks)} pending deliverables</b> exceeding committed milestone schedules.
                            </div>
                        </div>
                        <div style="text-align: right; padding-top: 14px; margin-bottom: -2px;">&nbsp;</div>
                    </div>
                """, unsafe_allow_html=True)
                if dt.button("Click for details →", key="btn_slip", help="Inspect delayed deliverables"):
                    show_slippage_drilldown(f_df)
            else:
                dt.markdown("""
                    <div class="insight-wrapper insight-healthy">
                        <div>
                            <div style="font-weight: 700; color: #34D399; margin-bottom: 4px; font-size: 14px;">🎯 Timeline Compliance</div>
                            <div style="color: #E2E8F0; font-size: 13px;">All filtered pending deliverables remain within schedule buffers.</div>
                        </div>
                        <div style="height: 18px;"></div>
                    </div>
                """, unsafe_allow_html=True)

            # 4. Critical Path Tracking
            urgent_active = f_df[(f_df['Priority'].str.contains("Urgent")) & (f_df['Category Status'] == 'ONGOING')][cite: 4]
            if not urgent_active.empty:[cite: 4]
                dt.markdown(f"""
                    <div class="insight-wrapper insight-critical">
                        <div>
                            <div style="font-weight: 700; color: #EF4444; margin-bottom: 4px; font-size: 14px;">🔥 Critical Path Production Pressure</div>
                            <div style="color: #E2E8F0; font-size: 13px; line-height: 1.5;">
                                Executing <b>{len(urgent_active)} URGENT priority deliverable(s)</b> requiring dedicated focus.
                            </div>
                        </div>
                        <div style="text-align: right; padding-top: 14px; margin-bottom: -2px;">&nbsp;</div>
                    </div>
                """, unsafe_allow_html=True)
                if dt.button("Click for details →", key="btn_crit", help="Inspect urgent issues"):
                    show_critical_drilldown(f_df)
            else:
                dt.markdown("""
                    <div class="insight-wrapper insight-velocity">
                        <div>
                            <div style="font-weight: 700; color: #94A3B8; margin-bottom: 4px; font-size: 14px;">✨ Critical Path Status</div>
                            <div style="color: #E2E8F0; font-size: 13px;">Zero critical or blocking issues flagged in production delivery.</div>
                        </div>
                        <div style="height: 18px;"></div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        dt.info("Adjust slicers to populate operational insights.")

    dt.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # Common Plotly Theme Settings
    chart_layout_base = dict(
        paper_bgcolor='rgba(15, 23, 42, 0.65)',
        plot_bgcolor='rgba(15, 23, 42, 0)',
        font=dict(family='Plus Jakarta Sans', color='#94A3B8', size=11),
        margin=dict(l=15, r=15, t=25, b=15),
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.05)', zeroline=False),
        yaxis=dict(gridcolor='rgba(255, 255, 255, 0.05)', zeroline=False)
    )

    # --- ROW 1: ANALYTICAL CHARTS ---
    col1, col2, col3 = dt.columns([3, 4, 3])[cite: 4]
    
    with col1:
        dt.markdown("##### 📋 Delivery Status Matrix")
        status_chart_data = f_df['Category Status'].value_counts().reset_index()[cite: 4]
        status_chart_data.columns = ['Status', 'Count'][cite: 4]
        
        status_colors = {
            'COMPLETED': '#10B981', 
            'HOLD': '#F59E0B', 
            'ONGOING': '#059669', 
            'NOT STARTED': '#64748B'
        }
        fig_status = px.bar(status_chart_data, x='Status', y='Count', color='Status', color_discrete_map=status_colors)[cite: 4]
        fig_status.update_layout(**chart_layout_base, showlegend=False, height=300)
        fig_status.update_traces(marker_line_color='rgba(255,255,255,0.15)', marker_line_width=1, opacity=0.92)
        dt.plotly_chart(fig_status, use_container_width=True)[cite: 4]
        
    with col2:
        dt.markdown("##### 🎯 Resource Allocation & Throughput Trend")
        if not f_df.empty:[cite: 4]
            res_df = f_df.groupby(['Owner', 'Category Status']).size().unstack(fill_value=0).reset_index()[cite: 4]
            total_per_owner = f_df.groupby('Owner').size().reset_index(name='Total Tasks')[cite: 4]
            res_merged = pd.merge(res_df, total_per_owner, on='Owner')[cite: 4]
            
            fig_res = go.Figure()[cite: 4]
            palette = [('COMPLETED', '#10B981'), ('HOLD', '#F59E0B'), ('ONGOING', '#059669'), ('NOT STARTED', '#475569')]
            for status_step, color_hex in palette:
                if status_step in res_merged.columns:[cite: 4]
                    fig_res.add_trace(go.Bar(name=status_step, x=res_merged['Owner'], y=res_merged[status_step], marker_color=color_hex))[cite: 4]
            
            fig_res.add_trace(go.Scatter(
                name='Total Volume Trend', 
                x=res_merged['Owner'], 
                y=res_merged['Total Tasks'], 
                mode='lines+markers', 
                line=dict(color='#A855F7', width=3, shape='spline'),
                marker=dict(size=7, color='#C084FC', line=dict(color='#FFFFFF', width=1.5))
            ))
            fig_res.update_layout(
                **chart_layout_base, 
                barmode='stack', 
                height=300, 
                legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=1, font=dict(size=10))
            )
            dt.plotly_chart(fig_res, use_container_width=True)[cite: 4]

    with col3:
        dt.markdown("##### 🔥 Priority Risk Distribution")
        priority_chart_data = f_df['Priority'].value_counts().reset_index()[cite: 4]
        priority_chart_data.columns = ['Priority', 'Count'][cite: 4]
        priority_chart_data = priority_chart_data.sort_values('Priority')[cite: 4]
        
        prio_colors = {
            "1. Urgent 🔴": "#DC2626",[cite: 4]
            "2. High 🟡": "#F59E0B",[cite: 4]
            "3. Normal 🔵": "#3B82F6",[cite: 4]
            "4. Low ⚪": "#10B981",[cite: 4]
            "5. None 📋": "#64748B"
        }
        fig_prio = px.bar(priority_chart_data, x='Count', y='Priority', orientation='h', color='Priority', color_discrete_map=prio_colors)[cite: 4]
        fig_prio.update_layout(**chart_layout_base, showlegend=False, height=300)
        fig_prio.update_traces(marker_line_color='rgba(255,255,255,0.15)', marker_line_width=1, opacity=0.92)
        dt.plotly_chart(fig_prio, use_container_width=True)[cite: 4]

    dt.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # --- ROW 2: CAPACITY PROFILE & CROSS TAB MATRIX ---
    r2_left, r2_right = dt.columns([4, 6])[cite: 4]
    
    with r2_left:
        dt.markdown("##### 👥 Team Workload Share Ratio")
        member_shares = f_df['Owner'].value_counts().reset_index()[cite: 4]
        member_shares.columns = ['Team Member', 'Total Work Volume'][cite: 4]
        
        rich_donuts = ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#06B6D4', '#64748B']
        fig_pie = px.pie(member_shares, values='Total Work Volume', names='Team Member', hole=0.55, color_discrete_sequence=rich_donuts)
        fig_pie.update_layout(**chart_layout_base, height=290, legend=dict(orientation="v", yanchor="middle", y=0.5, font=dict(size=10)))
        fig_pie.update_traces(marker=dict(line=dict(color='#0F172A', width=2)))
        dt.plotly_chart(fig_pie, use_container_width=True)[cite: 4]

    with r2_right:
        dt.markdown("##### 👥 Team Capacity Matrix Reference")
        cross_tab = pd.crosstab(f_df['Owner'], f_df['Category Status'])[cite: 4]
        for col_status in ['NOT STARTED', 'ONGOING', 'HOLD', 'COMPLETED']:[cite: 4]
            if col_status not in cross_tab.columns:[cite: 4]
                cross_tab[col_status] = 0[cite: 4]
        cross_tab = cross_tab[['NOT STARTED', 'ONGOING', 'HOLD', 'COMPLETED']][cite: 4]
        dt.dataframe(cross_tab, use_container_width=True)[cite: 4]

    dt.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # --- ROW 3: CALENDAR PIPELINES ---
    dt.markdown("### 📅 Operational Rolling Window Milestones")
    
    today_dt = datetime.now().date()[cite: 4]
    start_week = today_dt - timedelta(days=today_dt.weekday())[cite: 4]
    end_week = start_week + timedelta(days=6)[cite: 4]
    end_upcoming = end_week + timedelta(days=7)[cite: 4]
    
    weekly_matrix = f_df[(f_df['Due Date'] >= start_week) & (f_df['Due Date'] <= end_week)][cite: 4]
    upcoming_matrix = f_df[(f_df['Due Date'] > end_week) & (f_df['Due Date'] <= end_upcoming)][cite: 4]
    rest_matrix = f_df[(f_df['Due Date'] > end_upcoming) | (f_df['Due Date'].isnull())][cite: 4]
    
    tab1, tab2, tab3 = dt.tabs(["✨ Active Week Milestones", "🔮 Near-Horizon (Next Week)", "📥 Long-Range Pipeline"])
    
    with tab1:
        if not weekly_matrix.empty:[cite: 4]
            dt.dataframe(weekly_matrix[["Initiative / Task", "Owner", "Category Status", "Priority", "Due Date"]], hide_index=True, use_container_width=True)[cite: 4]
        else:
            dt.info("No deliverables scheduled to conclude within current week bounds.")

    with tab2:
        if not upcoming_matrix.empty:[cite: 4]
            dt.dataframe(upcoming_matrix[["Initiative / Task", "Owner", "Category Status", "Priority", "Due Date"]], hide_index=True, use_container_width=True)[cite: 4]
        else:
            dt.info("No secondary milestones mapped to the upcoming horizon frame.")[cite: 4]

    with tab3:
        if not rest_matrix.empty:[cite: 4]
            dt.dataframe(rest_matrix[["Initiative / Task", "Owner", "Category Status", "Priority", "Due Date"]], hide_index=True, use_container_width=True)[cite: 4]
        else:
            dt.info("Future queue data layer empty.")[cite: 4]

    dt.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # --- ROW 4: DATA ENGINE DRILLDOWN LEDGER ---
    with dt.expander("🔍 Enterprise Master Data Ledger (Full System Drilldown)", expanded=False):[cite: 4]
        dt.dataframe(
            f_df[["Task ID", "Initiative / Task", "Owner", "Full Team Allocated", "Category Status", "Raw Status", "Priority", "Due Date", "Segment"]].sort_values(by="Priority"),[cite: 4]
            use_container_width=True,[cite: 4]
            hide_index=True[cite: 4]
        )
