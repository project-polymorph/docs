import yaml
from datetime import datetime
import argparse
import matplotlib.pyplot as plt
import seaborn as sns
import os
from wordcloud import WordCloud
import pathlib
import subprocess
import sys
import requests
import tempfile
import json

def load_analysis_results(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def create_year_plot(year_data, output_dir, input_file):
    plt.figure(figsize=(12, 6))
    years = list(year_data.keys())
    counts = list(year_data.values())
    
    plt.bar(years, counts, color='skyblue')
    plt.title('年度内容分布')
    plt.xlabel('年份')
    plt.ylabel('内容数量')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # Get base name from input file
    base_name = pathlib.Path(input_file).stem
    plot_path = os.path.join(output_dir, f'{base_name}_year_distribution.png')
    plt.savefig(plot_path, bbox_inches='tight', dpi=300)
    plt.close()
    return f'{base_name}_year_distribution.png'

def create_region_pie(region_data, output_dir):
    plt.figure(figsize=(10, 10))
    plt.pie(region_data.values(), labels=region_data.keys(), autopct='%1.1f%%')
    plt.title('Regional Distribution')
    
    plot_path = os.path.join(output_dir, 'region_distribution.png')
    plt.savefig(plot_path, bbox_inches='tight', dpi=300)
    plt.close()
    return 'region_distribution.png'

def create_tag_cloud(tag_data, output_dir):
    plt.figure(figsize=(15, 8))
    sorted_tags = dict(sorted(tag_data.items(), key=lambda x: x[1], reverse=True)[:20])
    
    plt.bar(sorted_tags.keys(), sorted_tags.values(), color='lightcoral')
    plt.title('Top 20 Tags Distribution')
    plt.xlabel('Tags')
    plt.ylabel('Frequency')
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, alpha=0.3)
    
    plot_path = os.path.join(output_dir, 'tag_distribution.png')
    plt.savefig(plot_path, bbox_inches='tight', dpi=300)
    plt.close()
    return 'tag_distribution.png'

def ensure_chinese_font():
    """Download and get path to a Chinese font"""
    # Try different font paths
    possible_font_paths = [
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/usr/share/fonts/wqy-microhei/wqy-microhei.ttc',
        '/usr/share/fonts/truetype/wqy-microhei/wqy-microhei.ttc',
        '/usr/share/fonts/wqy/wqy-microhei.ttc',
        'wqy-microhei.ttc',  # If font is in current directory
        'SimHei.ttf',        # Windows font
        'msyh.ttc'          # Windows font
    ]
    
    font_path = None
    for path in possible_font_paths:
        if os.path.exists(path):
            font_path = path
            break
    
    if not font_path:
        print("Warning: Could not find a suitable font. Downloading WQY-Microhei...")
        # Download the font if not found
        font_url = "https://github.com/anthonyfok/fonts-wqy-microhei/raw/master/wqy-microhei.ttc"
        try:
            response = requests.get(font_url)
            response.raise_for_status()
            font_path = "wqy-microhei.ttc"
            with open(font_path, "wb") as f:
                f.write(response.content)
            print("Font downloaded successfully")
        except Exception as e:
            print(f"Warning: Could not download font - {str(e)}")
            return None
    
    return font_path

def create_tag_wordcloud(tag_data, output_dir, input_file):
    # Get base name from input file
    base_name = pathlib.Path(input_file).stem
    
    # Get font path
    font_path = ensure_chinese_font()
    if not font_path:
        print("Warning: Using default font, Chinese characters may not display correctly")
    
    try:
        # Create word frequencies dictionary
        wordcloud = WordCloud(
            width=1200,
            height=800,
            background_color='white',
            max_words=100,
            max_font_size=150,
            font_path=font_path,
            random_state=42
        ).generate_from_frequencies(tag_data)
        
        plt.figure(figsize=(16, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        
        plot_path = os.path.join(output_dir, f'{base_name}_wordcloud.png')
        plt.savefig(plot_path, bbox_inches='tight', dpi=300)
        plt.close()
        return f'{base_name}_wordcloud.png'
    except Exception as e:
        print(f"Warning: Could not generate wordcloud - {str(e)}")
        return None

def get_report_title(input_file):
    # Extract filename without extension and convert to title
    base_name = pathlib.Path(input_file).stem
    return ' '.join(word.capitalize() for word in base_name.replace('_', ' ').split()).replace('Analysis', '数据分析')

def get_spec_repo_info(analysis_name):
    try:
        with open('results/independence_repo.json', 'r', encoding='utf-8') as f:
            repos = json.load(f)
            # Convert analysis name to match repository name format
            analysis_name = analysis_name.replace('_analysis', '')
            
            # Try to find matching repository
            for repo in repos:
                # Skip restricted repos
                if repo.get('is_restricted', False):
                    continue
                    
                # Check if repository name contains our analysis name or vice versa
                if (analysis_name.lower() in repo['name'].lower() or 
                    repo['name'].lower() in analysis_name.lower()):
                    return {
                        'name': repo['name'],
                        'url': repo['url'],
                        'description': repo.get('description', '')
                    }
            
            # If no match found, return the first non-restricted repo
            for repo in repos:
                if not repo.get('is_restricted', False):
                    return {
                        'name': repo['name'],
                        'url': repo['url'],
                        'description': repo.get('description', '')
                    }
    except Exception as e:
        print(f"Warning: Could not read spec repo info from independence_repo.json - {str(e)}")
        return None

def generate_markdown_report(input_file, output_file, spec_repo_url=None, spec_repo_name=None, spec_repo_desc=None):
    # Load analysis results
    results = load_analysis_results(input_file)
    
    # Create output directory for images
    output_dir = os.path.dirname(output_file)
    os.makedirs(output_dir, exist_ok=True)
    
    # Get report title from input filename
    report_title = get_report_title(input_file)
    
    # Generate plots
    year_plot = create_year_plot(results['year_summary'], output_dir, input_file)
    wordcloud_plot = create_tag_wordcloud(results['tag_summary'], output_dir, input_file)
    
    # Get current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Prepare markdown content
    markdown = [
        "---",
        f"title: {report_title}",
        f"date: {current_date}",
        "description: 内容分布的综合分析（年度、主题）",
        "keywords: 数据分析, 内容分布, 主题分析",
        "---",
        "",
        f"# {report_title}",
        f"*生成日期：{current_date}*",
        "",
    ]

    # Add spec repo link if provided
    if spec_repo_url and spec_repo_name:
        markdown.extend([
            "## 数据来源",
            f"数据来自 [{spec_repo_name}]({spec_repo_url})",
        ])
        if spec_repo_desc:
            markdown.extend([
                "",
                spec_repo_desc,
            ])
        markdown.append("")

    markdown.extend([
        "## 执行摘要",
        f"本报告分析了 {format(sum(results['year_summary'].values()), ',')} 个项目的时间分布和主题分类。",
        "",
        "## 时间分布",
        "",
        f"![年度分布]({year_plot})",
        "",
        "### 年度明细",
        "",
        "| 年份 | 数量 |",
        "|------|-------|",
    ])
    
    # Add year connections
    for year, count in sorted(results['year_summary'].items(), reverse=True):
        markdown.append(f"| {year} | {count:,} |")
    
    markdown.extend([
        "",
        "## 地区分布",
        "",
    ])
    
    # Calculate total for percentages
    total_regions = sum(results['region_summary'].values())
    
    # Add region statistics
    sorted_regions = sorted(results['region_summary'].items(), key=lambda item: item[1], reverse=True)
    regions_str = ""
    for region, count in sorted_regions:
        percentage = (count / total_regions) * 100
        regions_str += f"  `{region}: {count:,} ({percentage:.1f}%)`"
    markdown.append(regions_str)
    
    markdown.extend([
        "",
        "## 主题分析",
        "",
        "### 标签词云",
    ])
    
    # Only add wordcloud section if generation was successful
    if wordcloud_plot:
        markdown.extend([
            f"![标签词云]({wordcloud_plot})",
            "",
        ])
    
    markdown.extend([
        "### 热门标签",
        "",
        "**前50个热门标签：**",
        "",
    ])
    
    # Add top 50 tags
    sorted_tags = sorted(results['tag_summary'].items(), key=lambda item: item[1], reverse=True)
    tags_str = ""
    for tag, count in sorted_tags[:50]:
        tags_str += (f"  `{tag}: {count:,}`")
    markdown.append(tags_str)
    markdown.extend([
        "",
        "<details markdown>",
        "<summary>查看更多标签</summary>",
        "",
    ])
    
    tags_str = ""

    # Add remaining tags
    for tag, count in sorted_tags[50:]:
        tags_str += (f" `{tag}: {count:,}`")
    markdown.append(tags_str)
    markdown.extend([
        "",
        "</details>",
        "",
        "## 说明",
        "- 所有统计数据截至报告生成日期",
        "- 标签保持原始大小写形式",
    ])
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(markdown))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Markdown report from analysis results')
    parser.add_argument('-i', '--input', required=True,
                       help='Input analysis YAML file path')
    parser.add_argument('-o', '--output', required=True,
                       help='Output Markdown file path')
    parser.add_argument('-s', '--spec-repo', 
                       help='URL to the specification repository (overrides the URL from independence_repo.json)')
    parser.add_argument('-n', '--spec-name',
                       help='Name of the specification repository (overrides the name from independence_repo.json)')
    parser.add_argument('-d', '--spec-desc',
                       help='Description of the specification repository (overrides the description from independence_repo.json)')

    args = parser.parse_args()
    
    # Use command line arguments if provided, otherwise try to read from independence_repo.json
    if args.spec_repo and args.spec_name:
        spec_repo_info = {
            'url': args.spec_repo, 
            'name': args.spec_name,
            'description': args.spec_desc
        }
    else:
        # Get the base name of the input file for matching
        input_base_name = pathlib.Path(args.input).stem
        spec_repo_info = get_spec_repo_info(input_base_name)
    
    generate_markdown_report(
        args.input, 
        args.output, 
        spec_repo_info['url'] if spec_repo_info else None,
        spec_repo_info['name'] if spec_repo_info else None,
        spec_repo_info['description'] if spec_repo_info else None
    )
