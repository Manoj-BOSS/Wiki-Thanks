from flask import Flask, jsonify
import requests
class WikiAPI:
    def __init__(self):
        self.base_url = "https://en.wikipedia.org/w/api.php"
        self.headers = {
            "User-Agent": "WikiContributorsHub/1.0 (your@email.com)"
        }
    def get_page_history(self, page_title):
        params = {
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "titles": page_title,
            "rvprop": "user|timestamp|comment|size|ids",
            "rvlimit": "50",
            "origin": "*"
        }
        
        response = requests.get(self.base_url, params=params, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            
            if "-1" in pages:  # Page not found
                return []
                
            page_id = list(pages.keys())[0]
            revisions = pages[page_id].get("revisions", [])
            
            contributors = []
            for rev in revisions:
                # URL encode the username for the avatar
                encoded_username = requests.utils.quote(rev["user"])
                contributors.append({
                    "user": rev["user"],
                    "timestamp": rev["timestamp"],
                    "comment": rev.get("comment", ""),
                    "size": rev.get("size", 0),
                    "revid": rev["revid"],
                    "avatar": f"https://ui-avatars.com/api/?name={encoded_username}&background=random&size=60"
                })
            return contributors
        return []
    def get_user_contributions(self, page_title, username):
        params = {
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "titles": page_title,
            "rvprop": "user|timestamp|comment|size|ids",
            "rvlimit": "50",
            "rvuser": username,
            "origin": "*"
        }
        
        response = requests.get(self.base_url, params=params, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            
            if "-1" in pages:
                return []
                
            page_id = list(pages.keys())[0]
            revisions = pages[page_id].get("revisions", [])
            
            user_changes = []
            for rev in revisions:
                if rev["user"] == username:
                    user_changes.append({
                        "timestamp": rev["timestamp"],
                        "comment": rev.get("comment", ""),
                        "sizediff": rev.get("size", 0),
                        "diff": "Sample diff text"
                    })
            return user_changes
        return []
