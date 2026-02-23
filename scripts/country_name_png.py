import json

with open('tide_gauge.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for row in data:
    cn = row.get('country_name')
    if cn and not cn.endswith('.png'):
        row['country_name'] = f'{cn}.png'

with open('tide_gauge.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')

print('Updated all country_name fields to end with .png')
