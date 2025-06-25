import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def available_couriers(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            payload = {
                "pickup_pincode": data.get("pickup_pincode"),
                "delivery_pincode": data.get("delivery_pincode"),
                "weight": data.get("weight"),
                "cod_amount": data.get("cod_amount"),
                "order_type": data.get("order_type"),
            }
            headers = {
                "api_key": "b09930a04b49c76fe894173a9f5c8814",
                "secret_key": "7ef3fd5fb052cdf4be701f182039d7bf",
                "Content-Type": "application/json",
            }
            url = "https://api.ithinklogistics.com/api_v3/shipping/available-carriers"
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            resp.raise_for_status()
            carriers = resp.json().get("data", [])
            result = []
            for c in carriers:
                result.append({
                    "company_name": c.get("company_name"),
                    "delivery_time": c.get("etd"),
                    "price": c.get("total_amount"),
                })
            return JsonResponse({"success": True, "carriers": result})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
    return JsonResponse({"error": "POST request required"}, status=405)
