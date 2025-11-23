import requests
from bs4 import BeautifulSoup
import pandas as pd
import tldextract
import re
from urllib.parse import urljoin, urlparse
import warnings

warnings.filterwarnings('ignore', category=DeprecationWarning)

def get_soup(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return BeautifulSoup(res.text, 'html.parser'), res.text
    except:
        pass
    return None, None

def extract_all_third_party_domains(url, html_content, soup):
    if not soup:
        return []
    
    try:
        main_domain = tldextract.extract(url).fqdn.split('.')[-2] + '.' + tldextract.extract(url).fqdn.split('.')[-1] if '.' in tldextract.extract(url).fqdn else tldextract.extract(url).domain
        third_party_domains = set()
        
        for script in soup.find_all('script', src=True):
            src = urljoin(url, script['src'])
            ext = tldextract.extract(src)
            domain = f"{ext.domain}.{ext.suffix}" if ext.suffix else ext.domain
            if domain and domain != main_domain and ext.domain:
                third_party_domains.add(domain)
        
        for iframe in soup.find_all('iframe', src=True):
            src = urljoin(url, iframe['src'])
            ext = tldextract.extract(src)
            domain = f"{ext.domain}.{ext.suffix}" if ext.suffix else ext.domain
            if domain and domain != main_domain and ext.domain:
                third_party_domains.add(domain)
        
        for img in soup.find_all('img', src=True):
            src = urljoin(url, img['src'])
            ext = tldextract.extract(src)
            domain = f"{ext.domain}.{ext.suffix}" if ext.suffix else ext.domain
            if domain and domain != main_domain and ext.domain:
                third_party_domains.add(domain)
        
        for link in soup.find_all('link', href=True):
            href = urljoin(url, link['href'])
            ext = tldextract.extract(href)
            domain = f"{ext.domain}.{ext.suffix}" if ext.suffix else ext.domain
            if domain and domain != main_domain and ext.domain:
                third_party_domains.add(domain)
        
        for media in soup.find_all(['video', 'audio', 'source']):
            src = media.get('src')
            if src:
                src = urljoin(url, src)
                ext = tldextract.extract(src)
                domain = f"{ext.domain}.{ext.suffix}" if ext.suffix else ext.domain
                if domain and domain != main_domain and ext.domain:
                    third_party_domains.add(domain)
        
        url_pattern = r'https?://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        all_urls = re.findall(url_pattern, html_content)
        
        for found_domain in all_urls:
            ext = tldextract.extract(found_domain)
            domain = f"{ext.domain}.{ext.suffix}" if ext.suffix else ext.domain
            if domain and domain != main_domain and ext.domain:
                third_party_domains.add(domain)
        
        return list(third_party_domains)
    
    except Exception as e:
        print(f"Error extracting domains: {e}")
        return []

#Here we're detecting ads using automation only
def detect_ads_automated(soup, html_content):
    if not soup:
        return "Unknown", "None", 0
    
    ad_indicators = 0
    ad_types = set()
    
    for element in soup.find_all(True):
        classes = ' '.join(element.get('class', [])).lower()
        if any(word in classes for word in ['ad', 'advertisement', 'sponsor', 'promo', 'banner']):
            ad_indicators += 1
            if 'banner' in classes:
                ad_types.add('Banner')
            elif 'video' in classes:
                ad_types.add('Video')
            elif 'popup' in classes or 'modal' in classes:
                ad_types.add('Popup')
            else:
                ad_types.add('Display')
        
        elem_id = element.get('id', '').lower()
        if any(word in elem_id for word in ['ad', 'advertisement', 'sponsor']):
            ad_indicators += 1
    
    #Check iframes
    iframes = soup.find_all('iframe')
    for iframe in iframes:
        src = iframe.get('src', '').lower()
        if any(pattern in src for pattern in ['ad', 'advertis', 'sponsor', 'promo', 'banner']):
            ad_indicators += 2
            ad_types.add('Third-party')
    
    #Check for ad-like scripts
    for script in soup.find_all('script', src=True):
        src = script.get('src', '').lower()
        if any(pattern in src for pattern in ['ad', 'advertis', 'sponsor']):
            ad_indicators += 1
    
    #Check HTML content for ad-related text
    if re.search(r'\bad[sv]?\b|\badvert', html_content.lower()):
        ad_indicators += 1
    
    if ad_indicators >= 5:
        ads_present = "Yes"
    elif ad_indicators >= 2:
        ads_present = "Likely"
    else:
        ads_present = "No"
    
    ad_type_str = ", ".join(ad_types) if ad_types else "None detected"
    
    return ads_present, ad_type_str, ad_indicators

def analyze_child_friendly_ui(soup):
    """Analyze UI for child-friendliness - automated scoring"""
    if not soup:
        return "Unknown", 0
    
    score = 0
    max_score = 10
    
    #Large buttons/interactive elements
    buttons = soup.find_all(['button', 'a'])
    large_button_count = 0
    for btn in buttons[:30]:
        classes = ' '.join(btn.get('class', [])).lower()
        if any(word in classes for word in ['large', 'big', 'btn-lg', 'primary', 'xl']):
            large_button_count += 1
    
    if large_button_count > 5:
        score += 2
    elif large_button_count > 2:
        score += 1
    
    #Playful/educational language
    text = soup.get_text().lower()
    child_keywords = ['fun', 'play', 'game', 'learn', 'explore', 'discover', 'adventure', 'exciting']
    keyword_count = sum(1 for word in child_keywords if word in text)
    score += min(keyword_count * 0.3, 2)
    
    #Visual content
    images = len(soup.find_all('img'))
    videos = len(soup.find_all('video'))
    
    if images > 20 or videos > 3:
        score += 2
    elif images > 10:
        score += 1
    
    #Interactive elements
    interactive = len(soup.find_all(['canvas', 'svg']))
    score += min(interactive * 0.5, 2)
    
    #Color-related content
    if any(word in text for word in ['color', 'rainbow', 'bright', 'vibrant']):
        score += 1
    
    #Simple navigation
    nav_elements = len(soup.find_all(['nav', 'header']))
    if nav_elements <= 3:
        score += 1
    
    #Minimal forms
    forms = len(soup.find_all('form'))
    if forms <= 1:
        score += 1
    
    percentage = (score / max_score) * 100
    
    if percentage >= 70:
        return "Highly Child-Friendly", round(percentage, 1)
    elif percentage >= 40:
        return "Moderately Child-Friendly", round(percentage, 1)
    else:
        return "Not Child-Friendly", round(percentage, 1)

def find_privacy_link(soup, base_url):
    """Find privacy policy link"""
    if not soup:
        return None
    
    for a in soup.find_all('a', href=True):
        href = a.get('href', '').lower()
        text = a.get_text().lower()
        
        if 'privacy' in href or 'privacy' in text:
            return urljoin(base_url, a['href'])
    
    return None

def check_coppa_compliance(soup, privacy_url, third_party_count, ads_present):
    compliance_score = 0
    max_score = 8
    issues = []
    
    if not soup:
        return {"score": 0, "percentage": 0, "compliant": False, "issues": ["Cannot access"]}
    
    #Privacy policy exists
    if privacy_url:
        compliance_score += 1
    else:
        issues.append("No privacy policy")
    
    #Check privacy policy content
    if privacy_url:
        privacy_soup, privacy_html = get_soup(privacy_url)
        if privacy_soup:
            privacy_text = privacy_soup.get_text().lower()
            
            #Children-specific section
            if any(word in privacy_text for word in ['child', 'children', 'minor', 'under 13', 'coppa']):
                compliance_score += 1
            else:
                issues.append("No child section in privacy policy")
            
            #Parental consent
            if any(word in privacy_text for word in ['parental consent', 'parent permission', 'guardian']):
                compliance_score += 1
            else:
                issues.append("No parental consent mechanism")
            
            #Data disclosure
            if 'collect' in privacy_text and 'personal information' in privacy_text:
                compliance_score += 1
            else:
                issues.append("Insufficient data disclosure")
        else:
            issues.append("Cannot access privacy policy")
    
    #Age verification on main site
    main_text = soup.get_text().lower()
    if any(word in main_text for word in ['age verification', 'enter your age', 'how old are you']):
        compliance_score += 1
    else:
        issues.append("No age verification")
    
    #Data minimization
    forms = soup.find_all('form')
    sensitive_found = False
    for form in forms:
        for inp in form.find_all('input'):
            name = inp.get('name', '').lower()
            if any(s in name for s in ['ssn', 'credit', 'card', 'location']):
                sensitive_found = True
                break
    
    if not sensitive_found:
        compliance_score += 1
    else:
        issues.append("Collects sensitive data")
    
    #Limited third-party connections
    if third_party_count <= 5:
        compliance_score += 1
    else:
        issues.append(f"Too many third-parties ({third_party_count})")
    
    #No behavioral advertising
    if ads_present == "No":
        compliance_score += 1
    else:
        issues.append("Advertising detected")
    
    percentage = (compliance_score / max_score) * 100
    
    return {
        "score": compliance_score,
        "total": max_score,
        "percentage": round(percentage, 2),
        "compliant": percentage >= 60,
        "issues": issues
    }

def analyze_website(url):
    """Main analysis function - completely automated"""
    print(f"\n🔍 Analyzing: {url}")
    
    soup, html_content = get_soup(url)
    
    if not soup:
        print(f"Failed to access")
        return None
    
    base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    
    #Find privacy policy
    privacy_link = find_privacy_link(soup, base_url)
    
    #Extract all third-party domains
    third_party_domains = extract_all_third_party_domains(url, html_content, soup)
    
    #Detect ads
    ads_visible, ad_type, ad_score = detect_ads_automated(soup, html_content)
    
    #UI analysis
    ui_friendliness, ui_score = analyze_child_friendly_ui(soup)
    
    #COPPA compliance
    coppa = check_coppa_compliance(soup, privacy_link, len(third_party_domains), ads_visible)
    
    #Check for personal data forms
    forms = soup.find_all('form')
    personal_data = "No"
    for form in forms:
        for inp in form.find_all('input'):
            name = inp.get('name', '').lower()
            if any(k in name for k in ['email', 'name', 'phone', 'age', 'birth']):
                personal_data = "Yes"
                break
    
    #Check for parental consent mentions
    main_text = soup.get_text().lower()
    parental_consent = "Yes" if any(word in main_text for word in ['parental consent', 'parent permission', 'guardian approval']) else "No"
    
    print(f" Third-parties: {len(third_party_domains)} | Ads: {ads_visible} | COPPA: {coppa['percentage']}%")
    
    return {
        "website": url,
        "privacy_policy_present": "Yes" if privacy_link else "No",
        "privacy_policy_url": privacy_link or "Not Found",
        "asks_personal_data": personal_data,
        "parental_consent_mentioned": parental_consent,
        "total_third_party_domains": len(third_party_domains),
        "third_party_domains_list": ", ".join(third_party_domains[:15]) + ("..." if len(third_party_domains) > 15 else ""),
        "ads_detected": ads_visible,
        "ad_types": ad_type,
        "ad_indicator_score": ad_score,
        "child_friendly_ui": ui_friendliness,
        "ui_score_percentage": f"{ui_score}%",
        "coppa_score": f"{coppa['score']}/{coppa['total']}",
        "coppa_percentage": f"{coppa['percentage']}%",
        "coppa_compliant": "Yes" if coppa['compliant'] else "No",
        "coppa_issues": "; ".join(coppa['issues']) if coppa['issues'] else "Compliant"
    }

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


print("="*70)
print("  CHILDREN'S WEBSITE PRIVACY AUDIT - FULLY AUTOMATED")
print("="*70)

results = []
for site in websites:
    result = analyze_website(site)
    if result:
        results.append(result)

df = pd.DataFrame(results)

output_file = "website_privacy_audit_automated.csv"
df.to_csv(output_file, index=False)

print("\n" + "="*70)
print("AUDIT COMPLETE")
print("="*70)
print(f"File: {output_file}")
print(f"\nRESULTS:")
print(f"  • Websites analyzed: {len(results)}")
print(f"  • Third-party domains found: {df['total_third_party_domains'].sum()}")
print(f"  • COPPA compliant: {df[df['coppa_compliant'] == 'Yes'].shape[0]}/{len(results)}")
print(f"  • Average COPPA score: {df['coppa_percentage'].str.rstrip('%').astype(float).mean():.1f}%")
print(f"  • Sites with ads: {df[df['ads_detected'].isin(['Yes', 'Likely'])].shape[0]}")
print("="*70)