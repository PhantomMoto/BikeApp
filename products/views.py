from django.shortcuts import render
from .models import Accessory, BikeModel, Category, BikeBrand, FeaturedProduct

def home(request):
    categories = Category.objects.all()
    brands = BikeBrand.objects.all()
    models = BikeModel.objects.all()
    featured = FeaturedProduct.objects.order_by('featured_at')
    # For new FeaturedProduct model, use accessories.all()
    featured_products = []
    for f in featured:
        featured_products.extend(f.accessories.all())
    return render(request, 'products/home.html', {
        'categories': categories,
        'brands': brands,
        'models': models,
        'featured_products': featured_products,
    })



    # return render(request, "products/home.html")
    

from django.contrib.auth.decorators import login_required

# @login_required(login_url='products:login')
from django.db.models import Q  # 👈 FIXED

def product_list(request):
    brand_id = request.GET.get('brand')
    model_id = request.GET.get('model')
    category_name = request.GET.get('category')
    search = request.GET.get('search')

    accessories = Accessory.objects.all()
    
    if category_name:
        accessories = accessories.filter(categories__name=category_name).distinct()
    
    if model_id:
        accessories = accessories.filter(
            Q(is_universal=True) | Q(bike_models__id=model_id)
        ).distinct()
    
    elif brand_id:
        accessories = accessories.filter(bike_models__brand__id=brand_id).distinct()
    
    if search:
        accessories = accessories.filter(name__icontains=search)

    brands = BikeBrand.objects.all()
    models = BikeModel.objects.all()

    return render(request, 'products/product_list.html', {
        'accessories': accessories,
        'brands': brands,
        'models': models,
    })





from django.http import JsonResponse
from .models import BikeModel  
    
def get_models_by_brand(request):
    brand_id = request.GET.get('brand_id')
    models = BikeModel.objects.filter(brand_id=brand_id).values('id', 'name')
    return JsonResponse(list(models), safe=False)


from django.http import JsonResponse
from .models import Accessory

def search_suggestions(request):
    from django.db.models import Q
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        # Accessories (products)
        accessories = Accessory.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).values('name', 'is_universal', 'id')[:5]
        for acc in accessories:
            if acc.get('is_universal'):
                label = 'All Bikes'
            else:
                # Get up to 3 bike model names for this accessory
                from .models import Accessory as AccModel
                try:
                    acc_obj = AccModel.objects.get(id=acc['id'])
                    bike_names = list(acc_obj.bike_models.values_list('name', flat=True)[:3])
                    if bike_names:
                        label = ', '.join(bike_names)
                        if acc_obj.bike_models.count() > 3:
                            label += ', ...'
                    else:
                        label = 'Specific Bike'
                except Exception:
                    label = 'Specific Bike'
            results.append({
                'name': acc['name'],
                'type': label,
                'id': acc['id'],
                'kind': 'product',
            })
        # Categories
        categories = Category.objects.filter(name__icontains=query).values('name', 'id')[:3]
        for cat in categories:
            results.append({
                'name': cat['name'],
                'type': 'Category',
                'id': cat['id'],
                'kind': 'category',
            })
        # Blogs
        from .models import Blog, YouTubeVideo
        blogs = Blog.objects.filter(title__icontains=query).values('title', 'slug')[:3]
        for blog in blogs:
            results.append({
                'name': blog['title'],
                'type': 'Blog',
                'id': blog['slug'],
                'kind': 'blog',
            })
        # YouTube Videos
        videos = YouTubeVideo.objects.filter(title__icontains=query).values('title', 'id')[:3]
        for video in videos:
            results.append({
                'name': video['title'],
                'type': 'Video',
                'id': video['id'],
                'kind': 'video',
            })
    return JsonResponse({'results': results})


from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('products:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'products/register.html', {'form': form})


from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required(login_url='products:login')
def account_view(request):
    # You can pass user info or orders or whatever here
    return render(request, 'products/account.html', {'user': request.user})

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('products:login')  # or homepage


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def login_view(request):
    error_msg = None
    if request.method == 'POST':
        identifier = request.POST.get('username')  # can be username or email
        password = request.POST.get('password')
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = None
        # Try to authenticate by username
        user = authenticate(request, username=identifier, password=password)
        if user is None:
            # Try to authenticate by email
            try:
                user_obj = User.objects.get(email=identifier)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        if user is not None:
            login(request, user)
            return redirect('products:account')
        else:
            error_msg = "Invalid username or email or password"
    
    return render(request, 'products/login.html', {'error_msg': error_msg})

from django.shortcuts import render, redirect, get_object_or_404
from .models import Accessory
from django.http import JsonResponse

@login_required(login_url='products:login')
def cart_view(request):
    cart = request.session.get('cart', {})
    accessories = []
    total = 0
    pay_items = []

    for key, qty in cart.items():
        if '|' in key:
            acc_id, color = key.split('|', 1)
        else:
            acc_id, color = key, ''
        accessory = get_object_or_404(Accessory, pk=acc_id)
        subtotal = accessory.offer_price * qty
        accessories.append({
            'accessory': accessory,
            'quantity': qty,
            'subtotal': subtotal,
            'color': color,  # pass color for display
        })
        pay_items.append({
            'id': accessory.id,
            'name': accessory.name,
            'offer_price': float(accessory.offer_price),
            'mrp': float(accessory.mrp),
            'quantity': qty,
            'subtotal': float(subtotal),
            'color': color,
        })
        total += subtotal

    request.session['paydetails'] = {
        'items': pay_items,
        'price': float(total),
    }

    return render(request, 'products/cart.html', {
        'cart_items': accessories,
        'total': total,
    })

def cart_add(request, accessory_id):
    color = request.POST.get('color', '').strip()
    numeric_id = str(accessory_id).split('|')[0]
    accessory = get_object_or_404(Accessory, pk=numeric_id)
    cart = request.session.get('cart', {})
    # If accessory has colors, require color selection (for home/featured)
    if accessory.colors.exists():
        if color:
            # Remove entry without color if adding with color
            cart.pop(str(numeric_id), None)
            key = f"{numeric_id}|{color}"
        else:
            # Remove all entries with color if adding without color
            keys_to_remove = [k for k in cart if k.startswith(f"{numeric_id}|")]
            for k in keys_to_remove:
                cart.pop(k, None)
            key = str(numeric_id)
    else:
        key = str(numeric_id)
    cart[key] = cart.get(key, 0) + 1
    request.session['cart'] = cart
    return redirect('products:cart')

def cart_remove(request, accessory_id):
    numeric_id = str(accessory_id).split('|')[0]
    cart = request.session.get('cart', {})
    # Remove all keys matching this accessory id (with or without color)
    keys_to_remove = [k for k in cart if k.split('|')[0] == str(numeric_id)]
    for k in keys_to_remove:
        cart.pop(k, None)
    request.session['cart'] = cart
    return redirect('products:cart')

def cart_update(request, accessory_id):
    numeric_id = str(accessory_id).split('|')[0]
    if request.method == 'POST':
        qty = int(request.POST.get('quantity', 1))
        color = request.POST.get('color', '').strip()
        cart = request.session.get('cart', {})
        # Remove all keys matching this accessory id (with or without color)
        keys_to_remove = [k for k in list(cart.keys()) if k.split('|')[0] == str(numeric_id)]
        for k in keys_to_remove:
            cart.pop(k, None)
        # Add new entry with updated color (if any)
        key = f"{numeric_id}|{color}" if color else str(numeric_id)
        if qty > 0:
            cart[key] = qty
        request.session['cart'] = cart
    return redirect('products:cart')



from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Accessory

@require_POST
def ajax_cart_add(request, accessory_id):
    import json
    data = json.loads(request.body.decode('utf-8')) if request.body else {}
    color = data.get('color', '').strip()
    numeric_id = str(accessory_id).split('|')[0]
    accessory = get_object_or_404(Accessory, pk=numeric_id)
    cart = request.session.get('cart', {})
    # If accessory has colors, require color selection (for home/featured)
    if accessory.colors.exists():
        if color:
            # Remove entry without color if adding with color
            cart.pop(str(numeric_id), None)
            key = f"{numeric_id}|{color}"
        else:
            # Remove all entries with color if adding without color
            keys_to_remove = [k for k in cart if k.startswith(f"{numeric_id}|")]
            for k in keys_to_remove:
                cart.pop(k, None)
            key = str(numeric_id)
    else:
        key = str(numeric_id)
    cart[key] = cart.get(key, 0) + 1
    request.session['cart'] = cart
    total_qty = sum(cart.values())
    return JsonResponse({'success': True, 'total_qty': total_qty})

def ajax_cart_count(request):
    cart = request.session.get('cart', {})
    total_qty = sum(cart.values())
    return JsonResponse({'total_qty': total_qty})

def ajax_cart_items(request):
    cart = request.session.get('cart', {})
    items = []
    for key, qty in cart.items():
        if '|' in key:
            acc_id, color = key.split('|', 1)
        else:
            acc_id, color = key, ''
        try:
            acc_id_int = int(acc_id)
        except Exception:
            continue
        accessory = Accessory.objects.filter(pk=acc_id_int).first()
        if accessory:
            display_name = accessory.name
            if color:
                display_name = f"{accessory.name} {color}"
            items.append({
                'id': str(acc_id_int),
                'name': display_name,
                'quantity': qty,
                'price': str(accessory.offer_price),
                'color': color if color else None,
                'image': accessory.image.url if accessory.image else '',
            })
    return JsonResponse({'items': items, 'total_qty': sum(cart.values())})

from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json

@require_POST
def ajax_cart_update(request, accessory_id):
    try:
        data = json.loads(request.body)
        delta = data.get('delta', 0)
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)

    cart = request.session.get('cart', {})
    accessory_id_str = str(accessory_id)
    current_qty = cart.get(accessory_id_str, 0)
    new_qty = max(0, current_qty + delta)

    if new_qty == 0:
        if accessory_id_str in cart:
            del cart[accessory_id_str]
    else:
        cart[accessory_id_str] = new_qty

    request.session['cart'] = cart
    total_qty = sum(cart.values())

    return JsonResponse({'success': True, 'quantity': new_qty, 'total_qty': total_qty})


import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest

from django.conf import settings

@csrf_exempt
def create_razorpay_order(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        amount = int(data.get('amount', 0))
        if amount <= 0:
            return HttpResponseBadRequest('Invalid amount')
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)) 
        order = client.order.create({
            'amount': amount,  # in paise
            'currency': 'INR',
            'payment_capture': 1
        })
        return JsonResponse({'order_id': order['id'], 'key': settings.RAZORPAY_KEY_ID})
    return HttpResponseBadRequest('Invalid request')

@csrf_exempt
def verify_razorpay_payment(request):

    import json
    try:
        data = json.loads(request.body)
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        params_dict = {
            'razorpay_order_id': data['razorpay_order_id'],
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_signature': data['razorpay_signature']
        }
        client.utility.verify_payment_signature(params_dict)
        # Mark order as paid, but DO NOT clear cart here!
        # Cart will be cleared after successful Delhivery order.
        return JsonResponse({'success': True, 'redirect_url': '/post-payment/'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        # Here you could send an email, save to DB, etc.
        return render(request, 'products/contact.html', {
            'success': True,
            'name': name
        })
    return render(request, 'products/contact.html')


from .models import Blog, YouTubeVideo
from django.shortcuts import get_object_or_404

def blog_list_view(request):
    blogs = Blog.objects.order_by('-published_at')
    videos = YouTubeVideo.objects.all()
    return render(request, 'products/blog_page.html', {'blogs': blogs, 'videos': videos})

def blog_detail_view(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    return render(request, 'products/blog_detail.html', {'blog': blog})




from django.shortcuts import render
from .models import Message

from django.shortcuts import render
from .models import Message

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name').strip()
        email = request.POST.get('email').strip()
        phone = request.POST.get('phone').strip()
        message_text = request.POST.get('message').strip()

        # Check if same message already sent by same email
        already_sent = Message.objects.filter(
            email=email,
            message=message_text
        ).exists()

        if already_sent:
            # Agar pehle se hai, to warning ke sath return kar
            return render(request, 'products/contact.html', {
                'error': True,
                'error_message': 'You have already sent this message!',
                'name': name,
                'email': email,
                'phone': phone,
                'message': message_text,
            })

        # Nahi toh message save kar
        Message.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message_text,
        )

        # # Notify the site owner via email
        # from django.core.mail import send_mail
        # owner_email = 'owner@example.com'  # <-- Change to your email
        # subject = f"New Contact Message from {name}"
        # message_body = f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message_text}"
        # send_mail(
        #     subject,
        #     message_body,
        #     'no-reply@phantommoto.in',  # From email (set a valid sender)
        #     [owner_email],
        #     fail_silently=True,
        # )

        return render(request, 'products/contact.html', {'success': True, 'name': name})

    return render(request, 'products/contact.html')
import requests

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Accessory
import requests
import json

# 🟢 Unified Shipping & Order Submission (no session juggling)
@csrf_exempt
@login_required
def submit_to_delhivery(request):
    if request.method == 'POST':
        # Get shipping info
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        priority = request.POST.get('priority')
        # Get order/cart info
        try:
            order_items = json.loads(request.POST.get('order_items', '[]'))
        except Exception:
            order_items = []
        total = float(request.POST.get('order_total', 0))
        if not (name and email and phone and address and city and state and pincode and order_items and total):
            return render(request, 'products/order_fail.html', {'error': 'Missing required order or shipping info.'})
        # Build order_id (could use user+timestamp or uuid)
        import uuid
        order_id = f"ORD-{request.user.id}-{uuid.uuid4().hex[:8]}"
        # Build products_desc
        products_desc = ', '.join([f"{item['accessory']['name']} x{item['quantity']}" for item in order_items])
        # Prepare Delhivery payload
        data = {
            'order_id': order_id,
            'name': name,
            'email': email,
            'phone': phone,
            'address': address,
            'city': city,
            'state': state,
            'pincode': pincode,
            'priority': priority,
            'amount': total,
            'products_desc': products_desc,
        }
        response = create_delhivery_order(data)
        # Debug: show full response if order not created
        waybill = None
        if response.get('packages') and response['packages'] and response['packages'][0].get('waybill'):
            waybill = response['packages'][0]['waybill']
            request.session['cart'] = {}  # Clear cart only after successful order
            return render(request, 'products/order_success.html', {'waybill': waybill, 'delhivery_response': response})
        else:
            # Show full response for debugging
            return render(request, 'products/order_fail.html', {'error': response})
    # On GET, show shipping form with cart summary
    cart = request.session.get('cart', {})
    accessories = []
    total = 0
    for key, qty in cart.items():
        if '|' in key:
            acc_id, color = key.split('|', 1)
        else:
            acc_id, color = key, ''
        accessory = Accessory.objects.filter(pk=acc_id).first()
        if accessory:
            accessories.append({
                'accessory': accessory,
                'quantity': qty,
                'color': color,
                'subtotal': accessory.price * qty
            })
            total += accessory.price * qty
    return render(request, 'shipping_form.html', {'cart_items': accessories, 'total': total})

# 🟢 Utility to Create Order via Delhivery API
# This is NOT a Django view! Only called from submit_to_delhivery

import json, requests
from django.conf import settings
from datetime import datetime


def create_delhivery_order(data):
    shipment = {
        "name": data['name'],
        "add": data['address'],
        "pin": data['pincode'],
        "city": data['city'],
        "state": data['state'],
        "country": "India",
        "phone": data['phone'],
        "order": data['order_id'],
        "payment_mode": "Prepaid",
        "return_pin": "",  # Optional
        "return_city": "",
        "return_phone": "",
        "return_add": "",
        "return_state": "",
        "return_country": "",
        "products_desc": data['products_desc'],
        "hsn_code": "",
        "cod_amount": "",
        "total_amount": str(data['amount']),
        "seller_add": "",
        "seller_name": "",
        "seller_inv": "",
        "quantity": "1",
        "waybill": "",
        "shipment_width": "10",
        "shipment_height": "5",
        "weight": "0.5",
        "shipping_mode": data['priority'],
        "address_type": "",
        "order_date": datetime.now().strftime("%Y-%m-%d")
    }

    api_body = {
        "shipments": [shipment],
        "pickup_location": {
            "name": "Phantom Moto"  # Replace with pickup name, NOT CODE
        }
    }

    # Create payload exactly as they expect: format=json & data={JSON string}
    payload = {
        "format": "json",
        "data": json.dumps(api_body)
    }

    headers = {
        "Authorization": f"Token {settings.DELHIVERY_API_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(
        "https://staging-express.delhivery.com/api/cmu/create.json",
        headers=headers,
        data=payload
    )

    print("📤 SENT TO DELHIVERY:")
    print(payload)
    print("📩 RESPONSE FROM DELHIVERY:")
    print(response.status_code, response.text)

    try:
        return response.json()
    except Exception as e:
        return {"error": str(e), "raw_response": response.text}

from django.shortcuts import get_object_or_404

def product_detail(request, slug):
    accessory = get_object_or_404(Accessory, slug=slug)
    return render(request, 'products/product_detail.html', {'accessory': accessory})




from django.http import HttpResponse
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def category_pdf(request):
    category_name = request.GET.get('category')
    if not category_name:
        return HttpResponse('No category specified.', status=400)
    accessories = Accessory.objects.filter(categories__name=category_name)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50
    p.setFont('Helvetica-Bold', 16)
    p.drawString(50, y, f'Products in Category: {category_name}')
    y -= 30
    p.setFont('Helvetica', 12)
    for acc in accessories:
        if y < 80:
            p.showPage()
            y = height - 50
            p.setFont('Helvetica', 12)
        p.drawString(60, y, f"{acc.name} - ₹{acc.offer_price} (MRP: ₹{acc.mrp})")
        y -= 22
        if acc.description:
            p.setFont('Helvetica-Oblique', 10)
            p.drawString(70, y, acc.description[:90])
            y -= 18
            p.setFont('Helvetica', 12)
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{category_name}_products.pdf"'
    return response
