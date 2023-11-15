from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from PIL import Image
import rembg
import io
import json
import base64   
import numpy as np
from datetime import datetime


@csrf_exempt
def shopify_webhook(request):
    if request.method == 'POST':
        hmac_header = request.headers.get('X-Shopify-Hmac-SHA256', '')
        data = request.body
        print("payload is here ")
        
        payload = json.loads(request.body)
        print(payload,"payloadddd hahhaahahaha")
        if payload:
            try:
                image_url = payload.get('images', [{}])[0].get('src', '')
                
                product_id = payload.get('id')
                
                if image_url:
                    print("image will process")
                    image_data = requests.get(image_url).content
                    input_image = Image.open(io.BytesIO(image_data))
                    input_array = np.array(input_image)
                    output_array = rembg.remove(input_array)
                    output_image = Image.fromarray(output_array).convert('RGB')
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    filename = f"output_{timestamp}.jpg"
                    processed_image_data = base64.b64encode(output_image.tobytes()).decode('utf-8')

                    output_image.save(filename)
                    
                    with open(filename, 'rb') as image_file:
                        processed_image_data = base64.b64encode(image_file.read()).decode('utf-8')
                        
                    shopify_api_url = f'https://f386cc.myshopify.com/admin/api/2023-01/products/{product_id}.json'
                    shopify_api_headers = {
                        'Content-Type': 'application/json',
                        'X-Shopify-Access-Token': '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',
                    }

                    data = {
                        'product': {
                            'id': product_id,
                            'images':[{ "attachment" : processed_image_data }]
                        }
                    }

                    response = requests.put(shopify_api_url, json=data, headers=shopify_api_headers)
                    print("responese")
                    if response.status_code == 200:
                        # Product updated successfully
                        return JsonResponse({'message': 'Product updated successfully'})
                    else:
                        return JsonResponse({'error': 'Failed to update product'}, status=response.status_code)
            except:
                return JsonResponse({'success': False, 'error': 'Invalid request method or missing payload'})

    
    return HttpResponse(status=400)  

