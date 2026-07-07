import json
with open('/opt/data/wiki-tech-automation/.automation/wiki-tech-selection.json', 'r') as f:
    data = json.load(f)
data['status'] = 'published'
data['published_at'] = '2026-06-25T18:00:00Z'
data['file_path'] = 'docs/cybersecurite/configurer-sudo-visudo.md'
data['published_title'] = "Configurer sudo en toute sécurité et limiter les privilèges avec visudo"
with open('/opt/data/wiki-tech-automation/.automation/wiki-tech-selection.json', 'w') as f:
    json.dump(data, f, indent=2)
