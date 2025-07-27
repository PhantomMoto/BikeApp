from django.shortcuts import render
from .models import Accessory, BikeModel, Category, BikeBrand, FeaturedProduct,SlideshowImage

def home(request):
    categories = Category.objects.all()
    brands = BikeBrand.objects.all()
    models = BikeModel.objects.all()
    featured = FeaturedProduct.objects.order_by('-featured_at')
    slideshow_images = SlideshowImage.objects.all()
    # For new FeaturedProduct model, use accessories.all()
    featured_products = []
    for f in featured:
        featured_products.extend(f.accessories.all())
    return render(request, 'products/home.html', {
        'categories': categories,
        'brands': brands,
        'models': models,
        'featured_products': featured_products,
        'slideshow_images': slideshow_images,
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

    accessories = Accessory.objects.filter(stock__gt=0)
    
    if category_name:
        accessories = accessories.filter(categories__name=category_name,stock__gt=0).distinct()
    
    if model_id:
        accessories = accessories.filter(
            Q(is_universal=True) | Q(bike_models__id=model_id,stock__gt=0)
        ).distinct()
    
    elif brand_id:
        accessories = accessories.filter(bike_models__brand__id=brand_id,stock__gt=0).distinct()
    
    if search:
        accessories = accessories.filter(name__icontains=search,stock__gt=0)

    brands = BikeBrand.objects.all()
    models = BikeModel.objects.all()
    accessories = accessories.order_by('-id')
    return render(request, 'products/product_list.html', {
        'accessories': accessories,
        'brands': brands,
        'models': models,
        'brand_id': brand_id,
        'model_id': model_id,
        'category_name': category_name,
        'search': search,

    })





from django.http import JsonResponse
from .models import BikeModel  
    
def get_models_by_brand(request):
    brand_id = request.GET.get('brand_id')
    models = BikeModel.objects.filter(brand_id=brand_id).values('id', 'name')
    return JsonResponse(list(models), safe=False)

# In your products/views.py or a new search/views.py

from django.shortcuts import render
from django.db.models import Q
from .models import Accessory, Category, Blog, YouTubeVideo # Make sure these are imported

def search_results(request):
    query = request.GET.get('q', '').strip()
    
    products = []
    categories = []
    blogs = []
    videos = []

    if query:
        # Get all matching products
        products = Accessory.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) # Consider adding description to search
        ).distinct() # Use distinct if products might appear multiple times from Q objects

        # Get all matching categories
        categories = Category.objects.filter(name__icontains=query).distinct()

     

    

    context = {
        'query': query,
        'products': products,
        'categories': categories,
    }
    return render(request, 'products/search.html', context)

from django.http import JsonResponse
from .models import Accessory
def search_suggestions(request):
    from django.db.models import Q
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        # Accessories: name starts with query initials (case-insensitive)
        accessories = Accessory.objects.filter(
            Q(name__icontains=query) 
        ).values('name', 'is_universal', 'id')[:5]

        for acc in accessories:
            if acc.get('is_universal'):
                label = 'All Bikes'
            else:
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

        # Categories: name starts with query initials
        categories = Category.objects.filter(name__istartswith=query).values('name', 'id')[:3]
        for cat in categories:
            results.append({
                'name': cat['name'],
                'type': 'Category',
                'id': cat['id'],
                'kind': 'category',
            })

        # Blogs: title starts with query initials
        from .models import Blog, YouTubeVideo
        blogs = Blog.objects.filter(title__istartswith=query).values('title', 'slug')[:3]
        for blog in blogs:
            results.append({
                'name': blog['title'],
                'type': 'Blog',
                'id': blog['slug'],
                'kind': 'blog',
            })

        # YouTube Videos: title starts with query initials
        videos = YouTubeVideo.objects.filter(title__istartswith=query).values('title', 'id')[:3]
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

from django.http import JsonResponse
from .models import BikeModel  # Update with your actual model class name

def get_models(request, brand_id):
    models = BikeModel.objects.filter(brand_id=brand_id).values('id', 'name')
    return JsonResponse({'models': list(models)})





from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Accessory

@require_POST
def ajax_cart_add(request, accessory_id):
    print("AJAX cart add called")
    import json
    data = json.loads(request.body.decode('utf-8')) if request.body else {}
    color = data.get('color', '').strip()
    numeric_id = str(accessory_id).split('|')[0]
    accessory = get_object_or_404(Accessory, pk=numeric_id)
    cart = request.session.get('cart', {})

    if accessory.colors.exists():
        if color:
            cart.pop(str(numeric_id), None)
            key = f"{numeric_id}|{color}"
        else:
            keys_to_remove = [k for k in cart if k.startswith(f"{numeric_id}|")]
            for k in keys_to_remove:
                cart.pop(k, None)
            key = str(numeric_id)
    else:
        key = str(numeric_id)

    cart[key] = cart.get(key, 0) + 1
    request.session['cart'] = cart
    total_qty = sum(cart.values())

    # SEND quantity of this item in response, which your JS expects!
    return JsonResponse({'success': True, 'total_qty': total_qty, 'quantity': cart[key]})

def ajax_cart_count(request):
    cart = request.session.get('cart', {})
    total_qty = sum(cart.values())
    return JsonResponse({'total_qty': total_qty})

from django.http import JsonResponse
from .models import Accessory

def ajax_cart_items(request):
    cart = request.session.get('cart', {})
    items = []
    for key, qty in cart.items():
        # key can be 'id' or 'id|color', ignore color part completely
        print(cart)
        acc_id = key.split('|')[0]
        try:
            acc_id_int = int(acc_id)
        except Exception:
            continue
        accessory = Accessory.objects.filter(pk=acc_id_int).first()
        if accessory:
            items.append({
                'id': str(acc_id_int),
                'name': accessory.name,
                'quantity': qty,
                'offer_price': float(accessory.offer_price),
                'mrp': float(accessory.mrp),
                'color': key.split('|')[1] if '|' in key else '',  # Get color if exists
                'image': accessory.image.url if accessory.image else '',
            })
    return JsonResponse({'items': items, 'total_qty': sum(cart.values())})

from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json

@require_POST
def ajax_cart_update(request, accessory_id):
    import json
    try:
        data = json.loads(request.body)
        delta = data.get('delta', 0)
        color = data.get('color', '').strip()
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)

    cart = request.session.get('cart', {})
    key = f"{accessory_id}|{color}" if color else str(accessory_id)
    current_qty = cart.get(key, 0)
    new_qty = max(0, current_qty + delta)

    if new_qty == 0:
        cart.pop(key, None)
    else:
        cart[key] = new_qty

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
        amount = request.session.get('final_amount', 0) * 100  # Convert to paise
        if amount <= 0:
            return JsonResponse({'success': False, 'error': 'Invalid amount'}, status=400)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        order = client.order.create({
            'amount': amount,
            'currency': 'INR',
            'payment_capture': 1
        })
        return JsonResponse({'success': True, 'order_id': order['id'], 'key': settings.RAZORPAY_KEY_ID})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

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
        return JsonResponse({'success': True, 'redirect_url': '/submit-to-delhivery/'})
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


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Accessory


@csrf_exempt
@login_required
def submit_to_delhivery(request):
 
    # Get shipping info from session
    shipping = request.session.get('shipping')
    order_items = request.session.get('order_items')
    total = request.session.get('final_amount')

    # Validate
    if not shipping or not order_items or not total:
        print("shipping:", shipping)
        print("order_items:", order_items)
        print("total:", total)
        # If any of these are missing, return error
        return render(request, 'products/order_fail.html', {'error': 'Session data missing! Please try again.'})

    # Check mandatory fields
    required_fields = ['name', 'email', 'phone', 'address', 'city', 'state', 'pincode', 'priority']
    if not all(shipping.get(field) for field in required_fields):
        return render(request, 'products/order_fail.html', {'error': 'Incomplete shipping info in session.'})

    # Create order ID
    import uuid
    # Use user ID and a random UUID for uniqueness
    order_id = f"ORD-{request.user.id}-{uuid.uuid4().hex[:8]}"

    # Build product description
    products_desc = ', '.join([f"{item['accessory']['name']} x{item['quantity']} x color-->{item['color']}" for item in order_items])
    print('products_desc',products_desc)
    # Prepare data for Delhivery
    data = {
        'order_id': order_id,
        'name': shipping['name'],
        'email': shipping['email'],
        'phone': shipping['phone'],
        'address': shipping['address'],
        'city': shipping['city'],
        'state': shipping['state'],
        'pincode': shipping['pincode'],
        'priority': shipping['priority'],
        'total_weight': shipping['total_weight'], # Save total weight for Delhivery
        'total_width': shipping['total_width'],   
        'total_length':shipping['total_length'],# Save total width for Delhivery
        'total_height': shipping['total_height'],   # Save total height for Delhivery
        'amount': total,
        'mode' : shipping['mode'],  # 'Pre-paid' or 'Cash on Delivery'
        'products_desc': products_desc,
    }

    # Call Delhivery API
    response = create_delhivery_order(request,data,mode=shipping['mode'])

    waybill = None
    if response.get('packages') and response['packages'][0].get('waybill'):
        waybill = response['packages'][0]['waybill']
        # Optionally, you can save the order details in your database here
        from .models import Order
        address = f"{shipping['address']}, {shipping['city']}, {shipping['state']} - {shipping['pincode']}"
        new_order = Order.objects.create(
                    user=request.user,
                    order_id=order_id,
                    waybill=waybill,
                    amount=request.session['final_amount'],
                    products_desc=products_desc,
                    address=address,
                    status='Pending'
                )
        new_order.save()

    # Check for errors in response
        if response.get('error'):
            return render(request, 'products/order_fail.html', {'error': response['error']})

        
        
       #clear session data
        request.session['shipping'] = None 
        request.session['cart'] = {}            # Clear cart
        request.session['shipping'] = None      # Clear shipping info
        request.session['order_items'] = None   # Clear order items
        request.session['final_amount'] = None  # Clear amount
        
        
        
        
        
        return render(request, 'products/order_success.html', {
            'waybill': waybill,
            'delhivery_response': response
        })
    else:
        return render(request, 'products/order_fail.html', {'error': response})

    


import json, requests
from django.conf import settings
from datetime import datetime


def create_delhivery_order(request,data,mode):
    shipping = request.session.get('shipping')
    shipment = {
        "name": data['name'],
        "add": data['address'],
        "pin": data['pincode'],
        "city": data['city'],
        "state": data['state'],
        "country": "India",
        "phone": data['phone'],
        "order": data['order_id'],
        "payment_mode": mode,  # 'Pre-paid' or 'Cash on Delivery'
        "return_pin": "",  # Optional
        "return_city": "",
        "return_phone": "",
        "return_add": "",
        "return_state": "",
        "return_country": "",
        "products_desc": data['products_desc'],
        "hsn_code": "",
        "cod_amount": str(data['amount']) if mode=="COD" else 0,
        "total_amount": str(data['amount']),
        "seller_add": "",
        "seller_name": "",
        "seller_inv": "",
        "quantity": "1",
        "waybill": "",
        "shipment_width": float(shipping.get('total_width', '5')),  # Default to 5 if not set
        "shipment_height": float(shipping.get('total_height', '5')),  # Default to 5 if not set
        "shipment_length": float(shipping.get('total_length', '5')),  # Default to 5 if not set
        "weight": float(shipping.get('total_weight', '1')),  # Default to 1 if not set
        "shipping_mode": data['priority'],
        "mode": data['mode'],  # 'Pre-paid' or 'Cash on Delivery'
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
        "https://track.delhivery.com/api/cmu/create.json",
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
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import os
from .models import Accessory
from django.conf import settings

from django.http import HttpResponse
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import os
from io import BytesIO

def category_pdf(request):
    try:
        brand_id = request.GET.get('brand')
        model_id = request.GET.get('model')
        category_name = request.GET.get('category')

        accessories = Accessory.objects.filter(stock__gt=0)

        if brand_id:
            accessories = accessories.filter(bike_models__brand__id=brand_id)
        
        if model_id:
            accessories = accessories.filter(bike_models__id=model_id)
        if category_name:
            accessories = accessories.filter(categories__name__iexact=category_name)

        accessories = accessories.distinct()

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
        elements = []
        styles = getSampleStyleSheet()

        title = Paragraph("Filtered Accessories Report", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))

        data = [["Image", "Name", "Offer Price (₹)", "MRP (₹)", "Description"]]

        for accessory in accessories:
            if accessory.image and accessory.image.path and os.path.exists(accessory.image.path):
                img = Image(accessory.image.path, width=50, height=50)
            else:
                img = Paragraph("No Image", styles['Normal'])

            offer_price = f"₹{accessory.offer_price}" if accessory.offer_price else "-"
            mrp = f"₹{accessory.mrp}" if accessory.mrp else "-"

            data.append([
                img,
                Paragraph(accessory.name, styles['Normal']),
                offer_price,
                mrp,
                Paragraph(accessory.description or "", styles['Normal']),
            ])

        table = Table(data, colWidths=[60, 120, 80, 80, 120])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
            ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
            ('ALIGN',(2,1),(3,-1),'RIGHT'),
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.gray),
            ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ]))

        elements.append(table)
        doc.build(elements)

        pdf = buffer.getvalue()
        buffer.close()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="filtered_accessories.pdf"'
        response.write(pdf)
        return response

    except Exception as e:
        import traceback
        print("PDF Generation Error:", e)
        traceback.print_exc()
        return HttpResponse("Server error during PDF generation. Check logs.", status=500)
from django.http import HttpResponse
from io import BytesIO
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.db.models import Q
import os
from .models import Accessory  # make sure this is imported

def search_pdf(request):
    try:
        query = request.GET.get('query', '')
        accessories = Accessory.objects.filter(stock__gt=0).filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).distinct()

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
        elements = []
        styles = getSampleStyleSheet()

        title = Paragraph(f"Accessories Matching '{query}'", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))

        data = [["Image", "Name", "Offer Price (₹)", "MRP (₹)", "Description"]]

        for accessory in accessories:
            if accessory.image and accessory.image.path and os.path.exists(accessory.image.path):
                img = Image(accessory.image.path, width=50, height=50)
            else:
                img = Paragraph("No Image", styles['Normal'])

            offer_price = f"₹{accessory.offer_price}" if accessory.offer_price else "-"
            mrp = f"₹{accessory.mrp}" if accessory.mrp else "-"

            data.append([
                img,
                Paragraph(accessory.name, styles['Normal']),
                offer_price,
                mrp,
                Paragraph(accessory.description or "", styles['Normal']),
            ])

        table = Table(data, colWidths=[60, 120, 80, 80, 120])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
            ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
            ('ALIGN',(2,1),(3,-1),'RIGHT'),
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.gray),
            ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ]))

        elements.append(table)
        doc.build(elements)

        pdf = buffer.getvalue()
        buffer.close()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="accessories_{query}.pdf"'
        response.write(pdf)
        return response

    except Exception as e:
        import traceback
        print("Search PDF Error:", e)
        traceback.print_exc()
        return HttpResponse("PDF generation failed.", status=500)




@login_required
def shipping_form(request):
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        priority = request.POST.get('priority')
        mode = request.POST.get('mode', 'Pre-paid')  # Default to Pre-paid if not set
        # mode = 
        cart = request.session.get('cart', {})
        
        accessories = []
        order_items = []
        total = 0
        for key, qty in cart.items():
            acc_id = key.split('|')[0]
            accessory = Accessory.objects.filter(pk=acc_id).first()
            if accessory:
                accessories.append({
                    'accessory': accessory,
                    'quantity': qty,
                    'subtotal': accessory.offer_price * qty,
                })
                total += accessory.offer_price * qty
                order_items.append({
                    'accessory': {
                        'id': accessory.id,
                        'name': accessory.name,
                        'price': float(accessory.offer_price),
                        'mrp': float(accessory.mrp),
                        'color': accessory.colors.first().name if accessory.colors.exists() else '',  # ADD THIS LINE
                    },
                    'color': key.split('|')[1] if '|' in key else '',  # ADD THIS LINE
                    'quantity': qty,
                })
        total_width = 0
        total_height = 0
        total_weight = 0
        total_length = 0

        

        for key, qty in cart.items():
            acc_id = key.split('|')[0]
            accessory = Accessory.objects.filter(pk=acc_id).first()
            if accessory:
                total_width += accessory.shipment_width * qty
                total_length += accessory.shipment_length * qty
                total_height += accessory.shipment_height * qty
                total_weight += accessory.shipment_weight * qty


        # Here you can calculate delivery cost, e.g.:
        # delivery_cost = 150 if pincode.startswith('4') else 200l
        if priority == 'Express':
            delivery_cost = get_delhivery_shipping_cost(dest_pin=pincode, weight_grams=total_weight, mode='E', payment_type=mode)
        else:
            delivery_cost = get_delhivery_shipping_cost(dest_pin=pincode, weight_grams=total_weight, mode='S', payment_type=mode)
            
        print("Delivery cost calculated:", delivery_cost)
        # Save in session
        
        request.session['shipping'] = {
            'name': name,
            'email': email,
            'phone': phone,
            'address': address,
            'city': city,
            'state': state,
            'pincode': pincode,
            'delivery_cost': delivery_cost,
            'priority': priority,
            'amount': float(total) + delivery_cost, 
            'total_weight': total_weight,  # Save total weight for Delhivery
            'total_width': total_width,    # Save total width for Delhivery
            'total_height': total_height,  # Save total height for Delhivery
            'total_length': total_length,  # Assuming length is not used, set to 0
            'mode': mode,  # 'Pre-paid' or 'Cash on Delivery'
            
        }
        request.session['order_items'] = order_items  # <-- Save order items in session too

        print("Shipping info saved in session:", request.session['shipping'])
        return redirect('products:order_summary')  # URL to summary page
    else:
        total = request.session.get('final_amount', 0)
        cart = request.session.get('cart', {})
        accessories = []
        order_items = []
        # accessory = Accessory.objects.filter(pk=acc_id).first()
        # for key,qty in cart.items():
        #     acc_id = key.split('|')[0]
    
            
        can_cod = all(
        Accessory.objects.get(pk=int(acc_key.split('|')[0])).is_COD
        for acc_key in cart.keys()
        )

            # print("Can COD for all items:", can_cod)
  
        # Check if all items can be COD
        # If you want to check if COD is available for all items, you can do it like this:
        # request.session['is_COD'] = can_cod  # Save in session if COD is available
        # print("Can COD:", can_cod)
        # if not can_cod:
        #     request.session['is_COD'] = False
        # else:
        #     request.session['is_COD'] = True
        total = 0
        for key, qty in cart.items():
            acc_id = key.split('|')[0]
            accessory = Accessory.objects.filter(pk=acc_id).first()
            if accessory:
                accessories.append({
                    'accessory': accessory,
                    'quantity': qty,
                    'subtotal': accessory.offer_price * qty,
                })
                total += accessory.offer_price * qty
                order_items.append({
                    'accessory': {
                        'id': accessory.id,
                        'name': accessory.name,
                        'price': float(accessory.offer_price),
                    },
                    'quantity': qty,
                })
        print(total)
        return render(request, 'products/shipping_form.html',{'total': total,'isCOD': can_cod, 'accessories': accessories, 'order_items': order_items})
@login_required
def order_summary(request):
    cart = request.session.get('cart', {})
    shipping = request.session.get('shipping')

    if not shipping:
        return redirect('products:shipping_form')  # force user to fill shipping first

    accessories = []
    total = 0
    for key, qty in cart.items():
        acc_id = key.split('|')[0]
        accessory = Accessory.objects.filter(pk=acc_id).first()
        if accessory:
            accessories.append({
                'accessory': accessory,
                'quantity': qty,
                'subtotal': accessory.offer_price * qty,
            })
            total += accessory.offer_price * qty

    delivery_cost = shipping.get('delivery_cost', 0)
    from decimal import Decimal

    grand_total = total + Decimal(str(delivery_cost))

    request.session['final_amount'] = float(grand_total)  # Save for payment

    return render(request, 'products/order_summary.html', {
        'cart_items': accessories,
        'subtotal': total,
        'delivery_cost': delivery_cost,
        'grand_total': grand_total,
        'shipping': shipping,
    })

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Order
import requests
from django.conf import settings

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'products/my_orders.html', {'orders': orders})

@login_required
def track_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)

    # Delhivery Tracking API logic
    waybill = order.waybill
    headers = {
        'Authorization': f'Token {settings.DELHIVERY_API_TOKEN}',  # Set in settings.py
    }
    url = f'https://track.delhivery.com/api/v1/packages/json/?waybill={waybill}&client_name={settings.DELHIVERY_CLIENT_NAME}'
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        tracking_data = response.json()
        shipment_data = tracking_data.get('ShipmentData', [{}])[0].get('Shipment', {})
        status_obj = shipment_data.get('Status', {})
        current_status = status_obj.get('Status', 'Unknown')
        current_status_date = status_obj.get('StatusDateTime', '')
        current_status_location = status_obj.get('StatusLocation', '')
        expected_delivery = shipment_data.get('ExpectedDeliveryDate')
        if not expected_delivery:
            expected_delivery = "Not available"
        scan_history = []
        scans = shipment_data.get('Scans', [])
        for scan in scans:
            detail = scan.get('ScanDetail', {})
            scan_history.append({
                'scan': detail.get('Scan', ''),
                'type': detail.get('ScanType', ''),
                'location': detail.get('ScannedLocation', ''),
                'datetime': detail.get('ScanDateTime', ''),
                'instructions': detail.get('Instructions', ''),
            })

        context = {
            'order': order,
            'current_status': current_status,
            'current_status_date': current_status_date,
            'current_status_location': current_status_location,
            'expected_delivery': expected_delivery,
            'scan_history': scan_history,
        }


    else:
        tracking_data = {'error': 'Unable to fetch tracking info from Delhivery.'}
        
    return render(request, 'products/track_order.html', context)

def get_delhivery_shipping_cost(origin_pin=401107, dest_pin=401107, weight_grams=1000, mode='S', payment_type='Pre-paid'):
    url = "https://track.delhivery.com/api/kinko/v1/invoice/charges/.json"
    params = {
        'md': mode,
        'ss': 'Delivered',
        'd_pin': dest_pin,
        'o_pin': origin_pin,
        'cgm': weight_grams,
        'pt': payment_type
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Token 5ef5b6f39ed14f7dc902f5d7aac7efcbff1c47d4"
    }
    resp = requests.get(url, params=params, headers=headers)
    data = resp.json()

    print("Response from Delhivery Cost API:", data)  # DEBUG: dekho kya aa raha

    if isinstance(data, list) and len(data) > 0:
        return data[0].get('total_amount', 0)
    elif isinstance(data, dict):
        return data.get('total_amount', 0)
    else:
        return 0

from django.shortcuts import render
from .models import CustomerFeedback
def terms(request):
    return render(request, 'products/terms.html')
def about(request):
    return render(request, 'products/about.html')
def feedback(request):
    feedbacks = CustomerFeedback.objects.order_by('-uploaded_at')
    return render(request, 'products/feedback.html',{'feedbacks':feedbacks})