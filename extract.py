import requests
from bs4 import BeautifulSoup
import pandas as pd
import tldextract

# Known tracker domains (you can expand this)
TRACKER_DOMAINS = [
    "google-analytics.com", "googletagmanager.com", "facebook.net", 
    "doubleclick.net", "adservice.google.com", "hotjar.com", 
    "mixpanel.com", "segment.io", "criteo.com", "twitter.com"
]

def get_soup(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return BeautifulSoup(res.text, 'html.parser')
    except:
        return None

def find_privacy_link(soup, base_url):
    if not soup:
        return None
    links = [a.get('href') for a in soup.find_all('a', href=True)]
    for link in links:
        if "privacy" in link.lower():
            if link.startswith('http'):
                return link
            else:
                return base_url.rstrip('/') + '/' + link.lstrip('/')
    return None

def analyze_privacy_policy(url):
    soup = get_soup(url)
    if not soup:
        return "Not Found"
    text = soup.get_text().lower()
    if any(word in text for word in ["child", "children", "minor", "under 13", "parental consent"]):
        return "Yes"
    return "No"

def detect_forms(soup):
    if not soup:
        return "No"
    inputs = [inp.get('name', '').lower() for inp in soup.find_all('input')]
    keywords = ["email", "name", "dob", "birth", "age", "phone", "contact"]
    return "Yes" if any(any(k in i for k in keywords) for i in inputs) else "No"

def detect_parental_consent(soup):
    if not soup:
        return "No"
    text = soup.get_text().lower()
    if any(word in text for word in ["parental consent", "guardian", "age verification", "over 13", "over 18"]):
        return "Yes"
    return "No"

def detect_trackers(base_url):
    try:
        res = requests.get(base_url, timeout=10)
        text = res.text.lower()
        found = [domain for domain in TRACKER_DOMAINS if domain in text]
        return ", ".join(found) if found else "None"
    except:
        return "Error"

def analyze_website(url):
    print(f"Analyzing: {url}")
    soup = get_soup(url)
    base_url = url.split("/")[0] + "//" + url.split("/")[2]
    
    privacy_link = find_privacy_link(soup, base_url)
    privacy_child_section = analyze_privacy_policy(privacy_link) if privacy_link else "Not Found"
    personal_data = detect_forms(soup)
    parental_consent = detect_parental_consent(soup)
    trackers = detect_trackers(url)

    return {
        "website": url,
        "privacy_policy_link_present": "Yes" if privacy_link else "No",
        "privacy_policy_child_section": privacy_child_section,
        "asks_for_personal_data": personal_data,
        "parental_consent_mechanism": parental_consent,
        "third_party_trackers_detected": trackers,
        "ads_visible_to_children": "Manual",
        "ad_type": "Manual",
        "child_friendly_UI": "Manual"
    }

# Input websites here
websites = [
    "https://pbskids.org",
    "https://www.nickjr.com",
    "https://disneyjunior.disney.com",
    "https://www.sesamestreet.org",
    "https://kids.nationalgeographic.com",
    "https://www.abcya.com",
    "https://www.starfall.com",
    "https://www.funbrain.com",
    "https://www.poptropica.com",
    "https://www.cartoonnetwork.com",
    "https://www.highlightskids.com",
    "https://kids.scholastic.com",
    "https://www.crayola.com",
    "https://kids.lego.com",
    "https://www.fisher-price.com",
    "https://www.coolmathgames.com",
    "https://www.brainpop.com",
    "https://www.funology.com",
    "https://www.switchzoo.com",
    "https://www.nwf.org/Kids",
    "https://www.abcmouse.com",
    "https://www.education.com",
    "https://www.turtlediary.com",
    "https://www.roomrecess.com",
    "https://www.splashlearn.com",
    "https://www.e-learningforkids.org",
    "https://www.coolkidfacts.com",
    "https://kids.nationalgeographic.com/littlekids",
    "https://www.nasa.gov/kidsclub",
    "https://www.dkfindout.com",
    "https://www.storylineonline.net",
    "https://abc.com/shows/abc-kids",
    "https://www.safekidgames.com",
    "https://kids.poki.com",
    "https://www.owlieboo.com",
    "https://www.happyclicks.net",
    "https://www.gamesgames.com/games/kids-games",
    "https://www.boomerangtv.co.uk/games",
    "https://kids.nationalgeographic.com/games",
    "https://www.timeforkids.com"
]

# Run analysis
results = [analyze_website(site) for site in websites]
df = pd.DataFrame(results)

# Save to CSV
df.to_csv("website_privacy_audit.csv", index=False)
print("\n Privacy audit completed. Results saved as website_privacy_audit.csv")
print(df)