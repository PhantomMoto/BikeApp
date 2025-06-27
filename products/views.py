from django.shortcuts import render
from .models import Accessory, BikeModel, Category , BikeBrand

def home(request):
    categories = Category.objects.all()
    brands = BikeBrand.objects.all()
    models = BikeModel.objects.all()
    return render(request, 'products/home.html', {'categories': categories,'brands':brands,'models':models})



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

    for acc_id, qty in cart.items():
        accessory = get_object_or_404(Accessory, pk=acc_id)

        subtotal = accessory.price * qty
        accessories.append({
            'accessory': accessory,
            'quantity': qty,
            'subtotal': subtotal
        })

        # 🟢 Only this part goes to session
        pay_items.append({
            'id': accessory.id,
            'name': accessory.name,
            'price': float(accessory.price),  # convert Decimal to float
            'quantity': qty,
            'subtotal': float(subtotal),
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
    cart = request.session.get('cart', {})
    cart[str(accessory_id)] = cart.get(str(accessory_id), 0) + 1
    request.session['cart'] = cart
    return redirect('products:cart')

def cart_remove(request, accessory_id):
    cart = request.session.get('cart', {})
    cart.pop(str(accessory_id), None)
    request.session['cart'] = cart
    return redirect('products:cart')

def cart_update(request, accessory_id):
    if request.method == 'POST':
        qty = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        if qty > 0:
            cart[str(accessory_id)] = qty
        else:
            cart.pop(str(accessory_id), None)
        request.session['cart'] = cart
    return redirect('products:cart')



from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Accessory

@require_POST
def ajax_cart_add(request, accessory_id):
    cart = request.session.get('cart', {})
    cart[str(accessory_id)] = cart.get(str(accessory_id), 0) + 1
    request.session['cart'] = cart
    
    # Calculate total items in cart for bubble count
    total_qty = sum(cart.values())
    return JsonResponse({'success': True, 'total_qty': total_qty})


def ajax_cart_count(request):
    cart = request.session.get('cart', {})
    total_qty = sum(cart.values())
    return JsonResponse({'total_qty': total_qty})

def ajax_cart_items(request):
    cart = request.session.get('cart', {})
    items = []
    for acc_id, qty in cart.items():
        accessory = Accessory.objects.filter(pk=acc_id).first()
        if accessory:
            items.append({
                'id': acc_id,
                'name': accessory.name,
                'quantity': qty,
                'price': str(accessory.price),
            })
    return JsonResponse({'items': items})

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
        if response.get('packages'):
            waybill = response['packages'][0]['waybill']
            request.session['cart'] = {}  # Clear cart only after successful order
            return render(request, 'products/order_success.html', {'waybill': waybill})
        else:
            return render(request, 'products/order_fail.html', {'error': response})
    # On GET, show shipping form with cart summary
    cart = request.session.get('cart', {})
    accessories = []
    total = 0
    for acc_id, qty in cart.items():
        accessory = Accessory.objects.filter(pk=acc_id).first()
        if accessory:
            accessories.append({
                'accessory': accessory,
                'quantity': qty,
                'subtotal': accessory.price * qty
            })
            total += accessory.price * qty
    return render(request, 'shipping_form.html', {'cart_items': accessories, 'total': total})

# 🟢 Utility to Create Order via Delhivery API
def create_delhivery_order(data):
    headers = {
        "Authorization": f"Token {settings.DELHIVERY_API_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "pickup_location": {
            "name": "Phantom Moto",
            "city": "Mumbai",
            "state": "Maharashtra",
            "country": "India",
            "phone": "8291056686",
            "address": "Flower Valley Complex CHSL, Shop No 37 H wing, Geeta Omkar, near Lifeline Hospital, Mira Road East, Mira Bhayandar, Maharashtra 401105",
            "pin": "401107"
        },
        "shipments": [
            {
                "waybill": "",
                "order": data['order_id'],
                "products_desc": "Bike Accessories",
                "total_amount": data['amount'],
                "payment_mode": "Prepaid",
                "consignee": data['name'],
                "consignee_address1": data['address'],
                "consignee_address2": "",
                "consignee_city": data['city'],
                "consignee_state": data['state'],
                "consignee_pincode": data['pincode'],
                "consignee_phone": data['phone'],
                "consignee_email": data['email'],
                "weight": 0.5,
                "length": 10,
                "breadth": 10,
                "height": 5,
                "shipping_mode": data['priority']
            }
        ]
    }
    import urllib.parse

    final_payload = {
        "format": "json",
        "data": json.dumps(payload)
    }

    res = requests.post(
        "https://track.delhivery.com/api/cmu/create.json",
        headers=headers,
        data=final_payload  # ✅ send as form data, not json
    )
    return res.json()