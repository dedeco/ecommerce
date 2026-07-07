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

def generate_sso_url(config):
    """Generates a signed Looker SSO Embed URL."""
    looker_url = config["looker_url"]       # e.g., https://your-company.looker.com
    secret = config["embed_secret"]         # SSO Embed Secret
    dashboard_id = config["dashboard_id"]   # e.g., training_ecommerce::business_pulse

    # Parse host
    parsed_url = urllib.parse.urlparse(looker_url)
    host = parsed_url.netloc
    if ":" not in host:
        host = f"{host}:443"  # Default to SSL port if not specified

    # Define the target embed path and the login path
    target_path = f"/embed/dashboards/{dashboard_id}"
    login_path = f"/login/embed/{urllib.parse.quote_plus(target_path)}"

    # User definition (mock data for the demo)
    external_user_id = "demo_user_1"
    first_name = "Demo"
    last_name = "User"
    
    # Permissions and Models granted to this embedded user
    # Must include 'access_data' and 'see_user_dashboards' (or 'see_looks' for looks)
    permissions = ["access_data", "see_user_dashboards"]
    models = ["training_ecommerce"]
    group_ids = []
    external_group_id = "demo_group"
    user_attributes = {}
    force_logout_login = "true"
    
    session_length = 3600  # Session validity in seconds (1 hour)
    nonce = uuid.uuid4().hex
    current_time = str(int(time.time()))

    # Construct the path to sign (MUST be in this exact order, separated by newlines)
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
        "last_name": last_name
    }

    # Build the final signed URL
    encoded_params = urllib.parse.urlencode(query_params)
    sso_url = f"{looker_url}{login_path}?{encoded_params}"
    return sso_url

class EmbedHandler(BaseHTTPRequestHandler):
    """Simple HTTP Handler to serve the HTML page containing the iframe."""
    def do_GET(self):
        if self.path == "/":
            config = load_config()
            try:
                sso_url = generate_sso_url(config)
                
                # HTML template
                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Looker SSO Embed Demo</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f4f6f8; color: #333; }}
                        iframe {{ border: 1px solid #ccc; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                        .header {{ margin-bottom: 20px; }}
                        code {{ background: #eef; padding: 2px 4px; border-radius: 4px; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>Looker SSO Embed Demo</h1>
                        <p>Embedding LookML Dashboard: <code>{config['dashboard_id']}</code></p>
                        <p>Generated SSO URL (valid for 1 hour): <a href="{sso_url}" target="_blank">Open in new tab</a></p>
                    </div>
                    <iframe src="{sso_url}" width="100%" height="800px" frameborder="0"></iframe>
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
    # Verify config exists before starting
    load_config()
    
    port = 8080
    server = HTTPServer(("localhost", port), EmbedHandler)
    print(f"SSO Embed Server started at http://localhost:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.server_close()

if __name__ == "__main__":
    run_server()
