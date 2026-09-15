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

# --- CUSTOM CARD & 3D GRADIENT STYLING ---
dt.markdown("""
    <style>
    .block-container {
        padding-top: 1.5rem; 
        padding-bottom: 2rem;
    }

    /* 3D Elevated Metric Tile Cards */
    .kpi-card {
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(0, 0, 0, 0.06);
        min-height: 118px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.05);
    }
    .kpi-label {
        font-size: 13px;
        font-weight: 600;
        color: #334155;
        margin-bottom: 4px;
    }
    .kpi-val {
        font-size: 34px;
        font-weight: 800;
        line-height: 1.1;
    }
    .kpi-badge {
        display: inline-block;
        font-size: 11px;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        margin-top: 6px;
        width: fit-content;
    }

    /* 5 Tile Color Gradients: Green Gradient (1 to 3), Yellow (4), Reddish (5) */
    .kpi-green-1 {
        background: linear-gradient(145deg, #F0FDF4, #DCFCE7);
        border-left: 4px solid #86EFAC;
    }
    .kpi-green-1 .kpi-val { color: #166534; }

    .kpi-green-2 {
        background: linear-gradient(145deg, #DCFCE7, #BBF7D0);
        border-left: 4px solid #4ADE80;
    }
    .kpi-green-2 .kpi-val { color: #15803D; }

    .kpi-green-3 {
        background: linear-gradient(145deg, #BBF7D0, #86EFAC);
        border-left: 4px solid #22C55E;
    }
    .kpi-green-3 .kpi-val { color: #14532D; }
    .kpi-green-3 .kpi-badge {
        background: #DCFCE7;
        color: #166534;
        border: 1px solid #86EFAC;
    }

    .kpi-yellow-4 {
        background: linear-gradient(145deg, #FFFBEB, #FEF3C7);
        border-left: 4px solid #F59E0B;
    }
    .kpi-yellow-4 .kpi-val { color: #B45309; }
    .kpi-yellow-4 .kpi-badge {
        background: #F3F4F6;
        color: #4B5563;
        border: 1px solid #E5E7EB;
    }

    .kpi-red-5 {
        background: linear-gradient(145deg, #FEF2F2, #FEE2E2);
        border-left: 4px solid #EF4444;
    }
    .kpi-red-5 .kpi-val { color: #B91C1C; }

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

    /* DataFrame Table */
    .stDataFrame {
        border: 1px solid #E5E7EB; 
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
    }
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

@dt.dialog("⚠️ Resource Allocation Details")
def show_resource_drilldown(df, owner):
    dt.markdown(f"**In-Flight Tasks Assigned to {owner}:**")
    active_user_tasks = df[(df['Owner'] == owner) & (df['Category Status'] == 'ONGOING')][COLS_TO_SHOW]
    dt.dataframe(active_user_tasks, hide_index=True, use_container_width=True)

@dt.dialog("🚨 Slippage Exception Details")
def show_slippage_drilldown(df):
    dt.markdown("**In-Flight Overdue Tasks Requiring Milestone Alignment (Excluding Hold & Backlog):**")
    today_val = datetime.now().date()
    overdue_df = df[(df['Category Status'] == 'ONGOING') & (df['Due Date'] < today_val) & (df['Due Date'].notnull())][COLS_TO_SHOW]
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
    
    with kpi1:
        dt.markdown(f"""
            <div class="kpi-card kpi-green-1">
                <div class="kpi-label">Total Scope Items</div>
                <div class="kpi-val">{total_volume}</div>
                <div>&nbsp;</div>
            </div>
        """, unsafe_allow_html=True)

    with kpi2:
        dt.markdown(f"""
            <div class="kpi-card kpi-green-2">
                <div class="kpi-label">Active (Ongoing)</div>
                <div class="kpi-val">{ongoing_volume}</div>
                <div>&nbsp;</div>
            </div>
        """, unsafe_allow_html=True)

    with kpi3:
        dt.markdown(f"""
            <div class="kpi-card kpi-green-3">
                <div class="kpi-label">Completed Scope</div>
                <div class="kpi-val">{completed_volume}</div>
                <div class="kpi-badge">↑ {closure_rate_calc}% Adjusted Closure Rate</div>
            </div>
        """, unsafe_allow_html=True)

    with kpi4:
        dt.markdown(f"""
            <div class="kpi-card kpi-yellow-4">
                <div class="kpi-label">On Hold Tasks</div>
                <div class="kpi-val">{hold_volume}</div>
                <div class="kpi-badge">↑ Excluded From Analytics</div>
            </div>
        """, unsafe_allow_html=True)

    with kpi5:
        dt.markdown(f"""
            <div class="kpi-card kpi-red-5">
                <div class="kpi-label">Backlog Pipeline</div>
                <div class="kpi-val">{unstarted_volume}</div>
                <div>&nbsp;</div>
            </div>
        """, unsafe_allow_html=True)

    dt.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # --- AUTOMATED KEY INSIGHTS WITH INLINE BOTTOM-RIGHT HYPERLINKS ---
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
            
            # 2. Backlog Risk Assessment
            if unstarted_volume > (total_volume * 0.40):
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

        with ins_col2:
            # 3. Adjusted Slippage Exception Logic: Strictly Ongoing in-flight tasks past due (Excludes Hold and Not Started)
            today_date = datetime.now().date()
            overdue_tasks = f_df[(f_df['Category Status'] == 'ONGOING') & (f_df['Due Date'] < today_date) & (f_df['Due Date'].notnull())]
            if not overdue_tasks.empty:
                dt.markdown(f"""
                    <div class="insight-wrapper insight-slippage">
                        <div>
                            <b>🚨 Slippage Exception:</b> Found <b>{len(overdue_tasks)} active in-flight tasks</b> with past due dates. Immediate milestone alignment required.
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
                            <b>🎯 Timeline Discipline:</b> Zero active ongoing items are overdue within this filtered dataset.
                        </div>
                        <div style="height: 18px;"></div>
                    </div>
                """, unsafe_allow_html=True)

            # 4. Critical Path Tracking
            urgent_active = f_df[(f_df['Priority'].str.contains("Urgent")) & (f_df['Category Status'] == 'ONGOING')]
            if not urgent_active.empty:
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
        dt.info("Adjust filters to generate automated system insights.")

    dt.markdown("---")

    # --- ROW 1: ANALYTICAL CHARTS MIX ---
    col1, col2, col3 = dt.columns([3, 4, 3])
    
    with col1:
        dt.subheader("📋 Status Distribution Breakdown")
        status_chart_data = f_df['Category Status'].value_counts().reset_index()
        status_chart_data.columns = ['Status', 'Count']
        
        status_colors = {'COMPLETED': '#10B981', 'HOLD': '#F59E0B', 'ONGOING': '#065F46', 'NOT STARTED': '#94A3B8'}
        fig_status = px.bar(status_chart_data, x='Status', y='Count', color='Status', color_discrete_map=status_colors)
        fig_status.update_layout(showlegend=False, height=300, margin=dict(l=10, r=10, t=10, b=10))
        dt.plotly_chart(fig_status, use_container_width=True)
        
    with col2:
        dt.subheader("🎯 Resource Productivity Breakdown + Trend")
        if not f_df.empty:
            res_df = f_df.groupby(['Owner', 'Category Status']).size().unstack(fill_value=0).reset_index()
            total_per_owner = f_df.groupby('Owner').size().reset_index(name='Total Tasks')
            res_merged = pd.merge(res_df, total_per_owner, on='Owner')
            
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
