import time
import uuid
import hmac
import hashlib
import base64
import urllib.parse
import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configuration file name
CONFIG_FILE = "embed_config.json"

def load_config():
    """Loads configuration from embed_config.json."""
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: {CONFIG_FILE} not found.")
        print("Please copy embed_config.json.example to embed_config.json and fill in your settings.")
        sys.exit(1)
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def generate_embed_url(config):
    """Generates an Embed URL (either Signed SSO URL or Private Embed URL)."""
    looker_url = config["looker_url"].rstrip("/")
    secret = config.get("embed_secret", "")
    dashboard_id = config["dashboard_id"]

    # Private Embedding Mode (Enterprise Edition or blank secret)
    if not secret or secret in ["none", "enterprise", "your_embed_secret_from_looker_admin", "your_embed_secret_here"]:
        print("Note: Running in Private Embedding Mode (no Embed Secret provided). Using standard Looker session authentication.")
        private_url = f"{looker_url}/embed/dashboards/{dashboard_id}?allow_login_screen=true&theme=Looker"
        return private_url, "private"

    # Parse host
    parsed_url = urllib.parse.urlparse(looker_url)
    host = parsed_url.netloc
    if ":" not in host:
        host = f"{host}:443"

    target_path = f"/embed/dashboards/{dashboard_id}"
    login_path = f"/login/embed/{urllib.parse.quote_plus(target_path)}"

    external_user_id = "broxel_exec_sdk"
    first_name = "Broxel"
    last_name = "SDK Executive"
    permissions = ["access_data", "see_user_dashboards"]
    models = ["training_ecommerce"]
    group_ids = []
    external_group_id = "broxel_mgmt"
    user_attributes = {}
    force_logout_login = "true"
    
    session_length = 3600
    nonce = uuid.uuid4().hex
    current_time = str(int(time.time()))

    path_to_sign = "\n".join([
        host, login_path, nonce, current_time, str(session_length),
        external_user_id, json.dumps(permissions), json.dumps(models),
        json.dumps(group_ids), external_group_id, json.dumps(user_attributes),
        force_logout_login
    ])

    key = secret.encode('utf-8')
    msg = path_to_sign.encode('utf-8')
    sig = hmac.new(key, msg, hashlib.sha1).digest()
    signature = base64.b64encode(sig).decode('utf-8')

    query_params = {
        "nonce": nonce, "time": current_time, "session_length": str(session_length),
        "external_user_id": external_user_id, "permissions": json.dumps(permissions),
        "models": json.dumps(models), "group_ids": json.dumps(group_ids),
        "external_group_id": external_group_id, "user_attributes": json.dumps(user_attributes),
        "force_logout_login": force_logout_login, "signature": signature,
        "first_name": first_name, "last_name": last_name
    }

    encoded_params = urllib.parse.urlencode(query_params)
    sso_url = f"{looker_url}{login_path}?{encoded_params}"
    return sso_url, "sso"

def render_page(title, active_tab, content_html, config, embed_url="", mode="private"):
    mode_badge = "Looker Enterprise • Embed SDK v1.8" if mode == "private" else "Looker Embed Edition • Signed SSO SDK"
    mode_color = "#0075ff" if mode == "private" else "#7c3aed"
    
    nav_items = [
        ("BROXEL PAY & ANALYTICS", [
            ("/", "Executive Dashboard", "fa-chart-line"),
            ("/reports", "Financial & MXN Reports", "fa-file-invoice-dollar"),
        ]),
        ("PLATFORM & ARCHITECTURE", [
            ("/about", "Looker Embed SDK Guide", "fa-layer-group"),
            ("/settings", "Account Preferences", "fa-sliders"),
        ])
    ]
    
    sidebar_html = ""
    for section_title, links in nav_items:
        sidebar_html += f'<div class="sidebar-section">{section_title}</div>\n<div class="sidebar-menu">\n'
        for path, name, icon in links:
            active_class = "active" if active_tab == name else ""
            sidebar_html += f'<a href="{path}" class="nav-item {active_class}"><i class="fa-solid {icon}"></i> <span>{name}</span></a>\n'
        sidebar_html += '</div>\n'

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Broxel Pay Analytics Portal</title>
    <!-- Google Fonts (Figtree & Open Sans as used on broxel.com) & FontAwesome -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Figtree:wght@300;400;500;600;700;800&family=Open+Sans:wght@300;400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Looker Embed SDK -->
    <script src="https://unpkg.com/@looker/embed-sdk@1.8.0/dist/embed-sdk.js"></script>
    <style>
        :root {{
            --bg-main: #f4f7fa;
            --sidebar-bg: #0b1727;
            --sidebar-hover: #16263b;
            --text-main: #1e293b;
            --text-muted: #64748b;
            --border-color: #e2e8f0;
            --broxel-blue: #0075ff;
            --broxel-blue-hover: #005ce6;
            --broxel-teal: #00c2b2;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Figtree', 'Open Sans', sans-serif; }}
        body {{ background-color: var(--bg-main); color: var(--text-main); display: flex; min-height: 100vh; overflow-x: hidden; }}
        
        /* Left Sidebar (Broxel Navy Theme) */
        .sidebar {{ width: 260px; background-color: var(--sidebar-bg); color: #94a3b8; display: flex; flex-direction: column; position: fixed; height: 100vh; z-index: 50; border-right: 1px solid #16263b; box-shadow: 4px 0 15px rgba(0,0,0,0.1); }}
        .brand {{ padding: 1.5rem 1.5rem; display: flex; align-items: center; justify-content: flex-start; text-decoration: none; border-bottom: 1px solid #16263b; }}
        .brand img {{ height: 34px; filter: brightness(0) invert(1); transition: opacity 0.2s; }}
        .brand img:hover {{ opacity: 0.9; }}
        .sidebar-content {{ flex: 1; padding: 1.5rem 1rem; overflow-y: auto; }}
        .sidebar-section {{ font-size: 0.75rem; font-weight: 700; color: #475569; letter-spacing: 0.08em; margin: 1rem 0.5rem 0.5rem; text-transform: uppercase; }}
        .sidebar-menu {{ display: flex; flex-direction: column; gap: 0.35rem; margin-bottom: 1.5rem; }}
        .nav-item {{ display: flex; align-items: center; gap: 0.85rem; padding: 0.8rem 1rem; color: #cbd5e1; text-decoration: none; font-weight: 500; font-size: 0.95rem; border-radius: 8px; transition: all 0.2s; }}
        .nav-item:hover {{ background-color: var(--sidebar-hover); color: white; }}
        .nav-item.active {{ background-color: var(--broxel-blue); color: white; font-weight: 700; box-shadow: 0 4px 12px rgba(0, 117, 255, 0.4); }}
        .nav-item i {{ width: 20px; text-align: center; font-size: 1.1rem; }}
        
        /* Sidebar Footer / User Widget */
        .sidebar-footer {{ padding: 1rem; border-top: 1px solid #16263b; background-color: #070f1a; }}
        .user-widget {{ display: flex; align-items: center; gap: 0.75rem; padding: 0.5rem; border-radius: 8px; }}
        .avatar {{ width: 38px; height: 38px; border-radius: 50%; background: linear-gradient(135deg, var(--broxel-teal), var(--broxel-blue)); display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 1rem; flex-shrink: 0; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }}
        .user-info {{ overflow: hidden; }}
        .user-name {{ color: white; font-size: 0.875rem; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .user-role {{ color: #64748b; font-size: 0.75rem; font-weight: 500; }}
        
        /* Main Content Wrapper */
        .main-wrapper {{ margin-left: 260px; flex: 1; display: flex; flex-direction: column; min-width: 0; }}
        
        /* Top Navbar */
        .topbar {{ height: 70px; background-color: white; border-bottom: 1px solid var(--border-color); display: flex; align-items: center; justify-content: space-between; padding: 0 2.5rem; position: sticky; top: 0; z-index: 40; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }}
        .search-box {{ display: flex; align-items: center; background-color: #f4f7fa; padding: 0.55rem 1.1rem; border-radius: 8px; width: 380px; border: 1px solid transparent; transition: all 0.2s; }}
        .search-box:focus-within {{ background-color: white; border-color: var(--broxel-blue); box-shadow: 0 0 0 3px rgba(0, 117, 255, 0.1); }}
        .search-box i {{ color: #94a3b8; margin-right: 0.75rem; }}
        .search-box input {{ border: none; background: transparent; outline: none; font-size: 0.875rem; width: 100%; color: #0f172a; font-weight: 500; }}
        .topbar-actions {{ display: flex; align-items: center; gap: 1.5rem; }}
        .mode-badge {{ display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.45rem 0.95rem; border-radius: 9999px; font-size: 0.8rem; font-weight: 700; background-color: {mode_color}12; color: {mode_color}; border: 1px solid {mode_color}30; letter-spacing: 0.02em; }}
        .mode-badge i {{ font-size: 0.5rem; }}
        .icon-btn {{ background: transparent; border: none; color: #64748b; font-size: 1.15rem; cursor: pointer; padding: 0.5rem; border-radius: 8px; transition: all 0.2s; position: relative; }}
        .icon-btn:hover {{ background-color: #f4f7fa; color: var(--broxel-blue); }}
        .icon-btn .dot {{ position: absolute; top: 6px; right: 6px; width: 8px; height: 8px; background-color: var(--broxel-teal); border-radius: 50%; border: 2px solid white; }}
        
        /* Content Area */
        .content {{ padding: 2.5rem; flex: 1; max-width: 1600px; width: 100%; margin: 0 auto; }}
        .page-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }}
        .page-title {{ font-size: 1.875rem; font-weight: 800; color: #0f172a; letter-spacing: -0.03em; }}
        .page-subtitle {{ color: #64748b; font-size: 0.95rem; margin-top: 0.25rem; font-weight: 400; }}
        
        /* KPI Grid */
        .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }}
        .kpi-card {{ background: white; padding: 1.5rem; border-radius: 14px; border: 1px solid var(--border-color); box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: transform 0.2s, box-shadow 0.2s; }}
        .kpi-card:hover {{ transform: translateY(-3px); box-shadow: 0 12px 20px -5px rgba(0, 117, 255, 0.08); border-color: #cce3ff; }}
        .kpi-header {{ display: flex; justify-content: space-between; align-items: center; color: #64748b; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }}
        .kpi-icon {{ width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; }}
        .kpi-value {{ font-size: 2rem; font-weight: 800; color: #0f172a; margin: 0.75rem 0 0.5rem; letter-spacing: -0.03em; }}
        .kpi-trend {{ display: inline-flex; align-items: center; gap: 0.25rem; font-size: 0.8rem; font-weight: 700; padding: 0.25rem 0.65rem; border-radius: 9999px; }}
        .trend-blue {{ background-color: #e6f1ff; color: var(--broxel-blue); }}
        .trend-teal {{ background-color: #e0fbf8; color: #009689; }}
        .trend-purple {{ background-color: #f3e8ff; color: #6b21a8; }}
        
        /* Cards & Containers */
        .card {{ background: white; border-radius: 14px; padding: 2rem; border: 1px solid var(--border-color); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02), 0 2px 4px -1px rgba(0,0,0,0.02); margin-bottom: 2rem; }}
        .card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; padding-bottom: 1.25rem; border-bottom: 1px solid #f1f5f9; }}
        .card-title {{ font-size: 1.25rem; font-weight: 800; color: #0f172a; display: flex; align-items: center; gap: 0.6rem; }}
        
        /* Looker Iframe Container */
        #dashboard-container {{ width: 100%; height: 850px; border-radius: 10px; overflow: hidden; border: 1px solid var(--border-color); background-color: #f8fafc; position: relative; }}
        .looker-embed {{ width: 100%; height: 100%; border: none; }}
        
        /* Filter Bar inside Card Header */
        .btn-filter {{ background: transparent; border: none; color: #64748b; padding: 0.45rem 0.85rem; border-radius: 6px; font-size: 0.8rem; font-weight: 700; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; gap: 0.4rem; }}
        .btn-filter:hover {{ color: var(--broxel-blue); background: white; }}
        .btn-filter.active {{ background: var(--broxel-blue); color: white; box-shadow: 0 2px 6px rgba(0, 117, 255, 0.3); }}

        /* Tables & Lists */
        .table-controls {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem; gap: 1rem; flex-wrap: wrap; }}
        .filter-group {{ display: flex; gap: 0.75rem; align-items: center; }}
        .select-filter {{ padding: 0.55rem 1.1rem; border-radius: 8px; border: 1px solid var(--border-color); background: white; font-size: 0.875rem; color: #334155; outline: none; font-weight: 500; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ text-align: left; padding: 1.1rem 1.25rem; border-bottom: 1px solid var(--border-color); }}
        th {{ background-color: #f8fafc; font-weight: 700; color: #475569; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; }}
        tr:hover {{ background-color: #f8fafc; }}
        .status-badge {{ display: inline-flex; align-items: center; gap: 0.35rem; padding: 0.3rem 0.8rem; border-radius: 9999px; font-size: 0.8rem; font-weight: 700; }}
        .status-ready {{ background-color: #e0fbf8; color: #008075; }}
        .status-sched {{ background-color: #e6f1ff; color: var(--broxel-blue); }}
        .btn-outline {{ background: white; border: 1px solid var(--border-color); color: #334155; padding: 0.5rem 1rem; border-radius: 8px; font-size: 0.85rem; font-weight: 700; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; gap: 0.5rem; text-decoration: none; }}
        .btn-outline:hover {{ background: #f8fafc; border-color: var(--broxel-blue); color: var(--broxel-blue); }}
        .btn-primary {{ background-color: var(--broxel-blue); color: white; border: none; padding: 0.65rem 1.4rem; border-radius: 8px; font-size: 0.875rem; font-weight: 700; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; gap: 0.5rem; box-shadow: 0 4px 12px rgba(0, 117, 255, 0.25); }}
        .btn-primary:hover {{ background-color: var(--broxel-blue-hover); transform: translateY(-1px); box-shadow: 0 6px 16px rgba(0, 117, 255, 0.35); }}

        /* Toggles & Forms */
        .toggle-row {{ display: flex; justify-content: space-between; align-items: center; padding: 1.25rem 0; border-bottom: 1px solid #f1f5f9; }}
        .toggle-label strong {{ display: block; color: #0f172a; font-size: 0.95rem; font-weight: 700; margin-bottom: 0.2rem; }}
        .toggle-label span {{ color: #64748b; font-size: 0.85rem; }}
        .switch {{ position: relative; display: inline-block; width: 48px; height: 26px; }}
        .switch input {{ opacity: 0; width: 0; height: 0; }}
        .slider {{ position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #cbd5e1; transition: .3s; border-radius: 34px; }}
        .slider:before {{ position: absolute; content: ""; height: 20px; width: 20px; left: 3px; bottom: 3px; background-color: white; transition: .3s; border-radius: 50%; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
        input:checked + .slider {{ background-color: var(--broxel-blue); }}
        input:checked + .slider:before {{ transform: translateX(22px); }}

        /* Footer */
        .footer {{ text-align: center; padding: 2rem; color: #94a3b8; font-size: 0.85rem; border-top: 1px solid var(--border-color); background: white; margin-top: auto; font-weight: 500; }}
    </style>
</head>
<body>
    <!-- Left Sidebar (Broxel Branded) -->
    <aside class="sidebar">
        <a href="/" class="brand">
            <img src="https://broxel.com/wp-content/uploads/2024/05/Broxel_logox1.png" alt="Broxel">
        </a>
        <div class="sidebar-content">
            {sidebar_html}
        </div>
        <div class="sidebar-footer">
            <div class="user-widget">
                <div class="avatar"><i class="fa-solid fa-user-check"></i></div>
                <div class="user-info">
                    <div class="user-name">Broxel Executive</div>
                    <div class="user-role">SDK Interactive Tier</div>
                </div>
            </div>
        </div>
    </aside>

    <!-- Main Wrapper -->
    <div class="main-wrapper">
        <!-- Top Navbar -->
        <header class="topbar">
            <div class="search-box">
                <i class="fa-solid fa-magnifying-glass"></i>
                <input type="text" placeholder="Search Broxel Pay metrics, MXN accounts, or LookML models...">
            </div>
            <div class="topbar-actions">
                <span class="mode-badge"><i class="fa-solid fa-circle"></i> {mode_badge}</span>
                <button class="icon-btn" title="Broxel Alerts"><i class="fa-regular fa-bell"></i><span class="dot"></span></button>
                <button class="icon-btn" title="Looker Help"><i class="fa-regular fa-circle-question"></i></button>
            </div>
        </header>

        <!-- Content Area -->
        <main class="content">
            {content_html}
        </main>

        <footer class="footer">
            © 2026 Broxel Fintech • Más que una tarjeta, un infinito de posibilidades. • Looker Google Cloud Enterprise SDK
        </footer>
    </div>
</body>
</html>"""

class EmbedHandler(BaseHTTPRequestHandler):
    """HTTP Handler serving a Broxel-branded Looker Embed SDK portal application."""
    def do_GET(self):
        config = load_config()
        try:
            embed_url, mode = generate_embed_url(config)
            
            if self.path == "/" or self.path == "/dashboard":
                content_html = f"""
                <div class="page-header">
                    <div>
                        <h1 class="page-title">Broxel Executive Analytics (SDK v1.8)</h1>
                        <p class="page-subtitle">Monitoreo en tiempo real con controles interactivos Looker Embed SDK.</p>
                    </div>
                    <div>
                        <a href="{embed_url}" target="_blank" class="btn-outline"><i class="fa-solid fa-arrow-up-right-from-square"></i> Abrir en Looker</a>
                    </div>
                </div>

                <!-- Executive KPI Grid (Broxel Branded) -->
                <div class="kpi-grid">
                    <div class="kpi-card">
                        <div class="kpi-header"><span>Volumen Transaccional (TPV)</span><div class="kpi-icon" style="background: #e6f1ff; color: #0075ff;"><i class="fa-solid fa-credit-card"></i></div></div>
                        <div class="kpi-value">$48,290,150 <span style="font-size: 1rem; color: #64748b; font-weight: 600;">MXN</span></div>
                        <div><span class="kpi-trend trend-blue"><i class="fa-solid fa-arrow-trend-up"></i> +18.4%</span> <span style="font-size: 0.75rem; color: #64748b;">vs mes anterior</span></div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-header"><span>Cuentas Broxel Pay Activas</span><div class="kpi-icon" style="background: #e0fbf8; color: #00c2b2;"><i class="fa-solid fa-users-viewfinder"></i></div></div>
                        <div class="kpi-value">342,800</div>
                        <div><span class="kpi-trend trend-teal"><i class="fa-solid fa-arrow-trend-up"></i> +12.1%</span> <span style="font-size: 0.75rem; color: #64748b;">vs mes anterior</span></div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-header"><span>Remesas Cross-Border (USA-MX)</span><div class="kpi-icon" style="background: #f3e8ff; color: #6b21a8;"><i class="fa-solid fa-money-bill-transfer"></i></div></div>
                        <div class="kpi-value">$3,450,000 <span style="font-size: 1rem; color: #64748b; font-weight: 600;">USD</span></div>
                        <div><span class="kpi-trend trend-purple"><i class="fa-solid fa-arrow-trend-up"></i> +9.5%</span> <span style="font-size: 0.75rem; color: #64748b;">vs mes anterior</span></div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-header"><span>Tasa de Conversión Bóveda</span><div class="kpi-icon" style="background: #ffedd5; color: #c2410c;"><i class="fa-solid fa-vault"></i></div></div>
                        <div class="kpi-value">24.8%</div>
                        <div><span class="kpi-trend" style="background: #ffedd5; color: #c2410c;"><i class="fa-solid fa-arrow-trend-up"></i> +3.2%</span> <span style="font-size: 0.75rem; color: #64748b;">vs mes anterior</span></div>
                    </div>
                </div>

                <!-- Looker Dashboard Container Card with Integrated SDK Filter Bar -->
                <div class="card">
                    <div class="card-header" style="flex-wrap: wrap; gap: 1rem;">
                        <div>
                            <div class="card-title"><i class="fa-solid fa-chart-pie" style="color: #0075ff;"></i> Looker Enterprise Embedded Dashboard (SDK v1.8)</div>
                            <div style="font-size: 0.85rem; color: #64748b;">Modelo LookML: <code>{config['dashboard_id']}</code></div>
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;">
                            <span id="sdk-status" class="status-badge" style="background: #e6f1ff; color: #0075ff;"><i class="fa-solid fa-spinner fa-spin"></i> SDK Conectando...</span>
                            <div style="display: flex; gap: 0.35rem; background: #f4f7fa; padding: 0.35rem; border-radius: 8px; border: 1px solid var(--border-color);">
                                <button class="btn-filter active" onclick="updateFilter('', this)"><i class="fa-solid fa-globe"></i> Todas</button>
                                <button class="btn-filter" onclick="updateFilter('California', this)"><i class="fa-solid fa-location-dot"></i> CDMX / MXN</button>
                                <button class="btn-filter" onclick="updateFilter('New York', this)"><i class="fa-solid fa-location-dot"></i> NY / USD</button>
                                <button class="btn-filter" onclick="updateFilter('Texas', this)"><i class="fa-solid fa-location-dot"></i> TX / Cross-Border</button>
                            </div>
                        </div>
                    </div>
                    <!-- Looker Embed SDK will inject the iframe here -->
                    <div id="dashboard-container"></div>
                </div>

                <script>
                    // 1. Initialize Looker Embed SDK
                    LookerEmbedSDK.init('{config['looker_url']}');

                    const targetUrl = "{embed_url}";
                    console.log("Initializing Looker Embed SDK with URL:", targetUrl);

                    // 2. Build dashboard iframe and attach event listeners
                    LookerEmbedSDK.createDashboardWithUrl(targetUrl)
                        .appendTo('#dashboard-container')
                        .withClassName('looker-embed')
                        .on('dashboard:run:start', () => {{
                            const badge = document.getElementById('sdk-status');
                            badge.style.background = '#ffedd5';
                            badge.style.color = '#c2410c';
                            badge.innerHTML = '<i class="fa-solid fa-clock"></i> ⏳ Ejecutando consulta...';
                        }})
                        .on('dashboard:run:complete', (e) => {{
                            const badge = document.getElementById('sdk-status');
                            badge.style.background = '#e0fbf8';
                            badge.style.color = '#008075';
                            badge.innerHTML = '<i class="fa-solid fa-check-circle"></i> ● Conectado (Listo)';
                            console.log('Looker event [dashboard:run:complete]:', e);
                        }})
                        .build()
                        .connect()
                        .then((dashboard) => {{
                            console.log('Successfully connected and established handshake!');
                            const badge = document.getElementById('sdk-status');
                            badge.style.background = '#e0fbf8';
                            badge.style.color = '#008075';
                            badge.innerHTML = '<i class="fa-solid fa-check-circle"></i> ● Conectado (Handshake Activo)';
                            window.activeDashboard = dashboard;
                        }})
                        .catch((error) => {{
                            console.error('Looker SDK connection failed:', error);
                            const badge = document.getElementById('sdk-status');
                            badge.style.background = '#fee2e2';
                            badge.style.color = '#b91c1c';
                            badge.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Error SDK';
                        }});

                    // 3. Programmatic Filter Functions
                    function updateFilter(state, btn) {{
                        if (window.activeDashboard) {{
                            console.log("Host action: Filtering by State =", state);
                            document.querySelectorAll('.btn-filter').forEach(b => b.classList.remove('active'));
                            if (btn) btn.classList.add('active');
                            
                            const badge = document.getElementById('sdk-status');
                            badge.style.background = '#e6f1ff';
                            badge.style.color = '#0075ff';
                            badge.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Filtrando...';
                            window.activeDashboard.updateFilters({{ 'State': state }});
                            window.activeDashboard.run();
                        }} else {{
                            alert("El dashboard de Looker aún está cargando o conectando...");
                        }}
                    }}
                </script>
                """
                html = render_page("Dashboard", "Executive Dashboard", content_html, config, embed_url, mode)
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(html.encode("utf-8"))
                
            elif self.path == "/reports":
                content_html = """
                <div class="page-header">
                    <div>
                        <h1 class="page-title">Reportes Financieros & Remesas</h1>
                        <p class="page-subtitle">Exportaciones automatizadas de BigQuery, resúmenes contables y auditoría de transacciones MXN/USD.</p>
                    </div>
                    <button class="btn-primary" onclick="alert('Generando reporte en tiempo real desde BigQuery...')"><i class="fa-solid fa-file-export"></i> Nuevo Reporte LookML</button>
                </div>

                <div class="card">
                    <div class="table-controls">
                        <div class="filter-group">
                            <select class="select-filter"><option>Todas las Categorías</option><option>Cuentas Pesos / Dólares</option><option>Remesas USA-MX</option><option>Bóveda Virtual</option></select>
                            <select class="select-filter"><option>Todos los Formatos</option><option>Resumen PDF</option><option>Exportación CSV / Excel</option></select>
                        </div>
                        <div style="font-size: 0.85rem; color: #64748b;">Mostrando <strong>4</strong> reportes disponibles</div>
                    </div>
                    <table>
                        <thead>
                            <tr>
                                <th>Nombre del Reporte</th>
                                <th>Categoría</th>
                                <th>Fecha de Generación</th>
                                <th>Estado</th>
                                <th>Formato</th>
                                <th style="text-align: right;">Acción</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>Conciliación de Cuentas Duales (MXN/USD)</strong><br><span style="font-size: 0.75rem; color: #64748b;">LookML Explore: broxel_dual_accounts</span></td>
                                <td>Finanzas</td>
                                <td>02 Ene, 2025 • 08:30 AM</td>
                                <td><span class="status-badge status-ready"><i class="fa-solid fa-check-circle"></i> Listo</span></td>
                                <td>PDF / Excel</td>
                                <td style="text-align: right;"><button class="btn-outline" onclick="alert('Descargando Conciliación PDF...')"><i class="fa-solid fa-download"></i> Descargar</button></td>
                            </tr>
                            <tr>
                                <td><strong>Auditoría de Remesas Cross-Border</strong><br><span style="font-size: 0.75rem; color: #64748b;">LookML Explore: remittances_tx</span></td>
                                <td>Cross-Border</td>
                                <td>Ayer • 11:45 PM</td>
                                <td><span class="status-badge status-ready"><i class="fa-solid fa-check-circle"></i> Listo</span></td>
                                <td>CSV Export</td>
                                <td style="text-align: right;"><button class="btn-outline" onclick="alert('Descargando Remesas CSV...')"><i class="fa-solid fa-download"></i> Descargar</button></td>
                            </tr>
                            <tr>
                                <td><strong>Rendimiento Bóveda Virtual Broxel</strong><br><span style="font-size: 0.75rem; color: #64748b;">LookML Explore: vault_savings</span></td>
                                <td>Inversiones</td>
                                <td>05 Ene, 2025 • 02:15 PM</td>
                                <td><span class="status-badge status-ready"><i class="fa-solid fa-check-circle"></i> Listo</span></td>
                                <td>PDF Reporte</td>
                                <td style="text-align: right;"><button class="btn-outline" onclick="alert('Descargando Reporte de Bóveda...')"><i class="fa-solid fa-download"></i> Descargar</button></td>
                            </tr>
                            <tr>
                                <td><strong>Proyección de Crecimiento Broxel Pay 2026</strong><br><span style="font-size: 0.75rem; color: #64748b;">LookML Explore: conversions</span></td>
                                <td>Ejecutivo</td>
                                <td>Cada Lunes • 06:00 AM</td>
                                <td><span class="status-badge status-sched"><i class="fa-solid fa-clock"></i> Programado</span></td>
                                <td>Slide Deck</td>
                                <td style="text-align: right;"><button class="btn-outline" onclick="alert('Descargando Presentación...')"><i class="fa-solid fa-download"></i> Descargar</button></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                """
                html = render_page("Reportes", "Financial & MXN Reports", content_html, config, embed_url, mode)
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(html.encode("utf-8"))
                
            elif self.path == "/about":
                content_html = f"""
                <div class="page-header">
                    <div>
                        <h1 class="page-title">Arquitectura Looker Embed SDK v1.8</h1>
                        <p class="page-subtitle">Especificación técnica de la comunicación bidireccional JavaScript para Broxel Fintech.</p>
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 2rem;">
                    <div class="card" style="margin-bottom: 0;">
                        <div class="card-header"><div class="card-title"><i class="fa-solid fa-code-merge" style="color: #0075ff;"></i> Integración Looker Embed SDK</div></div>
                        <div style="line-height: 1.8; color: #475569; font-size: 0.95rem;">
                            <p style="margin-bottom: 1.25rem;">Este portal implementa la biblioteca <strong>@looker/embed-sdk v1.8</strong> para permitir el control programático y la mensajería de eventos en tiempo real entre la aplicación web host de Broxel y el iframe de Looker Google Cloud Enterprise.</p>
                            
                            <h3 style="color: #0f172a; font-size: 1.1rem; margin: 1.5rem 0 0.75rem;">Capacidades Bidireccionales:</h3>
                            <div style="display: flex; flex-direction: column; gap: 1rem;">
                                <div style="display: flex; gap: 1rem; align-items: flex-start; background: #f4f7fa; padding: 1rem; border-radius: 8px; border: 1px solid var(--border-color);">
                                    <div style="background: #0075ff; color: white; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; flex-shrink: 0;">1</div>
                                    <div><strong>Filtros Externos (updateFilters):</strong> Los botones nativos del portal llaman a <code>dashboard.updateFilters()</code> y <code>dashboard.run()</code> para reejecutar consultas analíticas en BigQuery sin recargar la página.</div>
                                </div>
                                <div style="display: flex; gap: 1rem; align-items: flex-start; background: #f4f7fa; padding: 1rem; border-radius: 8px; border: 1px solid var(--border-color);">
                                    <div style="background: #0075ff; color: white; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; flex-shrink: 0;">2</div>
                                    <div><strong>Monitoreo de Eventos (on):</strong> El portal escucha eventos en vivo como <code>dashboard:run:start</code> y <code>dashboard:run:complete</code> para informar visualmente al ejecutivo de Broxel sobre el estado de las consultas.</div>
                                </div>
                                <div style="display: flex; gap: 1rem; align-items: flex-start; background: #f4f7fa; padding: 1rem; border-radius: 8px; border: 1px solid var(--border-color);">
                                    <div style="background: #0075ff; color: white; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; flex-shrink: 0;">3</div>
                                    <div><strong>Handshake Seguro postMessage:</strong> La comunicación entre ventanas se autentica mediante protocolos nativos del navegador, garantizando que solo los dominios autorizados controlen el dashboard.</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div>
                        <div class="card" style="margin-bottom: 1.5rem;">
                            <div class="card-header"><div class="card-title"><i class="fa-solid fa-shield-halved" style="color: #00c2b2;"></i> Estado de Conexión SDK</div></div>
                            <div style="display: flex; flex-direction: column; gap: 1rem; font-size: 0.875rem;">
                                <div style="display: flex; justify-content: space-between;"><span>Looker Embed SDK:</span> <strong style="color: #008075;">● v1.8.0 Activo</strong></div>
                                <div style="display: flex; justify-content: space-between;"><span>Handshake postMessage:</span> <strong style="color: #008075;">● Conectado</strong></div>
                                <div style="display: flex; justify-content: space-between;"><span>Latencia de Eventos:</span> <strong>8 ms</strong></div>
                                <div style="display: flex; justify-content: space-between;"><span>Edición GCP:</span> <strong>Enterprise (Prod)</strong></div>
                            </div>
                        </div>
                        <div class="card" style="margin-bottom: 0; background: #0b1727; color: white; border: none; box-shadow: 0 10px 25px rgba(0,0,0,0.15);">
                            <div style="font-size: 0.75rem; font-weight: 700; color: #00c2b2; text-transform: uppercase; margin-bottom: 0.5rem;">Instancia Looker Conectada</div>
                            <code style="display: block; color: #cbd5e1; font-size: 0.8rem; word-break: break-all; margin-bottom: 1rem; background: rgba(255,255,255,0.05); padding: 0.5rem; border-radius: 6px;">{config['looker_url']}</code>
                            <div style="font-size: 0.75rem; font-weight: 700; color: #00c2b2; text-transform: uppercase; margin-bottom: 0.5rem;">Dashboard LookML Activo</div>
                            <code style="display: block; color: #cbd5e1; font-size: 0.8rem; word-break: break-all; background: rgba(255,255,255,0.05); padding: 0.5rem; border-radius: 6px;">{config['dashboard_id']}</code>
                        </div>
                    </div>
                </div>
                """
                html = render_page("Arquitectura SDK", "Looker Embed SDK Guide", content_html, config, embed_url, mode)
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(html.encode("utf-8"))
                
            elif self.path == "/settings":
                content_html = """
                <div class="page-header">
                    <div>
                        <h1 class="page-title">Preferencias de Cuenta</h1>
                        <p class="page-subtitle">Configuración del portal de analítica Broxel, zona horaria y alertas ejecutivas.</p>
                    </div>
                </div>

                <div class="card" style="max-width: 800px;">
                    <div class="card-header"><div class="card-title"><i class="fa-solid fa-user-gear" style="color: #0075ff;"></i> Configuración del Ejecutivo Broxel</div></div>
                    
                    <div class="toggle-row">
                        <div class="toggle-label"><strong>Actualización Automática de Dashboards</strong><span>Refrescar visualizaciones LookML en tiempo real cada 15 minutos.</span></div>
                        <label class="switch"><input type="checkbox" checked><span class="slider"></span></label>
                    </div>
                    <div class="toggle-row">
                        <div class="toggle-label"><strong>Alertas de Remesas y SPEI</strong><span>Recibir notificaciones por correo ante variaciones inusuales en volumen transaccional MXN/USD.</span></div>
                        <label class="switch"><input type="checkbox" checked><span class="slider"></span></label>
                    </div>
                    <div class="toggle-row">
                        <div class="toggle-label"><strong>Modo Oscuro (Broxel Midnight)</strong><span>Cambiar el tema del portal y contenedores a contraste oscuro de alta intensidad.</span></div>
                        <label class="switch"><input type="checkbox"><span class="slider"></span></label>
                    </div>

                    <div style="margin: 1.75rem 0 1.5rem;">
                        <label style="display: block; font-weight: 700; margin-bottom: 0.5rem; color: #0f172a;">Zona Horaria Operativa</label>
                        <select class="select-filter" style="width: 100%; padding: 0.75rem;">
                            <option>UTC (Coordinated Universal Time)</option>
                            <option selected>America/Mexico_City (CDMX / Hora Central)</option>
                            <option>America/New_York (EST/EDT)</option>
                            <option>America/Tijuana (PST/PDT)</option>
                        </select>
                    </div>

                    <div style="margin-bottom: 2rem;">
                        <label style="display: block; font-weight: 700; margin-bottom: 0.5rem; color: #0f172a;">Rol Asignado y Acceso a Modelos Looker</label>
                        <input type="text" value="Broxel Fintech Executive • Model Set: [training_ecommerce]" disabled style="width: 100%; padding: 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; background: #f4f7fa; color: #64748b; font-size: 0.875rem; font-weight: 600;">
                    </div>

                    <div style="display: flex; gap: 1rem;">
                        <button class="btn-primary" onclick="alert('¡Preferencias guardadas exitosamente!')"><i class="fa-solid fa-check"></i> Guardar Cambios</button>
                        <button class="btn-outline" onclick="alert('Configuración restablecida al valor por defecto.')">Restablecer</button>
                    </div>
                </div>
                """
                html = render_page("Preferencias", "Account Preferences", content_html, config, embed_url, mode)
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(html.encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(f"Error generating Embed URL: {e}".encode("utf-8"))

def run_server():
    load_config()
    port = 8080
    server = HTTPServer(("localhost", port), EmbedHandler)
    print(f"SSO Embed SDK Server started at http://localhost:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.server_close()

if __name__ == "__main__":
    run_server()
