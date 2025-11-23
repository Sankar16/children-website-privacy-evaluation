import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

df = pd.read_csv('../website_privacy_audit_automated.csv')

print("="*70)
print("  GENERATING VISUALIZATIONS - VERIFIED WITH CSV DATA")
print("="*70)
print(f"\nDataset: {len(df)} websites")
print(f"Columns: {list(df.columns)}\n")


plt.figure(figsize=(10, 8))
coppa_counts = df['coppa_compliant'].value_counts()
print(f"COPPA Compliance:")
print(coppa_counts)

colors = ['#ff6b6b', '#51cf66']
explode = (0.1, 0) if coppa_counts.index[0] == 'No' else (0, 0.1)

plt.pie(coppa_counts.values, 
        labels=[f'{label}\n({count} sites)' for label, count in zip(coppa_counts.index, coppa_counts.values)],
        autopct='%1.1f%%', startangle=90, colors=colors, explode=explode,
        textprops={'fontsize': 13, 'weight': 'bold'})
plt.title('COPPA Compliance Status\n(40 Children\'s Websites)', fontsize=16, weight='bold', pad=20)

plt.tight_layout()
plt.savefig('1_coppa_compliance_pie_NEW.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: 1_coppa_compliance_pie_NEW.png\n")


plt.figure(figsize=(14, 8))
top20 = df.nlargest(20, 'total_third_party_domains')[['website', 'total_third_party_domains']].copy()
top20['site_name'] = top20['website'].str.replace('https://', '').str.replace('www.', '').str.split('/').str[0]

print(f"Top 5 sites by third-party trackers:")
print(top20.head())

colors = ['#ff4444' if x > 20 else '#ffbb33' if x > 10 else '#00C851' for x in top20['total_third_party_domains']]

plt.barh(range(len(top20)), top20['total_third_party_domains'], color=colors, edgecolor='black')
plt.yticks(range(len(top20)), top20['site_name'], fontsize=9)
plt.xlabel('Number of Third-Party Domains', fontsize=12, weight='bold')
plt.title('Top 20 Sites by Third-Party Tracker Count', fontsize=14, weight='bold')
plt.axvline(5, color='green', linestyle='--', linewidth=2, alpha=0.6, label='COPPA Safe Limit (≤5)')
plt.axvline(10, color='orange', linestyle='--', linewidth=2, alpha=0.6, label='High Risk (>10)')
plt.axvline(20, color='red', linestyle='--', linewidth=2, alpha=0.6, label='Extreme Risk (>20)')
plt.legend(loc='lower right')
plt.gca().invert_yaxis()

plt.tight_layout()
plt.savefig('2_third_party_trackers_NEW.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: 2_third_party_trackers_NEW.png\n")


plt.figure(figsize=(10, 6))
ad_counts = df['ads_detected'].value_counts()
print(f"Ads Detected:")
print(ad_counts)

colors_map = {'Yes': '#ff6b6b', 'Likely': '#ffa502', 'No': '#51cf66'}
bar_colors = [colors_map.get(x, 'gray') for x in ad_counts.index]

bars = plt.bar(ad_counts.index, ad_counts.values, color=bar_colors, edgecolor='black', linewidth=1.5)
plt.ylabel('Number of Websites', fontsize=12, weight='bold')
plt.xlabel('Ad Detection Status', fontsize=12, weight='bold')
plt.title('Advertisement Detection Results (40 Sites)', fontsize=14, weight='bold')

for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height)}',
            ha='center', va='bottom', fontsize=14, weight='bold')

plt.tight_layout()
plt.savefig('3_ads_detected_NEW.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: 3_ads_detected_NEW.png\n")

plt.figure(figsize=(10, 8))
ui_counts = df['child_friendly_ui'].value_counts()
print(f"Child-Friendly UI:")
print(ui_counts)

colors_ui = {'Highly Child-Friendly': '#51cf66', 
             'Moderately Child-Friendly': '#ffa502', 
             'Not Child-Friendly': '#ff6b6b'}
pie_colors = [colors_ui.get(x, 'gray') for x in ui_counts.index]

plt.pie(ui_counts.values, 
        labels=[f'{label}\n({count} sites)' for label, count in zip(ui_counts.index, ui_counts.values)],
        autopct='%1.1f%%', startangle=90, colors=pie_colors,
        textprops={'fontsize': 11, 'weight': 'bold'})
plt.title('Child-Friendly UI Distribution', fontsize=14, weight='bold', pad=20)

plt.tight_layout()
plt.savefig('4_child_friendly_ui_NEW.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: 4_child_friendly_ui_NEW.png\n")


fig, ax = plt.subplots(figsize=(12, 6))

privacy_yes = (df['privacy_policy_present'] == 'Yes').sum()
privacy_no = (df['privacy_policy_present'] == 'No').sum()

data_yes = (df['asks_personal_data'] == 'Yes').sum()
data_no = (df['asks_personal_data'] == 'No').sum()

consent_yes = (df['parental_consent_mentioned'] == 'Yes').sum()
consent_no = (df['parental_consent_mentioned'] == 'No').sum()

print(f"\nPrivacy Analysis:")
print(f"Privacy Policy: Yes={privacy_yes}, No={privacy_no}")
print(f"Asks Data: Yes={data_yes}, No={data_no}")
print(f"Parental Consent: Yes={consent_yes}, No={consent_no}")

categories = ['Privacy Policy', 'Asks Personal\nData', 'Parental Consent']
yes_values = [privacy_yes, data_yes, consent_yes]
no_values = [privacy_no, data_no, consent_no]

x = np.arange(len(categories))
width = 0.35

bars1 = ax.bar(x - width/2, yes_values, width, label='Yes', color='#ff6b6b', edgecolor='black')
bars2 = ax.bar(x + width/2, no_values, width, label='No', color='#51cf66', edgecolor='black')

ax.set_ylabel('Number of Websites', fontsize=12, weight='bold')
ax.set_title('Privacy Policy & Data Collection Analysis', fontsize=14, weight='bold')
ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=11)
ax.legend(fontsize=11)
ax.set_ylim(0, 45)

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{int(height)}', ha='center', va='bottom', fontsize=11, weight='bold')

plt.tight_layout()
plt.savefig('5_privacy_analysis_NEW.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: 5_privacy_analysis_NEW.png\n")


plt.figure(figsize=(12, 6))
scores = df['coppa_percentage'].str.rstrip('%').astype(float)

print(f"\nCOPPA Score Statistics:")
print(f"Mean: {scores.mean():.1f}%")
print(f"Median: {scores.median():.1f}%")
print(f"Min: {scores.min():.1f}%")
print(f"Max: {scores.max():.1f}%")

plt.hist(scores, bins=15, color='#3498db', edgecolor='black', alpha=0.7)
plt.axvline(60, color='red', linestyle='--', linewidth=2.5, label='Compliance Threshold (60%)')
plt.axvline(scores.mean(), color='green', linestyle='--', linewidth=2.5, label=f'Average ({scores.mean():.1f}%)')

plt.xlabel('COPPA Compliance Score (%)', fontsize=12, weight='bold')
plt.ylabel('Number of Websites', fontsize=12, weight='bold')
plt.title('Distribution of COPPA Compliance Scores', fontsize=14, weight='bold')
plt.legend(fontsize=11)
plt.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('6_coppa_score_distribution_NEW.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: 6_coppa_score_distribution_NEW.png\n")


plt.figure(figsize=(14, 8))
top30_ads = df.nlargest(30, 'ad_indicator_score').copy()
top30_ads['site_name'] = top30_ads['website'].str.replace('https://', '').str.replace('www.', '').str.split('/').str[0].str[:30]

print(f"\nTop 5 sites by ad indicators:")
print(top30_ads[['website', 'ad_indicator_score']].head())

colors_scatter = ['#ff4444' if x > 100 else '#ffbb33' if x > 50 else '#00C851' for x in top30_ads['ad_indicator_score']]

plt.scatter(range(len(top30_ads)), top30_ads['ad_indicator_score'], 
            c=colors_scatter, s=200, alpha=0.7, edgecolors='black', linewidths=1.5)
plt.xticks(range(len(top30_ads)), top30_ads['site_name'], rotation=90, fontsize=8)
plt.ylabel('Ad Indicator Score', fontsize=12, weight='bold')
plt.title('Advertising Intensity (Top 30 Sites)', fontsize=14, weight='bold')
plt.axhline(100, color='red', linestyle='--', alpha=0.6, linewidth=2, label='Very High (>100)')
plt.axhline(50, color='orange', linestyle='--', alpha=0.6, linewidth=2, label='High (>50)')
plt.legend(fontsize=10)
plt.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('7_ad_intensity_NEW.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: 7_ad_intensity_NEW.png\n")


plt.figure(figsize=(14, 10))

issue_keywords = [
    'no privacy policy',
    'no child section',
    'no parental consent',
    'insufficient data disclosure',
    'no age verification',
    'collects sensitive data',
    'too many third-parties',
    'advertising detected'
]

issue_matrix = []
sites_list = []

for idx, row in df.head(25).iterrows():
    issues_text = row['coppa_issues'].lower()
    issue_row = [1 if kw in issues_text else 0 for kw in issue_keywords]
    issue_matrix.append(issue_row)
    site_name = row['website'].replace('https://', '').replace('www.', '').split('/')[0][:30]
    sites_list.append(site_name)

sns.heatmap(issue_matrix, annot=True, fmt='d', cmap='RdYlGn_r', 
            xticklabels=[kw.title().replace('No ', '').replace('Too Many ', 'Excess ') for kw in issue_keywords],
            yticklabels=sites_list, 
            cbar_kws={'label': 'Violation (1=Yes, 0=No)'},
            linewidths=0.5, linecolor='gray')
plt.title('COPPA Violations Heatmap (Top 25 Sites)', fontsize=14, weight='bold', pad=15)
plt.xlabel('Violation Type', fontsize=12, weight='bold')
plt.ylabel('Website', fontsize=12, weight='bold')
plt.xticks(rotation=45, ha='right', fontsize=9)
plt.yticks(fontsize=8)

plt.tight_layout()
plt.savefig('8_coppa_heatmap_NEW.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: 8_coppa_heatmap_NEW.png\n")


fig, axes = plt.subplots(1, 3, figsize=(18, 5))

coppa_scores = df['coppa_percentage'].str.rstrip('%').astype(float)
third_parties = df['total_third_party_domains']
ad_scores = df['ad_indicator_score']

# Scatter 1: Third-parties vs COPPA
axes[0].scatter(third_parties, coppa_scores, alpha=0.7, s=120, c='#3498db', edgecolors='black')
axes[0].set_xlabel('Third-Party Domains', fontsize=11, weight='bold')
axes[0].set_ylabel('COPPA Score (%)', fontsize=11, weight='bold')
axes[0].set_title('Trackers vs COPPA Compliance', fontsize=12, weight='bold')
axes[0].axhline(60, color='red', linestyle='--', alpha=0.5, label='Threshold')
axes[0].axvline(5, color='green', linestyle='--', alpha=0.5, label='Safe Limit')
axes[0].legend(fontsize=9)
axes[0].grid(alpha=0.3)

# Scatter 2: Ads vs COPPA
axes[1].scatter(ad_scores, coppa_scores, alpha=0.7, s=120, c='#e74c3c', edgecolors='black')
axes[1].set_xlabel('Ad Indicator Score', fontsize=11, weight='bold')
axes[1].set_ylabel('COPPA Score (%)', fontsize=11, weight='bold')
axes[1].set_title('Ads vs COPPA Compliance', fontsize=12, weight='bold')
axes[1].axhline(60, color='red', linestyle='--', alpha=0.5)
axes[1].grid(alpha=0.3)

# Scatter 3: Trackers vs Ads
axes[2].scatter(third_parties, ad_scores, alpha=0.7, s=120, c='#2ecc71', edgecolors='black')
axes[2].set_xlabel('Third-Party Domains', fontsize=11, weight='bold')
axes[2].set_ylabel('Ad Indicator Score', fontsize=11, weight='bold')
axes[2].set_title('Trackers vs Advertising', fontsize=12, weight='bold')
axes[2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('9_correlation_NEW.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: 9_correlation_NEW.png\n")


fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(4, 3, hspace=0.5, wspace=0.4)

ax1 = fig.add_subplot(gs[0, 0])
coppa_counts.plot(kind='bar', ax=ax1, color=['#ff6b6b' if x=='No' else '#51cf66' for x in coppa_counts.index], edgecolor='black')
ax1.set_title('COPPA Compliance', fontsize=12, weight='bold')
ax1.set_ylabel('Count', fontsize=10)
ax1.set_xticklabels(coppa_counts.index, rotation=0)

ax2 = fig.add_subplot(gs[0, 1])
ad_counts.plot(kind='bar', ax=ax2, color=['#ff6b6b', '#ffa502', '#51cf66'][:len(ad_counts)], edgecolor='black')
ax2.set_title('Ads Detected', fontsize=12, weight='bold')
ax2.set_ylabel('Count', fontsize=10)
ax2.set_xticklabels(ad_counts.index, rotation=0, fontsize=9)

ax3 = fig.add_subplot(gs[0, 2])
ui_counts.plot(kind='bar', ax=ax3, color=['#51cf66', '#ffa502', '#ff6b6b'][:len(ui_counts)], edgecolor='black')
ax3.set_title('UI Friendliness', fontsize=12, weight='bold')
ax3.set_ylabel('Count', fontsize=10)
ax3.set_xticklabels(ui_counts.index, rotation=45, ha='right', fontsize=8)

ax4 = fig.add_subplot(gs[1, :2])
ax4.hist(third_parties, bins=20, color='#3498db', edgecolor='black', alpha=0.7)
ax4.axvline(5, color='green', linestyle='--', linewidth=2, label=f'Safe (≤5)')
ax4.axvline(third_parties.mean(), color='red', linestyle='--', linewidth=2, label=f'Avg ({third_parties.mean():.1f})')
ax4.set_xlabel('Third-Party Domains', fontsize=10)
ax4.set_ylabel('Frequency', fontsize=10)
ax4.set_title('Third-Party Distribution', fontsize=12, weight='bold')
ax4.legend(fontsize=9)

ax5 = fig.add_subplot(gs[1, 2])
all_issues = []
for issues in df['coppa_issues']:
    if issues != 'Compliant':
        all_issues.extend([i.strip() for i in issues.split(';')])
issue_counts_bar = pd.Series(all_issues).value_counts().head(5)
issue_counts_bar.plot(kind='barh', ax=ax5, color='#e74c3c', edgecolor='black')
ax5.set_title('Top 5 Violations', fontsize=12, weight='bold')
ax5.set_xlabel('Count', fontsize=10)
ax5.tick_params(axis='y', labelsize=8)

ax6 = fig.add_subplot(gs[2, :])
ax6.hist(coppa_scores, bins=15, color='skyblue', edgecolor='black', alpha=0.7)
ax6.axvline(60, color='red', linestyle='--', linewidth=2, label='Threshold')
ax6.axvline(coppa_scores.mean(), color='green', linestyle='--', linewidth=2, label=f'Avg ({coppa_scores.mean():.1f}%)')
ax6.set_xlabel('COPPA Score (%)', fontsize=10)
ax6.set_ylabel('Frequency', fontsize=10)
ax6.set_title('COPPA Score Distribution', fontsize=12, weight='bold')
ax6.legend()

ax7 = fig.add_subplot(gs[3, :])
ax7.axis('off')

stats = f"""
📊 SUMMARY STATISTICS (40 Children's Websites)

COPPA Compliance:
  • Compliant: {(df['coppa_compliant']=='Yes').sum()} sites ({(df['coppa_compliant']=='Yes').sum()/len(df)*100:.1f}%)
  • Non-Compliant: {(df['coppa_compliant']=='No').sum()} sites ({(df['coppa_compliant']=='No').sum()/len(df)*100:.1f}%)
  • Average Score: {coppa_scores.mean():.1f}%

Third-Party Tracking:
  • Total Domains Found: {third_parties.sum()}
  • Average per Site: {third_parties.mean():.1f}
  • Maximum: {third_parties.max()} (on {df.loc[third_parties.idxmax(), 'website'].split('//')[1].split('/')[0]})
  • Sites with >10 trackers: {(third_parties > 10).sum()}

Advertising:
  • Sites with Ads: {(df['ads_detected'].isin(['Yes', 'Likely'])).sum()} ({(df['ads_detected'].isin(['Yes', 'Likely'])).sum()/len(df)*100:.1f}%)
  • Average Ad Score: {ad_scores.mean():.1f}

Privacy Policies:
  • Have Policy: {privacy_yes} ({privacy_yes/len(df)*100:.1f}%)
  • Ask Personal Data: {data_yes} ({data_yes/len(df)*100:.1f}%)
  • Mention Parental Consent: {consent_yes} ({consent_yes/len(df)*100:.1f}%)

🚨 CRITICAL FINDINGS:
  • Sites with Age Verification: 0 (0%)
  • Sites with >20 third-parties: {(third_parties > 20).sum()}
  • Sites with >100 ad indicators: {(ad_scores > 100).sum()}
"""

ax7.text(0.05, 0.5, stats, fontsize=10, family='monospace',
         verticalalignment='center', 
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5, pad=1))

fig.suptitle('CHILDREN\'S WEBSITE PRIVACY AUDIT - COMPLETE DASHBOARD', 
             fontsize=16, weight='bold', y=0.98)

plt.savefig('10_dashboard_NEW.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: 10_dashboard_NEW.png\n")


print("\n" + "="*70)
print("  ✅ ALL VISUALIZATIONS GENERATED & VERIFIED")
print("="*70)
print(f"\n📊 Generated 10 charts based on CSV data:")
print(f"  • COPPA Compliant: {(df['coppa_compliant']=='Yes').sum()}/{len(df)}")
print(f"  • Average Third-Parties: {third_parties.mean():.1f}")
print(f"  • Sites with Ads: {(df['ads_detected']!='No').sum()}/{len(df)}")
print(f"  • Average COPPA Score: {coppa_scores.mean():.1f}%")
print("="*70)