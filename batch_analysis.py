#!/usr/bin/env python3
"""
Batch Analysis Script

Analyze multiple GitHub repositories for feature file evolution.
Great for comparing multiple BDD projects or tracking evolution over time.

Usage:
    python3 batch_analysis.py
    python3 batch_analysis.py --repos owner/repo1 owner/repo2 owner/repo3
    python3 batch_analysis.py --repos-file my_repos.txt
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List
import pandas as pd
from datetime import datetime

from feature_evolution_analyzer import FeatureEvolutionAnalyzer


class BatchAnalyzer:
    """Manages analysis of multiple repositories."""
    
    def __init__(self, output_base_dir: str = "batch_analysis_results"):
        """
        Initialize batch analyzer.
        
        Args:
            output_base_dir: Base directory for all output
        """
        self.output_base = Path(output_base_dir)
        self.output_base.mkdir(exist_ok=True)
        self.results = {}
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def analyze_repo(self, repo_url: str) -> bool:
        """Analyze a single repository."""
        try:
            # Create repo-specific output directory
            repo_name = repo_url.split("/")[-1]
            output_dir = self.output_base / f"{repo_name}_{self.timestamp}"
            
            print(f"\n{'='*70}")
            print(f"Analyzing: {repo_url}")
            print(f"Output: {output_dir}")
            print(f"{'='*70}")
            
            # Run analysis
            analyzer = FeatureEvolutionAnalyzer(repo_url, str(output_dir))
            success = analyzer.run_analysis()
            
            if success:
                # Store results for summary
                stats_file = output_dir / "evolution_stats.json"
                if stats_file.exists():
                    with open(stats_file) as f:
                        stats = json.load(f)
                    
                    self.results[repo_url] = {
                        'repo': repo_url,
                        'status': 'SUCCESS',
                        'output_dir': str(output_dir),
                        'total_commits': stats.get('total_commits', 0),
                        'feature_files': stats.get('feature_files_created', 0),
                        'current_files': stats.get('feature_files_at_latest', 0),
                        'total_lines': stats.get('total_lines_at_latest', 0),
                        'growth_rate': stats.get('growth_rate', 0),
                    }
                    return True
            
            self.results[repo_url] = {
                'repo': repo_url,
                'status': 'FAILED',
                'output_dir': str(output_dir),
            }
            return False
            
        except Exception as e:
            print(f"✗ Error analyzing {repo_url}: {e}")
            self.results[repo_url] = {
                'repo': repo_url,
                'status': 'ERROR',
                'error': str(e),
            }
            return False
    
    def analyze_batch(self, repositories: List[str]) -> None:
        """Analyze multiple repositories."""
        print(f"\n{'='*70}")
        print(f"BATCH ANALYSIS - {len(repositories)} repositories")
        print(f"{'='*70}\n")
        
        successful = 0
        failed = 0
        
        for i, repo in enumerate(repositories, 1):
            progress = f"[{i}/{len(repositories)}]"
            print(f"\n{progress} Processing...")
            
            if self.analyze_repo(repo):
                successful += 1
            else:
                failed += 1
        
        # Generate summary
        self._generate_summary(successful, failed)
    
    def _generate_summary(self, successful: int, failed: int) -> None:
        """Generate analysis summary."""
        print(f"\n{'='*70}")
        print(f"BATCH ANALYSIS SUMMARY")
        print(f"{'='*70}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Total: {len(self.results)}")
        
        # Create comparison CSV
        successful_results = [r for r in self.results.values() if r['status'] == 'SUCCESS']
        
        if successful_results:
            df = pd.DataFrame(successful_results)
            
            # Sort by lines of code
            df = df.sort_values('total_lines', ascending=False)
            
            print(f"\n{'Repository Statistics:':^70}")
            print(f"{'-'*70}")
            
            for col in ['repo', 'total_commits', 'feature_files', 'total_lines', 'growth_rate']:
                if col in df.columns:
                    print(f"  {col}: {df[col].dtype}")
            
            print(f"\n{df[['repo', 'total_commits', 'feature_files', 'total_lines']].to_string(index=False)}")
            
            # Save comparison
            comparison_file = self.output_base / f"comparison_{self.timestamp}.csv"
            df.to_csv(comparison_file, index=False)
            print(f"\n✓ Comparison saved: {comparison_file}")
            
            # Rankings
            print(f"\n{'Rankings:':^70}")
            print(f"{'─'*70}")
            
            if 'total_lines' in df.columns:
                print("\n📊 Largest codebases (lines of code):")
                for i, (_, row) in enumerate(df.nlargest(3, 'total_lines').iterrows(), 1):
                    print(f"  {i}. {row['repo']}: {row['total_lines']:,} lines")
            
            if 'feature_files' in df.columns:
                print("\n📁 Most feature files:")
                for i, (_, row) in enumerate(df.nlargest(3, 'feature_files').iterrows(), 1):
                    print(f"  {i}. {row['repo']}: {row['feature_files']} files")
            
            if 'growth_rate' in df.columns:
                print("\n📈 Fastest growing (lines/commit):")
                for i, (_, row) in enumerate(df.nlargest(3, 'growth_rate').iterrows(), 1):
                    rate = row['growth_rate']
                    print(f"  {i}. {row['repo']}: {rate:.2f} lines/commit")
        
        print(f"\n{'='*70}")
        print(f"Output directory: {self.output_base}")
        print(f"{'='*70}\n")


def get_default_repos() -> List[str]:
    """Get default list of popular BDD repositories."""
    return [
        "cucumber/cucumber-ruby",
        "behave/behave",
        "gherkin/gherkin",
        "cucumber/cucumber-jvm",
        "cucumber/cucumber-js",
        "SerenityOS/serenity",
    ]


def load_repos_from_file(filepath: str) -> List[str]:
    """Load repository list from file."""
    repos = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    repos.append(line)
        return repos
    except FileNotFoundError:
        print(f"✗ File not found: {filepath}")
        return []


def main():
    parser = argparse.ArgumentParser(
        description="Batch analyze multiple GitHub repositories for feature evolution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 batch_analysis.py
  python3 batch_analysis.py --repos cucumber/cucumber-ruby behave/behave
  python3 batch_analysis.py --repos-file my_repos.txt
  python3 batch_analysis.py --output-dir my_results

Repository List File Format:
  # Comments start with #
  cucumber/cucumber-ruby
  behave/behave
  gherkin/gherkin
  https://github.com/owner/repo
        """
    )
    
    parser.add_argument(
        "--repos",
        nargs="+",
        help="Repository URLs or owner/repo to analyze"
    )
    parser.add_argument(
        "--repos-file", "-f",
        help="File containing list of repositories (one per line)"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="batch_analysis_results",
        help="Output directory for results (default: batch_analysis_results)"
    )
    
    args = parser.parse_args()
    
    # Determine which repositories to analyze
    if args.repos:
        repositories = args.repos
    elif args.repos_file:
        repositories = load_repos_from_file(args.repos_file)
        if not repositories:
            sys.exit(1)
    else:
        repositories = get_default_repos()
        print(f"No repositories specified, using default list ({len(repositories)} repos)")
    
    # Run batch analysis
    analyzer = BatchAnalyzer(args.output_dir)
    analyzer.analyze_batch(repositories)


if __name__ == "__main__":
    main()
