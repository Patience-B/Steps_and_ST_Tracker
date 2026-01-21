import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from datetime import datetime, timedelta
import seaborn as sns

# Read the CSV file
df = pd.read_csv('data.csv')

# Clean and prepare the data
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
df['Week'] = pd.to_datetime(df['Week'], format='%d/%m/%Y')

# Convert Screen_time from HH:MM:SS to minutes
def time_to_minutes(time_str):
    try:
        parts = str(time_str).split(':')
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            return hours * 60 + minutes + seconds / 60
        return 0
    except:
        return 0

df['Screen_time_minutes'] = df['Screen_time'].apply(time_to_minutes)

# Clean steps data (remove commas)
df['Steps'] = df['Steps'].astype(str).str.replace(',', '').astype(float)

# Sort by date
df = df.sort_values('Date')

# Calculate statistics
stats = {
    'total_days': len(df),
    'date_range': f"{df['Date'].min().strftime('%d/%m/%Y')} to {df['Date'].max().strftime('%d/%m/%Y')}",
    'avg_steps': df['Steps'].mean(),
    'max_steps': df['Steps'].max(),
    'min_steps': df['Steps'].min(),
    'total_steps': df['Steps'].sum(),
    'avg_screen_time': df['Screen_time_minutes'].mean(),
    'max_screen_time': df['Screen_time_minutes'].max(),
    'min_screen_time': df['Screen_time_minutes'].min(),
    'total_screen_time': df['Screen_time_minutes'].sum()
}

def create_github_style_graph(df, value_column, title, filename, color_scheme='Greens'):
    """Create a GitHub-style contribution graph"""
    # Prepare data
    df_plot = df[['Date', value_column]].copy()
    df_plot = df_plot.set_index('Date')
    
    # Fill in missing dates
    date_range = pd.date_range(start=df_plot.index.min(), end=df_plot.index.max(), freq='D')
    df_plot = df_plot.reindex(date_range, fill_value=0)
    
    # Calculate week start (Monday)
    df_plot['week'] = df_plot.index.to_series().apply(lambda x: x - timedelta(days=x.weekday()))
    df_plot['weekday'] = df_plot.index.weekday
    
    # Pivot for heatmap
    pivot = df_plot.pivot_table(values=value_column, index='weekday', columns='week', fill_value=0)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(20, 4))
    
    # Create custom colormap
    if color_scheme == 'Greens':
        colors = ['#ebedf0', '#9be9a8', '#40c463', '#30a14e', '#216e39']
    else:  # Blues for screen time
        colors = ['#ebedf0', '#9ecae1', '#4292c6', '#2171b5', '#084594']
    
    cmap = LinearSegmentedColormap.from_list('custom', colors, N=256)
    
    # Plot heatmap
    sns.heatmap(pivot, cmap=cmap, linewidths=2, linecolor='white', 
                square=True, cbar=False, ax=ax, vmin=0)
    
    # Customize axes
    ax.set_xlabel('Week', fontsize=12, fontweight='bold')
    ax.set_ylabel('')
    ax.set_yticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], rotation=0)
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    # Format x-axis to show months
    week_labels = [col.strftime('%b') if col.day <= 7 else '' for col in pivot.columns]
    ax.set_xticklabels(week_labels, rotation=0)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Created {filename}")

# Create GitHub-style graphs
create_github_style_graph(df, 'Steps', 'Daily Steps - Contribution Graph', 'steps_github.png', 'Greens')
create_github_style_graph(df, 'Screen_time_minutes', 'Daily Screen Time (minutes) - Contribution Graph', 
                          'screen_time_github.png', 'Blues')

# Create additional analysis graphs
fig, axes = plt.subplots(2, 2, figsize=(16, 10))

# 1. Steps trend over time
axes[0, 0].plot(df['Date'], df['Steps'], marker='o', linewidth=2, markersize=4, color='#40c463')
axes[0, 0].axhline(y=stats['avg_steps'], color='red', linestyle='--', label=f"Avg: {stats['avg_steps']:,.0f}")
axes[0, 0].set_title('Steps Trend Over Time', fontsize=14, fontweight='bold')
axes[0, 0].set_xlabel('Date')
axes[0, 0].set_ylabel('Steps')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)
axes[0, 0].tick_params(axis='x', rotation=45)

# 2. Screen time trend over time
axes[0, 1].plot(df['Date'], df['Screen_time_minutes'], marker='o', linewidth=2, markersize=4, color='#4292c6')
axes[0, 1].axhline(y=stats['avg_screen_time'], color='red', linestyle='--', 
                   label=f"Avg: {stats['avg_screen_time']:.0f} min")
axes[0, 1].set_title('Screen Time Trend Over Time', fontsize=14, fontweight='bold')
axes[0, 1].set_xlabel('Date')
axes[0, 1].set_ylabel('Minutes')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)
axes[0, 1].tick_params(axis='x', rotation=45)

# 3. Steps distribution
axes[1, 0].hist(df['Steps'], bins=20, color='#40c463', alpha=0.7, edgecolor='black')
axes[1, 0].axvline(x=stats['avg_steps'], color='red', linestyle='--', linewidth=2, label='Average')
axes[1, 0].set_title('Steps Distribution', fontsize=14, fontweight='bold')
axes[1, 0].set_xlabel('Steps')
axes[1, 0].set_ylabel('Frequency')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3, axis='y')

# 4. Screen time distribution
axes[1, 1].hist(df['Screen_time_minutes'], bins=20, color='#4292c6', alpha=0.7, edgecolor='black')
axes[1, 1].axvline(x=stats['avg_screen_time'], color='red', linestyle='--', linewidth=2, label='Average')
axes[1, 1].set_title('Screen Time Distribution', fontsize=14, fontweight='bold')
axes[1, 1].set_xlabel('Minutes')
axes[1, 1].set_ylabel('Frequency')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('detailed_analysis.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Created detailed_analysis.png")

# Day of week analysis
df['DayOfWeek'] = df['Date'].dt.day_name()
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow_stats = df.groupby('DayOfWeek').agg({
    'Steps': 'mean',
    'Screen_time_minutes': 'mean'
}).reindex(day_order)

fig, axes = plt.subplots(1, 2, figsize=(16, 5))

# Steps by day of week
axes[0].bar(dow_stats.index, dow_stats['Steps'], color='#40c463', alpha=0.7, edgecolor='black')
axes[0].set_title('Average Steps by Day of Week', fontsize=14, fontweight='bold')
axes[0].set_ylabel('Average Steps')
axes[0].tick_params(axis='x', rotation=45)
axes[0].grid(True, alpha=0.3, axis='y')

# Screen time by day of week
axes[1].bar(dow_stats.index, dow_stats['Screen_time_minutes'], color='#4292c6', alpha=0.7, edgecolor='black')
axes[1].set_title('Average Screen Time by Day of Week', fontsize=14, fontweight='bold')
axes[1].set_ylabel('Average Minutes')
axes[1].tick_params(axis='x', rotation=45)
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('day_of_week_analysis.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Created day_of_week_analysis.png")

# Generate README
readme_content = f"""# Health Data Analysis Report

> 🤖 **Auto-generated** | Last updated: {datetime.now().strftime('%B %d, %Y at %H:%M UTC')}

## Overview
This report analyzes your health and activity data from **{stats['date_range']}** ({stats['total_days']} days).

---

## 📊 GitHub-Style Activity Graphs

### Daily Steps
![Steps GitHub Graph](steps_github.png)

### Daily Screen Time
![Screen Time GitHub Graph](screen_time_github.png)

---

## 📈 Key Statistics

### Steps Summary
- **Total Steps**: {stats['total_steps']:,.0f}
- **Average Daily Steps**: {stats['avg_steps']:,.0f}
- **Maximum Steps (Single Day)**: {stats['max_steps']:,.0f}
- **Minimum Steps (Single Day)**: {stats['min_steps']:,.0f}
- **10,000+ Step Days**: {len(df[df['Steps'] >= 10000])} days ({len(df[df['Steps'] >= 10000])/stats['total_days']*100:.1f}%)

### Screen Time Summary
- **Total Screen Time**: {stats['total_screen_time']/60:.1f} hours ({stats['total_screen_time']:,.0f} minutes)
- **Average Daily Screen Time**: {stats['avg_screen_time']:.0f} minutes ({stats['avg_screen_time']/60:.1f} hours)
- **Maximum Screen Time (Single Day)**: {stats['max_screen_time']:.0f} minutes ({stats['max_screen_time']/60:.1f} hours)
- **Minimum Screen Time (Single Day)**: {stats['min_screen_time']:.0f} minutes ({stats['min_screen_time']/60:.1f} hours)

---

## 📉 Detailed Analysis

### Trends and Distributions
![Detailed Analysis](detailed_analysis.png)

### Day of Week Patterns
![Day of Week Analysis](day_of_week_analysis.png)

---

## 🔍 Insights

### Steps Insights
- **Most Active Day**: {dow_stats['Steps'].idxmax()} (avg: {dow_stats['Steps'].max():,.0f} steps)
- **Least Active Day**: {dow_stats['Steps'].idxmin()} (avg: {dow_stats['Steps'].min():,.0f} steps)
- **Daily Goal Achievement**: {"You're meeting the recommended 10,000 steps! 🎉" if stats['avg_steps'] >= 10000 else f"You're {10000 - stats['avg_steps']:,.0f} steps away from the recommended 10,000 daily steps. 💪"}

### Screen Time Insights
- **Highest Screen Time Day**: {dow_stats['Screen_time_minutes'].idxmax()} (avg: {dow_stats['Screen_time_minutes'].max():.0f} minutes)
- **Lowest Screen Time Day**: {dow_stats['Screen_time_minutes'].idxmin()} (avg: {dow_stats['Screen_time_minutes'].min():.0f} minutes)
- **Weekly Screen Time**: Approximately {stats['avg_screen_time'] * 7 / 60:.1f} hours per week

### Correlation
- **Steps vs Screen Time Correlation**: {df['Steps'].corr(df['Screen_time_minutes']):.3f}
  - {"⚠️ Negative correlation suggests more screen time = fewer steps" if df['Steps'].corr(df['Screen_time_minutes']) < -0.3 else "✅ Positive correlation suggests more screen time = more steps" if df['Steps'].corr(df['Screen_time_minutes']) > 0.3 else "➡️ Weak correlation between screen time and steps"}

---

## 💡 Recommendations

1. **Steps**: {"Great job! Keep maintaining your activity levels. 🌟" if stats['avg_steps'] >= 10000 else "Try to increase daily steps gradually to reach 10,000. 🚶"}
2. **Screen Time**: {"Consider reducing screen time for better work-life balance. 📱" if stats['avg_screen_time'] > 360 else "Your screen time is well-balanced. ✅"}
3. **Consistency**: Focus on maintaining regular activity patterns throughout the week.

---

## 📅 Weekly Breakdown

| Day of Week | Avg Steps | Avg Screen Time (min) |
|-------------|-----------|----------------------|
"""

for day in day_order:
    if day in dow_stats.index:
        readme_content += f"| {day} | {dow_stats.loc[day, 'Steps']:,.0f} | {dow_stats.loc[day, 'Screen_time_minutes']:.0f} |\n"

readme_content += """
---

## 🔄 How This Works

This README is automatically updated whenever you push changes to `data.csv`. The analysis pipeline:

1. 📥 Detects changes to data.csv
2. 🔬 Runs Python analysis script
3. 📊 Generates visualizations
4. 📝 Updates README with latest insights
5. 🚀 Commits and pushes changes

**To update**: Simply edit `data.csv` and push to the main branch!

---

*🤖 Auto-generated from data.csv using GitHub Actions*
"""

# Write README
with open('README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)

print("✓ Created README.md")
print("\n" + "="*50)
print("Analysis complete! Files generated:")
print("  1. steps_github.png")
print("  2. screen_time_github.png")
print("  3. detailed_analysis.png")
print("  4. day_of_week_analysis.png")
print("  5. README.md")
print("="*50)
