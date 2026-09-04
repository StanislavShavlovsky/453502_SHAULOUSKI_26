import base64
import calendar
import datetime
import io
import logging
import statistics
import zoneinfo
from collections import Counter

import matplotlib
import numpy as np
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.core.exceptions import ValidationError
from django.db.models import Avg, Count, Sum, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import PropertyForm, ReviewForm, UserLoginForm, UserRegistrationForm, ArticleForm
from .models import (
    Article,
    ClientProfile,
    CompanyInfo,
    Deal,
    EmployeeProfile,
    FAQ,
    Partner,
    PromoCode,
    Property,
    PropertyType,
    Review,
    Vacancy,
)

matplotlib.use('Agg')
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)


def get_usd_rate():
    try:
        response = requests.get('https://developer.nbrb.by/api/exrates/rates/145', timeout=3)
        if response.status_code == 200:
            data = response.json()
            return float(data['Cur_OfficialRate'])
    except Exception as e:
        logger.warning("Failed to fetch alternative USD rate: %s", e)
    return 3.00


# =========================================================================
# GENERAL VIEWS
# =========================================================================

def home_view(request):
    """
    Главная страница:
    - Баннеры рекламы (список путей к изображениям)
    - Каталог объектов/услуг из БД
    - Последняя опубликованная статья из БД
    - Список компаний-партнёров с логотипами и ссылками
    """
    latest_article = Article.objects.order_by('-published_date').first()
    properties = Property.objects.filter(is_active=True)[:6]
    partners = Partner.objects.all()

    # Рекламные баннеры (статические изображения)
    banners = [
        'images/banner1.jpg',
        'images/banner2.jpg',
        'images/banner3.jpg',
    ]

    context = {
        'properties': properties,
        'latest_article': latest_article,
        'partners': partners,
        'banners': banners,
        'company_info': CompanyInfo.objects.first(),
    }
    return render(request, 'agency/home.html', context)


def about_view(request):
    company_sections = CompanyInfo.objects.all()
    return render(request, 'agency/about.html', {'company_sections': company_sections})


def contacts_view(request):
    employees = EmployeeProfile.objects.all().select_related('user')
    return render(request, 'agency/contacts.html', {'employees': employees})


def privacy_view(request):
    return render(request, 'agency/privacy.html')


def glossary_view(request):
    faqs = FAQ.objects.all().order_by('-id')
    return render(request, 'agency/glossary.html', {'faqs': faqs})


def faq_view(request):
    faq_items = FAQ.objects.all()
    return render(request, 'agency/glossary.html', {'faq_items': faq_items})


def vacancies_view(request):
    vacancies = Vacancy.objects.all()
    return render(request, 'agency/vacancies.html', {'vacancies': vacancies})


def promocodes_view(request):
    today = timezone.now().date()
    active = PromoCode.objects.filter(valid_until__gte=today)
    archived = PromoCode.objects.filter(valid_until__lt=today)

    return render(request, 'agency/promocodes.html', {
        'active': active,
        'archived': archived
    })


# =========================================================================
# REAL ESTATE CATALOG, DETAIL PAGE & CART MANAGEMENT
# =========================================================================

def property_list_view(request):
    search_query = request.GET.get('search', '').strip()
    type_query = request.GET.get('type', '')
    deal_type_query = request.GET.get('deal_type', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    sort_query = request.GET.get('sort', 'title')

    properties = Property.objects.filter(is_active=True)

    if search_query:
        properties = properties.filter(Q(title__icontains=search_query) | Q(address__icontains=search_query))
    if type_query:
        properties = properties.filter(prop_type_id=type_query)
    if deal_type_query:
        properties = properties.filter(deal_type=deal_type_query)
    if price_min:
        try:
            properties = properties.filter(price__gte=price_min)
        except (ValueError, TypeError):
            pass
    if price_max:
        try:
            properties = properties.filter(price__lte=price_max)
        except (ValueError, TypeError):
            pass

    if sort_query in ['title', 'price', '-price']:
        properties = properties.order_by(sort_query)

    types = PropertyType.objects.all()
    managers = EmployeeProfile.objects.select_related('user').all()

    context = {
        'properties': properties,
        'types': types,
        'managers': managers,
    }
    return render(request, 'agency/property_list.html', context)


def property_detail_view(request, pk):
    """
    Страница отдельного объекта (карточка товара/услуги).
    """
    property_obj = get_object_or_404(Property, pk=pk)
    rate = get_usd_rate()
    price_byn = float(property_obj.price or 0) * rate
    managers = EmployeeProfile.objects.select_related('user').all()

    context = {
        'property': property_obj,
        'price_byn': f"{price_byn:,.2f}".replace(",", " "),
        'managers': managers,
    }
    return render(request, 'agency/property_detail.html', context)


# =========================================================================
# CART & CHECKOUT VIEWS (Корзина и Оплата)
# =========================================================================

def cart_view(request):
    """
    Страница корзины заказов.
    """
    cart = request.session.get('cart', {})
    properties = Property.objects.filter(id__in=cart.keys())

    cart_items = []
    total_usd = 0

    for prop in properties:
        item_qty = cart.get(str(prop.id), 1)
        subtotal = float(prop.price) * item_qty
        total_usd += subtotal
        cart_items.append({
            'property': prop,
            'quantity': item_qty,
            'subtotal': subtotal
        })

    rate = get_usd_rate()
    total_byn = total_usd * rate

    context = {
        'cart_items': cart_items,
        'total_usd': total_usd,
        'total_byn': f"{total_byn:,.2f}".replace(",", " "),
        'managers': EmployeeProfile.objects.select_related('user').all(),
    }
    return render(request, 'agency/cart.html', context)


def cart_add_view(request, property_id):
    """
    Добавление объекта в сессионную корзину.
    """
    property_obj = get_object_or_404(Property, id=property_id)
    cart = request.session.get('cart', {})

    str_id = str(property_id)
    if str_id in cart:
        cart[str_id] += 1
    else:
        cart[str_id] = 1

    request.session['cart'] = cart
    messages.success(request, f'Объект «{property_obj.title}» успешно добавлен в корзину.')
    return redirect('cart_detail')


def cart_remove_view(request, property_id):
    """
    Удаление объекта или уменьшение количества в корзине.
    """
    cart = request.session.get('cart', {})
    str_id = str(property_id)

    action = request.GET.get('action', 'delete')

    if str_id in cart:
        if action == 'decrease' and cart[str_id] > 1:
            cart[str_id] -= 1
        else:
            del cart[str_id]

        request.session['cart'] = cart
        messages.info(request, 'Корзина обновлена.')

    return redirect('cart_detail')


@login_required
def checkout_view(request):
    """
    Страница оплаты / оформления сделок из корзины.
    """
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, 'Ваша корзина пуста.')
            return redirect('property_list')

        employee_id = request.POST.get('employee_id')
        if not employee_id:
            messages.error(request, 'Пожалуйста, выберите персонального менеджера.')
            return redirect('cart_detail')

        employee = get_object_or_404(EmployeeProfile, id=employee_id)

        try:
            client_profile = request.user.clientprofile
        except ClientProfile.DoesNotExist:
            messages.error(request, 'Профиль клиента не найден.')
            return redirect('cart_detail')

        created_count = 0
        for prop_id_str, qty in cart.items():
            prop = Property.objects.filter(id=int(prop_id_str), is_active=True).first()
            if prop:
                Deal.objects.create(
                    property=prop,
                    client=client_profile,
                    employee=employee,
                    final_price=prop.price,
                    deal_type=prop.deal_type
                )
                prop.is_active = False
                prop.save()
                created_count += 1

        request.session['cart'] = {}
        messages.success(request,
                         f'Оплата прошла успешно! Оформлено сделок: {created_count}. Менеджер свяжется с вами.')
        return redirect('dashboard')

    return redirect('cart_detail')


@login_required
@permission_required('agency.add_property', raise_exception=True)
def property_create_view(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Объект успешно добавлен в каталог!")
            return redirect('property_list')
    else:
        form = PropertyForm()
    return render(request, 'agency/property_form.html', {'form': form, 'action': 'Добавить'})


@login_required
@permission_required('agency.change_property', raise_exception=True)
def property_update_view(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Данные объекта успешно обновлены!")
            return redirect('property_list')
    else:
        form = PropertyForm(instance=property_obj)
    return render(request, 'agency/property_form.html', {'form': form, 'action': 'Редактировать'})


@login_required
@permission_required('agency.delete_property', raise_exception=True)
def property_delete_view(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        property_obj.delete()
        messages.success(request, "Объект недвижимости успешно удален.")
        return redirect('property_list')
    return render(request, 'agency/property_confirm_delete.html', {'property': property_obj})


# =========================================================================
# NEWSFEED CHANNELS & ARTICLES
# =========================================================================

def news_view(request):
    articles = Article.objects.all().order_by('-published_date')
    return render(request, 'agency/news.html', {'articles': articles})


def article_detail_view(request, pk):
    article = get_object_or_404(Article, pk=pk)
    return render(request, 'agency/article_detail.html', {'article': article})


@login_required
@permission_required('agency.add_article', raise_exception=True)
def article_create_view(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Новость успешно опубликована!")
            return redirect('news')
    else:
        form = ArticleForm()
    return render(request, 'agency/article_form.html', {'form': form, 'action': 'Добавить'})


@login_required
@permission_required('agency.change_article', raise_exception=True)
def article_update_view(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, "Новость успешно обновлена!")
            return redirect('news')
    else:
        form = ArticleForm(instance=article)
    return render(request, 'agency/article_form.html', {'form': form, 'action': 'Редактировать', 'article': article})


@login_required
@permission_required('agency.delete_article', raise_exception=True)
def article_delete_view(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        article.delete()
        messages.success(request, "Новость успешно удалена.")
        return redirect('news')
    return render(request, 'agency/article_confirm_delete.html', {'article': article})


# =========================================================================
# REVIEWS & AUTHENTICATION
# =========================================================================

@login_required
def reviews_view(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            messages.success(request, "Спасибо! Ваш отзыв опубликован.")
            return redirect('reviews')
    else:
        form = ReviewForm()

    reviews = Review.objects.all().order_by('-created_at')
    return render(request, 'agency/reviews.html', {'form': form, 'reviews': reviews})


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация завершена успешно!")
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'agency/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = UserLoginForm()
    return render(request, 'agency/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


# =========================================================================
# DASHBOARD LOGIC
# =========================================================================

@login_required
def dashboard_view(request):
    user_tz_name = 'Europe/Minsk'
    if hasattr(request.user, 'clientprofile'):
        user_tz_name = getattr(request.user.clientprofile, 'timezone', 'Europe/Minsk') or 'Europe/Minsk'
    elif hasattr(request.user, 'employeeprofile'):
        user_tz_name = getattr(request.user.employeeprofile, 'timezone', 'Europe/Minsk') or 'Europe/Minsk'

    user_tz = zoneinfo.ZoneInfo(user_tz_name)
    current_utc = timezone.now()
    current_local = current_utc.astimezone(user_tz)

    rate = get_usd_rate()
    text_calendar = calendar.TextCalendar(firstweekday=0).formatmonth(current_local.year, current_local.month)

    if hasattr(request.user, 'employeeprofile'):
        employee_profile = request.user.employeeprofile
        deals_queryset = Deal.objects.filter(employee=employee_profile).select_related(
            'property__prop_type', 'client__user'
        ).order_by('-created_at_utc')

        clients_queryset = ClientProfile.objects.select_related('user').filter(
            id__in=deals_queryset.values_list('client_id', flat=True))
        stats_data = deals_queryset.aggregate(total_usd=Sum('final_price'), avg_usd=Avg('final_price'))

        for deal in deals_queryset:
            deal.amount = f"{float(deal.final_price or 0) * rate:,.0f}".replace(",", " ")
            deal.created_at_local = deal.created_at_utc.astimezone(user_tz)

        return render(request, 'agency/dashboard_employee.html', {
            'deals': deals_queryset,
            'clients': clients_queryset,
            'text_calendar': text_calendar,
        })
    else:
        try:
            client_profile = ClientProfile.objects.prefetch_related('promo_codes').get(user=request.user)
            promo_codes = client_profile.promo_codes.all()
        except ClientProfile.DoesNotExist:
            client_profile, promo_codes = None, []

        purchases_queryset = Deal.objects.filter(client__user=request.user).select_related('property').order_by(
            '-created_at_utc')

        for purchase in purchases_queryset:
            purchase.amount_byn = f"{float(purchase.final_price or 0) * rate:,.0f}".replace(",", " ")
            purchase.created_at_local = purchase.created_at_utc.astimezone(user_tz)

        return render(request, 'agency/dashboard_client.html', {
            'profile': client_profile,
            'promo_codes': promo_codes,
            'purchases': purchases_queryset,
            'text_calendar': text_calendar,
        })


# =========================================================================
# STATS & API
# =========================================================================

def statistics_view(request):
    return render(request, 'agency/statistics.html')


def secured_agency_stats_api(request):
    return JsonResponse({'status': 'success'})


@login_required
@require_POST
def create_deal_ajax(request, property_id):
    next_url = request.META.get('HTTP_REFERER', 'property_list')

    if request.user.is_superuser or hasattr(request.user, 'employeeprofile'):
        messages.error(request, 'Сотрудники не могут оформлять покупки.')
        return redirect(next_url)

    try:
        client_profile = request.user.clientprofile
    except ClientProfile.DoesNotExist:
        messages.error(request, 'Профиль клиента не найден.')
        return redirect(next_url)

    employee_id = request.POST.get('employee_id')
    employee = get_object_or_404(EmployeeProfile, id=employee_id)
    property_obj = get_object_or_404(Property, id=property_id, is_active=True)

    Deal.objects.create(
        property=property_obj,
        client=client_profile,
        employee=employee,
        final_price=property_obj.price,
        deal_type=property_obj.deal_type
    )
    property_obj.is_active = False
    property_obj.save()

    messages.success(request, f'Заявка на "{property_obj.title}" создана!')
    return redirect('dashboard')