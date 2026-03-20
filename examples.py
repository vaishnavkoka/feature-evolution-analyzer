#!/usr/bin/env python3
"""
Example Usage Scripts for Feature Evolution Analyzer

Shows different ways to use the analyzer programmatically.
"""

from feature_evolution_analyzer import FeatureEvolutionAnalyzer
import pandas as pd
import json
from pathlib import Path


# ============================================================================
# EXAMPLE 1: Basic Analysis
# ============================================================================

def basic_analysis():
    """Simple analysis of a repository."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Analysis")
    print("="*70)
    
    analyzer = FeatureEvolutionAnalyzer(
        repo_url="https://github.com/cucumber/cucumber-ruby",
        output_dir="example1_output"
    )
    
    analyzer.run_analysis()


# ============================================================================
# EXAMPLE 2: Custom Analysis with Data Access
# ============================================================================

def custom_analysis():
    """Access evolution data programmatically after analysis."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Custom Analysis with Data Access")
    print("="*70)
    
    analyzer = FeatureEvolutionAnalyzer(
        repo_url="behave/behave",
        output_dir="example2_output"
    )
    
    # Run analysis
    if not analyzer.run_analysis():
        return
    
    # Access raw data
    print("\nAccessing evolution data programmatically:")
    print(f"Total entries: {len(analyzer.evolution_data)}")
    print(f"Total files: {len(analyzer.file_stats)}")
    
    # First commit
    first = analyzer.evolution_data[0]
    print(f"\nFirst commit: {first['commit_hash']}")
    print(f"  Date: {first['timestamp']}")
    print(f"  Files: {first['feature_files_count']}")
    print(f"  Lines: {first['total_lines']}")
    
    # Last commit
    last = analyzer.evolution_data[-1]
    print(f"\nLast commit: {last['commit_hash']}")
    print(f"  Date: {last['timestamp']}")
    print(f"  Files: {last['feature_files_count']}")
    print(f"  Lines: {last['total_lines']}")
    
    # Growth analysis
    growth = last['total_lines'] - first['total_lines']
    commits = len(analyzer.evolution_data)
    growth_rate = growth / commits if commits > 0 else 0
    
    print(f"\nGrowth Analysis:")
    print(f"  Total growth: {growth:+,} lines")
    print(f"  Total commits: {commits}")
    print(f"  Growth rate: {growth_rate:.2f} lines/commit")
    
    # File statistics
    print(f"\nFile Statistics:")
    oldest_files = sorted(
        analyzer.file_stats.items(),
        key=lambda x: x[1]['created']
    )[:5]
    
    print("  Oldest files:")
    for filepath, stats in oldest_files:
        print(f"    • {filepath} ({stats['created'].year}-{stats['created'].month:02d})")


# ============================================================================
# EXAMPLE 3: Batch Analysis Multiple Repositories
# ============================================================================

def batch_analysis():
    """Analyze multiple repositories and compare them."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Batch Analysis")
    print("="*70)
    
    repositories = [
        "gherkin/gherkin",
        "behave/behave",
        "SerenityOS/serenity",
    ]
    
    results = {}
    
    for repo in repositories:
        print(f"\nAnalyzing {repo}...")
        
        analyzer = FeatureEvolutionAnalyzer(
            repo_url=repo,
            output_dir=f"batch_output/{repo.replace('/', '_')}"
        )
        
        if analyzer.run_analysis():
            # Store results
            results[repo] = {
                'commits': len(analyzer.evolution_data),
                'files': len(analyzer.file_stats),
                'current_files': analyzer.evolution_data[-1]['feature_files_count'],
                'current_lines': analyzer.evolution_data[-1]['total_lines'],
            }
    
    # Compare results
    print("\n" + "="*70)
    print("COMPARISON RESULTS")
    print("="*70)
    
    if results:
        df = pd.DataFrame(results).T
        df = df.sort_values('current_lines', ascending=False)
        
        print("\n", df.to_string())
        
        print(f"\nLargest codebase: {df['current_lines'].idxmax()}")
        print(f"Most feature files: {df['files'].idxmax()}")
        print(f"Most commits: {df['commits'].idxmax()}")


# ============================================================================
# EXAMPLE 4: Analyze CSV Output for Insights
# ============================================================================

def analyze_csv_output():
    """Read and analyze the CSV outputs."""
    print("\n" + "="*70)
    print("EXAMPLE 4: CSV Analysis")
    print("="*70)
    
    # First run an analysis if needed
    analyzer = FeatureEvolutionAnalyzer(
        repo_url="cucumber/cucumber-jvm",
        output_dir="example4_output"
    )
    analyzer.run_analysis()
    
    # Read the CSV
    timeline_path = Path("example4_output/evolution_timeline.csv")
    if timeline_path.exists():
        df = pd.read_csv(timeline_path)
        df['Date'] = pd.to_datetime(df['Date'])
        
        print("\nTimeline Summary:")
        print(f"  Earliest commit: {df['Date'].min()}")
        print(f"  Latest commit: {df['Date'].max()}")
        print(f"  Date range: {(df['Date'].max() - df['Date'].min()).days} days")
        
        # Year-by-year analysis
        df['Year'] = df['Date'].dt.year
        yearly_stats = df.groupby('Year').agg({
            'Feature Files': 'max',
            'Total Lines': 'max'
        })
        
        print("\nYear-by-Year Growth:")
        print(yearly_stats.to_string())
        
        # Peak activity
        peak_year = yearly_stats['Total Lines'].idxmax()
        peak_lines = yearly_stats['Total Lines'].max()
        print(f"\nPeak year: {peak_year} ({peak_lines:,} lines)")
        
        # Average growth per year
        years = yearly_stats.index
        if len(years) > 1:
            avg_growth = yearly_stats['Total Lines'].diff().mean()
            print(f"Avg growth/year: {avg_growth:,.0f} lines")


# ============================================================================
# EXAMPLE 5: Focus on Specific Date Ranges
# ============================================================================

def date_range_analysis():
    """Analyze specific time periods."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Date Range Analysis")
    print("="*70)
    
    analyzer = FeatureEvolutionAnalyzer(
        repo_url="gherkin/gherkin",
        output_dir="example5_output"
    )
    analyzer.run_analysis()
    
    # Access evolution data
    df = pd.DataFrame([
        {
            'Date': e['timestamp'],
            'Files': e['feature_files_count'],
            'Lines': e['total_lines'],
        }
        for e in analyzer.evolution_data
    ])
    
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Analyze last year
    one_year_ago = df['Date'].max() - pd.Timedelta(days=365)
    recent = df[df['Date'] > one_year_ago]
    
    if len(recent) > 0:
        print("\n📊 Last Year Analysis:")
        print(f"  Commits: {len(recent)}")
        print(f"  File growth: {recent['Files'].max() - recent['Files'].min()}")
        print(f"  Line growth: {recent['Lines'].max() - recent['Lines'].min():+,}")
        
        # Activity level
        months_with_changes = len([
            recent['Files'].max() - recent['Files'].min()
            for _ in range(1)
        ])
        
        if months_with_changes > 0:
            print(f"  Status: ACTIVE")
        else:
            print(f"  Status: MAINTENANCE")


# ============================================================================
# EXAMPLE 6: Generate Custom Report
# ============================================================================

def custom_report():
    """Create a custom HTML report from analysis data."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Custom Report Generation")
    print("="*70)
    
    analyzer = FeatureEvolutionAnalyzer(
        repo_url="https://github.com/behave/behave",
        output_dir="example6_output"
    )
    analyzer.run_analysis()
    
    # Create HTML report
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Feature Evolution Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            .metric { margin: 10px 0; padding: 10px; background: #f0f0f0; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #4CAF50; color: white; }
        </style>
    </head>
    <body>
        <h1>Feature Evolution Report</h1>
    """
    
    # Load stats
    stats_path = Path("example6_output/evolution_stats.json")
    if stats_path.exists():
        with open(stats_path) as f:
            stats = json.load(f)
        
        html_content += f"""
        <h2>Repository: {stats['repository']}</h2>
        <div class="metric">
            <strong>Total Commits:</strong> {stats['total_commits']}
        </div>
        <div class="metric">
            <strong>Feature Files Created:</strong> {stats['feature_files_created']}
        </div>
        <div class="metric">
            <strong>Current Lines of Code:</strong> {stats['total_lines_at_latest']}
        </div>
        <div class="metric">
            <strong>Average Growth:</strong> {stats['average_lines_per_commit']:.2f} lines/commit
        </div>
        """
    
    html_content += """
        </body>
    </html>
    """
    
    # Save HTML
    output_html = Path("example6_output/report.html")
    with open(output_html, 'w') as f:
        f.write(html_content)
    
    print(f"\n✓ HTML report saved: {output_html}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run examples."""
    print("\n" + "="*70)
    print("FEATURE EVOLUTION ANALYZER - EXAMPLE SCRIPTS")
    print("="*70)
    
    examples = [
        ("1. Basic Analysis", basic_analysis),
        ("2. Custom Analysis with Data Access", custom_analysis),
        ("3. Batch Analysis Multiple Repos", batch_analysis),
        ("4. CSV Output Analysis", analyze_csv_output),
        ("5. Date Range Analysis", date_range_analysis),
        ("6. Custom Report Generation", custom_report),
    ]
    
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    choice = input("\nEnter example number (1-6) or 'all': ").strip().lower()
    
    if choice == 'all':
        for name, func in examples:
            try:
                func()
            except Exception as e:
                print(f"\n✗ {name} failed: {e}")
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(examples):
                examples[idx][1]()
            else:
                print("Invalid choice")
        except (ValueError, IndexError):
            print("Invalid input")


if __name__ == "__main__":
    main()
