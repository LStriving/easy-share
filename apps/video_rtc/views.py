# Create your views here.
# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import base64
import io
from PIL import Image
import random
from django.views.generic import TemplateView

@csrf_exempt
def upload_frame(request):
    if request.method == 'POST':
        data = request.POST.get('frame')
        if data:
            # Convert base64 data to image
            img_data = base64.b64decode(data.split(',')[1])
            img = Image.open(io.BytesIO(img_data))

            # Process the image (perform machine learning predictions)
            # You can use a machine learning model for predictions here

            # random prediction result for demonstration
            res = random.randint(0, 1000)
            # Example: Return a JsonResponse with the prediction result
            prediction_result = {'prediction': f'{res}'}
            return JsonResponse(prediction_result)

    return JsonResponse({'error': 'Invalid request'})

class demoWeb(TemplateView):
    template_name = 'demo.html'

class socketWeb(TemplateView):
    template_name = 'demo2.html'
    