import os
import requests

# 1. Setup and Authentication
TOKEN = os.getenv("GH_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github.v3+json"}
USERNAME = "nami-rangana"

# Languages to ignore (Goodbye, Roff!)
IGNORE_LIST = ["Roff", "Jupyter Notebook", "HTML", "CSS"]

def get_language_stats():
    # Fetch all repositories (public and private) accessible by the token
    repos_url = f"https://api.github.com/search/repositories?q=user:{USERNAME}"
    response = requests.get(repos_url, headers=HEADERS).json()
    
    language_bytes = {}
    
    # Iterate through repos and fetch language data
    for repo in response.get("items", []):
        lang_url = repo["languages_url"]
        langs = requests.get(lang_url, headers=HEADERS).json()
        
        for lang, bytes_count in langs.items():
            if lang not in IGNORE_LIST:
                language_bytes[lang] = language_bytes.get(lang, 0) + bytes_count
                
    return language_bytes

def generate_svg(stats):
    total_bytes = sum(stats.values())
    
    # Sort languages by usage
    sorted_langs = sorted(stats.items(), key=lambda x: x[1], reverse=True)[:5] # Top 5
    
    # Basic SVG generation (You can style this to match the Dracula theme later)
    svg_content = f'''<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="#282a36" rx="10"/>
        <text x="20" y="30" font-family="Arial" font-size="18" fill="#ff79c6" font-weight="bold">Most Used Languages</text>
    '''
    
    y_offset = 70
    for lang, b in sorted_langs:
        percentage = (b / total_bytes) * 100
        svg_content += f'<text x="20" y="{y_offset}" font-family="Arial" font-size="14" fill="#f8f8f2">{lang}: {percentage:.1f}%</text>\n'
        y_offset += 25
        
    svg_content += '</svg>'
    
    with open("languages.svg", "w") as f:
        f.write(svg_content)

if __name__ == "__main__":
    stats = get_language_stats()
    generate_svg(stats)
    print("SVG generated successfully.")
