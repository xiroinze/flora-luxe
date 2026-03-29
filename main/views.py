from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.conf import settings
from django.contrib.auth.models import User
import urllib.parse
import urllib.request
import secrets
import json
import base64
import time
from django.views.decorators.csrf import csrf_exempt

from .models import Flower, Category, Order, OrderItem, Review, Profile
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .ai_helper import get_ai_response


def home(request):
    flowers = Flower.objects.filter(available=True).select_related('category').order_by('-created_at')[:8]
    return render(request, 'main/home.html', {'flowers': flowers})


def catalog(request):
    flowers = Flower.objects.filter(available=True).select_related('category')
    categories = Category.objects.all()
    search_query = request.GET.get('search', '')
    category_slug = request.GET.get('category', '')

    if search_query:
        flowers = flowers.filter(name__icontains=search_query)
    if category_slug:
        flowers = flowers.filter(category__slug=category_slug)

    return render(request, 'main/catalog.html', {
        'flowers': flowers,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_slug,
    })


def flower_detail(request, pk):
    flower = get_object_or_404(Flower, pk=pk, available=True)
    reviews = Review.objects.filter(flower=flower, is_approved=True).select_related('user')
    related = Flower.objects.filter(category=flower.category, available=True).exclude(pk=pk)[:4]
    return render(request, 'main/flower_detail.html', {
        'flower': flower,
        'reviews': reviews,
        'related_flowers': related,
    })


def about(request):
    return render(request, 'main/about.html')


def contacts(request):
    if request.method == 'POST':
        messages.success(request, 'Сообщение отправлено! Мы свяжемся с вами скоро 🌸')
        return redirect('contacts')
    return render(request, 'main/contacts.html')


def cart(request):
    cart_data = request.session.get('cart', {})
    cart_items = []
    total = 0
    if cart_data:
        flower_ids = [int(fid) for fid in cart_data.keys()]
        flowers_map = {f.pk: f for f in Flower.objects.filter(pk__in=flower_ids).select_related('category')}
        for flower_id, qty in cart_data.items():
            flower = flowers_map.get(int(flower_id))
            if flower:
                item_total = flower.price * qty
                total += item_total
                cart_items.append({'flower': flower, 'quantity': qty, 'total': item_total})
    return render(request, 'main/cart.html', {'cart_items': cart_items, 'total': total})


def add_to_cart(request, pk):
    flower = get_object_or_404(Flower, pk=pk, available=True)
    cart_data = request.session.get('cart', {})
    key = str(pk)
    cart_data[key] = cart_data.get(key, 0) + 1
    request.session['cart'] = cart_data
    request.session.modified = True
    messages.success(request, f'🌸 {flower.name} добавлен в корзину!')
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or '/catalog/'
    return redirect(next_url)


@require_POST
def update_cart(request, pk):
    cart_data = request.session.get('cart', {})
    quantity = request.POST.get('quantity', 1)
    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        quantity = 1
    key = str(pk)
    if quantity > 0:
        cart_data[key] = min(quantity, 99)  # максимум 99 штук
    else:
        cart_data.pop(key, None)
    request.session['cart'] = cart_data
    request.session.modified = True
    return redirect('cart')


def remove_from_cart(request, pk):
    cart_data = request.session.get('cart', {})
    cart_data.pop(str(pk), None)
    request.session['cart'] = cart_data
    request.session.modified = True
    return redirect('cart')


@login_required
def checkout(request):
    cart_data = request.session.get('cart', {})
    if not cart_data:
        messages.warning(request, 'Корзина пуста.')
        return redirect('cart')

    flower_ids = [int(fid) for fid in cart_data.keys()]
    flowers_map = {f.pk: f for f in Flower.objects.filter(pk__in=flower_ids, available=True).select_related('category')}

    # Убираем из корзины товары, которых нет в наличии
    valid_cart = {fid: qty for fid, qty in cart_data.items() if int(fid) in flowers_map}
    if not valid_cart:
        request.session['cart'] = {}
        messages.error(request, 'Товары в корзине больше недоступны.')
        return redirect('catalog')

    if request.method == 'POST':
        address = request.POST.get('address', '').strip()
        phone = request.POST.get('phone', '').strip()
        comment = request.POST.get('comment', '').strip()
        payment_method = request.POST.get('payment_method', 'cash')

        if payment_method not in ('cash', 'card', 'pickup', 'payme', 'click'):
            payment_method = 'cash'

        if not address or not phone:
            messages.error(request, 'Укажите адрес и телефон.')
        else:
            total = 0
            order = Order.objects.create(
                user=request.user, address=address, phone=phone,
                total_price=0, payment_method=payment_method, comment=comment
            )
            items_to_create = []
            for flower_id, qty in valid_cart.items():
                flower = flowers_map.get(int(flower_id))
                if flower:
                    items_to_create.append(OrderItem(order=order, flower=flower, quantity=qty, price=flower.price))
                    total += flower.price * qty
            OrderItem.objects.bulk_create(items_to_create)
            order.total_price = total
            order.save()
            request.session['cart'] = {}
            request.session.modified = True
            return redirect('order_success', receipt_code=order.receipt_code)

    cart_items = []
    total = 0
    for flower_id, qty in valid_cart.items():
        flower = flowers_map.get(int(flower_id))
        if flower:
            item_total = flower.price * qty
            total += item_total
            cart_items.append({'flower': flower, 'quantity': qty, 'total': item_total})

    profile_obj = getattr(request.user, 'profile', None)
    return render(request, 'main/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'profile': profile_obj,
    })


@login_required
def order_success(request, receipt_code):
    order = get_object_or_404(Order, receipt_code=receipt_code)
    if order.user != request.user and not request.user.is_staff:
        raise Http404
    return render(request, 'main/order_success.html', {'order': order})


def check_receipt(request):
    order = None
    code = ''
    error = ''
    if request.method == 'POST' or request.GET.get('code'):
        code = (request.POST.get('code') or request.GET.get('code', '')).strip().upper()
        if code:
            try:
                order = Order.objects.prefetch_related('items__flower').get(receipt_code=code)
            except Order.DoesNotExist:
                error = 'Заказ с таким кодом не найден.'
    return render(request, 'main/check_receipt.html', {'order': order, 'code': code, 'error': error})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = CustomAuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'🌸 Добро пожаловать, {user.username}!')
        next_url = request.GET.get('next', 'home')
        # Защита от open redirect
        if next_url and next_url.startswith('/') and not next_url.startswith('//'):
            return redirect(next_url)
        return redirect('home')
    return render(request, 'main/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, '👋 Вы вышли из аккаунта')
    return redirect('home')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = CustomUserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'🌸 Добро пожаловать, {user.username}! Аккаунт создан.')
        return redirect('home')
    return render(request, 'main/register.html', {'form': form})


@login_required
def profile(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '').strip()[:150]
        user.last_name = request.POST.get('last_name', '').strip()[:150]
        email = request.POST.get('email', '').strip()
        # Проверяем уникальность email (если изменился)
        if email and email != user.email:
            if User.objects.filter(email=email).exclude(pk=user.pk).exists():
                messages.error(request, 'Этот email уже используется.')
                orders = Order.objects.filter(user=request.user).prefetch_related('items__flower').order_by('-created_at')
                return render(request, 'main/profile.html', {'orders': orders, 'profile': profile_obj})
        user.email = email
        user.save()
        profile_obj.phone = request.POST.get('phone', '').strip()[:20]
        profile_obj.address = request.POST.get('address', '').strip()
        if 'avatar' in request.FILES:
            avatar = request.FILES['avatar']
            # Проверяем тип файла
            if avatar.content_type in ('image/jpeg', 'image/png', 'image/webp'):
                profile_obj.avatar = avatar
            else:
                messages.error(request, 'Допустимы только изображения JPG, PNG, WEBP.')
        profile_obj.save()
        messages.success(request, '✅ Профиль обновлён!')
        return redirect('profile')
    orders = Order.objects.filter(user=request.user).prefetch_related('items__flower').order_by('-created_at')
    return render(request, 'main/profile.html', {'orders': orders, 'profile': profile_obj})


@require_POST
def add_review(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'not authenticated'}, status=403)
    flower_id = request.POST.get('flower_id')
    if not flower_id:
        messages.error(request, 'Не указан товар.')
        return redirect('catalog')
    try:
        rating = int(request.POST.get('rating', 5))
        rating = max(1, min(5, rating))
    except (ValueError, TypeError):
        rating = 5
    text = request.POST.get('text', '').strip()
    if not text:
        messages.error(request, 'Текст отзыва не может быть пустым.')
        return redirect('flower_detail', pk=flower_id)
    if len(text) > 2000:
        messages.error(request, 'Отзыв слишком длинный (максимум 2000 символов).')
        return redirect('flower_detail', pk=flower_id)
    flower = get_object_or_404(Flower, pk=flower_id)
    # Один отзыв от пользователя на товар
    if Review.objects.filter(user=request.user, flower=flower).exists():
        messages.warning(request, 'Вы уже оставляли отзыв на этот товар.')
        return redirect('flower_detail', pk=flower_id)
    Review.objects.create(user=request.user, flower=flower, rating=rating, text=text)
    messages.success(request, '💬 Отзыв отправлен на модерацию!')
    return redirect('flower_detail', pk=flower_id)


def reviews_api(request, flower_id):
    reviews = Review.objects.filter(
        flower_id=flower_id, is_approved=True
    ).select_related('user').values('user__username', 'rating', 'text')
    return JsonResponse({'reviews': list(reviews)})


@require_POST
def ai_chat(request):
    try:
        data = json.loads(request.body)
        question = data.get('question', '').strip()
        if not question or len(question) > 1000:
            return JsonResponse({'response': 'Слишком длинный или пустой вопрос 🌸'})
        lang = request.session.get('language', 'ru')
        response = get_ai_response(question, lang)
        return JsonResponse({'response': response})
    except (json.JSONDecodeError, Exception):
        return JsonResponse({'response': 'Извините, произошла ошибка 🌸'})


@require_POST
def change_language(request):
    lang = request.POST.get('language', 'ru')
    if lang in ('ru', 'uz', 'en'):
        request.session['language'] = lang
        request.session.modified = True
    return JsonResponse({'status': 'ok'})


def google_login(request):
    if not getattr(settings, 'GOOGLE_CLIENT_ID', ''):
        messages.error(request, '⚠️ Google OAuth не настроен.')
        return redirect('login')
    state = secrets.token_urlsafe(16)
    request.session['google_oauth_state'] = state
    redirect_uri = request.build_absolute_uri('/auth/google/callback/')
    request.session['google_redirect_uri'] = redirect_uri
    params = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state,
    }
    url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urllib.parse.urlencode(params)
    return redirect(url)


def google_callback(request):
    state_session = request.session.get('google_oauth_state', '')
    state_param = request.GET.get('state', '')
    if not state_session or state_session != state_param:
        messages.error(request, '⚠️ Ошибка безопасности.')
        return redirect('login')
    code = request.GET.get('code')
    if not code:
        messages.error(request, '⚠️ Вход через Google отменён.')
        return redirect('login')
    try:
        redirect_uri = request.session.get('google_redirect_uri', request.build_absolute_uri('/auth/google/callback/'))
        token_data = urllib.parse.urlencode({
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }).encode()
        req = urllib.request.Request(
            'https://oauth2.googleapis.com/token',
            data=token_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            tokens = json.loads(resp.read())
    except Exception as e:
        messages.error(request, f'⚠️ Ошибка токена: {e}')
        return redirect('login')

    access_token = tokens.get('access_token')
    if not access_token:
        messages.error(request, '⚠️ Не удалось получить токен Google.')
        return redirect('login')

    try:
        req2 = urllib.request.Request(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'},
        )
        with urllib.request.urlopen(req2, timeout=10) as resp:
            userinfo = json.loads(resp.read())
    except Exception as e:
        messages.error(request, f'⚠️ Ошибка профиля: {e}')
        return redirect('login')

    email = userinfo.get('email')
    if not email:
        messages.error(request, '⚠️ Google не дал email.')
        return redirect('login')

    # Безопасная генерация уникального username из email
    base_username = email.split('@')[0][:30]
    username = base_username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username[:27]}_{counter}"
        counter += 1

    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'username': username,
            'first_name': userinfo.get('given_name', '')[:150],
            'last_name': userinfo.get('family_name', '')[:150],
        }
    )
    if created:
        user.set_unusable_password()
        user.save()
        Profile.objects.get_or_create(user=user)

    # Очищаем state из сессии
    request.session.pop('google_oauth_state', None)

    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    messages.success(request, f'🌸 Добро пожаловать, {user.first_name or user.username}!')
    return redirect('home')





@user_passes_test(lambda u: u.is_staff)
def admin_block_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if user == request.user:
        messages.error(request, 'Нельзя заблокировать себя')
    elif user.is_superuser:
        messages.error(request, 'Нельзя заблокировать суперпользователя')
    else:
        user.is_active = not user.is_active
        user.save()
        status = 'заблокирован' if not user.is_active else 'разблокирован'
        messages.success(request, f'Пользователь {user.username} {status}')
    return redirect(request.META.get('HTTP_REFERER', '/admin/'))


@user_passes_test(lambda u: u.is_staff)
def admin_delete_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if user == request.user:
        messages.error(request, 'Нельзя удалить себя')
    elif user.is_superuser:
        messages.error(request, 'Нельзя удалить суперпользователя')
    else:
        username = user.username
        user.delete()
        messages.success(request, f'Пользователь {username} удалён')
    return redirect(request.META.get('HTTP_REFERER', '/admin/'))


@login_required
def pay(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status in ('paid', 'delivered', 'cancelled'):
        messages.warning(request, f'Заказ уже имеет статус: {order.get_status_display()}')
        return redirect('order_success', receipt_code=order.receipt_code)

    method = request.GET.get('method')

    if method == 'payme':
        merchant_id = getattr(settings, 'PAYME_MERCHANT_ID', '')
        if not merchant_id or merchant_id == 'YOUR_MERCHANT_ID':
            messages.error(request, '⚠️ Payme не настроен.')
            return redirect('order_success', receipt_code=order.receipt_code)
        payme_params = f"m={merchant_id};ac.order_id={order.id};a={int(order.total_price) * 100}"
        payme_token = base64.b64encode(payme_params.encode()).decode()
        return redirect(f"https://checkout.paycom.uz/{payme_token}")

    if method == 'click':
        service_id = getattr(settings, 'CLICK_SERVICE_ID', '')
        merchant_id = getattr(settings, 'CLICK_MERCHANT_ID', '')
        if not service_id or service_id == 'YOUR_SERVICE_ID':
            messages.error(request, '⚠️ Click не настроен.')
            return redirect('order_success', receipt_code=order.receipt_code)
        click_url = (
            f"https://my.click.uz/services/pay"
            f"?service_id={service_id}"
            f"&merchant_id={merchant_id}"
            f"&amount={order.total_price}"
            f"&transaction_param={order.id}"
        )
        return redirect(click_url)

    # Тестовая оплата (только если DEBUG)
    if settings.DEBUG:
        order.status = 'paid'
        order.save()
        messages.success(request, '✅ Оплата (тест) прошла!')
        return redirect('order_success', receipt_code=order.receipt_code)

    messages.error(request, 'Способ оплаты не выбран.')
    return redirect('order_success', receipt_code=order.receipt_code)


@csrf_exempt
def payme(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, Exception):
        return JsonResponse({"jsonrpc": "2.0", "id": None, "result": None,
                             "error": {"code": -32700, "message": "Parse error"}})

    method = data.get('method')
    params = data.get('params', {})
    request_id = data.get('id')

    def response(result=None, error=None):
        return JsonResponse({"jsonrpc": "2.0", "id": request_id, "result": result, "error": error})

    # Auth check
    auth = request.headers.get('Authorization', '')
    if not auth or not auth.startswith('Basic '):
        return response(error={"code": -32504, "message": "Unauthorized"})
    try:
        key = base64.b64decode(auth.split()[1]).decode()
        expected = f"Paycom:{settings.PAYME_SECRET}"
        if key != expected:
            return response(error={"code": -32504, "message": "Unauthorized"})
    except Exception:
        return response(error={"code": -32504, "message": "Unauthorized"})

    if method == "CheckPerformTransaction":
        order_id = params.get('account', {}).get('order_id')
        try:
            order = Order.objects.get(id=order_id)
            if order.status == 'cancelled':
                return response(error={"code": -31008, "message": "Order cancelled"})
            return response(result={"allow": True})
        except Order.DoesNotExist:
            return response(error={"code": -31050, "message": "Order not found"})

    if method == "CreateTransaction":
        order_id = params.get('account', {}).get('order_id')
        transaction_id = params.get('id')
        try:
            order = Order.objects.get(id=order_id)
            if order.status == 'cancelled':
                return response(error={"code": -31008, "message": "Order cancelled"})
            order.transaction_id = transaction_id
            order.status = 'processing'
            order.save()
            return response(result={"create_time": int(time.time() * 1000), "transaction": transaction_id, "state": 1})
        except Order.DoesNotExist:
            return response(error={"code": -31050, "message": "Order not found"})

    if method == "PerformTransaction":
        transaction_id = params.get('id')
        try:
            order = Order.objects.get(transaction_id=transaction_id)
            order.status = 'paid'
            order.save()
            return response(result={"transaction": transaction_id, "perform_time": int(time.time() * 1000), "state": 2})
        except Order.DoesNotExist:
            return response(error={"code": -31051, "message": "Transaction not found"})

    if method == "CheckTransaction":
        transaction_id = params.get('id')
        try:
            order = Order.objects.get(transaction_id=transaction_id)
            state = 2 if order.status == 'paid' else 1
            return response(result={"transaction": transaction_id, "state": state})
        except Order.DoesNotExist:
            return response(error={"code": -31051, "message": "Transaction not found"})

    if method == "CancelTransaction":
        transaction_id = params.get('id')
        try:
            order = Order.objects.get(transaction_id=transaction_id)
            if order.status != 'paid':
                order.status = 'cancelled'
                order.save()
            return response(result={"transaction": transaction_id, "cancel_time": int(time.time() * 1000), "state": -1})
        except Order.DoesNotExist:
            return response(error={"code": -31051, "message": "Transaction not found"})

    return response(error={"code": -32601, "message": "Method not found"})
