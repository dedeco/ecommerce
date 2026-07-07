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

def generate_sso_url(config, embed_domain):
    """Generates a signed Looker SSO Embed URL, including embed_domain for SDK handshake."""
    looker_url = config["looker_url"]       # e.g., https://your-company.looker.com
    secret = config["embed_secret"]         # SSO Embed Secret
    dashboard_id = config["dashboard_id"]   # e.g., training_ecommerce::business_pulse

    # Parse host
    parsed_url = urllib.parse.urlparse(looker_url)
    host = parsed_url.netloc
    if ":" not in host:
        host = f"{host}:443"

    # Define target path and login path
    target_path = f"/embed/dashboards/{dashboard_id}"
    login_path = f"/login/embed/{urllib.parse.quote_plus(target_path)}"

    # User definition (mock data)
    external_user_id = "demo_user_sdk"
    first_name = "SDK"
    last_name = "User"
    
    # Permissions and Models
    permissions = ["access_data", "see_user_dashboards"]
    models = ["training_ecommerce"]
    group_ids = []
    external_group_id = "demo_group"
    user_attributes = {}
    force_logout_login = "true"
    
    session_length = 3600
    nonce = uuid.uuid4().hex
    current_time = str(int(time.time()))

    # Construct path to sign (MUST be in this exact order)
    path_to_sign = "\n".join([
        host,
        login_path,
        nonce,
        current_time,
        str(session_length),
        external_user_id,
        json.dumps(permissions),
        json.dumps(models),
        json.dumps(group_ids),
        external_group_id,
        json.dumps(user_attributes),
        force_logout_login
    ])

    # Generate HMAC-SHA1 signature
    key = secret.encode('utf-8')
    msg = path_to_sign.encode('utf-8')
    sig = hmac.new(key, msg, hashlib.sha1).digest()
    signature = base64.b64encode(sig).decode('utf-8')

    # Construct query parameters
    query_params = {
        "nonce": nonce,
        "time": current_time,
        "session_length": str(session_length),
        "external_user_id": external_user_id,
        "permissions": json.dumps(permissions),
        "models": json.dumps(models),
        "group_ids": json.dumps(group_ids),
        "external_group_id": external_group_id,
        "user_attributes": json.dumps(user_attributes),
        "force_logout_login": force_logout_login,
        "signature": signature,
        "first_name": first_name,
        "last_name": last_name,
        # CRITICAL: embed_domain is required for Looker Embed SDK to establish communication
        "embed_domain": embed_domain 
    }

    # Build signed URL
    encoded_params = urllib.parse.urlencode(query_params)
    sso_url = f"{looker_url}{login_path}?{encoded_params}"
    return sso_url

class EmbedHandler(BaseHTTPRequestHandler):
    """Serves the HTML page containing Looker Embed SDK script and controls."""
    def do_GET(self):
        if self.path == "/":
            config = load_config()
            
            # Determine embed_domain dynamically from request headers
            host_header = self.headers.get("Host", "localhost:8080")
            embed_domain = f"http://{host_header}" # Assume HTTP for local dev

            try:
                sso_url = generate_sso_url(config, embed_domain)
                
                # HTML with Embed SDK integration
                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Looker Embed SDK Demo</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f4f6f8; color: #333; }}
                        .header {{ margin-bottom: 20px; }}
                        .controls {{ margin-bottom: 15px; padding: 15px; background: #fff; border: 1px solid #ccc; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
                        button {{ padding: 8px 12px; margin-right: 10px; cursor: pointer; background: #1a73e8; color: white; border: none; border-radius: 4px; font-weight: bold; }}
                        button:hover {{ background: #1557b0; }}
                        .status-bar {{ font-weight: bold; margin-bottom: 10px; color: #666; font-size: 0.9em; }}
                        #dashboard-container {{ background: white; border: 1px solid #ccc; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                        .looker-embed {{ width: 100%; height: 800px; border: none; }}
                        code {{ background: #eef; padding: 2px 4px; border-radius: 4px; }}
                    </style>
                    <!-- Load Looker Embed SDK from CDN -->
                    <script src="https://unpkg.com/@looker/embed-sdk@1.8.0/dist/embed-sdk.js"></script>
                </head>
                <body>
                    <div class="header">
                        <h1>Looker Embed SDK Demo</h1>
                        <p>Interacting with Dashboard: <code>{config['dashboard_id']}</code></p>
                    </div>

                    <div class="controls">
                        <h3 style="margin-top: 0;">Custom Host Controls (Sends messages to iframe)</h3>
                        <button onclick="updateFilter('California')">Filter: California</button>
                        <button onclick="updateFilter('New York')">Filter: New York</button>
                        <button onclick="clearFilter()">Clear Filter</button>
                    </div>

                    <div class="status-bar" id="status">Status: Initializing SDK...</div>

                    <!-- Container where the SDK will build the Looker iframe -->
                    <div id="dashboard-container"></div>

                    <script>
                        // 1. Initialize the SDK with the Looker Base URL
                        LookerEmbedSDK.init('{config['looker_url']}');

                        // 2. Use the signed SSO URL generated by the backend
                        const ssoUrl = "{sso_url}";

                        console.log("Initializing Looker Embed SDK...");

                        // 3. Create the dashboard, append it, listen to events, and connect
                        LookerEmbedSDK.createDashboardWithUrl(ssoUrl)
                            .appendTo('#dashboard-container')
                            .withClassName('looker-embed')
                            // Listen to events sent from Looker iframe
                            .on('dashboard:run:start', () => {{
                                document.getElementById('status').innerText = 'Status: Looker is running queries...';
                            }})
                            .on('dashboard:run:complete', (e) => {{
                                document.getElementById('status').innerText = 'Status: Loaded';
                                console.log('Looker event [dashboard:run:complete]:', e);
                            }})
                            .build()
                            .connect()
                            .then((dashboard) => {{
                                console.log('Successfully connected and established handshake!');
                                document.getElementById('status').innerText = 'Status: Connected (Ready)';
                                // Save the dashboard instance globally to use in control buttons
                                window.activeDashboard = dashboard;
                            }})
                            .catch((error) => {{
                                console.error('Looker SDK connection failed:', error);
                                document.getElementById('status').innerText = 'Status: Connection Failed';
                            }});

                        // Control functions (Sends actions into Looker iframe)
                        function updateFilter(state) {{
                            if (window.activeDashboard) {{
                                console.log("Host action: Filtering by State =", state);
                                document.getElementById('status').innerText = 'Status: Sending filter update...';
                                // Update the 'State' filter
                                window.activeDashboard.updateFilters({{ 'State': state }});
                                // Trigger the dashboard to run and apply the new filter
                                window.activeDashboard.run();
                            }} else {{
                                console.warn("Dashboard is not connected yet.");
                            }}
                        }}

                        function clearFilter() {{
                            if (window.activeDashboard) {{
                                console.log("Host action: Clearing State filter");
                                document.getElementById('status').innerText = 'Status: Clearing filter...';
                                window.activeDashboard.updateFilters({{ 'State': '' }});
                                window.activeDashboard.run();
                            }}
                        }}
                    </script>
                </body>
                </html>
                """
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(html.encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(f"Error generating SSO URL: {e}".encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

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
