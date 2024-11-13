import requests
import json
import time
import os
from typing import Dict, Optional, List
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'

class FarcasterDog:
    def __init__(self):
        self.base_url = "https://api.farcasterdog.xyz"
        self.token_file = "token.txt"
        self.headers = {
            "Accept": "application/json",
            "Origin": "https://farcasterdog.xyz",
            "Referer": "https://farcasterdog.xyz/",
            "Content-Type": "application/json"
        }

    def save_token(self, token: str) -> None:
        with open(self.token_file, "w") as f:
            f.write(token)

    def load_token(self) -> Optional[str]:
        if os.path.exists(self.token_file):
            with open(self.token_file, "r") as f:
                return f.read().strip()
        return None

    def get_user_data(self, jwt_token: str) -> Optional[Dict]:
        verify_url = f"{self.base_url}/api/user/select"
        headers = {**self.headers, "Cookie": f"token={jwt_token}"}
        try:
            response = requests.get(verify_url, headers=headers)
            if response.status_code == 200:
                return response.json()[0]
            return None
        except Exception:
            return None

    def get_updated_points(self, fid: int, jwt_token: str) -> Optional[int]:
        url = f"{self.base_url}/api/point/select_point_by_fid"
        headers = {**self.headers, "Cookie": f"token={jwt_token}"}
        payload = {"fid": fid}
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                return data[0]['Point']
            return None
        except Exception:
            return None

    def update_points(self, task_id: int, fid: int, points: int, jwt_token: str) -> bool:
        url = f"{self.base_url}/api/user/update_point"
        headers = {**self.headers, "Cookie": f"token={jwt_token}"}
        payload = {
            "taskId": task_id,
            "fid": fid,
            "point": points
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)

            return response.status_code == 200 and "Update point thành công" in response.json().get("message", "")
        except Exception:
            return False
    def update_points_main(self, task_id: int, fid: int, points: int, jwt_token: str) -> bool:
        url = f"{self.base_url}/api/user/update_point"
        headers = {**self.headers, "Cookie": f"token={jwt_token}"}
        payload = {
            "taskId": task_id,
            "fid": fid,
            "point": points
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            
            # Check for both success and already claimed status
            if response.status_code == 200 and "Update point thành công" in response.json().get("message", ""):
                return True
            elif response.status_code == 202:
                print(f"{Colors.YELLOW}        -> Points already claimed{Colors.RESET}")
                return True
            return False
        except Exception:
            return False

    def display_user_info(self, user_data: Dict) -> None:
        print(f"\n{Colors.GREEN}[+] Login Success !!!{Colors.RESET}")
        print(f"{Colors.BLUE}[+] userName : {Colors.YELLOW}{user_data['userName']}{Colors.RESET}")
        print(f"{Colors.BLUE}[+] fid      : {Colors.YELLOW}{user_data['fid']}{Colors.RESET}")
        print(f"{Colors.BLUE}[+] Point    : {Colors.YELLOW}{user_data['Point']}{Colors.RESET}")
        print(f"{Colors.BLUE}[+] Follow   : {Colors.YELLOW}{user_data['followCount']}{Colors.RESET}")
        print(f"{Colors.BLUE}[+] Time     : {Colors.YELLOW}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")

    def get_daily_tasks(self, fid_id: int, jwt_token: str) -> List[Dict]:
        url = f"{self.base_url}/api/user/all_task/task_daily"
        headers = {**self.headers, "Cookie": f"token={jwt_token}"}
        payload = {
            "fidId": fid_id,
            "page": 1,
            "limit": 10
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception:
            return []

    def click_task(self, task_id: int, fid: int, task_name: str, jwt_token: str) -> bool:
        url = f"{self.base_url}/api/user/reg_click_status"
        headers = {**self.headers, "Cookie": f"token={jwt_token}"}
        payload = {
            "taskId": task_id,
            "fid": fid,
            "taskName": task_name,
            "clickStatus": None
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            return response.status_code == 200 or response.status_code == 202
        except Exception:
            return False

    def update_task_status(self, fid_id: int, task_id: int, jwt_token: str) -> Dict:
        url = f"{self.base_url}/api/user/task/task_daily/select_updated_task"
        headers = {**self.headers, "Cookie": f"token={jwt_token}"}
        payload = {
            "fidId": fid_id,
            "taskId": task_id
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json()[0]
            return {}
        except Exception:
            return {}

    def process_tasks(self, user_data: Dict, jwt_token: str):
        fid_id = user_data['fid']
        print(f"{Colors.BLUE}[+] Starting Daily Tasks Processing...{Colors.RESET}")
        
        tasks = self.get_daily_tasks(fid_id, jwt_token)
        if not tasks:
            print(f"{Colors.RED}        -> No daily tasks found{Colors.RESET}")
            return

        total_points_gained = 0
        for task in tasks:
            task_id = task['taskId']
            task_name = task['taskName']
            task_points = task['point']
            
            print(f"{Colors.BLUE}        -> Task Name : {Colors.YELLOW}{task_name}{Colors.RESET}")
            
            # Click task
            if self.click_task(task_id, fid_id, task_name, jwt_token):
                time.sleep(1)  # Small delay after clicking
                
                # Update task status
                updated_task = self.update_task_status(fid_id, task_id, jwt_token)
                if updated_task.get('clickStatus') == 1:
                    # Claim points
                    if self.update_points(task_id, fid_id, task_points, jwt_token):
                        total_points_gained += task_points
                        print(f"{Colors.GREEN}        -> Successfully claimed - Points {task_points}{Colors.RESET}")
                    else:
                        print(f"{Colors.RED}        -> Failed to claim points{Colors.RESET}")
                else:
                    print(f"{Colors.RED}        -> Task not ready to claim{Colors.RESET}")
                
                time.sleep(2)  # Wait before next task
            else:
                print(f"{Colors.RED}        -> Failed to process task{Colors.RESET}")

        # Get updated points
        new_points = self.get_updated_points(fid_id, jwt_token)
        if new_points:
            print(f"\n{Colors.GREEN}        -> Total points gained: {total_points_gained}{Colors.RESET}")
            print(f"{Colors.GREEN}        -> Current total points: {new_points}{Colors.RESET}")

        print(f"\n{Colors.GREEN}=== [ Daily tasks processing completed! ] ==={Colors.RESET}\n")

    def get_main_tasks(self, fid_id: int, jwt_token: str) -> List[Dict]:
        url = f"{self.base_url}/api/user/all_task/task_main"
        headers = {**self.headers, "Cookie": f"token={jwt_token}"}
        payload = {
            "fidId": fid_id,
            "page": 1,
            "limit": 10
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception:
            return []

    def process_main_tasks(self, user_data: Dict, jwt_token: str):
        fid_id = user_data['fid']
        print(f"{Colors.BLUE}[+] Starting Main Tasks Processing...{Colors.RESET}")
        
        tasks = self.get_main_tasks(fid_id, jwt_token)
        if not tasks:
            print(f"{Colors.RED}        -> No main tasks found{Colors.RESET}")
            return

        total_points_gained = 0
        for task in tasks:
            task_id = task['taskId']
            task_name = task['taskName']
            task_points = task['point']
            
            print(f"{Colors.BLUE}        -> Task Name : {Colors.YELLOW}{task_name}{Colors.RESET}")
            
            # Click task
            if self.click_task(task_id, fid_id, task_name, jwt_token):
                time.sleep(1)  # Small delay after clicking
                
                # Update task status
                self.update_task_status(fid_id, task_id, jwt_token)
                 
                if self.update_points_main(task_id, fid_id, task_points, jwt_token):
                        total_points_gained += task_points
                        print(f"{Colors.GREEN}        -> Successfully claimed - Points {task_points}{Colors.RESET}")
                else:
                        print(f"{Colors.RED}        -> Failed to claim points{Colors.RESET}")
                 
                
                time.sleep(2)  # Wait before next task
            else:
                print(f"{Colors.RED}        -> Failed to process task{Colors.RESET}")

        # Get updated points
        new_points = self.get_updated_points(fid_id, jwt_token)
        if new_points:
            print(f"\n{Colors.GREEN}        -> Total points gained: {total_points_gained}{Colors.RESET}")
            print(f"{Colors.GREEN}        -> Current total points: {new_points}{Colors.RESET}")

        print(f"\n{Colors.GREEN}=== [ Main tasks processing completed! ] ==={Colors.RESET}\n")
    def start(self) -> None:
        jwt_token = self.load_token()
        if not jwt_token:
            print(f"{Colors.RED}[-] Token not found. Please login first.{Colors.RESET}")
            return

        user_data = self.get_user_data(jwt_token)
        if not user_data:
            print(f"{Colors.RED}[-] Failed to get user data{Colors.RESET}")
            return

        self.display_user_info(user_data)
        self.process_tasks(user_data, jwt_token)
        self.process_main_tasks(user_data, jwt_token)

def main():
    bot = FarcasterDog()
    bot.start()

if __name__ == "__main__":
    main()