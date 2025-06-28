import json
from string import Template

def load_repo_data():
    with open('independence_repo.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def format_repo_card(repo):
    icon = 'folder-alert' if repo['is_restricted'] else 'folder-open'
    return f"""
-   :material-{icon}:{{ .lg .middle }} __{repo['name']}__

    ---
    
    {repo['description']}
    
    [:octicons-arrow-right-24: 访问资料库]({repo['url']})
"""

def generate_markdown():
    repos = load_repo_data()
    
    # Split repositories by type
    general_repos = [repo for repo in repos if not repo['is_restricted']]
    restricted_repos = [repo for repo in repos if repo['is_restricted']]
    
    # Calculate statistics
    total_size = sum(repo['size'] for repo in repos)
    
    # Load template
    with open('.github/templates/doc_index.template.md', 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Format repository cards
    general_repos_content = ''.join(format_repo_card(repo) for repo in general_repos)
    restricted_repos_content = ''.join(format_repo_card(repo) for repo in restricted_repos)
    
    # Replace template variables
    markdown = Template(template).safe_substitute(
        total_repos=len(repos),
        total_size=f"{total_size:,}",
        general_repos=general_repos_content,
        restricted_repos=restricted_repos_content
    )

    # Write to file
    with open('docs/index.md', 'w', encoding='utf-8') as f:
        f.write(markdown)

if __name__ == '__main__':
    generate_markdown() 
