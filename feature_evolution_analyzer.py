"""
GitHub Feature File Evolution Analyzer

Tracks how .feature files evolve over time in a GitHub repository.
Analyzes commits, changes, additions, deletions, and growth metrics.

Usage:
    python3 feature_evolution_analyzer.py "https://github.com/owner/repo"
    python3 feature_evolution_analyzer.py "owner/repo"
"""

import argparse
import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

from git import Repo
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


class FeatureEvolutionAnalyzer:
    """Analyzes evolution of .feature files in GitHub repositories."""
    
    def __init__(self, repo_url: str, output_dir: str = None):
        """
        Initialize the analyzer.
        
        Args:
            repo_url: GitHub repository URL (flexible formats)
            output_dir: Directory to save analysis results. If None, creates unique directory
                       per repo with timestamp (e.g., evolution_analysis_cucumber_gherkin_20260320_143022/)
        """
        self.repo_url = repo_url.rstrip("/")
        self.repo = None
        self.local_repo_dir = None
        
        # Parse repo info from URL first
        self.owner, self.repo_name = self._parse_repo_url(repo_url)
        
        # Generate output directory with repo name and timestamp if not specified
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"evolution_analysis_{self.owner}_{self.repo_name}_{timestamp}"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Data storage
        self.evolution_data: List[Dict] = []
        self.file_stats: Dict[str, Dict] = defaultdict(lambda: {
            'created': None,
            'last_modified': None,
            'additions': 0,
            'deletions': 0,
            'commits': 0,
            'lines': 0,
        })
        
    def _parse_repo_url(self, url: str) -> Tuple[str, str]:
        """Extract owner and repo name from various URL formats.
        
        Supports:
            - https://github.com/owner/repo
            - https://github.com/owner/repo.git
            - git@github.com:owner/repo.git
            - owner/repo
        """
        url = url.strip()
        
        # Remove .git suffix if present
        url = url.rstrip('/')
        if url.endswith('.git'):
            url = url[:-4]
        
        # Handle SSH format: git@github.com:owner/repo
        ssh_match = re.search(r"git@github\.com:([^/]+)/(.+)$", url)
        if ssh_match:
            return ssh_match.group(1), ssh_match.group(2)
        
        # If it's owner/repo format
        if "/" in url and not url.startswith("http"):
            parts = url.split("/")
            if len(parts) >= 2:
                return parts[0], parts[1]
        
        # If it's a GitHub URL (https:// or http://)
        match = re.search(r"github\.com/([^/]+)/([^/?#]+)", url)
        if match:
            return match.group(1), match.group(2)
        
        # Helpful error message
        error_msg = f"Invalid GitHub URL format: '{url}'\n\n"
        error_msg += "Supported formats:\n"
        error_msg += "  • https://github.com/owner/repo\n"
        error_msg += "  • https://github.com/owner/repo.git\n"
        error_msg += "  • git@github.com:owner/repo.git\n"
        error_msg += "  • owner/repo\n\n"
        error_msg += "Examples:\n"
        error_msg += "  • https://github.com/cucumber/cucumber-ruby\n"
        error_msg += "  • behave/behave\n"
        error_msg += "  • git@github.com:cucumber/cucumber-js.git\n"
        raise ValueError(error_msg)
    
    def clone_repository(self) -> bool:
        """Clone the repository locally."""
        try:
            # Clean up existing clone
            self.local_repo_dir = Path(f"/tmp/{self.owner}_{self.repo_name}")
            if self.local_repo_dir.exists():
                shutil.rmtree(self.local_repo_dir)
            
            # Construct HTTPS URL
            https_url = f"https://github.com/{self.owner}/{self.repo_name}.git"
            
            print(f"🔲 Cloning repository: {https_url}")
            print(f"   Destination: {self.local_repo_dir}")
            
            self.repo = Repo.clone_from(https_url, str(self.local_repo_dir))
            
            print(f"✓ Repository cloned successfully")
            return True
            
        except Exception as e:
            error_msg = str(e)
            
            # Provide specific guidance based on error type
            if "Repository not found" in error_msg or "not found" in error_msg.lower():
                print(f"✗ Repository not found: {https_url}")
                print(f"\n  • Check the repository URL is correct")
                print(f"  • Verify the repository is public (or configure git credentials for private repos)")
                print(f"  • Try: https://github.com/owner/repo")
            elif "Connection" in error_msg or "timeout" in error_msg.lower():
                print(f"✗ Connection error: Could not reach GitHub")
                print(f"  • Check your internet connection")
                print(f"  • Verify GitHub is accessible")
            else:
                print(f"✗ Failed to clone repository: {e}")
            
            return False
    
    def get_feature_files_at_commit(self, commit) -> List[str]:
        """Get all .feature files at a specific commit."""
        feature_files = []
        try:
            for item in commit.tree.traverse():
                if item.path.endswith(".feature"):
                    feature_files.append(item.path)
        except:
            pass
        return feature_files
    
    
    def analyze_evolution(self) -> bool:
        """Analyze how .feature files evolved over time."""
        if not self.repo:
            print("✗ Repository not loaded")
            return False
        
        try:
            print("\n🔍 Analyzing feature file evolution...")
            
            commits = list(reversed(list(self.repo.iter_commits())))
            total_commits = len(commits)
            
            # Sequential processing of commits with progress tracking
            print(f"   Processing {total_commits} commits...")
            
            for commit in tqdm(commits, desc="Analysis"):
                feature_files = self.get_feature_files_at_commit(commit)
                
                # Count total lines in all feature files
                total_lines = 0
                for feature_file in feature_files:
                    try:
                        blob = commit.tree / feature_file
                        content = blob.data_stream.read().decode('utf-8', errors='ignore')
                        total_lines += len(content.splitlines())
                    except:
                        pass
                
                # Create evolution entry
                evolution_entry = {
                    'commit_hash': commit.hexsha[:7],
                    'timestamp': datetime.fromtimestamp(commit.committed_date),
                    'author': commit.author.name,
                    'message': commit.message.strip()[:100],
                    'feature_files_count': len(feature_files),
                    'total_lines': total_lines,
                    'files': feature_files,
                }
                
                self.evolution_data.append(evolution_entry)
                
                # Track individual file stats
                for feature_file in feature_files:
                    if feature_file not in self.file_stats:
                        self.file_stats[feature_file]['created'] = evolution_entry['timestamp']
                    self.file_stats[feature_file]['last_modified'] = evolution_entry['timestamp']
                    self.file_stats[feature_file]['commits'] += 1
            
            # Sort by timestamp to maintain chronological order
            self.evolution_data.sort(key=lambda x: x['timestamp'])
            
            # Calculate diffs for changes
            self._calculate_changes()
            
            print(f"✓ Analyzed {len(self.evolution_data)} commits")
            print(f"✓ Found {len(self.file_stats)} unique feature files")
            
            return True
            
        except Exception as e:
            print(f"✗ Error analyzing evolution: {e}")
            return False
    
    def _calculate_changes(self):
        """Calculate additions/deletions/modifications between commits."""
        print("   Calculating changes...")
        
        for i in range(len(self.evolution_data) - 1):
            current = self.evolution_data[i]
            next_entry = self.evolution_data[i + 1]
            
            current_files = set(current['files'])
            next_files = set(next_entry['files'])
            
            # Files added in next commit
            added = next_files - current_files
            # Files removed in next commit
            removed = current_files - next_files
            # Files modified (present in both)
            modified = next_files & current_files
            
            # Calculate lines changed
            for feature_file in added:
                self.file_stats[feature_file]['additions'] += next_entry['total_lines']
            
            for feature_file in removed:
                self.file_stats[feature_file]['deletions'] += next_entry['total_lines']
    
    def generate_report(self) -> bool:
        """Generate detailed evolution report."""
        if not self.evolution_data:
            print("✗ No evolution data to report")
            return False
        
        try:
            print("\n📊 Generating report...")
            
            # Create DataFrame from evolution data
            df = pd.DataFrame([
                {
                    'Commit': entry['commit_hash'],
                    'Date': entry['timestamp'],
                    'Author': entry['author'],
                    'Feature Files': entry['feature_files_count'],
                    'Total Lines': entry['total_lines'],
                    'Message': entry['message'],
                }
                for entry in self.evolution_data
            ])
            
            # Save to CSV
            output_csv = self.output_dir / "evolution_timeline.csv"
            df.to_csv(output_csv, index=False)
            print(f"✓ Timeline saved: {output_csv.name}")
            
            # Calculate statistics
            stats = {
                'repository': f"{self.owner}/{self.repo_name}",
                'total_commits': len(self.evolution_data),
                'date_range': {
                    'start': self.evolution_data[0]['timestamp'].isoformat() if self.evolution_data else None,
                    'end': self.evolution_data[-1]['timestamp'].isoformat() if self.evolution_data else None,
                },
                'feature_files_created': len(self.file_stats),
                'feature_files_at_latest': self.evolution_data[-1]['feature_files_count'] if self.evolution_data else 0,
                'total_lines_at_latest': self.evolution_data[-1]['total_lines'] if self.evolution_data else 0,
                'average_lines_per_commit': np.mean([e['total_lines'] for e in self.evolution_data]),
                'max_lines_in_commit': max([e['total_lines'] for e in self.evolution_data]),
                'min_lines_in_commit': min([e['total_lines'] for e in self.evolution_data]),
                'growth_rate': self._calculate_growth_rate(),
            }
            
            # Print summary
            print("\n" + "="*70)
            print("FEATURE FILE EVOLUTION SUMMARY")
            print("="*70)
            print(f"Repository: {stats['repository']}")
            print(f"Total Commits: {stats['total_commits']}")
            print(f"Date Range: {stats['date_range']['start']} to {stats['date_range']['end']}")
            print(f"\nFeature Files:")
            print(f"  • Created: {stats['feature_files_created']}")
            print(f"  • Current: {stats['feature_files_at_latest']}")
            print(f"  • Lines of code: {stats['total_lines_at_latest']:,}")
            print(f"\nGrowth Metrics:")
            print(f"  • Avg lines/commit: {stats['average_lines_per_commit']:.0f}")
            print(f"  • Max lines in commit: {stats['max_lines_in_commit']}")
            print(f"  • Growth rate: {stats['growth_rate']:.2f} lines/commit")
            print("="*70 + "\n")
            
            # Save stats as JSON
            output_json = self.output_dir / "evolution_stats.json"
            with open(output_json, 'w') as f:
                json.dump(stats, f, indent=2, default=str)
            print(f"✓ Stats saved: {output_json.name}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error generating report: {e}")
            return False
    
    def _calculate_growth_rate(self) -> float:
        """Calculate average lines added per commit."""
        if len(self.evolution_data) < 2:
            return 0
        
        first = self.evolution_data[0]['total_lines']
        last = self.evolution_data[-1]['total_lines']
        commits = len(self.evolution_data)
        
        if commits == 0:
            return 0
        
        return (last - first) / commits
    
    def visualize_evolution(self) -> bool:
        """Create visualization of feature file evolution."""
        if not self.evolution_data:
            print("✗ No data to visualize")
            return False
        
        try:
            print("\n📈 Creating visualizations...")
            
            # Prepare data
            timestamps = [e['timestamp'] for e in self.evolution_data]
            feature_counts = [e['feature_files_count'] for e in self.evolution_data]
            total_lines = [e['total_lines'] for e in self.evolution_data]
            
            # Create figure with subplots
            fig, axes = plt.subplots(2, 2, figsize=(16, 10))
            fig.suptitle(f"Feature File Evolution: {self.owner}/{self.repo_name}", fontsize=16, fontweight='bold')
            
            # Plot 1: Number of feature files over time
            ax = axes[0, 0]
            ax.plot(timestamps, feature_counts, marker='o', linewidth=2, markersize=4, color='#4C9BE8')
            ax.fill_between(timestamps, feature_counts, alpha=0.3, color='#4C9BE8')
            ax.set_title("Feature Files Count Over Time", fontweight='bold')
            ax.set_xlabel("Date")
            ax.set_ylabel("Number of .feature Files")
            ax.grid(True, alpha=0.3)
            ax.tick_params(axis='x', rotation=45)
            
            # Plot 2: Total lines of code over time
            ax = axes[0, 1]
            ax.plot(timestamps, total_lines, marker='s', linewidth=2, markersize=4, color='#63C6A0')
            ax.fill_between(timestamps, total_lines, alpha=0.3, color='#63C6A0')
            ax.set_title("Total Lines of Code Over Time", fontweight='bold')
            ax.set_xlabel("Date")
            ax.set_ylabel("Total Lines")
            ax.grid(True, alpha=0.3)
            ax.tick_params(axis='x', rotation=45)
            
            # Plot 3: Growth rate (moving average)
            ax = axes[1, 0]
            window = max(1, len(self.evolution_data) // 10)
            moving_avg = pd.Series(total_lines).rolling(window=window).mean()
            ax.plot(timestamps, moving_avg, linewidth=2.5, color='#F5A623', label='Moving Average')
            ax.scatter(timestamps, total_lines, alpha=0.3, s=20, color='#F5A623', label='Actual')
            ax.set_title(f"Growth Rate (Moving Average, window={window})", fontweight='bold')
            ax.set_xlabel("Date")
            ax.set_ylabel("Lines of Code")
            ax.legend()
            ax.grid(True, alpha=0.3)
            ax.tick_params(axis='x', rotation=45)
            
            # Plot 4: Statistics
            ax = axes[1, 1]
            ax.axis('off')
            
            stats_text = f"""
EVOLUTION STATISTICS

Repository: {self.owner}/{self.repo_name}
Commits Analyzed: {len(self.evolution_data):,}

Feature Files:
  • Created: {len(self.file_stats)}
  • Current: {feature_counts[-1]}
  • Growth: {feature_counts[-1] - feature_counts[0]} files

Lines of Code:
  • Current: {total_lines[-1]:,} LOC
  • Started: {total_lines[0]:,} LOC
  • Growth: {total_lines[-1] - total_lines[0]:+,} lines
  
Metrics:
  • Avg growth: {(total_lines[-1] - total_lines[0]) / len(self.evolution_data):.1f} lines/commit
  • Peak: {max(total_lines):,} lines
  • Lowest: {min(total_lines):,} lines
            """
            
            ax.text(0.1, 0.5, stats_text, fontsize=11, verticalalignment='center',
                   fontfamily='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            plt.tight_layout()
            
            # Save figure
            output_png = self.output_dir / "evolution_visualization.png"
            plt.savefig(output_png, dpi=100, bbox_inches='tight')
            print(f"✓ Visualization saved: {output_png.name}")
            
            plt.close()
            return True
            
        except Exception as e:
            print(f"✗ Error creating visualization: {e}")
            return False
    
    def generate_file_timeline(self) -> bool:
        """Generate a timeline of individual file changes."""
        if not self.file_stats:
            print("✗ No file stats to report")
            return False
        
        try:
            print("\n📁 Generating file timeline...")
            
            file_timeline = []
            for file_path, stats in self.file_stats.items():
                file_timeline.append({
                    'File': file_path,
                    'Created': stats['created'],
                    'Last Modified': stats['last_modified'],
                    'Total Commits': stats['commits'],
                    'Lines Added': stats['additions'],
                    'Lines Deleted': stats['deletions'],
                    'Current Lines': stats['lines'],
                })
            
            df = pd.DataFrame(file_timeline)
            df = df.sort_values('Created')
            
            output_csv = self.output_dir / "file_timeline.csv"
            df.to_csv(output_csv, index=False)
            print(f"✓ File timeline saved: {output_csv.name}")
            print(f"   Total files tracked: {len(file_timeline)}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error generating file timeline: {e}")
            return False
    
    def run_analysis(self) -> bool:
        """Run complete analysis pipeline."""
        print("\n" + "="*70)
        print("FEATURE FILE EVOLUTION ANALYZER")
        print("="*70)
        
        # Clone repository
        if not self.clone_repository():
            return False
        
        # Analyze evolution
        if not self.analyze_evolution():
            return False
        
        # Generate reports
        if not self.generate_report():
            return False
        
        # Visualize
        if not self.visualize_evolution():
            return False
        
        # File timeline
        if not self.generate_file_timeline():
            return False
        
        # Cleanup
        if self.local_repo_dir and self.local_repo_dir.exists():
            shutil.rmtree(self.local_repo_dir)
            print(f"\n✓ Cleaned up temporary files")
        
        print("\n" + "="*70)
        print("✅ ANALYSIS COMPLETE")
        print("="*70)
        print(f"\nOutput files in: {self.output_dir}/")
        print("  • evolution_timeline.csv - Commit-by-commit timeline")
        print("  • evolution_stats.json - Statistics summary")
        print("  • file_timeline.csv - Individual file changes")
        print("  • evolution_visualization.png - Visual charts")
        print("="*70 + "\n")
        
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Analyze feature file evolution in GitHub repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Supported URL Formats:
  • https://github.com/owner/repo
  • https://github.com/owner/repo.git
  • git@github.com:owner/repo.git
  • owner/repo (shorthand)

Examples:
  python3 feature_evolution_analyzer.py "https://github.com/cucumber/cucumber-ruby"
  python3 feature_evolution_analyzer.py "cucumber/cucumber-ruby"
  python3 feature_evolution_analyzer.py "behave/behave" --output-dir "my_analysis"
  python3 feature_evolution_analyzer.py "git@github.com:gherkin/gherkin.git"
  
Common Repositories:
  • cucumber/cucumber-ruby - Ruby implementation (mature)
  • behave/behave - Python BDD framework
  • gherkin/gherkin - Gherkin parser
  • cucumber/cucumber-jvm - Java implementation
        """
    )
    
    parser.add_argument(
        "repo_url",
        help="GitHub repository URL or owner/repo format"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=None,
        help="Output directory for analysis results. If specified, uses that directory. "
             "If not specified, creates unique directory with repo name and timestamp "
             "(e.g., evolution_analysis_owner_repo_20260320_143022/)"
    )
    args = parser.parse_args()
    
    analyzer = FeatureEvolutionAnalyzer(args.repo_url, args.output_dir)
    success = analyzer.run_analysis()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
