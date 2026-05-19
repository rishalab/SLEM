import json
import numpy as np
from PIL import Image

with open('payload_100KB.json', 'w') as f: json.dump({"data": "A" * 100_000}, f)
with open('payload_10MB.json', 'w') as f: json.dump({"data": "A" * 10_000_000}, f)

Image.fromarray((np.random.rand(512, 512, 3) * 255).astype('uint8')).save('img_512.jpg')
Image.fromarray((np.random.rand(2048, 2048, 3) * 255).astype('uint8')).save('img_2048.jpg')
print("Fixtures generated successfully.")