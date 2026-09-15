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

# --- REFINED LIGHT-FIRST 3D UI STYLING ---
dt.markdown("""
    <style>
    .block-container {
        padding-top: 1.5rem; 
        padding-bottom: 2rem;
    }

    /* 3D Elevated Metric Cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #FFFFFF, #F8FAFC);
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05), inset 0 1px 0 rgba(255, 255, 255, 0.9);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.04);
    }
    div[data-testid="stMetricValue"] {
        font-size: 32px !important; 
        font-weight: 800 !important; 
        color: #1E3A8A !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 12px !important; 
        font-weight: 700 !important; 
        color: #4B5563 !important; 
        text-transform: uppercase !important;
        letter-spacing: 0.05em;
    }

    /* 3D Elevated Insight Containers */
    .insight-wrapper {
        border-radius: 10px;
        padding: 16px 18px 8px 18px;
        margin-bottom: 12px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 110px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.06), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    .insight-crunch {
        background: linear-gradient(145deg, #FEF3C7, #FDE68A);
        border-left: 5px solid #F59E0B;
        color: #92400E;
    }
    .insight-slippage {
        background: linear-gradient(145deg, #FEE2E2, #FECACA);
        border-left: 5px solid #EF4444;
        color: #991B1B;
    }
    .insight-velocity {
        background: linear-gradient(145deg, #EFF6FF, #DBEAFE);
        border-left: 5px solid #3B82F6;
        color: #1E40AF;
    }
    .insight-critical {
        background: linear-gradient(145deg, #FEE2E2, #FCA5A5);
        border-left: 5px solid #DC2626;
        color: #7F1D1D;
    }
    .insight-healthy {
        background: linear-gradient(145deg, #ECFDF5, #D1FAE5);
        border-left: 5px solid #10B981;
        color: #065F46;
    }

    /* Embedded Bottom-Right Action Link */
    div[data-testid*="btn_"] button {
        background: transparent !important;
        border: none !important;
        color: #1E3A8A !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        text-decoration: underline !important;
        cursor: pointer !important;
        box-shadow: none !important;
        padding: 0px 4px !important;
        float: right !important;
        margin-top: -24px !important;
        transition: color 0.15s ease !important;
    }
    div[data-testid*="btn_"] button:hover {
        color: #2563EB !important;
        background: transparent !important;
    }

    /* DataFrame Borders */
    .stDataFrame {
        border: 1px solid #E5E7EB; 
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
    }

    /* Dark Mode High-Contrast Overrides */
    @media (prefers-color-scheme: dark) {
        div[data-testid="stMetric"] {
            background: linear-gradient(145deg, #1E293B, #0F172A);
            border: 1px solid #334155;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
        }
        div[data-testid="stMetricValue"] {
            color: #60A5FA !important;
        }
        div[data-testid="stMetricLabel"] {
            color: #94A3B8 !important;
        }
        .insight-crunch {
            background: linear-gradient(145deg, #451A03, #78350F);
            color: #FDE68A;
            border-left-color: #F59E0B;
        }
        .insight-slippage {
            background: linear-gradient(145deg, #450A0A, #7F1D1D);
            color: #FECACA;
            border-left-color: #EF4444;
        }
        .insight-velocity {
            background: linear-gradient(145deg, #172554, #1E3A8A);
            color: #BFDBFE;
            border-left-color: #3B82F6;
        }
        .insight-critical {
            background: linear-gradient(145deg, #500724, #881337);
            color: #FBCFE8;
            border-left-color: #F43F5E;
        }
        .insight-healthy {
            background: linear-gradient(145deg, #022C22, #064E3B);
            color: #A7F3D0;
            border-left-color: #10B981;
        }
        div[data-testid*="btn_"] button {
            color: #93C5FD !important;
        }
        div[data-testid*="btn_"] button:hover {
            color: #FFFFFF !important;
        }
        .stDataFrame {
            border: 1px solid #334155;
        }
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
        # Date Normalization
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

        # Assignee Extraction
        assignees_list = [user.get('username', 'Unassigned') for user in t.get('assignees', [])][cite: 4]
        primary_assignee = assignees_list[0] if assignees_list else "Unassigned"[cite: 4]
        all_team = ", ".join(assignees_list) if assignees_list else "Unassigned"[cite: 4]
        
        # Priority Normalization
        p_map = {"1": "1. Urgent 🔴", "2": "2. High 🟡", "3": "3. Normal 🔵", "4": "4. Low ⚪"}[cite: 4]
        p_info = t.get('priority')[cite: 4]
        priority_str = p_map.get(str(p_info.get('id')) if p_info else "", "5. None 📋")[cite: 4]
        
        # BI Status Categorization
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

        # Segment Extraction
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

@dt.dialog("⚠️ Resource Allocation Details")
def show_resource_drilldown(df, owner):
    dt.markdown(f"**In-Flight Tasks Assigned to {owner}:**")
    active_user_tasks = df[(df['Owner'] == owner) & (df['Category Status'] == 'ONGOING')][COLS_TO_SHOW]
    dt.dataframe(active_user_tasks, hide_index=True, use_container_width=True)

@dt.dialog("🚨 Slippage Exception Details")
def show_slippage_drilldown(df):
    dt.markdown("**Overdue Tasks Requiring Milestone Alignment:**")
    today_val = datetime.now().date()
    overdue_df = df[(df['Category Status'] != 'COMPLETED') & (df['Due Date'] < today_val) & (df['Due Date'].notnull())][COLS_TO_SHOW]
    dt.dataframe(overdue_df.sort_values(by="Due Date"), hide_index=True, use_container_width=True)

@dt.dialog("📋 Backlog Pipeline Details")
def show_backlog_drilldown(df):
    dt.markdown("**Unstarted Scope & Intake Backlog Tasks:**")
    backlog_df = df[df['Category Status'] == 'NOT STARTED'][COLS_TO_SHOW]
    dt.dataframe(backlog_df, hide_index=True, use_container_width=True)

@dt.dialog("🔥 Critical Path Pressure Details")
def show_critical_drilldown(df):
    dt.markdown("**Urgent In-Flight Production Tasks:**")
    urgent_df = df[(df['Priority'].str.contains("Urgent")) & (df['Category Status'] == 'ONGOING')][COLS_TO_SHOW]
    dt.dataframe(urgent_df, hide_index=True, use_container_width=True)

# --- RUN BI PIPELINE ---
raw_data = fetch_all_clickup_tasks(LIST_ID)[cite: 4]
master_df = transform_and_enrich_data(raw_data)[cite: 4]

if master_df.empty:[cite: 4]
    dt.info("📡 Connecting to ClickUp data layers... Confirm items populate your workspace list.")[cite: 4]
else:
    # --- ENTERPRISE HEADER ---
    dt.title("📊 Strategic Project Portfolio & Resource Intelligence Hub")[cite: 4]
    dt.caption(f"Sync Engine: Operational Continuous Polling | System Time: {datetime.now().strftime('%Y-%m-%d %H:%M')} IST")[cite: 4]
    dt.markdown("---")[cite: 4]

    # --- ADVANCED DATE & FIELD SLICER SIDEBAR ---
    with dt.sidebar:[cite: 4]
        dt.header("🎛️ Interactive Filter Slicers")[cite: 4]
        
        dt.subheader("🗓️ Temporal Slicers")[cite: 4]
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
        
        start_date, end_date = dt.date_input("Custom Date Range Window", [min_date, max_date])[cite: 4]

        dt.markdown("---")[cite: 4]
        dt.subheader("👥 Resource & Structural Slicers")[cite: 4]
        sel_owners = dt.multiselect("Filter Task Owners", options=sorted(master_df['Owner'].unique()), default=master_df['Owner'].unique())[cite: 4]
        sel_priorities = dt.multiselect("Filter Priority Levels", options=sorted(master_df['Priority'].unique()), default=master_df['Priority'].unique())[cite: 4]
        sel_segments = dt.multiselect("Filter Functional Segments", options=sorted(master_df['Segment'].unique()), default=master_df['Segment'].unique())[cite: 4]

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

    # Calculation adjustment: Exclude HOLD status from completion denominator completely[cite: 4]
    effective_denominator = total_volume - hold_volume[cite: 4]
    if effective_denominator > 0:[cite: 4]
        closure_rate_calc = int((completed_volume / effective_denominator) * 100)[cite: 4]
    else:
        closure_rate_calc = 0[cite: 4]

    kpi1, kpi2, kpi3, kpi4, kpi5 = dt.columns(5)[cite: 4]
    kpi1.metric("Total Scope Items", total_volume)[cite: 4]
    kpi2.metric("Active (Ongoing)", ongoing_volume)[cite: 4]
    kpi3.metric("Completed Scope", completed_volume, delta=f"{closure_rate_calc}% Adjusted Closure Rate")[cite: 4]
    kpi4.metric("On Hold Tasks", hold_volume, delta="Excluded From Analytics", delta_color="off")[cite: 4]
    kpi5.metric("Backlog Pipeline", unstarted_volume)[cite: 4]

    dt.markdown("---")[cite: 4]

    # --- AUTOMATED KEY INSIGHTS WITH INLINE BOTTOM-RIGHT HYPERLINKS ---
    dt.subheader("💡 Automated Executive Insights & Exceptions")[cite: 4]
    
    if not f_df.empty:[cite: 4]
        ins_col1, ins_col2 = dt.columns(2)[cite: 4]
        
        with ins_col1:[cite: 4]
            # 1. Resource Workload Bottleneck Insight[cite: 4]
            active_only = f_df[f_df['Category Status'] == 'ONGOING'][cite: 4]
            if not active_only.empty:[cite: 4]
                top_owner = active_only['Owner'].value_counts().idxmax()[cite: 4]
                top_owner_count = active_only['Owner'].value_counts().max()[cite: 4]
                if top_owner != "Unassigned" and top_owner_count >= 3:[cite: 4]
                    dt.markdown(f"""
                        <div class="insight-wrapper insight-crunch">
                            <div>
                                <b>⚠️ Resource Allocation Crunch:</b> <b>{top_owner}</b> is currently managing the highest volume of in-flight work with <b>{top_owner_count} active tasks</b>.
                            </div>
                            <div style="text-align: right; padding-top: 14px;">&nbsp;</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if dt.button("Click for details →", key="btn_res", help="Inspect in-flight tasks"):
                        show_resource_drilldown(f_df, top_owner)
                else:
                    dt.markdown("""
                        <div class="insight-wrapper insight-healthy">
                            <div>
                                <b>✅ Balanced Allocation:</b> Active tasks are distributed evenly across the immediate delivery team.
                            </div>
                            <div style="height: 18px;"></div>
                        </div>
                    """, unsafe_allow_html=True)
            
            # 2. Backlog Risk Assessment[cite: 4]
            if unstarted_volume > (total_volume * 0.40):[cite: 4]
                dt.markdown(f"""
                    <div class="insight-wrapper insight-velocity">
                        <div>
                            <b>📋 Pipeline Concentration:</b> Over 40% of your project scope (<b>{unstarted_volume} tasks</b>) is sitting in 'Not Started'.
                        </div>
                        <div style="text-align: right; padding-top: 14px;">&nbsp;</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                dt.markdown("""
                    <div class="insight-wrapper insight-velocity">
                        <div>
                            <b>📋 Pipeline Velocity:</b> Backlog is under control, representing healthy future queue metrics.
                        </div>
                        <div style="text-align: right; padding-top: 14px;">&nbsp;</div>
                    </div>
                """, unsafe_allow_html=True)
            if dt.button("Click for details →", key="btn_pipe", help="Inspect backlog items"):
                show_backlog_drilldown(f_df)

        with ins_col2:[cite: 4]
            # 3. Overdue Check[cite: 4]
            today_date = datetime.now().date()[cite: 4]
            overdue_tasks = f_df[(f_df['Category Status'] != 'COMPLETED') & (f_df['Due Date'] < today_date) & (f_df['Due Date'].notnull())][cite: 4]
            if not overdue_tasks.empty:[cite: 4]
                dt.markdown(f"""
                    <div class="insight-wrapper insight-slippage">
                        <div>
                            <b>🚨 Slippage Exception:</b> Found <b>{len(overdue_tasks)} pending tasks</b> with past due dates. Immediate milestone alignment required.
                        </div>
                        <div style="text-align: right; padding-top: 14px;">&nbsp;</div>
                    </div>
                """, unsafe_allow_html=True)
                if dt.button("Click for details →", key="btn_slip", help="Inspect overdue deliverables"):
                    show_slippage_drilldown(f_df)
            else:
                dt.markdown("""
                    <div class="insight-wrapper insight-healthy">
                        <div>
                            <b>🎯 Timeline Discipline:</b> Zero pending items are overdue within this filtered dataset.
                        </div>
                        <div style="height: 18px;"></div>
                    </div>
                """, unsafe_allow_html=True)

            # 4. Critical Path Tracking[cite: 4]
            urgent_active = f_df[(f_df['Priority'].str.contains("Urgent")) & (f_df['Category Status'] == 'ONGOING')][cite: 4]
            if not urgent_active.empty:[cite: 4]
                dt.markdown(f"""
                    <div class="insight-wrapper insight-critical">
                        <div>
                            <b>🔥 Critical Path Pressure:</b> There are <b>{len(urgent_active)} URGENT tasks actively running</b> in production.
                        </div>
                        <div style="text-align: right; padding-top: 14px;">&nbsp;</div>
                    </div>
                """, unsafe_allow_html=True)
                if dt.button("Click for details →", key="btn_crit", help="Inspect urgent issues"):
                    show_critical_drilldown(f_df)
            else:
                dt.markdown("""
                    <div class="insight-wrapper insight-velocity">
                        <div>
                            <b>✨ Critical Path Stability:</b> Zero urgent items currently in flight.
                        </div>
                        <div style="height: 18px;"></div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        dt.info("Adjust filters to generate automated system insights.")[cite: 4]

    dt.markdown("---")[cite: 4]

    # --- ROW 1: ANALYTICAL CHARTS MIX ---
    col1, col2, col3 = dt.columns([3, 4, 3])[cite: 4]
    
    with col1:[cite: 4]
        dt.subheader("📋 Status Distribution Breakdown")[cite: 4]
        status_chart_data = f_df['Category Status'].value_counts().reset_index()[cite: 4]
        status_chart_data.columns = ['Status', 'Count'][cite: 4]
        
        # Original color profile[cite: 4]
        status_colors = {'COMPLETED': '#10B981', 'HOLD': '#F59E0B', 'ONGOING': '#065F46', 'NOT STARTED': '#94A3B8'}[cite: 4]
        fig_status = px.bar(status_chart_data, x='Status', y='Count', color='Status', color_discrete_map=status_colors)[cite: 4]
        fig_status.update_layout(showlegend=False, height=300, margin=dict(l=10, r=10, t=10, b=10))[cite: 4]
        dt.plotly_chart(fig_status, use_container_width=True)[cite: 4]
        
    with col2:[cite: 4]
        dt.subheader("🎯 Resource Productivity Breakdown + Trend")[cite: 4]
        if not f_df.empty:[cite: 4]
            # Cross-tab allocation groups[cite: 4]
            res_df = f_df.groupby(['Owner', 'Category Status']).size().unstack(fill_value=0).reset_index()[cite: 4]
            total_per_owner = f_df.groupby('Owner').size().reset_index(name='Total Tasks')[cite: 4]
            res_merged = pd.merge(res_df, total_per_owner, on='Owner')[cite: 4]
            
            # Composite Bar & Trend Line generation[cite: 4]
            fig_res = go.Figure()[cite: 4]
            for status_step, color_hex in [('COMPLETED', '#10B981'), ('HOLD', '#F59E0B'), ('ONGOING', '#065F46'), ('NOT STARTED', '#94A3B8')]:[cite: 4]
                if status_step in res_merged.columns:[cite: 4]
                    fig_res.add_trace(go.Bar(name=status_step, x=res_merged['Owner'], y=res_merged[status_step], marker_color=color_hex))[cite: 4]
            
            fig_res.add_trace(go.Scatter(name='Total Volume Trend', x=res_merged['Owner'], y=res_merged['Total Tasks'], mode='lines+markers', line=dict(color='#8B5CF6', width=3)))[cite: 4]
            fig_res.update_layout(barmode='stack', height=300, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), margin=dict(l=10, r=10, t=10, b=10))[cite: 4]
            dt.plotly_chart(fig_res, use_container_width=True)[cite: 4]

    with col3:[cite: 4]
        dt.subheader("🔥 Current Priority Allocation")[cite: 4]
        priority_chart_data = f_df['Priority'].value_counts().reset_index()[cite: 4]
        priority_chart_data.columns = ['Priority', 'Count'][cite: 4]
        priority_chart_data = priority_chart_data.sort_values('Priority')[cite: 4]
        
        # Original Priority custom color gradient[cite: 4]
        prio_colors = {
            "1. Urgent 🔴": "#DC2626",[cite: 4]
            "2. High 🟡": "#F59E0B",[cite: 4]
            "3. Normal 🔵": "#3B82F6",[cite: 4]
            "4. Low ⚪": "#10B981",[cite: 4]
            "5. None 📋": "#94A3B8"[cite: 4]
        }
        fig_prio = px.bar(priority_chart_data, x='Count', y='Priority', orientation='h', color='Priority', color_discrete_map=prio_colors)[cite: 4]
        fig_prio.update_layout(showlegend=False, height=300, margin=dict(l=10, r=10, t=10, b=10))[cite: 4]
        dt.plotly_chart(fig_prio, use_container_width=True)[cite: 4]

    dt.markdown("---")[cite: 4]

    # --- ROW 2: TEAM CAPACITY PIE MATRIX ---
    r2_left, r2_right = dt.columns([4, 6])[cite: 4]
    
    with r2_left:[cite: 4]
        dt.subheader("👥 Overall Task Share Distribution")[cite: 4]
        member_shares = f_df['Owner'].value_counts().reset_index()[cite: 4]
        member_shares.columns = ['Team Member', 'Total Work Volume'][cite: 4]
        
        fig_pie = px.pie(member_shares, values='Total Work Volume', names='Team Member', hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe)[cite: 4]
        fig_pie.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="v", yanchor="middle", y=0.5))[cite: 4]
        dt.plotly_chart(fig_pie, use_container_width=True)[cite: 4]

    with r2_right:[cite: 4]
        dt.subheader("👥 Cross-Tabulation Workload Matrix Reference")[cite: 4]
        cross_tab = pd.crosstab(f_df['Owner'], f_df['Category Status'])[cite: 4]
        for col_status in ['NOT STARTED', 'ONGOING', 'HOLD', 'COMPLETED']:[cite: 4]
            if col_status not in cross_tab.columns:[cite: 4]
                cross_tab[col_status] = 0[cite: 4]
        cross_tab = cross_tab[['NOT STARTED', 'ONGOING', 'HOLD', 'COMPLETED']][cite: 4]
        dt.dataframe(cross_tab, use_container_width=True)[cite: 4]

    dt.markdown("---")[cite: 4]

    # --- ROW 3: CALENDAR ESSENTIALS DELIVERIES ---
    dt.subheader("📅 Operational Delivery: Rolling Window Pipelines")[cite: 4]
    
    today_dt = datetime.now().date()[cite: 4]
    start_week = today_dt - timedelta(days=today_dt.weekday())[cite: 4]
    end_week = start_week + timedelta(days=6)[cite: 4]
    end_upcoming = end_week + timedelta(days=7)[cite: 4]
    
    # Bucket allocation filter layers[cite: 4]
    weekly_matrix = f_df[(f_df['Due Date'] >= start_week) & (f_df['Due Date'] <= end_week)][cite: 4]
    upcoming_matrix = f_df[(f_df['Due Date'] > end_week) & (f_df['Due Date'] <= end_upcoming)][cite: 4]
    rest_matrix = f_df[(f_df['Due Date'] > end_upcoming) | (f_df['Due Date'].isnull())][cite: 4]
    
    tab1, tab2, tab3 = dt.tabs(["✨ This Week Essentials", "🔮 Upcoming (Next Week Window)", "📥 Future Queue / Rest of Scope"])[cite: 4]
    
    with tab1:[cite: 4]
        if not weekly_matrix.empty:[cite: 4]
            dt.dataframe(weekly_matrix[["Initiative / Task", "Owner", "Category Status", "Priority", "Due Date"]], hide_index=True, use_container_width=True)[cite: 4]
        else:
            dt.info("No tasks are scheduled to terminate within the current calendar week parameters.")[cite: 4]
            
    with tab2:[cite: 4]
        if not upcoming_matrix.empty:[cite: 4]
            dt.dataframe(upcoming_matrix[["Initiative / Task", "Owner", "Category Status", "Priority", "Due Date"]], hide_index=True, use_container_width=True)[cite: 4]
        else:
            dt.info("No mid-term milestones mapped to the upcoming horizon frame.")[cite: 4]
            
    with tab3:[cite: 4]
        if not rest_matrix.empty:[cite: 4]
            dt.dataframe(rest_matrix[["Initiative / Task", "Owner", "Category Status", "Priority", "Due Date"]], hide_index=True, use_container_width=True)[cite: 4]
        else:
            dt.info("Future queue data layer empty.")[cite: 4]

    dt.markdown("###")[cite: 4]

    # --- ROW 4: DATA ENGINE DRILLDOWN LEDGER ---
    with dt.expander("🔍 Enterprise Master Data Ledger (Full System Drilldown)", expanded=False):[cite: 4]
        dt.dataframe(
            f_df[["Task ID", "Initiative / Task", "Owner", "Full Team Allocated", "Category Status", "Raw Status", "Priority", "Due Date", "Segment"]].sort_values(by="Priority"),[cite: 4]
            use_container_width=True, [cite: 4]
            hide_index=True[cite: 4]
        )
