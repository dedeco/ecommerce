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

# Import Looker SDK (required for Step 4 API calls)
try:
    import looker_sdk
    from looker_sdk import models40 as models
except ImportError:
    print("Warning: looker_sdk Python library not found.")
    print("Please install it using: pip install looker-sdk")
    # We don't exit immediately so the server can still start and show errors in browser

# Configuration files
EMBED_CONFIG_FILE = "embed_config.json"
LOOKER_INI_FILE = "looker.ini"

# Global API SDK instance
api_sdk = None

def get_api_sdk():
    """Initializes and returns the Looker API SDK instance."""
    global api_sdk
    if api_sdk is None:
        if os.path.exists(LOOKER_INI_FILE):
            try:
                print("Initializing Looker API SDK...")
                api_sdk = looker_sdk.init40()
            except Exception as e:
                print(f"Error initializing Looker API SDK: {e}")
        else:
            print(f"Warning: {LOOKER_INI_FILE} not found. API features will fail.")
    return api_sdk

def load_embed_config():
    """Loads embedding configuration."""
    if not os.path.exists(EMBED_CONFIG_FILE):
        print(f"Error: {EMBED_CONFIG_FILE} not found.")
        print("Please copy embed_config.json.example to embed_config.json and fill in settings.")
        sys.exit(1)
    with open(EMBED_CONFIG_FILE, "r") as f:
        return json.load(f)

def generate_sso_url(config, embed_domain):
    """Generates a signed Looker SSO Embed URL or Private Embed URL."""
    looker_url = config["looker_url"].rstrip("/")
    secret = config.get("embed_secret", "")
    dashboard_id = config["dashboard_id"]

    if not secret or secret in ["none", "enterprise", "your_embed_secret_from_looker_admin", "your_embed_secret_here"]:
        print("Note: Running in Private Embedding Mode (no Embed Secret provided). Using standard Looker session authentication.")
        return f"{looker_url}/embed/dashboards/{dashboard_id}?allow_login_screen=true&theme=Looker&sdk=2&embed_domain={embed_domain}"

    parsed_url = urllib.parse.urlparse(looker_url)
    host = parsed_url.netloc
    if ":" not in host:
        host = f"{host}:443"

    target_path = f"/embed/dashboards/{dashboard_id}?embed_domain={embed_domain}&sdk=2"
    login_path = f"/login/embed/{urllib.parse.quote_plus(target_path)}"

    external_user_id = "demo_rich_user"
    first_name = "RichApp"
    last_name = "User"
    
    permissions = ["access_data", "see_user_dashboards"]
    models = ["training_ecommerce"]
    group_ids = []
    external_group_id = "demo_group"
    user_attributes = {}
    force_logout_login = "true"
    
    session_length = 3600
    nonce = uuid.uuid4().hex
    current_time = str(int(time.time()))

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

    key = secret.encode('utf-8')
    msg = path_to_sign.encode('utf-8')
    sig = hmac.new(key, msg, hashlib.sha1).digest()
    signature = base64.b64encode(sig).decode('utf-8')

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
        "embed_domain": embed_domain
    }

    encoded_params = urllib.parse.urlencode(query_params)
    sso_url = f"{looker_url}{login_path}?{encoded_params}"
    return sso_url

class RichAppHandler(BaseHTTPRequestHandler):
    """Router for the Rich Application (API + Embed)."""
    
    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(message.encode("utf-8"))

    def do_GET(self):
        # Route: Home Page
        if self.path == "/":
            self.serve_html()
        
        # Route: API to get signed SSO URL
        elif self.path == "/api/embed-url":
            self.serve_embed_url()
        
        # Route: API to get Brands list (calls Looker API)
        elif self.path == "/api/brands":
            self.serve_brands()
            
        else:
            self.send_response(404)
            self.end_headers()

    def serve_html(self):
        config = load_embed_config()
        # We inject the Looker URL into the frontend so the Embed SDK knows where to point
        looker_url = config["looker_url"]
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Looker Rich App Demo</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f4f6f8; color: #333; }}
                .header {{ margin-bottom: 20px; }}
                .controls {{ margin-bottom: 15px; padding: 15px; background: #fff; border: 1px solid #ccc; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
                select {{ padding: 8px; margin-right: 10px; border-radius: 4px; border: 1px solid #ccc; font-size: 1em; width: 250px; }}
                .status-bar {{ font-weight: bold; margin-bottom: 10px; color: #666; font-size: 0.9em; }}
                #dashboard-container {{ background: white; border: 1px solid #ccc; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .looker-embed {{ width: 100%; height: 800px; border: none; }}
                code {{ background: #eef; padding: 2px 4px; border-radius: 4px; }}
            </style>
            <!-- Load Looker Embed SDK -->
            <script src="https://unpkg.com/@looker/embed-sdk@1.8.0/dist/main.js"></script>
        </head>
        <body>
            <div class="header">
                <h1>Looker Rich App Demo (API + Embed)</h1>
                <p>This portal uses **Looker API** to fetch filter options dynamically and **Embed SDK** to apply them.</p>
            </div>

            <div class="controls">
                <h3 style="margin-top: 0;">Dynamic Brand Filter (Populated via Looker API)</h3>
                <label for="brand-select">Select Brand: </label>
                <select id="brand-select" onchange="brandChanged()" disabled>
                    <option value="">Loading brands via API...</option>
                </select>
            </div>

            <div class="status-bar" id="status">Status: Initializing...</div>

            <!-- Dashboard container -->
            <div id="dashboard-container"></div>

            <script>
                let activeDashboard = null;

                // 1. Initialize Embed SDK (resolve UMD namespace export LookerEmbedSDK.LookerEmbedSDK)
                const EmbedSDK = (window.LookerEmbedSDK && window.LookerEmbedSDK.LookerEmbedSDK) ? window.LookerEmbedSDK.LookerEmbedSDK : window.LookerEmbedSDK;
                if (!EmbedSDK || typeof EmbedSDK.init !== 'function') {{
                    console.error("LookerEmbedSDK failed to resolve correctly. window.LookerEmbedSDK:", window.LookerEmbedSDK);
                }} else {{
                    window.LookerEmbedSDK = EmbedSDK;
                }}
                EmbedSDK.init('{looker_url}');

                // 2. Load everything on page load
                window.onload = async () => {{
                    updateStatus('Fetching brands and embed URL...');
                    await Promise.all([
                        loadBrands(),
                        embedDashboard()
                    ]);
                }};

                function updateStatus(msg) {{
                    document.getElementById('status').innerText = 'Status: ' + msg;
                }}

                // Fetch brands from local API (which proxies to Looker API)
                async function loadBrands() {{
                    try {{
                        const response = await fetch('/api/brands');
                        if (!response.ok) {{
                            const errorText = await response.text();
                            throw new Error(errorText || 'Failed to fetch brands');
                        }}
                        const data = await response.json();
                        
                        const select = document.getElementById('brand-select');
                        select.innerHTML = '<option value="">All Brands</option>';
                        
                        data.forEach(row => {{
                            // Looker API returns list of dicts. We query products.brand.
                            const brand = row['products.brand'];
                            if (brand) {{
                                const option = document.createElement('option');
                                option.value = brand;
                                option.text = brand;
                                select.appendChild(option);
                            }}
                        }});
                        select.disabled = false;
                        console.log("Brands successfully loaded via Looker API");
                    }} catch (error) {{
                        console.error('Error loading brands:', error);
                        document.getElementById('brand-select').innerHTML = `<option value="">Error: ${{error.message}}</option>`;
                    }}
                }}

                // Fetch signed SSO URL and embed
                async function embedDashboard() {{
                    try {{
                        const response = await fetch('/api/embed-url');
                        if (!response.ok) throw new Error('Failed to fetch embed URL');
                        const data = await response.json();
                        let targetUrl = data.url;
                        if (targetUrl.indexOf('sdk=2') === -1) {{
                            const sep = targetUrl.indexOf('?') !== -1 ? '&' : '?';
                            targetUrl += sep + 'sdk=2&embed_domain=' + encodeURIComponent(window.location.origin);
                        }}
                        console.log("Embedding dashboard using fetched SSO URL:", targetUrl);

                        EmbedSDK.createDashboardWithUrl(targetUrl)
                            .appendTo('#dashboard-container')
                            .withClassName('looker-embed')
                            .on('dashboard:run:start', () => updateStatus('Looker is running queries...'))
                            .on('dashboard:run:complete', () => updateStatus('Loaded'))
                            .build()
                            .connect()
                            .then((dashboard) => {{
                                console.log('Embed SDK Connected!');
                                updateStatus('Ready');
                                activeDashboard = dashboard;
                            }})
                            .catch((error) => {{
                                console.error('Embed SDK Connection failed:', error);
                                updateStatus('Embed Connection Failed');
                            }});

                    }} catch (error) {{
                        console.error('Error embedding:', error);
                        updateStatus('Failed to get Embed URL');
                    }}
                }}

                // Handle filter change
                function brandChanged() {{
                    if (!activeDashboard) {{
                        console.warn("Dashboard not ready");
                        return;
                    }}
                    const selectedBrand = document.getElementById('brand-select').value;
                    console.log("Host action: Filtering by Brand =", selectedBrand);
                    updateStatus('Applying brand filter: ' + (selectedBrand || 'All') + '...');
                    
                    // Update 'Brand' filter and run
                    activeDashboard.updateFilters({{ 'Brand': selectedBrand }});
                    activeDashboard.run();
                }}
            </script>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def serve_embed_url(self):
        config = load_embed_config()
        host_header = self.headers.get("Host", "localhost:8080")
        embed_domain = f"http://{host_header}"
        try:
            sso_url = generate_sso_url(config, embed_domain)
            response_data = {"url": sso_url}
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode("utf-8"))
        except Exception as e:
            self.send_error_response(500, f"Error generating SSO URL: {e}")

    def serve_brands(self):
        sdk = get_api_sdk()
        if sdk is None:
            self.send_error_response(500, "Looker API SDK not initialized. Is looker.ini configured?")
            return

        try:
            # Query Looker API to get distinct brands from order_items explore
            query = models.WriteQuery(
                model="training_ecommerce",
                view="order_items", # Explore name
                fields=["products.brand"],
                limit="20",
                sorts=["products.brand asc"]
            )
            result_json = sdk.run_inline_query(
                result_format="json",
                body=query
            )
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(result_json.encode("utf-8"))

        except Exception as e:
            self.send_error_response(500, f"Looker API Error: {e}")

def run_server():
    # Load config to verify it exists
    load_embed_config()
    # Try to initialize API SDK
    get_api_sdk()
    
    port = 8080
    server = HTTPServer(("localhost", port), RichAppHandler)
    print(f"Rich App Server started at http://localhost:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.server_close()

if __name__ == "__main__":
    run_server()
