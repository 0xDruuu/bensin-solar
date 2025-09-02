import requests
import json
import time
from colorama import init, Fore, Style

# Inisialisasi colorama
init()

# Load konfigurasi
def load_config(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"{Fore.RED}Error loading {file_path}: {e}{Style.RESET_ALL}")
        return None

# Load akun dan proxy
ACCOUNTS = load_config("accounts.json")
PROXY = load_config("proxy.json")
BASE_URL = "https://api-appmini.solr.ltd/api"

def check_ip(session):
    """Cek IP yang dipake proxy"""
    try:
        response = session.get("https://api.ipify.org", timeout=5)
        if response.status_code == 200:
            return response.text
        return None
    except Exception:
        return None

def authenticate(init_data, session):
    """Autentikasi pake initData"""
    endpoint = f"{BASE_URL}/validate"
    payload = {"initData": init_data}
    ip = check_ip(session)
    print(f"{Fore.BLUE}Using IP: {ip or 'Unknown'} for authentication{Style.RESET_ALL}")
    try:
        response = session.post(endpoint, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()["data"]
            return {
                "bearer_token": data["tokenBear"],
                "accept_token": data["token"],
                "user_id": data["userData"]["user_id"]
            }
        else:
            print(f"{Fore.RED}Error auth: {response.status_code} - {response.text}{Style.RESET_ALL}")
            return None
    except Exception as e:
        print(f"{Fore.RED}Authentication error: {e}{Style.RESET_ALL}")
        return None

def get_tasks(bearer_token, accept_token, user_id, session):
    """Ambil daftar task"""
    endpoint = f"{BASE_URL}/user/tasks"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "accept-token": accept_token,
        "Content-Type": "application/json",
        "user-id": str(user_id)
    }
    ip = check_ip(session)
    print(f"{Fore.BLUE}Using IP: {ip or 'Unknown'} for getting tasks{Style.RESET_ALL}")
    try:
        response = session.get(endpoint, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()["data"]["earns"]
        else:
            print(f"{Fore.RED}Error getting tasks: {response.status_code} - {response.text}{Style.RESET_ALL}")
            return None
    except Exception as e:
        print(f"{Fore.RED}Error fetching tasks: {e}{Style.RESET_ALL}")
        return None

def check_task(bearer_token, accept_token, user_id, task_id, task_value, task_type, session):
    """Verifikasi task"""
    endpoint = f"{BASE_URL}/user/check/task"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "accept-token": accept_token,
        "Content-Type": "application/json",
        "user-id": str(user_id)
    }
    payload = {
        "id": task_id,
        "value": task_value,
        "type": task_type
    }
    ip = check_ip(session)
    print(f"{Fore.BLUE}Using IP: {ip or 'Unknown'} for checking task {task_id}{Style.RESET_ALL}")
    try:
        response = session.post(endpoint, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"{Fore.GREEN}Task {task_id} ({task_value}) checked for user {user_id}: {response.json()}{Style.RESET_ALL}")
            return response.json()
        else:
            print(f"{Fore.RED}Error checking task {task_id} for user {user_id}: {response.status_code} - {response.text}{Style.RESET_ALL}")
            return None
    except Exception as e:
        print(f"{Fore.RED}Error checking task for user {user_id}: {e}{Style.RESET_ALL}")
        return None

def daily_checkin(bearer_token, accept_token, user_id, session):
    """Daily check-in"""
    endpoint = f"{BASE_URL}/user/check/in"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "accept-token": accept_token,
        "Content-Type": "application/json",
        "user-id": str(user_id)
    }
    payload = {}
    ip = check_ip(session)
    print(f"{Fore.BLUE}Using IP: {ip or 'Unknown'} for daily check-in{Style.RESET_ALL}")
    try:
        response = session.post(endpoint, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"{Fore.GREEN}Daily check-in successful for user {user_id}: {response.json()}{Style.RESET_ALL}")
            return response.json()
        else:
            print(f"{Fore.RED}Error daily check-in for user {user_id}: {response.status_code} - {response.text}{Style.RESET_ALL}")
            return None
    except Exception as e:
        print(f"{Fore.RED}Error daily check-in for user {user_id}: {e}{Style.RESET_ALL}")
        return None

def get_proxy_config():
    """Mengembalikan konfigurasi proxy untuk satu sesi"""
    if not PROXY:
        return None
    # Ambil proxy langsung dari field 'http' di proxy.json
    proxy_url = PROXY.get("http")
    if not proxy_url:
        print(f"{Fore.RED}Error: No 'http' field found in proxy.json{Style.RESET_ALL}")
        return None
    return {
        "http": proxy_url,
        "https": proxy_url
    }

def main():
    """Main loop"""
    if not ACCOUNTS or not PROXY:
        print(f"{Fore.RED}Error: Failed to load accounts.json or proxy.json{Style.RESET_ALL}")
        return

    print(f"{Fore.CYAN}Starting airdrop automation for @solrappbot...{Style.RESET_ALL}")
    for account in ACCOUNTS:
        init_data = account.get("initData")
        user_id = account.get("user_id")
        if not init_data or not user_id:
            print(f"{Fore.RED}Invalid account data: {account}{Style.RESET_ALL}")
            continue

        print(f"{Fore.CYAN}Processing account: {user_id}{Style.RESET_ALL}")

        # Dapatkan proxy dan buat session untuk akun ini
        proxy = get_proxy_config()
        if not proxy:
            print(f"{Fore.RED}Failed to configure proxy for account {user_id}{Style.RESET_ALL}")
            continue

        # Buat session sekali untuk semua proses di akun ini
        session = requests.Session()
        session.proxies = proxy

        # Autentikasi
        tokens = authenticate(init_data, session)
        if not tokens:
            print(f"{Fore.RED}Failed to authenticate account: {user_id}{Style.RESET_ALL}")
            continue

        # Daily check-in
        daily_checkin(tokens["bearer_token"], tokens["accept_token"], tokens["user_id"], session)
        time.sleep(1)  # Jeda 1 detik untuk menghindari rate limit

        # Ambil task
        tasks = get_tasks(tokens["bearer_token"], tokens["accept_token"], tokens["user_id"], session)
        if tasks:
            for task in tasks:
                if not task["is_active"]:
                    print(f"{Fore.YELLOW}Processing task: {task['title']} ({task['value']}) for user {user_id}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}Manually complete this task first: {task['link']}{Style.RESET_ALL}")
                    check_task(
                        tokens["bearer_token"],
                        tokens["accept_token"],
                        tokens["user_id"],
                        task["id"],
                        task["value"],
                        task["type"],
                        session
                    )
                    time.sleep(2)  # Jeda 2 detik antar task
                else:
                    print(f"{Fore.GREEN}Task {task['title']} already completed for user {user_id}.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}No tasks available for user {user_id}.{Style.RESET_ALL}")
        time.sleep(5)  # Jeda 5 detik antar akun

if __name__ == "__main__":
    main()