#!/bin/bash

# Exit on any error
set -e
export OPENAI_TEMPERATURE=0.7

# Create results directory if it doesn't exist
mkdir -p results
mkdir -p index/

python .github/scripts/toc/independence_info.py
cp independence_repo.json results/independence_repo.json

python scripts/analysis/download.py

echo "Download complete."

# Process each search_index.yml file
for index_file in index/*/search_index.yml; do
    # Extract the [name] part from the path
    name=$(basename $(dirname "$index_file"))
    
    # Create output path
    output_file="results/${name}_analysis.yml"
    
    echo "Processing $name..."
    python .github/scripts/file/analysis_search_index.py \
        -i "$index_file" \
        -o "$output_file"
    python scripts/analysis/basic_report.py \
        -i "$output_file" \
        -o "docs/项目运营/数据统计/${name}.md"
done

echo "Analysis complete. Results saved in results/"

python scripts/analysis/merge_index.py

python scripts/generate_homepage.py

echo "Merge complete. Results saved in index/combined_index.yml"
