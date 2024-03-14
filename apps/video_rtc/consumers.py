# consumers.py
import base64
import time
from PIL import Image
from io import BytesIO
import json
import numpy as np
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.surgery.utils import load_model

class SegmentationConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = load_model()

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        # Receive a message from the client (if needed)
        data = json.loads(text_data)
        image_data = data['frame']
        # convert base64 data to image
        image_data,width, height = self.base64_to_image(image_data, 1920, 1080)
        # get process speed
        start_time = time.time()
        result_frame, flag_1_345, flag_8_910 = self.model.get_vis_flag(image_data)
        print("Process time: ", time.time() - start_time)
        # resize the image back to the original size
        result_frame = self.resize_image(result_frame, width, height)
        # Perform video segmentation and send the result back to the client
        # Convert the result image to base64
        result_frame = self.image_to_base64(result_frame)
        segmentation_result = {
            'result_frame': result_frame,
            'flag_1_345': flag_1_345,
            'flag_8_910': flag_8_910
        }
        await self.send(text_data=json.dumps(segmentation_result))

    def base64_to_image(self, base64_string, new_width, new_height):
        # Remove the 'data:image/jpeg;base64,' prefix
        base64_data = base64_string.split(',')[1]

        # Decode base64 to bytes
        image_bytes = base64.b64decode(base64_data)

        # Convert bytes to PIL Image
        image = Image.open(BytesIO(image_bytes)).convert('RGB')
        # get the image size
        width, height = image.size
        # resize the image
        image = image.resize((new_width, new_height))
        # convert the image to numpy array
        image = np.array(image)
        return image, width, height
    
    def image_to_base64(self, image):
        # Convert PIL Image to base64
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        result_image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        return result_image_base64
    
    def resize_image(self, image, width, height):
        # Convert the numpy array to PIL Image
        image = Image.fromarray(image)
        # resize the image
        image = image.resize((width, height))
        return image