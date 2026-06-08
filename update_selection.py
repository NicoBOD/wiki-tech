import json
import datetime

file_path = '/opt/data/website-zamania/.automation/zamania-selection.json'

with open(file_path, 'r') as f:
    data = json.load(f)

data['status'] = 'published'
data['published_at'] = datetime.datetime.now().isoformat()
data['slug'] = 'ia-qualification-pipeline-commercial'
data['links'] = {
    'fr': 'https://zamania.fr/blog/ia-qualification-pipeline-commercial.html',
    'en': 'https://zamania.fr/en/blog/ia-qualification-pipeline-commercial.html',
    'ar': 'https://zamania.fr/ar/blog/ia-qualification-pipeline-commercial.html'
}

with open(file_path, 'w') as f:
    json.dump(data, f, indent=2)
