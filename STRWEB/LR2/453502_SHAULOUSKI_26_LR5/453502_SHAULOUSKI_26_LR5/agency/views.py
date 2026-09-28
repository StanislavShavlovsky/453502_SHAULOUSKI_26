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
    Banner
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
    - Баннеры из БД (активные)
    - Каталог объектов
    - Последняя статья
    - Партнёры
    """
    latest_article = Article.objects.order_by('-published_date').first()
    properties = Property.objects.filter(is_active=True)[:6]
    partners = Partner.objects.all()
    banners = Banner.objects.filter(is_active=True)

    context = {
        'properties': properties,
        'latest_article': latest_article,
        'partners': partners,
        'banners': banners,
        'company_info': CompanyInfo.objects.first(),
    }
    return render(request, 'agency/home.html', context)


def about_view(request):
    """Страница о компании с историей, видео, сертификатом и реквизитами."""
    company_info = CompanyInfo.objects.first()

    # История по годам — если она хранится как список в тексте, парсим
    history_list = []
    if company_info and company_info.history_by_years:
        for line in company_info.history_by_years.splitlines():
            line = line.strip()
            if not line:
                continue
            # Ожидаем формат: "2005 — Открытие компании"
            if '—' in line:
                year, event = line.split('—', 1)
                history_list.append({
                    'year': year.strip(),
                    'event': event.strip(),
                })
            elif '-' in line:
                year, event = line.split('-', 1)
                history_list.append({
                    'year': year.strip(),
                    'event': event.strip(),
                })

    return render(request, 'agency/about.html', {
        'company_info': company_info,
        'history_list': history_list,
    })


def contacts_view(request):
    employees = EmployeeProfile.objects.all().select_related('user')
    return render(request, 'agency/contacts.html', {'employees': employees})


def privacy_view(request):
    return render(request, 'agency/privacy.html')


def glossary_view(request):
    faqs = FAQ.objects.all().order_by('-id')
    return render(request, 'agency/glossary.html', {'faqs': faqs})


def faq_view(request):
    faqs = FAQ.objects.all()
    return render(request, 'agency/glossary.html', {'faqs': faqs})


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
    cart = request.session.get('cart', {})
    properties = Property.objects.filter(id__in=cart.keys())

    cart_items = []
    total_usd = 0
    for prop in properties:
        qty = cart.get(str(prop.id), 1)
        subtotal = float(prop.price) * qty
        total_usd += subtotal
        cart_items.append({
            'property': prop,
            'quantity': qty,
            'subtotal': subtotal,
        })

    rate = get_usd_rate()
    total_byn = total_usd * rate

    return render(request, 'agency/cart.html', {
        'cart_items': cart_items,
        'total_usd': total_usd,
        'total_byn': f"{total_byn:,.2f}".replace(",", " "),
    })

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
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Ваша корзина пуста.')
        return redirect('property_list')

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        if not employee_id:
            messages.error(request, 'Пожалуйста, выберите персонального менеджера.')
            return redirect('checkout')

        client_profile, _ = ClientProfile.objects.get_or_create(
            user=request.user,
            defaults={'phone': ''}
        )
        employee = get_object_or_404(EmployeeProfile, id=employee_id)

        created_count = 0
        for prop_id_str, qty in cart.items():
            prop = Property.objects.filter(id=int(prop_id_str), is_active=True).first()
            if prop:
                for _ in range(qty):
                    Deal.objects.create(
                        property=prop,
                        client=client_profile,
                        employee=employee,
                        final_price=prop.price,
                        deal_type=prop.deal_type
                    )
                    created_count += 1
                prop.is_active = False
                prop.save()

        request.session['cart'] = {}
        request.session.modified = True

        messages.success(request, f'Оплата прошла успешно! Оформлено сделок: {created_count}.')
        return redirect('dashboard')

    # GET
    properties = Property.objects.filter(id__in=cart.keys())
    cart_items = []
    total_usd = 0
    for prop in properties:
        qty = cart.get(str(prop.id), 1)
        subtotal = float(prop.price) * qty
        total_usd += subtotal
        cart_items.append({
            'property': prop,
            'quantity': qty,
            'subtotal': subtotal,
        })

    rate = get_usd_rate()
    total_byn = total_usd * rate

    return render(request, 'agency/checkout.html', {
        'cart_items': cart_items,
        'total_usd': total_usd,
        'total_byn': f"{total_byn:,.2f}".replace(",", " "),
        'managers': EmployeeProfile.objects.select_related('user').all(),
    })


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

def reviews_view(request):
    """Страница отзывов. Доступна всем, но оставлять могут только авторизованные клиенты."""
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Необходимо войти в систему для отправки отзыва.")
            return redirect('login')

        # Запрет для сотрудников и админов
        if request.user.is_superuser or hasattr(request.user, 'employeeprofile'):
            messages.error(request, "Сотрудники и администраторы не могут оставлять отзывы.")
            return redirect('reviews')

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
    properties = Property.objects.filter(is_active=True)

    return render(request, 'agency/reviews.html', {
        'form': form,
        'reviews': reviews,
        'properties': properties,
    })


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            # ← ГЛАВНОЕ: создаём профиль клиента
            ClientProfile.objects.create(
                user=user,
                phone=form.cleaned_data.get('phone', '') or '',
            )

            login(request, user)
            messages.success(request, "Регистрация завершена успешно!")
            return redirect('home')
        else:
            print("FORM ERRORS:", form.errors)
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
    """Личный кабинет клиента или панель сотрудника с учётом таймзоны."""
    import statistics
    from collections import Counter

    # Определяем таймзону пользователя
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

    # ===================== СОТРУДНИК =====================
    if hasattr(request.user, 'employeeprofile'):
        employee_profile = request.user.employeeprofile
        deals_queryset = Deal.objects.filter(employee=employee_profile).select_related(
            'property__prop_type', 'client__user'
        ).order_by('-created_at_utc')

        clients_queryset = ClientProfile.objects.select_related('user').filter(
            id__in=deals_queryset.values_list('client_id', flat=True))

        # Метрики по сделкам
        deals_list = list(deals_queryset)
        amounts = [float(d.final_price or 0) * rate for d in deals_list]

        total_sales = sum(amounts)
        avg_sales = round(statistics.mean(amounts), 2) if amounts else 0
        median_sales = round(statistics.median(amounts), 2) if amounts else 0
        mode_sales = Counter(amounts).most_common(1)[0][0] if amounts else 0

        # Количество сделок по типам
        sale_count = sum(1 for d in deals_list if d.deal_type == 'sale')
        rent_count = sum(1 for d in deals_list if d.deal_type == 'rent')

        # Популярный тип недвижимости
        types_counter = Counter(d.property.prop_type.name for d in deals_list)
        popular_type = types_counter.most_common(1)[0][0] if types_counter else '—'

        # График популярности типов недвижимости
        chart_data = ""
        if types_counter:
            plt.figure(figsize=(8, 5))
            plt.bar(list(types_counter.keys()), list(types_counter.values()), color='#17a2b8')
            plt.title('Популярность типов недвижимости')
            plt.ylabel('Количество сделок')
            plt.xticks(rotation=30, ha='right')
            plt.tight_layout()

            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight')
            buffer.seek(0)
            chart_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close()

        # Локальное время для каждой сделки
        for deal in deals_queryset:
            deal.amount = f"{float(deal.final_price or 0) * rate:,.0f}".replace(",", " ")
            deal.created_at_local = deal.created_at_utc.astimezone(user_tz)

        return render(request, 'agency/dashboard_employee.html', {
            'deals': deals_queryset,
            'clients': clients_queryset,
            'text_calendar': text_calendar,
            'tz_name': user_tz_name,

            'total_sales': f"{total_sales:,.0f}".replace(",", " "),
            'avg_sales': avg_sales,
            'median_sales': median_sales,
            'mode_sales': mode_sales,
            'avg_age': sale_count,
            'median_age': rent_count,
            'popular_type': popular_type,
            'chart_data': chart_data,
        })

    # ===================== КЛИЕНТ =====================
    else:
        try:
            client_profile = ClientProfile.objects.prefetch_related('promo_codes').get(user=request.user)
            promo_codes = client_profile.promo_codes.all()
        except ClientProfile.DoesNotExist:
            client_profile, promo_codes = None, []

        purchases_queryset = Deal.objects.filter(client__user=request.user).select_related(
            'property'
        ).order_by('-created_at_utc')

        for purchase in purchases_queryset:
            purchase.amount_byn = f"{float(purchase.final_price or 0) * rate:,.0f}".replace(",", " ")
            purchase.created_at_local = purchase.created_at_utc.astimezone(user_tz)

        return render(request, 'agency/dashboard_client.html', {
            'profile': client_profile,
            'promo_codes': promo_codes,
            'purchases': purchases_queryset,
            'text_calendar': text_calendar,
            'tz_name': user_tz_name,
            'current_local_iso': current_local.isoformat(),
        })


# =========================================================================
# STATS & API
# =========================================================================

def statistics_view(request):
    """Страница аналитики с графиками и метриками."""
    import statistics as st
    from collections import Counter

    rate = get_usd_rate()

    properties = Property.objects.filter(is_active=True)
    total_properties = properties.count()

    # Цены в USD
    prices = [float(p.price or 0) for p in properties]

    avg_price = round(st.mean(prices), 2) if prices else 0
    median_price = round(st.median(prices), 2) if prices else 0

    # Распределение по типам
    type_counter = Counter(p.prop_type.name for p in properties)

    # Самая дорогая и самая популярная категории
    most_expensive_type = None
    most_popular_type = None

    if type_counter:
        most_popular_type = type_counter.most_common(1)[0][0]

    type_avg_price = {}
    for p in properties:
        type_avg_price.setdefault(p.prop_type.name, []).append(float(p.price or 0))

    if type_avg_price:
        most_expensive_type = max(
            type_avg_price.items(),
            key=lambda kv: sum(kv[1]) / len(kv[1])
        )[0]

    # ============ ГРАФИКИ ============

    chart_pie = ""
    chart_bar = ""
    chart_line = ""

    # 1. Круговая диаграмма — доли типов
    if type_counter:
        plt.figure(figsize=(7, 7))
        plt.pie(
            list(type_counter.values()),
            labels=list(type_counter.keys()),
            autopct='%1.1f%%',
            startangle=90,
        )
        plt.title('Доли типов недвижимости в каталоге')
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight')
        buffer.seek(0)
        chart_pie = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

    # 2. Столбчатая диаграмма — средние цены по типам
    if type_avg_price:
        type_names = list(type_avg_price.keys())
        avg_prices = [sum(v) / len(v) for v in type_avg_price.values()]

        plt.figure(figsize=(9, 5))
        plt.bar(type_names, avg_prices, color='#227c9d')
        plt.title('Средние цены по типам недвижимости (USD)')
        plt.ylabel('Цена ($)')
        plt.xticks(rotation=30, ha='right')
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight')
        buffer.seek(0)
        chart_bar = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

    # 3. Линейный график — тренд (например, цены по объектам)
    if prices:
        sorted_prices = sorted(prices)

        plt.figure(figsize=(10, 5))
        plt.plot(range(1, len(sorted_prices) + 1), sorted_prices,
                 color='#1890ff', linewidth=2.5, marker='o',
                 markersize=6, markerfacecolor='#ff6b6b')
        plt.title('Рыночный тренд стоимости объектов (USD)')
        plt.xlabel('Порядковый номер объекта (от дешёвого к дорогому)')
        plt.ylabel('Цена ($)')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight')
        buffer.seek(0)
        chart_line = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

    context = {
        'usd_rate': rate,
        'total_properties': total_properties,
        'avg_price': avg_price,
        'median_price': median_price,
        'most_expensive_type': most_expensive_type,
        'most_popular_type': most_popular_type,
        'chart_pie': chart_pie,
        'chart_bar': chart_bar,
        'chart_line': chart_line,
    }

    return render(request, 'agency/statistics.html', context)


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


def demo_view(request):
    """Демонстрационная страница всех HTML-элементов из лекций."""
    return render(request, 'agency/demo.html')