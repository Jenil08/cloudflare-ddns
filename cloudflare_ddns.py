import requests
import sys

# 🔹 Your Cloudflare API Token (Replace this!)
CLOUDFLARE_API_TOKEN = "eGrWGR6WcpmbxW1HBAbxuG5Bt-yhJmIy0N1da0Fx"

# 🔹 Your domain and subdomain
ZONE_NAME = "tic.ip-ddns.com"  # Main domain
RECORD_NAME = "tic.ip-ddns.com"  # Subdomain to update (use same as zone if it's the root domain)

# API Endpoints
ZONE_URL = "https://api.cloudflare.com/client/v4/zones"
IP_URL = "https://api64.ipify.org?format=json"

# Headers for API authentication
HEADERS = {
    "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
    "Content-Type": "application/json",
}

# Function to get the current public IP
def get_public_ip():
    try:
        response = requests.get(IP_URL)
        response.raise_for_status()
        return response.json().get("ip")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching public IP: {e}")
        sys.exit(1)

# Function to get Cloudflare Zone ID
def get_zone_id():
    try:
        response = requests.get(ZONE_URL, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        
        for zone in data.get("result", []):
            if zone["name"] == ZONE_NAME:
                return zone["id"]
        print(f"❌ Zone ID not found for domain: {ZONE_NAME}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching Zone ID: {e}")
        sys.exit(1)

# Function to get DNS Record ID
def get_dns_record_id(zone_id):
    url = f"{ZONE_URL}/{zone_id}/dns_records"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        
        for record in data.get("result", []):
            if record["name"] == RECORD_NAME:
                return record["id"]
        print(f"❌ DNS record not found for {RECORD_NAME}. Make sure it exists in Cloudflare.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching DNS Record ID: {e}")
        sys.exit(1)

# Function to update DNS Record
def update_dns_record(zone_id, record_id, new_ip):
    url = f"{ZONE_URL}/{zone_id}/dns_records/{record_id}"
    data = {
        "type": "A",
        "name": RECORD_NAME,
        "content": new_ip,
        "ttl": 1,  # Auto TTL
        "proxied": False,  # Set to True if using Cloudflare Proxy
    }
    try:
        response = requests.put(url, headers=HEADERS, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error updating DNS record: {e}")
        sys.exit(1)

# Main Execution
if __name__ == "__main__":
    public_ip = get_public_ip()
    print(f"🌍 Current Public IP: {public_ip}")

    zone_id = get_zone_id()
    if not zone_id:
        print("❌ Zone ID not found. Check API token & domain name.")
        sys.exit(1)

    record_id = get_dns_record_id(zone_id)
    if not record_id:
        print("❌ DNS record ID not found. Ensure the record exists in Cloudflare.")
        sys.exit(1)

    update_response = update_dns_record(zone_id, record_id, public_ip)
    if update_response.get("success"):
        print(f"✅ DNS record updated: {RECORD_NAME} -> {public_ip}")
    else:
        print(f"❌ Failed to update DNS record: {update_response}")


