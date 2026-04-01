import os
import requests

# 1. Setup and Authentication
TOKEN = os.getenv("GH_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github.v3+json"}
USERNAME = "nami-rangana"

# Languages to ignore
IGNORE_LIST = ["Roff", "Jupyter Notebook", "HTML", "CSS"]

# Standard GitHub Language Colors
LANG_COLORS = {
    "Python": "#3572A5",
    "Shell": "#89e051",
    "C++": "#f34b7d",
    "C": "#555555",
    "Fortran": "#4d41b1",
    "CUDA": "#3A4E3A",
    "CMake": "#DA3434",
    "JavaScript": "#f1e05a",
    "Other": "#858585"
}

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
    if not stats:
        return

    total_bytes = sum(stats.values())
    
    # Sort languages by usage and grab Top 5
    sorted_langs = sorted(stats.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # SVG Dimensions and Layout config
    svg_width = 400
    svg_height = 160  # Increased slightly to accommodate 3 rows of legend
    bar_x = 20
    bar_y = 50
    bar_width = 360
    bar_height = 10
    bar_radius = 5

    # Basic SVG generation with GitHub-style CSS
    svg_content = f'''<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
    <style>
        .bg {{ fill: #0d1117; }}
        .title {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 600; fill: #ffffff; }}
        .lang-name {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 12px; font-weight: 600; fill: #ffffff; }}
        .lang-pct {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 12px; font-weight: 400; fill: #8b949e; }}
    </style>
    
    <rect width="100%" height="100%" class="bg" rx="10"/>
    <text x="{bar_x}" y="30" class="title">Languages</text>
    
    <defs>
        <clipPath id="bar-clip">
            <rect x="{bar_x}" y="{bar_y}" width="{bar_width}" height="{bar_height}" rx="{bar_radius}"/>
        </clipPath>
    </defs>
    
    <g clip-path="url(#bar-clip)">
    '''
    
    # Draw the segments of the bar
    current_x = bar_x
    for lang, b in sorted_langs:
        percentage = (b / total_bytes) * 100
        seg_width = (percentage / 100) * bar_width
        color = LANG_COLORS.get(lang, LANG_COLORS["Other"])
        
        if seg_width > 0:
            svg_content += f'        <rect x="{current_x}" y="{bar_y}" width="{seg_width}" height="{bar_height}" fill="{color}"/>\n'
            current_x += seg_width
            
    svg_content += '    </g>\n\n    \n'
    
    # Draw the legend dynamically in columns
    leg_start_x = bar_x
    leg_start_y = bar_y + 35
    col_width = 170 # Widened for 2 columns
    items_per_row = 2 # Changed to max 2 columns
    
    for i, (lang, b) in enumerate(sorted_langs):
        percentage = (b / total_bytes) * 100
        color = LANG_COLORS.get(lang, LANG_COLORS["Other"])
        
        row = i // items_per_row
        col = i % items_per_row
        
        cx = leg_start_x + (col * col_width)
        cy = leg_start_y + (row * 25)
        
        svg_content += f'''
    <g transform="translate({cx}, {cy})">
        <circle cx="0" cy="-4" r="4" fill="{color}"/>
        <text x="10" y="0">
            <tspan class="lang-name">{lang} </tspan>
            <tspan class="lang-pct">{percentage:.1f}%</tspan>
        </text>
    </g>'''
        
    svg_content += '\n</svg>'
    
    with open("languages.svg", "w") as f:
        f.write(svg_content)

if __name__ == "__main__":
    stats = get_language_stats()
    generate_svg(stats)
    print("SVG generated successfully.")
