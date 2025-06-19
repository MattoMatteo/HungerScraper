from enum import Enum

selenium_coockies = []

selenium_user_agent = "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

Ministers = [
    {"names": "Mark Carney", "nation": "Canada"},
    {"names": "Emmanuel Macron", "nation": "Francia"},
    {"names": "Friedrich Merz", "nation": "Germania"},
    {"names": "Giorgia Meloni", "nation": "Italy"},
    {"names": "Shigeru Ishiba", "nation": "Giappone"},
    {"names": "Keir Starmer", "nation": "Regno Unito"},
    {"names": "Donald Trump", "nation": "Stati Uniti"},
    {"names": "António Costa", "nation": "Unione Europea"},
    {"names": "Ursula von der Leyen", "nation": "Unione Europea"},
]

Priorities = [
    "Protecting our communities and the world",
    "Building energy security and accelerating the digital transition",
    "Securing the partnerships of the future",
    "War in Ukraine"
]

engagement_groups = [
    {"name": "Business 7", "code_name": "B7"},
    {"name": "Civil Society 7", "code_name": "C7"},
    {"name": "Labour 7", "code_name": "L7"},
    {"name": "Science 7", "code_name": "S7"},
    {"name": "Think 7", "code_name": "T7"},
    {"name": "Women 7", "code_name": "W7"},
    {"name": "Youth 7", "code_name": "Y7"}
]

class Tablist(Enum):
    TOP = 1,
    LATEST = 2,

def generate_X_page_from_hashtag(hashtag: str, tablist:Tablist) -> str:
    if tablist == Tablist.TOP:
        return f"https://x.com/search?q=%23{hashtag}&src=typed_query"
    elif tablist == Tablist.LATEST:
        return f"https://x.com/search?q=%23{hashtag}&src=typed_query&f=live"