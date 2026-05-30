import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ── Styling ──────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.titlesize': 13,
    'axes.titleweight': 'bold',
    'axes.labelsize': 11,
    'figure.facecolor': '#f9f9f9',
    'axes.facecolor': '#f9f9f9',
})
PALETTE = ['#4C72B0', '#DD8452', '#55A868', '#C44E52', '#8172B2']

# ── Load & Clean ──────────────────────────────────────────────────────────────
df = pd.read_csv('/Users/nidhika/Downloads/smmh.csv')

# Rename columns for ease
df.columns = [
    'timestamp', 'age', 'gender', 'relationship', 'occupation', 'org_type',
    'uses_social_media', 'platforms', 'daily_usage', 'purposeless_use',
    'distracted_when_busy', 'restless_without_sm', 'easily_distracted',
    'bothered_by_worries', 'difficulty_concentrating', 'social_comparison',
    'comparison_feeling', 'seek_validation', 'feel_depressed', 'interest_fluctuates',
    'sleep_issues'
]

# Clean age
df['age'] = pd.to_numeric(df['age'], errors='coerce')
df = df[(df['age'] >= 13) & (df['age'] <= 65)].copy()

# Map daily usage to numeric hours for ordering
usage_order = [
    'Less than an Hour', 'Between 1 and 2 hours', 'Between 2 and 3 hours',
    'Between 3 and 4 hours', 'Between 4 and 5 hours', 'More than 5 hours'
]
df['daily_usage'] = pd.Categorical(df['daily_usage'], categories=usage_order, ordered=True)
df['usage_numeric'] = df['daily_usage'].cat.codes + 1  # 1–6 scale

# Mental health composite score (higher = worse)
mental_health_cols = [
    'easily_distracted', 'bothered_by_worries', 'difficulty_concentrating',
    'social_comparison', 'seek_validation', 'feel_depressed',
    'interest_fluctuates', 'sleep_issues'
]
df['mental_health_score'] = df[mental_health_cols].mean(axis=1)

# Productivity proxy: distracted when busy + purposeless use
df['productivity_impact'] = (df['distracted_when_busy'] + df['purposeless_use']) / 2

print(f"Dataset: {len(df)} respondents | Age range: {int(df['age'].min())}–{int(df['age'].max())}")
print(f"Mental health score range: {df['mental_health_score'].min():.2f}–{df['mental_health_score'].max():.2f}")

# ── Figure: 4 subplots ────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle(
    'Social Media Use: Effects on Mental Health & Workplace Productivity\n'
    'Analysis of 480 Survey Respondents',
    fontsize=15, fontweight='bold', y=1.01
)
plt.subplots_adjust(hspace=0.45, wspace=0.35)

# ── Plot 1: Daily usage distribution ─────────────────────────────────────────
ax1 = axes[0, 0]
usage_counts = df['daily_usage'].value_counts().reindex(usage_order)
bars = ax1.barh(usage_order, usage_counts.values, color=PALETTE[0], alpha=0.85)
ax1.set_title('1. Daily Social Media Usage')
ax1.set_xlabel('Number of Respondents')
for bar, val in zip(bars, usage_counts.values):
    ax1.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
             str(val), va='center', fontsize=9)
ax1.tick_params(axis='y', labelsize=8)

# ── Plot 2: Usage vs Mental Health Score ─────────────────────────────────────
ax2 = axes[0, 1]
mh_by_usage = df.groupby('daily_usage', observed=True)['mental_health_score'].mean().reindex(usage_order)
short_labels = ['<1h', '1–2h', '2–3h', '3–4h', '4–5h', '>5h']
colors = [PALETTE[0] if v < mh_by_usage.mean() else PALETTE[3] for v in mh_by_usage.values]
bars2 = ax2.bar(short_labels, mh_by_usage.values, color=colors, alpha=0.85)
ax2.set_title('2. Usage vs Mental Health Impact\n(higher score = more distress)')
ax2.set_xlabel('Daily Usage')
ax2.set_ylabel('Avg Mental Health Score')
ax2.set_ylim(0, 5)
for bar, val in zip(bars2, mh_by_usage.values):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
             f'{val:.2f}', ha='center', fontsize=9)
low_patch = mpatches.Patch(color=PALETTE[0], alpha=0.85, label='Below avg impact')
high_patch = mpatches.Patch(color=PALETTE[3], alpha=0.85, label='Above avg impact')
ax2.legend(handles=[low_patch, high_patch], fontsize=8)

# ── Plot 3: Usage vs Productivity Impact ─────────────────────────────────────
ax3 = axes[1, 0]
prod_by_usage = df.groupby('daily_usage', observed=True)['productivity_impact'].mean().reindex(usage_order)
ax3.plot(short_labels, prod_by_usage.values, marker='o', color=PALETTE[1],
         linewidth=2.5, markersize=8)
ax3.fill_between(range(len(short_labels)), prod_by_usage.values,
                 alpha=0.15, color=PALETTE[1])
ax3.set_xticks(range(len(short_labels)))
ax3.set_xticklabels(short_labels)
ax3.set_title('3. Usage vs Productivity Distraction\n(higher = more distracted at work)')
ax3.set_xlabel('Daily Usage')
ax3.set_ylabel('Avg Distraction Score')
ax3.set_ylim(1, 5)
for i, val in enumerate(prod_by_usage.values):
    ax3.text(i, val + 0.1, f'{val:.2f}', ha='center', fontsize=9)

# ── Plot 4: Gender vs Mental Health ──────────────────────────────────────────
ax4 = axes[1, 1]
gender_map = {'Male': 'Male', 'Female': 'Female', 'Non-binary': 'Non-binary'}
df['gender_clean'] = df['gender'].map(gender_map).fillna('Other')
gender_mh = df.groupby('gender_clean')['mental_health_score'].mean().sort_values(ascending=False)
gender_counts = df['gender_clean'].value_counts()
labels_with_n = [f"{g}\n(n={gender_counts.get(g, 0)})" for g in gender_mh.index]
bars4 = ax4.bar(labels_with_n, gender_mh.values,
                color=PALETTE[:len(gender_mh)], alpha=0.85)
ax4.set_title('4. Mental Health Impact by Gender')
ax4.set_ylabel('Avg Mental Health Score')
ax4.set_ylim(0, 5)
for bar, val in zip(bars4, gender_mh.values):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
             f'{val:.2f}', ha='center', fontsize=9)

plt.tight_layout()
plt.savefig('/Users/nidhika/Downloads/social_media_analysis.png', dpi=150, bbox_inches='tight')
print("Chart saved!")

# ── Key Findings ──────────────────────────────────────────────────────────────
print("\n── KEY FINDINGS ─────────────────────────────────────────")
print(f"1. Most common usage: '{usage_counts.idxmax()}' ({usage_counts.max()} respondents)")
print(f"2. Highest mental health impact group: users spending '{mh_by_usage.idxmax()}' daily (score: {mh_by_usage.max():.2f}/5)")
print(f"3. Lowest mental health impact group: users spending '{mh_by_usage.idxmin()}' daily (score: {mh_by_usage.min():.2f}/5)")
print(f"4. Productivity distraction increases from {prod_by_usage.iloc[0]:.2f} (<1hr users) to {prod_by_usage.iloc[-1]:.2f} (>5hr users)")
corr = df['usage_numeric'].corr(df['mental_health_score'])
print(f"5. Correlation between usage & mental health score: r = {corr:.3f}")
