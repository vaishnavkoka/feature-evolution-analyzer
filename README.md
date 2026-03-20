# Feature File Evolution Analyzer

Analyze how `.feature` files evolve over time in a GitHub repository. Track growth metrics, identify patterns, and visualize the history of BDD test suites.

## Overview

This tool performs deep analysis of Gherkin/BDD feature files across a repository's entire git history, providing insights into:

- **Growth Metrics**: How many feature files exist at each point in history
- **Code Growth**: Total lines of code in feature files over time
- **Commit Timeline**: When features were added, modified, or removed
- **Statistical Analysis**: Trends, averages, peak activity
- **Visualizations**: Interactive charts showing evolution patterns

## Features

✅ Clone any GitHub repository  
✅ Parse entire git history efficiently  
✅ Track per-commit feature file statistics  
✅ Calculate growth rates and trends  
✅ Generate CSV reports  
✅ Create beautiful visualizations  
✅ Handle large repositories (1000s of commits)  
✅ Support flexible GitHub URL formats  

## Installation

```bash
# Navigate to the FeatureEvolution directory
cd /home/vaishnavkoka/RE4BDD/FeatureEvolution

# Install dependencies
pip install -r requirements.txt
```

### Requirements

- Python 3.8+
- GitPython - For git repository analysis
- Pandas - For data aggregation and CSV generation
- Matplotlib - For visualization
- NumPy - For numerical calculations
- tqdm - For progress bars

## Usage

### Basic Usage

```bash
# Analyze a repository
python3 feature_evolution_analyzer.py "https://github.com/cucumber/cucumber-ruby"

# Or use owner/repo shorthand
python3 feature_evolution_analyzer.py "cucumber/cucumber-ruby"
```

### Output Directory Auto-Naming

Each analysis automatically creates a unique directory with the repository name and timestamp:

```bash
python3 feature_evolution_analyzer.py "cucumber/gherkin"
# Creates: evolution_analysis_cucumber_gherkin_20260320_143022/

python3 feature_evolution_analyzer.py "behave/behave"
# Creates: evolution_analysis_behave_behave_20260320_143100/

# Both directories coexist - no overwrites!
```

**Benefits:**
- ✅ Each run gets its own directory
- ✅ Repository name is in the directory
- ✅ Timestamp prevents collisions
- ✅ Can analyze same repo multiple times
- ✅ Useful for tracking changes over time

### Advanced Usage

```bash
# Specify CUSTOM output directory (overrides auto-naming)
python3 feature_evolution_analyzer.py "behave/behave" --output-dir "my_analysis"

# Custom name won't get auto-timestamp (use exactly as specified)
python3 feature_evolution_analyzer.py "gherkin/gherkin" -o "output"
```

## Output Files

After analysis completes, the following files are generated in your output directory:

### 1. **evolution_timeline.csv**
Commit-by-commit timeline with feature file counts and lines of code.

```
Commit,Date,Author,Feature Files,Total Lines,Message
abc1234,2020-01-15 10:30:00,John Doe,5,250,Add initial feature tests
def5678,2020-02-20 14:45:00,Jane Smith,7,380,Expand feature coverage
...
```

**Columns:**
- `Commit` - Short commit hash
- `Date` - Commit timestamp
- `Author` - Committer name
- `Feature Files` - Number of .feature files at this commit
- `Total Lines` - Total lines of code across all feature files
- `Message` - Commit message

### 2. **evolution_stats.json**
Statistical summary of the evolution analysis.

```json
{
  "repository": "owner/repo",
  "total_commits": 2345,
  "date_range": {
    "start": "2020-01-15T10:30:00",
    "end": "2026-03-20T14:45:00"
  },
  "feature_files_created": 45,
  "feature_files_at_latest": 45,
  "total_lines_at_latest": 12450,
  "average_lines_per_commit": 5.31,
  "max_lines_in_commit": 8950,
  "min_lines_in_commit": 0,
  "growth_rate": 5.31
}
```

### 3. **file_timeline.csv**
Individual file creation and modification timeline.

```
File,Created,Last Modified,Total Commits,Lines Added,Lines Deleted,Current Lines
features/login.feature,2020-01-15,2024-12-01,23,450,50,400
features/checkout.feature,2020-02-20,2024-11-15,18,380,20,360
...
```

### 4. **evolution_visualization.png**
Four-panel visualization showing:

**Panel 1 (Top-Left): Feature Files Count**
- Trend of how many .feature files exist over time
- Shows growth or decline patterns

**Panel 2 (Top-Right): Lines of Code**
- Total lines of Gherkin code over time
- Indicates feature test complexity growth

**Panel 3 (Bottom-Left): Growth Rate**
- Moving average trend line
- Smooths out commit-to-commit noise
- Shows velocity of feature development

**Panel 4 (Bottom-Right): Statistics**
- Summary metrics
- Key numbers at a glance

## Example Analysis

### Analyzing cucumber-ruby

```bash
$ python3 feature_evolution_analyzer.py "https://github.com/cucumber/cucumber-ruby"

======================================================================
FEATURE FILE EVOLUTION ANALYZER
======================================================================
🔲 Cloning repository: https://github.com/cucumber/cucumber-ruby.git
   Destination: /tmp/cucumber_cucumber-ruby
✓ Repository cloned successfully

🔍 Analyzing feature file evolution...
   Processing 2567 commits...
   [████████████████████████] 2567/2567 [100%]
✓ Analyzed 2567 commits
✓ Found 247 unique feature files

📊 Generating report...
✓ Timeline saved: evolution_timeline.csv
✓ Stats saved: evolution_stats.json

📈 Creating visualizations...
✓ Visualization saved: evolution_visualization.png

📁 Generating file timeline...
✓ File timeline saved: file_timeline.csv
   Total files tracked: 247

✓ Cleaned up temporary files

======================================================================
✅ ANALYSIS COMPLETE
======================================================================

Output files in: evolution_analysis/
  • evolution_timeline.csv - Commit-by-commit timeline
  • evolution_stats.json - Statistics summary
  • file_timeline.csv - Individual file changes
  • evolution_visualization.png - Visual charts
======================================================================
```

### Key Insights from Example

From the analysis above:
- **Repository**: cucumber/cucumber-ruby
- **Total Commits**: 2,567
- **Feature Files**: 247 created over time
- **Code Volume**: Thousands of lines of Gherkin code
- **Growth Pattern**: Steady addition of features and tests
- **Development Pace**: Visible acceleration/deceleration periods

## Interpreting Results

### Growth Curves

**Exponential Growth** 📈
- Steep upward curve indicates rapid feature development
- May indicate new features or expanded test coverage
- Typical for active projects

**Linear Growth** 📊
- Steady, consistent addition of tests
- Indicates stable development pace
- Good for mature projects

**Plateau** 📉
- Flat line indicates maintenance phase
- No new features being added
- Could indicate project maturity or pause

**Decline** ⬇️
- Decreasing feature files
- May indicate refactoring or cleanup
- Unusual but can indicate test consolidation

### Key Metrics

**Files Created**: Total unique feature files that existed at any point
**Files at Latest**: Current number of feature files in repository
**Growth Rate**: Average lines added per commit
**Peak**: Maximum lines in a single commit (indicates large feature additions)

## Performance

The analyzer is designed to handle large repositories:

- **Small repos** (< 500 commits): ~5-10 seconds
- **Medium repos** (500-2000 commits): ~20-40 seconds
- **Large repos** (2000+ commits): ~1-3 minutes

Speed depends on:
- Repository size
- Number of feature files
- Network speed (initial clone)
- Disk I/O

## Troubleshooting

### "Failed to clone repository"
- Verify the GitHub URL is correct
- Check internet connection
- Can you access the repository in your browser?

### "No data to report"
- Repository may have no .feature files
- Check if files exist: Look in Features/, features/, test/features/, etc.

### "Permission denied" errors
- May need to authenticate with GitHub
- For private repos, configure Git credentials

### Out of Memory
- For very large repos, consider analyzing subdirectories first
- Or analyze in multiple runs with different commit ranges

## Advanced Usage

### Analyzing Subdirectories

To focus on specific feature directories:

```bash
# After analysis, examine file_timeline.csv
# Filter for specific directory patterns
grep "features/api/" file_timeline.csv
```

### Comparing Multiple Repositories

```bash
# Run analysis on multiple repos
for repo in cucumber-ruby cucumber-jvm behave gherkin; do
  python3 feature_evolution_analyzer.py "owner/$repo" -o "output_$repo"
done

# Compare growth rates in evolution_stats.json files
```

### Custom Time-Series Analysis

With the CSV outputs, you can do custom analysis using pandas:

```python
import pandas as pd

df = pd.read_csv('evolution_timeline.csv')
df['Date'] = pd.to_datetime(df['Date'])

# Calculate year-over-year growth
df['Year'] = df['Date'].dt.year
yearly = df.groupby('Year')['Feature Files'].max()
print(yearly)
```

## API Reference

### FeatureEvolutionAnalyzer

Main class for feature evolution analysis.

#### Constructor
```python
analyzer = FeatureEvolutionAnalyzer(
    repo_url: str,              # GitHub URL or owner/repo
    output_dir: str = None      # Output directory (auto-generated if None)
)
```

**Parameters:**
- `repo_url` (required): GitHub repository URL or owner/repo format
- `output_dir` (optional): 
  - If `None` (default): Creates unique directory: `evolution_analysis_{owner}_{repo}_{timestamp}/`
  - If specified: Uses exactly that directory name (no timestamp added)

#### Methods

**`clone_repository() -> bool`**
- Clones the GitHub repository locally
- Returns True on success

**`analyze_evolution() -> bool`**
- Analyzes git history
- Calculates feature file metrics per commit
- Stores in `self.evolution_data`

**`generate_report() -> bool`**
- Creates CSV timeline and JSON stats
- Prints summary to console

**`visualize_evolution() -> bool`**
- Generates 4-panel visualization PNG
- Shows growth trends

**`generate_file_timeline() -> bool`**
- Creates individual file tracking CSV

**`run_analysis() -> bool`**
- Orchestrates complete pipeline
- Cleans up temporary files
- Returns overall success status

## Development Notes

### Data Structures

**evolution_data** - List of dictionaries:
```python
{
    'commit_hash': str,
    'timestamp': datetime,
    'author': str,
    'message': str,
    'feature_files_count': int,
    'total_lines': int,
    'files': List[str],
}
```

**file_stats** - Dictionary mapping file paths to:
```python
{
    'created': datetime,
    'last_modified': datetime,
    'additions': int,
    'deletions': int,
    'commits': int,
    'lines': int,
}
```

### Extending the Analyzer

To add custom metrics:

```python
class CustomAnalyzer(FeatureEvolutionAnalyzer):
    def analyze_evolution(self):
        super().analyze_evolution()
        
        # Custom analysis here
        for entry in self.evolution_data:
            # Your logic
            pass
```

## License

Part of the RE4BDD project.

## Contributing

To improve this analyzer:

1. Test with different repository types (Cucumber, Behave, etc.)
2. Report bugs or unexpected behavior
3. Suggest new metrics or visualizations
4. Optimize for larger repositories

## See Also

- [Gherkin Language](https://cucumber.io/docs/gherkin/reference/)
- [GitPython Documentation](https://gitpython.readthedocs.io/)
- [Cucumber Ruby Repository](https://github.com/cucumber/cucumber-ruby)
- [Behave Repository](https://github.com/behave/behave)
