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

from EasyShare.settings.base import MAX_CONCURRENT_REQUESTS


@csrf_exempt
def upload_frame(request):
    # Check if the number of concurrent requests exceeds the limit
    current_concurrent_requests = cache.get('concurrent_requests', 0)
    if current_concurrent_requests >= MAX_CONCURRENT_REQUESTS:
        return JsonResponse('Too many concurrent requests. Try again later.', status=503)

    # Increment the concurrent requests count
    cache.incr('concurrent_requests')
    try:
        if request.method == 'POST':
            data = request.POST.get('frame')
            if data:
                # Convert base64 data to image
                img_data = base64.b64decode(data.split(',')[1])
                img = Image.open(io.BytesIO(img_data))

                # Process the image (perform machine learning predictions)
                

                # random prediction result for demonstration
                res = random.randint(0, 1000)
                # Example: Return a JsonResponse with the prediction result
                prediction_result = {'prediction': f'{res}'}
                return JsonResponse(prediction_result)

            return JsonResponse({'error': 'Invalid request'})
    finally:
        # Decrement the concurrent requests count after processing
        cache.decr('concurrent_requests')

class demoWeb(TemplateView):
    template_name = 'demo.html'

class socketWeb(TemplateView):
    template_name = 'demo2.html'
    