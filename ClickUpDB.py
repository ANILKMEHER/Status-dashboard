import streamlit as dt
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- CONFIGURATION ---
CLICKUP_TOKEN = "pk_63097086_RCS1F8Y5W38W0FHXFYWA45346XRZGS0P"
LIST_ID = "901612921295"  
REFRESH_INTERVAL = 120  # Smart local cache lifetime (2 minutes)

headers = {
    "Authorization": CLICKUP_TOKEN,
    "Content-Type": "application/json"
}

dt.set_page_config(layout="wide", page_title="Executive Delivery Insights", page_icon="📊")

# --- HIGH-END UI STYLING ---
dt.markdown("""
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 1rem;}
    div[data-testid="stMetricValue"] {font-size: 32px; font-weight: 800; color: #1E3A8A;}
    div[data-testid="stMetricLabel"] {font-size: 13px; font-weight: 700; color: #4B5563; text-transform: uppercase;}
    .stDataFrame {border: 1px solid #E5E7EB; border-radius: 8px;}
    </style>
    """, unsafe_allow_html=True)

# --- DATA EXTRACTION WITH PAGINATION ENGINE ---
@dt.cache_data(ttl=REFRESH_INTERVAL)
def fetch_all_clickup_tasks(list_id):
    all_tasks = []
    page = 0
    has_more = True
    
    while has_more:
        url = f"https://api.clickup.com/api/v2/list/{list_id}/task?include_closed=true&page={page}"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            if page == 0:
                alt_url = f"https://api.clickup.com/api/v2/space/{list_id}/task?include_closed=true&page={page}"
                response = requests.get(alt_url, headers=headers)
                if response.status_code != 200:
                    break
            else:
                break
                
        data = response.json()
        page_tasks = data.get('tasks', [])
        all_tasks.extend(page_tasks)
        
        if len(page_tasks) == 20:  
            page += 1
        else:
            has_more = False
            
    return all_tasks

def transform_and_enrich_data(tasks):
    if not tasks:
        return pd.DataFrame()
    
    records = []
    for t in tasks:
        # Date Normalization
        raw_due = t.get('due_date')
        due_dt = datetime.fromtimestamp(int(raw_due) / 1000) if raw_due else None
        
        if due_dt:
            task_year = str(due_dt.year)
            task_month = due_dt.strftime('%B')
            task_quarter = f"Q{(due_dt.month - 1) // 3 + 1}"
            task_date = due_dt.date()
        else:
            task_year = "No Date Allocated"
            task_month = "No Date Allocated"
            task_quarter = "No Date Allocated"
            task_date = None

        # Assignee Extraction
        assignees_list = [user.get('username', 'Unassigned') for user in t.get('assignees', [])]
        primary_assignee = assignees_list[0] if assignees_list else "Unassigned"
        all_team = ", ".join(assignees_list) if assignees_list else "Unassigned"
        
        # Priority Normalization
        p_map = {"1": "1. Urgent 🔴", "2": "2. High 🟡", "3": "3. Normal 🔵", "4": "4. Low ⚪"}
        p_info = t.get('priority')
        priority_str = p_map.get(str(p_info.get('id')) if p_info else "", "5. None 📋")
        
        # BI Status Categorization
        status_obj = t.get('status', {})
        raw_status = status_obj.get('status', 'OPEN').upper()
        is_closed_type = status_obj.get('type') == 'closed'
        
        if is_closed_type or raw_status in ['CLOSED', 'COMPLETE', 'DONE', 'RESOLVED']:
            bi_status = 'COMPLETED'
        elif raw_status in ['ON HOLD', 'HOLD', 'BLOCKED', 'DEFERRED']:
            bi_status = 'HOLD'
        elif raw_status in ['OPEN', 'NOT STARTED', 'BACKLOG', 'TO DO']:
            bi_status = 'NOT STARTED'
        else:
            bi_status = 'ONGOING'

        # Segment Extraction
        custom_category = "General Initiatives"
        for cf in t.get('custom_fields', []):
            if 'category' in cf.get('name', '').lower() and cf.get('value'):
                if isinstance(cf.get('value'), list):
                    custom_category = cf['value'][0]
                elif isinstance(cf.get('value'), int) and cf.get('type_config', {}).get('options'):
                    opts = cf['type_config']['options']
                    custom_category = next((o['name'] for o in opts if o['orderindex'] == cf['value']), "General Initiatives")
                else:
                    custom_category = str(cf.get('value'))

        records.append({
            "Task ID": t.get('id'),
            "Initiative / Task": t.get('name'),
            "Raw Status": raw_status,
            "Category Status": bi_status,
            "Priority": priority_str,
            "Owner": primary_assignee,
            "Full Team Allocated": all_team,
            "Due Date": task_date,
            "Year": task_year,
            "Quarter": task_quarter,
            "Month": task_month,
            "Segment": custom_category
        })
        
    return pd.DataFrame(records)

# --- DRILLDOWN MODAL DEFINITIONS ---
COLS_TO_SHOW = ["Task ID", "Initiative / Task", "Owner", "Category Status", "Priority", "Due Date", "Segment"]

@dt.dialog("⚠️ Resource Allocation Drilldown")
def show_resource_drilldown(df, owner):
    dt.write(f"Showing all active tasks currently assigned to **{owner}**:")
    active_user_tasks = df[(df['Owner'] == owner) & (df['Category Status'] == 'ONGOING')][COLS_TO_SHOW]
    dt.dataframe(active_user_tasks, hide_index=True, use_container_width=True)

@dt.dialog("🚨 Slippage Exception Drilldown")
def show_slippage_drilldown(df):
    dt.write("Showing all pending tasks with past due dates:")
    today_val = datetime.now().date()
    overdue_df = df[(df['Category Status'] != 'COMPLETED') & (df['Due Date'] < today_val) & (df['Due Date'].notnull())][COLS_TO_SHOW]
    dt.dataframe(overdue_df.sort_values(by="Due Date"), hide_index=True, use_container_width=True)

@dt.dialog("📋 Pipeline Velocity & Backlog Drilldown")
def show_backlog_drilldown(df):
    dt.write("Showing all unstarted backlog tasks:")
    backlog_df = df[df['Category Status'] == 'NOT STARTED'][COLS_TO_SHOW]
    dt.dataframe(backlog_df, hide_index=True, use_container_width=True)

@dt.dialog("🔥 Critical Path Pressure Drilldown")
def show_critical_drilldown(df):
    dt.write("Showing active Urgent tasks in production:")
    urgent_df = df[(df['Priority'].str.contains("Urgent")) & (df['Category Status'] == 'ONGOING')][COLS_TO_SHOW]
    dt.dataframe(urgent_df, hide_index=True, use_container_width=True)

# --- RUN BI PIPELINE ---
raw_data = fetch_all_clickup_tasks(LIST_ID)
master_df = transform_and_enrich_data(raw_data)

if master_df.empty:
    dt.info("📡 Connecting to ClickUp data layers... Confirm items populate your workspace list.")
else:
    # --- ENTERPRISE HEADER ---
    dt.title("📊 Strategic Project Portfolio & Resource Intelligence Hub")
    dt.caption(f"Sync Engine: Operational Continuous Polling | System Time: {datetime.now().strftime('%Y-%m-%d %H:%M')} IST")
    dt.markdown("---")

    # --- ADVANCED DATE & FIELD SLICER SIDEBAR ---
    with dt.sidebar:
        dt.header("🎛️ Interactive Filter Slicers")
        
        dt.subheader("🗓️ Temporal Slicers")
        years_available = sorted(master_df['Year'].unique(), reverse=True)
        sel_years = dt.multiselect("Select Year", options=years_available, default=years_available)
        
        quarters_available = sorted(master_df['Quarter'].unique())
        sel_quarters = dt.multiselect("Select Quarter", options=quarters_available, default=quarters_available)
        
        months_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "No Date Allocated"]
        months_available = [m for m in months_order if m in master_df['Month'].unique()]
        sel_months = dt.multiselect("Select Month", options=months_available, default=months_available)
        
        valid_dates = master_df[master_df['Due Date'].notnull()]['Due Date']
        min_date = valid_dates.min() if not valid_dates.empty else datetime.now().date()
        max_date = valid_dates.max() if not valid_dates.empty else datetime.now().date() + timedelta(days=90)
        
        start_date, end_date = dt.date_input("Custom Date Range Window", [min_date, max_date])

        dt.markdown("---")
        dt.subheader("👥 Resource & Structural Slicers")
        sel_owners = dt.multiselect("Filter Task Owners", options=sorted(master_df['Owner'].unique()), default=master_df['Owner'].unique())
        sel_priorities = dt.multiselect("Filter Priority Levels", options=sorted(master_df['Priority'].unique()), default=master_df['Priority'].unique())
        sel_segments = dt.multiselect("Filter Functional Segments", options=sorted(master_df['Segment'].unique()), default=master_df['Segment'].unique())

    # --- PROCESS FILTER LOGIC ---
    f_df = master_df[
        (master_df['Year'].isin(sel_years)) & 
        (master_df['Quarter'].isin(sel_quarters)) & 
        (master_df['Month'].isin(sel_months)) & 
        (master_df['Owner'].isin(sel_owners)) & 
        (master_df['Priority'].isin(sel_priorities)) & 
        (master_df['Segment'].isin(sel_segments))
    ]
    
    def date_bound_check(row_date):
        if row_date is None:
            return True  
        return start_date <= row_date <= end_date
        
    if not f_df.empty:
        f_df = f_df[f_df['Due Date'].apply(date_bound_check)]

    # --- EXECUTIVE SCORECARD METRICS ---
    total_volume = len(f_df)
    completed_volume = len(f_df[f_df['Category Status'] == 'COMPLETED'])
    ongoing_volume = len(f_df[f_df['Category Status'] == 'ONGOING'])
    hold_volume = len(f_df[f_df['Category Status'] == 'HOLD'])
    unstarted_volume = len(f_df[f_df['Category Status'] == 'NOT STARTED'])

    # Calculation adjustment: Exclude HOLD status from completion denominator completely
    effective_denominator = total_volume - hold_volume
    if effective_denominator > 0:
        closure_rate_calc = int((completed_volume / effective_denominator) * 100)
    else:
        closure_rate_calc = 0

    kpi1, kpi2, kpi3, kpi4, kpi5 = dt.columns(5)
    kpi1.metric("Total Scope Items", total_volume)
    kpi2.metric("Active (Ongoing)", ongoing_volume)
    kpi3.metric("Completed Scope", completed_volume, delta=f"{closure_rate_calc}% Adjusted Closure Rate")
    kpi4.metric("On Hold Tasks", hold_volume, delta="Excluded From Analytics", delta_color="off")
    kpi5.metric("Backlog Pipeline", unstarted_volume)

    dt.markdown("---")

    # --- AUTOMATED KEY INSIGHTS ENGINE (WITH MODAL POPUPS) ---
    dt.subheader("💡 Automated Executive Insights & Exceptions")
    
    if not f_df.empty:
        ins_col1, ins_col2 = dt.columns(2)
        
        with ins_col1:
            # 1. Resource Workload Bottleneck Insight
            active_only = f_df[f_df['Category Status'] == 'ONGOING']
            if not active_only.empty:
                top_owner = active_only['Owner'].value_counts().idxmax()
                top_owner_count = active_only['Owner'].value_counts().max()
                if top_owner != "Unassigned" and top_owner_count >= 3:
                    dt.warning(f"⚠️ **Resource Allocation Crunch:** **{top_owner}** is currently managing the highest volume of in-flight work with **{top_owner_count} active tasks**.")
                    if dt.button(f"🔍 Drilldown: View {top_owner}'s Tasks", key="btn_resource_crunch", help="Click for more info on active tasks"):
                        show_resource_drilldown(f_df, top_owner)
                else:
                    dt.success("AI Insight: Active tasks are distributed evenly across the immediate delivery team.")
            
            # 2. Backlog Risk Assessment
            if unstarted_volume > (total_volume * 0.40):
                dt.info(f"📋 **Pipeline Concentration:** Over 40% of your project scope ({unstarted_volume} tasks) is sitting in 'Not Started'.")
            else:
                dt.info(f"📋 **Pipeline Velocity:** Backlog is under control, representing healthy future queue metrics.")
            if dt.button("🔍 Drilldown: View Backlog Pipeline", key="btn_backlog", help="Click for more info on unstarted backlog items"):
                show_backlog_drilldown(f_df)

        with ins_col2:
            # 3. Overdue Check (Slippage Exception)
            today_date = datetime.now().date()
            overdue_tasks = f_df[(f_df['Category Status'] != 'COMPLETED') & (f_df['Due Date'] < today_date) & (f_df['Due Date'].notnull())]
            if not overdue_tasks.empty:
                dt.error(f"🚨 **Slippage Exception:** Found **{len(overdue_tasks)} pending tasks** with past due dates. Immediate milestone alignment required.")
                if dt.button(f"🔍 Drilldown: View {len(overdue_tasks)} Overdue Tasks", key="btn_slippage", help="Click for more info on delayed tasks"):
                    show_slippage_drilldown(f_df)
            else:
                dt.success("🎯 **Timeline Discipline:** Zero pending items are overdue within this filtered dataset.")

            # 4. Critical Path Tracking
            urgent_active = f_df[(f_df['Priority'].str.contains("Urgent")) & (f_df['Category Status'] == 'ONGOING')]
            if not urgent_active.empty:
                dt.error(f"🔥 **Critical Path Pressure:** There are **{len(urgent_active)} URGENT tasks actively running** in production.")
                if dt.button(f"🔍 Drilldown: View {len(urgent_active)} Critical Tasks", key="btn_critical", help="Click for more info on critical path tasks"):
                    show_critical_drilldown(f_df)
            else:
                dt.info("No urgent tasks currently flagged in production.")
    else:
        dt.info("Adjust filters to generate automated system insights.")

    dt.markdown("---")

    # --- ROW 1: ANALYTICAL CHARTS MIX ---
    col1, col2, col3 = dt.columns([3, 4, 3])
    
    with col1:
        dt.subheader("📋 Status Distribution Breakdown")
        status_chart_data = f_df['Category Status'].value_counts().reset_index()
        status_chart_data.columns = ['Status', 'Count']
        
        # Color profile mapping rule applied explicitly
        status_colors = {'COMPLETED': '#10B981', 'HOLD': '#F59E0B', 'ONGOING': '#065F46', 'NOT STARTED': '#94A3B8'}
        fig_status = px.bar(status_chart_data, x='Status', y='Count', color='Status', color_discrete_map=status_colors)
        fig_status.update_layout(showlegend=False, height=300, margin=dict(l=10, r=10, t=10, b=10))
        dt.plotly_chart(fig_status, use_container_width=True)
        
    with col2:
        dt.subheader("🎯 Resource Productivity Breakdown + Trend")
        if not f_df.empty:
            # Cross-tab allocation groups
            res_df = f_df.groupby(['Owner', 'Category Status']).size().unstack(fill_value=0).reset_index()
            total_per_owner = f_df.groupby('Owner').size().reset_index(name='Total Tasks')
            res_merged = pd.merge(res_df, total_per_owner, on='Owner')
            
            # Composite Bar & Trend Line generation
            fig_res = go.Figure()
            for status_step, color_hex in [('COMPLETED', '#10B981'), ('HOLD', '#F59E0B'), ('ONGOING', '#065F46'), ('NOT STARTED', '#94A3B8')]:
                if status_step in res_merged.columns:
                    fig_res.add_trace(go.Bar(name=status_step, x=res_merged['Owner'], y=res_merged[status_step], marker_color=color_hex))
            
            fig_res.add_trace(go.Scatter(name='Total Volume Trend', x=res_merged['Owner'], y=res_merged['Total Tasks'], mode='lines+markers', line=dict(color='#8B5CF6', width=3)))
            fig_res.update_layout(barmode='stack', height=300, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), margin=dict(l=10, r=10, t=10, b=10))
            dt.plotly_chart(fig_res, use_container_width=True)

    with col3:
        dt.subheader("🔥 Current Priority Allocation")
        priority_chart_data = f_df['Priority'].value_counts().reset_index()
        priority_chart_data.columns = ['Priority', 'Count']
        priority_chart_data = priority_chart_data.sort_values('Priority')
        
        # Priority custom color gradient: Urgent (Deep Red) down to None (Soft Muted Slate)
        prio_colors = {
            "1. Urgent 🔴": "#DC2626",
            "2. High 🟡": "#F59E0B",
            "3. Normal 🔵": "#3B82F6",
            "4. Low ⚪": "#10B981",
            "5. None 📋": "#94A3B8"
        }
        fig_prio = px.bar(priority_chart_data, x='Count', y='Priority', orientation='h', color='Priority', color_discrete_map=prio_colors)
        fig_prio.update_layout(showlegend=False, height=300, margin=dict(l=10, r=10, t=10, b=10))
        dt.plotly_chart(fig_prio, use_container_width=True)

    dt.markdown("---")

    # --- ROW 2: TEAM CAPACITY PIE MATRIX ---
    r2_left, r2_right = dt.columns([4, 6])
    
    with r2_left:
        dt.subheader("👥 Overall Task Share Distribution")
        member_shares = f_df['Owner'].value_counts().reset_index()
        member_shares.columns = ['Team Member', 'Total Work Volume']
        
        fig_pie = px.pie(member_shares, values='Total Work Volume', names='Team Member', hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe)
        fig_pie.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="v", yanchor="middle", y=0.5))
        dt.plotly_chart(fig_pie, use_container_width=True)

    with r2_right:
        dt.subheader("👥 Cross-Tabulation Workload Matrix Reference")
        cross_tab = pd.crosstab(f_df['Owner'], f_df['Category Status'])
        for col_status in ['NOT STARTED', 'ONGOING', 'HOLD', 'COMPLETED']:
            if col_status not in cross_tab.columns:
                cross_tab[col_status] = 0
        cross_tab = cross_tab[['NOT STARTED', 'ONGOING', 'HOLD', 'COMPLETED']]
        dt.dataframe(cross_tab, use_container_width=True)

    dt.markdown("---")

    # --- ROW 3: CALENDAR ESSENTIALS DELIVERIES ---
    dt.subheader("📅 Operational Delivery: Rolling Window Pipelines")
    
    today_dt = datetime.now().date()
    start_week = today_dt - timedelta(days=today_dt.weekday())
    end_week = start_week + timedelta(days=6)
    end_upcoming = end_week + timedelta(days=7)
    
    # Bucket allocation filter layers
    weekly_matrix = f_df[(f_df['Due Date'] >= start_week) & (f_df['Due Date'] <= end_week)]
    upcoming_matrix = f_df[(f_df['Due Date'] > end_week) & (f_df['Due Date'] <= end_upcoming)]
    rest_matrix = f_df[(f_df['Due Date'] > end_upcoming) | (f_df['Due Date'].isnull())]
    
    tab1, tab2, tab3 = dt.tabs(["✨ This Week Essentials", "🔮 Upcoming (Next Week Window)", "📥 Future Queue / Rest of Scope"])
    
    with tab1:
        if not weekly_matrix.empty:
            dt.dataframe(weekly_matrix[["Initiative / Task", "Owner", "Category Status", "Priority", "Due Date"]], hide_index=True, use_container_width=True)
        else:
            dt.info("No tasks are scheduled to terminate within the current calendar week parameters.")
            
    with tab2:
        if not upcoming_matrix.empty:
            dt.dataframe(upcoming_matrix[["Initiative / Task", "Owner", "Category Status", "Priority", "Due Date"]], hide_index=True, use_container_width=True)
        else:
            dt.info("No mid-term milestones mapped to the upcoming horizon frame.")
            
    with tab3:
        if not rest_matrix.empty:
            dt.dataframe(rest_matrix[["Initiative / Task", "Owner", "Category Status", "Priority", "Due Date"]], hide_index=True, use_container_width=True)
        else:
            dt.info("Future queue data layer empty.")

    dt.markdown("###")

    # --- ROW 4: DATA ENGINE DRILLDOWN LEDGER ---
    with dt.expander("🔍 Enterprise Master Data Ledger (Full System Drilldown)", expanded=False):
        dt.dataframe(
            f_df[["Task ID", "Initiative / Task", "Owner", "Full Team Allocated", "Category Status", "Raw Status", "Priority", "Due Date", "Segment"]].sort_values(by="Priority"),
            use_container_width=True, 
            hide_index=True
        )
