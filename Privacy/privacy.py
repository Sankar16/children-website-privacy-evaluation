import pandas as pd
import matplotlib.pyplot as plt

# Load your CSV file
df = pd.read_csv('C:/Users/vinee/Downloads/Privacy/Dataset.csv')

# Clean column names by stripping whitespace and newlines
df.columns = df.columns.str.strip()

# Print column names to verify
print("Column names:")
print(df.columns.tolist())
print("\nDataset shape:", df.shape)

# ----------- Bar Chart: Ads Visible by Category -----------
plt.figure(figsize=(10,6))
ad_counts = df.groupby(['category', 'ads_visible_to_children']).size().unstack(fill_value=0)
ax = ad_counts.plot(kind='bar', stacked=True, color=['skyblue', 'salmon'])
plt.title('Ads Visible to Children by Category')
plt.ylabel('Number of Sites')
plt.xlabel('Category')
plt.xticks(rotation=45, ha='right')
plt.legend(['No Ads', 'Ads Visible'])
plt.tight_layout()
plt.savefig('ads_visible_by_category.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------- Pie Chart: Privacy Policy Link Presence -----------
plt.figure(figsize=(8,8))
privacy_counts = df['privacy_policy_link_present'].value_counts()
colors = ['lightgreen', 'lightcoral']
plt.pie(privacy_counts.values, labels=privacy_counts.index, autopct='%1.1f%%', 
        startangle=90, colors=colors)
plt.title('Privacy Policy Link Present')
plt.tight_layout()
plt.savefig('privacy_policy_pie.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------- Bar Chart: Third-party Trackers by Category -----------
plt.figure(figsize=(10,6))
tracker_counts = df.groupby(['category', 'third_party_trackers_detected']).size().unstack(fill_value=0)
ax = tracker_counts.plot(kind='bar', stacked=True, color=['#7fc97f','#beaed4'])
plt.title('Third-party Trackers Detected by Category')
plt.ylabel('Number of Sites')
plt.xlabel('Category')
plt.xticks(rotation=45, ha='right')
plt.legend(['No Trackers', 'Trackers Detected'])
plt.tight_layout()
plt.savefig('trackers_by_category.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------- Bar Chart: Parental Consent Mechanism by Category -----------
plt.figure(figsize=(10,6))
consent_counts = df.groupby(['category', 'parental_consent_mechanism']).size().unstack(fill_value=0)
ax = consent_counts.plot(kind='bar', stacked=True, color=['#fdc086','#386cb0'])
plt.title('Parental Consent Mechanism by Category')
plt.ylabel('Number of Sites')
plt.xlabel('Category')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('parental_consent_by_category.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------- Bar Chart: Ad Type Distribution -----------
plt.figure(figsize=(14,8))
# Clean ad_type data - remove tabs, newlines, and extra spaces
df['ad_type_clean'] = df['ad_type'].str.replace('\t', '').str.replace('\n', '').str.strip()
ad_type_counts = df['ad_type_clean'].value_counts()

# Create horizontal bar chart for better readability
ax = ad_type_counts.plot(kind='barh', color='lightblue', figsize=(12,8))
plt.title('Ad Type Distribution')
plt.xlabel('Number of Sites')
plt.ylabel('Ad Type')
plt.tight_layout()
plt.savefig('ad_type_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------- Pie Chart: Child Friendly UI -----------
plt.figure(figsize=(8,8))
ui_counts = df['child_friendly_UI'].value_counts()
colors = ['#a6cee3','#b2df8a']
plt.pie(ui_counts.values, labels=ui_counts.index, autopct='%1.1f%%', 
        startangle=90, colors=colors)
plt.title('Child-Friendly UI Distribution')
plt.tight_layout()
plt.savefig('child_friendly_ui_pie.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------- Bar Chart: Privacy Policy Child Section by Category -----------
plt.figure(figsize=(10,6))
child_section_counts = df.groupby(['category', 'privacy_policy_child_section']).size().unstack(fill_value=0)
ax = child_section_counts.plot(kind='bar', stacked=True, color=['#ff9999','#66b3ff'])
plt.title('Privacy Policy Child Section by Category')
plt.ylabel('Number of Sites')
plt.xlabel('Category')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('privacy_child_section_by_category.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------- Bar Chart: Personal Data Collection by Category -----------
plt.figure(figsize=(10,6))
personal_data_counts = df.groupby(['category', 'asks_for_personal_data']).size().unstack(fill_value=0)
ax = personal_data_counts.plot(kind='bar', stacked=True, color=['#90EE90','#FFB6C1'])
plt.title('Personal Data Collection by Category')
plt.ylabel('Number of Sites')
plt.xlabel('Category')
plt.xticks(rotation=45, ha='right')
plt.legend(['No Personal Data', 'Asks for Personal Data'])
plt.tight_layout()
plt.savefig('personal_data_by_category.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------- Summary Statistics -----------
print("\n=== PRIVACY ANALYSIS SUMMARY ===")
print(f"Total websites analyzed: {len(df)}")
print(f"\nWebsites by category:")
print(df['category'].value_counts())

print(f"\nPrivacy policy present: {df['privacy_policy_link_present'].value_counts()}")
print(f"\nChild-friendly UI: {df['child_friendly_UI'].value_counts()}")
print(f"\nAds visible to children: {df['ads_visible_to_children'].value_counts()}")
print(f"\nThird-party trackers detected: {df['third_party_trackers_detected'].value_counts()}")

print('\n=== Charts saved as PNG files ===')
print('1. ads_visible_by_category.png - Ads visibility by website category')
print('2. privacy_policy_pie.png - Privacy policy presence distribution')
print('3. trackers_by_category.png - Third-party trackers by category')
print('4. parental_consent_by_category.png - Parental consent mechanisms')
print('5. ad_type_distribution.png - Distribution of advertisement types')
print('6. child_friendly_ui_pie.png - Child-friendly UI distribution')
print('7. privacy_child_section_by_category.png - Privacy policy child sections')
print('8. personal_data_by_category.png - Personal data collection practices')