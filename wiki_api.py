from flask import Flask, jsonify
import requests
class WikiAPI:
    def __init__(self):
        self.base_url = "https://api.wikimedia.org/core/v1/wikipedia/en"
        self.headers = {
            "Authorization": "Bearer YOUR_ACCESS_TOKEN",
            "Api-User-Agent": "YourApp (your@email.com)"
        }
    def get_page_history(self, page_title):
        url = f"{self.base_url}/page/{page_title}/history"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            revisions = response.json().get("revisions", [])
            contributors = []
            for rev in revisions:
                contributors.append({
                    "id": rev["id"],
                    "name": rev["user"]["name"],
                    "avatar": f"https://ui-avatars.com/api/?name={rev['user']['name']}&background=random",
                    "editDate": rev["timestamp"],
                    "editDescription": rev["comment"],
                    "thanked": False,
                    "role": "Contributor"
                })
            return contributors
        return []
