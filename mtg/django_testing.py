from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def my_view(request):
    if request.method == "GET":
        return JsonResponse({"message": "This is a GET request"})

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            return JsonResponse({"message": "Received POST request", "data": data})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({"error": "Method not allowed"}, status=405)
