import ast

# Read the file
with open('c:\\code\\Rena Python\\MVA5\\metadata\\MICROBIAL_DISCARDING.py', 'r') as f:
    content = f.read()

# Find the MICROBIAL_DISCARDING dict
start = content.find('MICROBIAL_DISCARDING = {')
start = content.find('{', start)
# Find the end before # Default
default_pos = content.find('# Default settings')
end = content.rfind('}', 0, default_pos) + 1

dict_str = content[start:end]

data = ast.literal_eval(dict_str)

# Now transform
for method, config in data.items():
    if 'info' in config:
        info = config['info']
        # Move title, description, algorithm to main
        if 'title' in info:
            config['title'] = info['title']
        if 'description' in info:
            config['description'] = info['description']  # overwrite existing
        if 'algorithm' in info:
            config['algorithm'] = info['algorithm']
        
        # Move parameters
        if 'parameters' in info:
            params_list = list(config['parameters'].keys())
            for i, param_key in enumerate(params_list):
                if i < len(info['parameters']):
                    info_param = info['parameters'][i]
                    config['parameters'][param_key]['info'] = info_param
        
        # Remove from info
        for key in ['title', 'description', 'algorithm', 'parameters']:
            info.pop(key, None)

# Now, write back
new_content = f"MICROBIAL_DISCARDING = {repr(data)}\n\n# Default settings for quick start\nDEFAULT_MICROBIAL_DISCARDING_SETTINGS = {{\n    'prevalence_filtering': {{\n        'enabled': True,\n        'detection_threshold': 0.0,\n        'min_prevalence': 0.1\n    }},\n    'abundance_filtering': {{\n        'enabled': True,\n        'min_mean_abundance': 0.0001,\n        'min_median_abundance': 0.00005\n    }}\n}}"

with open('c:\\code\\Rena Python\\MVA5\\metadata\\MICROBIAL_DISCARDING_new.py', 'w') as f:
    f.write(new_content)