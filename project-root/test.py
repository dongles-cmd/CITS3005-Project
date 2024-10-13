import json
with open("data/pc.json", 'r') as file:
    data = json.load(file)

count = 0
for i in data:
    count += 1
print(count)