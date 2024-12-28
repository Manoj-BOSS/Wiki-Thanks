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
            "rvprop": "user|timestamp|comment|size|ids|content",
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
                # Get the diff for this revision
                diff_params = {
                    "action": "compare",
                    "format": "json",
                    "fromrev": rev["revid"],
                    "torelative": "prev",
                    "prop": "diff|ids|title|content",
                    "origin": "*"
                }
                
                try:
                    # Get the current revision content
                    current_params = {
                        "action": "query",
                        "format": "json",
                        "prop": "revisions",
                        "revids": rev["revid"],
                        "rvprop": "content|ids",
                        "origin": "*"
                    }
                    
                    diff_response = requests.get(self.base_url, params=diff_params, headers=self.headers)
                    current_response = requests.get(self.base_url, params=current_params, headers=self.headers)
                    
                    diff_data = diff_response.json()
                    current_data = current_response.json()
                    
                    # Get current content from the revision
                    current_content = ""
                    if "query" in current_data and "pages" in current_data["query"]:
                        for page in current_data["query"]["pages"].values():
                            if "revisions" in page and len(page["revisions"]) > 0:
                                current_content = page["revisions"][0].get("*", "")
                    
                    user_changes.append({
                        "timestamp": rev["timestamp"],
                        "comment": rev.get("comment", ""),
                        "sizediff": rev.get("size", 0),
                        "revid": rev["revid"],
                        "before": diff_data.get("compare", {}).get("fromtext", "Previous content not available"),
                        "after": current_content or "Content not available",
                        "diff_html": diff_data.get("compare", {}).get("*", "")
                    })
                except Exception as e:
                    print(f"Error fetching diff: {e}")
                    continue
                
            return user_changes
        return []
