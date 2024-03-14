# Create your views here.
# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import base64
import io
from PIL import Image
from io import BytesIO
import random
from django.views.generic import TemplateView
from django.core.cache import cache
import redis
from apps.sharefiles.redis_pool import POOL
from EasyShare.settings.base import MAX_CONCURRENT_REQUESTS
from apps.surgery.utils import load_model


@csrf_exempt
def upload_frame(request):
    # TODO:Check if the number of concurrent requests exceeds the limit
    # conn = redis.Redis(connection_pool=POOL)
    # with conn.lock('requests'):
    #     current_concurrent_requests = cache.get('concurrent_requests', 0)
    #     # Increment the concurrent requests count
    #     cache.incr('concurrent_requests')
    #     if current_concurrent_requests >= MAX_CONCURRENT_REQUESTS:
    #         return JsonResponse('Too many concurrent requests. Try again later.', status=503)
    try:
        if request.method == 'POST':
            data = request.POST.get('frame')
            if data:
                # Convert base64 data to image
                img_data = base64.b64decode(data.split(',')[1])
                img = Image.open(io.BytesIO(img_data))
                # get the image size
                width, height = img.size
                # resize the image
                img = img.resize((1920, 1080))
                model = load_model()
                # Process the image (perform machine learning predictions)
                out_frame, flag_1_345, flag_8_910 = model.get_vis_flag(img)
                print("done")
                # resize the image back to the original size
                out_frame = out_frame.resize((width, height))
                # return the result
                buffered = BytesIO()
                out_frame.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
                return JsonResponse({'frame': img_str, 'flag_1_345': flag_1_345, 'flag_8_910': flag_8_910})
            return JsonResponse({'error': 'Invalid request'})
    finally:
        # Decrement the concurrent requests count after processing
        # cache.decr('concurrent_requests')
        ...

class demoWeb(TemplateView):
    template_name = 'demo.html'

class socketWeb(TemplateView):
    template_name = 'demo2.html'
    