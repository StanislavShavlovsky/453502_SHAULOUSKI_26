import base64
import calendar
import datetime
import io
import logging
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
from .models import Article, ClientProfile, CompanyInfo, Deal, EmployeeProfile, FAQ, PromoCode, Property, Review, \
    Vacancy, PropertyType

# Configure matplotlib to use a non-GUI backend for stability in multi-threaded environments
matplotlib.use('Agg')
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


def superuser_required(view_func):
    """
    Decorator to restrict view access only to superusers.
    """
    return user_passes_test(lambda u: u.is_superuser)(view_func)


def get_usd_rate():
    """
    Fetches the current USD/BYN official exchange rate from the NBRB API.
    Returns a fallback value of 3.00 if the API is unavailable.
    """
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
    Renders the main landing page with active properties, latest news, and local metadata.
    """
    properties = Property.objects.filter(is_active=True)[:6]
    latest_article = Article.objects.all().order_by('-published_date').first()
    current_local = timezone.now()
    tz_name = getattr(settings, 'TIME_ZONE', 'Europe/Minsk')

    now = datetime.datetime.now()
    cal = calendar.TextCalendar(calendar.MONDAY)
    text_calendar = cal.formatmonth(now.year, now.month)

    context = {
        'properties': properties,
        'latest_article': latest_article,
        'tz_name': tz_name,
        'current_local_iso': current_local.isoformat(),
        'text_calendar': text_calendar,
    }
    return render(request, 'agency/home.html', context)


def about_view(request):
    """
    Renders the company background and dynamic descriptive sections.
    """
    company_sections = CompanyInfo.objects.all()
    return render(request, 'agency/about.html', {'company_sections': company_sections})


def contacts_view(request):
    """
    Displays the list of agency employees with their structural profiles.
    """
    employees = EmployeeProfile.objects.all().select_related('user')
    return render(request, 'agency/contacts.html', {'employees': employees})


def privacy_view(request):
    """
    Renders the privacy policy page.
    """
    return render(request, 'agency/privacy.html')


def glossary_view(request):
    """
    Renders the glossary/FAQ interface ordered descending by identifiers.
    """
    faqs = FAQ.objects.all().order_by('-id')
    return render(request, 'agency/glossary.html', {'faqs': faqs})


def faq_view(request):
    """
    An alternative routing target for fetching FAQ items.
    """
    faq_items = FAQ.objects.all()
    return render(request, 'agency/glossary.html', {'faq_items': faq_items})


def vacancies_view(request):
    """
    Displays currently open job vacancies.
    """
    vacancies = Vacancy.objects.all()
    return render(request, 'agency/vacancies.html', {'vacancies': vacancies})


def promocodes_view(request):
    """
    Displays promo codes categorized by active or archived status based on current date.
    """
    today = timezone.now().date()
    active = PromoCode.objects.filter(valid_until__gte=today)
    archived = PromoCode.objects.filter(valid_until__lt=today)

    return render(request, 'agency/promocodes.html', {
        'active': active,
        'archived': archived
    })


# =========================================================================
# REAL ESTATE CATALOG & MANAGEMENT
# =========================================================================

def property_list_view(request):
    """
    Handles listing, filtering, sorting, and external data injection for properties.
    """
    # 1. Сбор всех параметров фильтрации и сортировки из GET-запроса
    search_query = request.GET.get('search', '').strip()
    type_query = request.GET.get('type', '')
    deal_type_query = request.GET.get('deal_type', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    sort_query = request.GET.get('sort', 'title')

    logger.info(
        "Catalog requested. Params: search='%s', type='%s', deal_type='%s', price_min='%s', price_max='%s', sort='%s'",
        search_query, type_query, deal_type_query, price_min, price_max, sort_query
    )

    # Инициализируем базовый QuerySet (выбираем только доступные объекты)
    properties = Property.objects.filter(is_active=True)

    # 2. Применение фильтров на основе переданных данных

    # Поиск по ключевым словам (ищет в названии или в адресе объекта)
    if search_query:
        properties = properties.filter(
            Q(title__icontains=search_query) | Q(address__icontains=search_query)
        )

    # Фильтрация по виду недвижимости (Квартира, Офис, Таунхаус...)
    if type_query:
        properties = properties.filter(prop_type_id=type_query)

    # Фильтрация по типу сделки (Продажа / Аренда)
    if deal_type_query:
        properties = properties.filter(deal_type=deal_type_query)

    # Фильтрация по минимальной цене ($)
    if price_min:
        try:
            properties = properties.filter(price__gte=price_min)
        except (ValueError, TypeError):
            logger.warning("Invalid price_min value received: '%s'", price_min)

    # Фильтрация по максимальной цене ($)
    if price_max:
        try:
            properties = properties.filter(price__lte=price_max)
        except (ValueError, TypeError):
            logger.warning("Invalid price_max value received: '%s'", price_max)

    # 3. Применение сортировки
    if sort_query in ['title', 'price', '-price']:
        properties = properties.order_by(sort_query)
    else:
        logger.warning("Unsupported sorting parameter provided: '%s'", sort_query)
        # Фолбэк на дефолтную сортировку по алфавиту, если передано что-то странное
        properties = properties.order_by('title')

    # Безопасное получение списка PropertyType для выпадающего списка
    try:
        types = PropertyType.objects.all()
    except Exception as e:
        logger.error("Error fetching PropertyType; switching to inline fallback: %s", e)
        types = list(set([p.prop_type for p in Property.objects.all() if p.prop_type]))

    # Внешняя интеграция: Курс USD от НБРБ
    usd_rate = "Data unavailable"
    fact_of_the_day = "A wonderful day to purchase real estate!"
    rate = 3.25

    try:
        res = requests.get('https://api.nbrb.by/exrates/rates/USD?parammode=2', timeout=3)
        if res.status_code == 200:
            data = res.json()
            rate_val = data.get('Cur_OfficialRate')
            if rate_val:
                rate = float(rate_val)
                usd_rate = f"{rate:.4f} BYN"
            else:
                logger.warning("NBRB response lacks 'Cur_OfficialRate' key.")
        else:
            logger.warning("NBRB endpoint returned status code: %d", res.status_code)
    except Exception as e:
        logger.exception("Error occurred while contacting NBRB API: %s", e)
        usd_rate = "NBRB Server temporarily unavailable"

    # Внешняя интеграция: Бесполезный факт дня с автопереводом
    try:
        res = requests.get('https://uselessfacts.jsph.pl/api/v2/facts/today', timeout=2)
        if res.status_code == 200:
            fact_en = res.json().get('text', '')
            trans = requests.get(f"https://api.mymemory.translated.net/get?q={fact_en}&langpair=en|ru", timeout=2)
            if trans.status_code == 200:
                fact_of_the_day = trans.json().get('responseData', {}).get('translatedText', fact_en)
            else:
                fact_of_the_day = fact_en
    except Exception as e:
        logger.warning("Could not retrieve fact of the day: %s", e)

    # Получение списка менеджеров для модальных окон бронирования
    managers = EmployeeProfile.objects.select_related('user').all()

    # Формирование контекста для передачи в шаблон
    context = {
        'properties': properties,
        'types': types,
        'fact_of_the_day': fact_of_the_day,
        'usd_rate': usd_rate,
        'raw_usd_rate': rate,
        'managers': managers,
    }
    return render(request, 'agency/property_list.html', context)

@login_required
@permission_required('agency.add_property', raise_exception=True)
def property_create_view(request):
    """
    CRUD: Create an object entry in the property catalog.
    """
    logger.info("User %s opened the property creation page.", request.user.username)

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            new_property = form.save()
            logger.info("User %s created property '%s' (ID: %d)", request.user.username, new_property.title, new_property.id)
            messages.success(request, "Объект успешно добавлен в каталог!")
            return redirect('property_list')
        else:
            logger.warning("Form validation failed for property creation by %s", request.user.username)
    else:
        form = PropertyForm()

    return render(request, 'agency/property_form.html', {'form': form, 'action': 'Добавить'})


@login_required
@permission_required('agency.change_property', raise_exception=True)
def property_update_view(request, pk):
    """
    CRUD: Update historical metrics or descriptive parameters of a specific property.
    """
    property_obj = get_object_or_404(Property, pk=pk)
    logger.info("User %s requested edit view for property ID: %d", request.user.username, pk)

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        if form.is_valid():
            form.save()
            logger.info("User %s successfully updated property ID: %d", request.user.username, pk)
            messages.success(request, "Данные объекта успешно обновлены!")
            return redirect('property_list')
        else:
            logger.warning("Validation failure on property update for ID: %d by user %s", pk, request.user.username)
    else:
        form = PropertyForm(instance=property_obj)

    return render(request, 'agency/property_form.html', {'form': form, 'action': 'Редактировать'})


@login_required
@permission_required('agency.delete_property', raise_exception=True)
def property_delete_view(request, pk):
    """
    CRUD: Delete an asset listing from the catalog schema.
    """
    property_obj = get_object_or_404(Property, pk=pk)
    logger.info("User %s accessed deletion request for property ID: %d (%s)", request.user.username, pk, property_obj.title)

    if request.method == 'POST':
        title_for_log = property_obj.title
        property_obj.delete()
        logger.info("User %s purged property record '%s' (ID: %d)", request.user.username, title_for_log, pk)
        messages.success(request, "Объект недвижимости успешно удален.")
        return redirect('property_list')

    return render(request, 'agency/property_confirm_delete.html', {'property': property_obj})


# =========================================================================
# NEWSFEED CHANNELS & ARTICLES
# =========================================================================

def news_view(request):
    """
    Renders public blog-style entries ordered chronologically descending.
    """
    articles = Article.objects.all().order_by('-published_date')
    return render(request, 'agency/news.html', {'articles': articles})


def article_detail_view(request, pk):
    """
    Fetches details of a single journalistic entry.
    """
    article = get_object_or_404(Article, pk=pk)
    return render(request, 'agency/article_detail.html', {'article': article})


@login_required
@permission_required('agency.add_article', raise_exception=True)
def article_create_view(request):
    """
    Creates a new informational or news article.
    """
    logger.info("User %s requested article creation form.", request.user.username)

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            logger.info("User %s published news article: '%s'", request.user.username, form.cleaned_data.get('title'))
            messages.success(request, "Новость успешно опубликована!")
            return redirect('news')
        else:
            logger.warning("Article form validation failed for user %s", request.user.username)
    else:
        form = ArticleForm()

    return render(request, 'agency/article_form.html', {'form': form, 'action': 'Добавить'})


@login_required
@permission_required('agency.change_article', raise_exception=True)
def article_update_view(request, pk):
    """
    Modifies content blocks or assets inside historical articles.
    """
    article = get_object_or_404(Article, pk=pk)
    logger.info("User %s requested updates for article ID: %d", request.user.username, pk)

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            logger.info("User %s modified news block identifier: %d", request.user.username, pk)
            messages.success(request, "Новость успешно обновлена!")
            return redirect('news')
        else:
            logger.warning("Validation error on updating article ID: %d by user %s", pk, request.user.username)
    else:
        form = ArticleForm(instance=article)

    return render(request, 'agency/article_form.html', {'form': form, 'action': 'Редактировать', 'article': article})


@login_required
@permission_required('agency.delete_article', raise_exception=True)
def article_delete_view(request, pk):
    """
    Removes an article from the database schema entirely.
    """
    article = get_object_or_404(Article, pk=pk)
    logger.info("User %s triggered deletion confirmation UI for article ID: %d ('%s')", request.user.username, pk, article.title)

    if request.method == 'POST':
        title_for_log = article.title
        article.delete()
        logger.info("User %s dropped article entry: '%s' (ID: %d)", request.user.username, title_for_log, pk)
        messages.success(request, "Новость успешно удалена.")
        return redirect('news')

    return render(request, 'agency/article_confirm_delete.html', {'article': article})


# =========================================================================
# REVIEWS MANAGEMENT
# =========================================================================

@login_required
def reviews_view(request):
    """
    Fetches and records feedback strings linked to validated user sessions.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')

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


# =========================================================================
# SYSTEM AUTHENTICATION
# =========================================================================

def register_view(request):
    """
    Registers a new standard user client profile.
    """
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
    """
    Validates credentials against standard backend engines.
    """
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
    """
    Flushes request session and logs out user context.
    """
    logout(request)
    return redirect('home')


# =========================================================================
# DASHBOARD LOGIC (EMPLOYEES AND CLIENTS)
# =========================================================================

@login_required
def dashboard_view(request):
    """
    Differentiates roles to output structured analytic reports or historical consumer panels.
    """
    logger.info("User %s (ID: %d) accessed the management dashboard view.", request.user.username, request.user.id)

    current_utc = timezone.now()
    current_local = timezone.localtime(current_utc)
    current_tz_name = timezone.get_current_timezone_name()

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get('https://api.nbrb.by/exrates/rates/431', headers=headers, timeout=4)
        rate = float(response.json()['Cur_OfficialRate']) if response.status_code == 200 else 3.25
    except Exception as e:
        logger.error("Dashboard currency extraction failed: %s", e)
        rate = 3.25

    text_calendar = calendar.TextCalendar(firstweekday=0).formatmonth(current_local.year, current_local.month)

    # 1. EMPLOYEE DASHBOARD INTERFACE
    if hasattr(request.user, 'employeeprofile'):
        plt.clf()
        plt.cla()
        plt.close('all')

        employee_profile = request.user.employeeprofile
        deals_queryset = Deal.objects.filter(employee=employee_profile).select_related(
            'property__prop_type', 'client__user'
        ).order_by('-created_at_utc')

        unique_clients = {}
        for deal in deals_queryset:
            if deal.client and deal.client.pk not in unique_clients:
                unique_clients[deal.client.pk] = deal.client
        clients_list = list(unique_clients.values())

        stats_data = deals_queryset.aggregate(total_usd=Sum('final_price'), avg_usd=Avg('final_price'))
        raw_total = stats_data['total_usd'] or 0.0
        raw_avg = stats_data['avg_usd'] or 0.0

        total_sales_byn = float(raw_total) * rate
        total_sales = f"{total_sales_byn:,.0f}".replace(",", " ")
        avg_sales = float(raw_avg) * rate

        prices_list = [float(deal.final_price) * rate for deal in deals_queryset if deal.final_price]

        if prices_list:
            median_val = np.median(prices_list)
            median_sales = f"{median_val:,.0f}".replace(",", " ")

            occurence_count = Counter(prices_list)
            most_common_price = occurence_count.most_common(1)[0][0]
            mode_sales = f"{most_common_price:,.0f}".replace(",", " ")
        else:
            median_sales = "0"
            mode_sales = "0"

        sales_count = deals_queryset.filter(deal_type='sale').count()
        rent_count = deals_queryset.filter(deal_type='rent').count()

        popular_type = "No data available"
        chart_data = None

        if deals_queryset.exists():
            type_counts = (deals_queryset
                           .values('property__prop_type__name')
                           .annotate(total=Count('id'))
                           .order_by('-total'))

            if type_counts and type_counts[0]['property__prop_type__name']:
                popular_type = type_counts[0]['property__prop_type__name']

            try:
                labels_chart = [item['property__prop_type__name'] or 'Other' for item in type_counts]
                values_chart = [item['total'] for item in type_counts]

                fig, ax = plt.subplots(figsize=(4, 4))
                colors = ['#17c3b2', '#227c9d', '#ffcb77', '#fec5bb', '#ff6b6b']
                current_colors = (colors * (len(values_chart) // len(colors) + 1))[:len(values_chart)]

                ax.pie(
                    values_chart, labels=labels_chart, autopct='%1.0f%%', startangle=90, colors=current_colors,
                    textprops=dict(color="#2d3748", fontsize=9)
                )
                ax.set_title("Deals by Categories", fontsize=10, weight='bold', pad=10)
                plt.tight_layout()

                buf = io.BytesIO()
                fig.savefig(buf, format='png', bbox_inches='tight', dpi=110)
                buf.seek(0)
                chart_data = base64.b64encode(buf.read()).decode('utf-8')
                buf.close()
                plt.close(fig)
            except Exception as e:
                logger.error("Error generating metrics pie chart for employee dashboard: %s", e)

        for deal in deals_queryset:
            if deal.final_price:
                deal.amount = f"{float(deal.final_price) * rate:,.0f}".replace(",", " ")
            else:
                deal.amount = "0"

        context = {
            'deals': deals_queryset,
            'clients': clients_list,
            'total_sales': total_sales,
            'avg_sales': avg_sales,
            'median_sales': median_sales,
            'mode_sales': mode_sales,
            'avg_age': sales_count,
            'median_age': rent_count,
            'popular_type': popular_type,
            'chart_data': chart_data,
            'text_calendar': text_calendar,
            'tz_name': current_tz_name,
            'current_local_iso': current_local.isoformat(),
            'current_utc': current_utc,
        }
        return render(request, 'agency/dashboard_employee.html', context)

    # 2. CLIENT DASHBOARD INTERFACE
    else:
        try:
            client_profile = ClientProfile.objects.prefetch_related('promo_codes').get(user=request.user)
            promo_codes = client_profile.promo_codes.all()
            phone = client_profile.phone
        except ClientProfile.DoesNotExist:
            logger.warning("Client profile record missing for authenticated user context: %s", request.user.username)
            client_profile = None
            promo_codes = []
            phone = "Not provided"

        purchases_queryset = Deal.objects.filter(client__user=request.user).select_related('property').order_by('-created_at_utc')

        for purchase in purchases_queryset:
            if purchase.final_price:
                purchase.amount_byn = f"{float(purchase.final_price) * rate:,.0f}".replace(",", " ")
            else:
                purchase.amount_byn = "0"

        context = {
            'profile': client_profile,
            'promo_codes': promo_codes,
            'purchases': purchases_queryset,
            'phone': phone,
            'text_calendar': text_calendar,
            'tz_name': current_tz_name,
            'current_local_iso': current_local.isoformat(),
            'current_utc': current_utc,
        }
        return render(request, 'agency/dashboard_client.html', context)


# =========================================================================
# DATA ANALYTICS & VISUALIZATION (MATPLOTLIB & ADVANCED APIS)
# =========================================================================

def statistics_view(request):
    plt.close('all')

    # 1. Настройки стиля "Premium/Corporate"
    plt.style.use('bmh')  # Базовый чистый стиль
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Segoe UI', 'Arial', 'DejaVu Sans'],
        'axes.titlesize': 14,
        'axes.titleweight': 'bold',
        'axes.spines.top': False,
        'axes.spines.right': False,
    })

    # Курс валют
    try:
        response = requests.get('https://api.nbrb.by/exrates/rates/431', timeout=3)
        usd_rate = f"{response.json()['Cur_OfficialRate']:.4f} BYN" if response.status_code == 200 else "3.2500 BYN"
    except:
        usd_rate = "3.2500 BYN"

    def figure_to_base64(fig):
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=150, transparent=True)
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        plt.close(fig)
        return img_str

    # --- CHART 1: PIE (Doughnut) ---
    data = Property.objects.values('prop_type__name').annotate(count=Count('id'))
    labels, counts = [i['prop_type__name'] or "Другое" for i in data], [i['count'] for i in data]

    fig1, ax1 = plt.subplots(figsize=(6, 4))
    colors = ['#2c3e50', '#17c3b2', '#2980b9', '#f39c12']
    wedges, texts, autotexts = ax1.pie(counts, labels=labels, autopct='%1.0f%%',
                                       pctdistance=0.8, colors=colors,
                                       wedgeprops={'width': 0.5, 'edgecolor': 'white', 'linewidth': 2})
    plt.setp(autotexts, size=10, weight="bold", color="white")
    ax1.set_title("СТРУКТУРА КАТАЛОГА")
    chart_pie = figure_to_base64(fig1)

    # --- CHART 2: BAR (Compare Prices) ---
    price_data = Property.objects.values('deal_type').annotate(avg_price=Avg('price'))
    deal_types = [('sale', 'Продажа'), ('rent', 'Аренда')]

    bar_labels = [d[1] for d in deal_types]
    bar_values = [float(next((i['avg_price'] for i in price_data if i['deal_type'] == d[0]), 0)) for d in deal_types]

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    bars = ax2.bar(bar_labels, bar_values, color=['#2c3e50', '#17c3b2'], width=0.4, capsize=5)
    ax2.set_title("СРЕДНИЙ ЧЕК (USD)")
    ax2.set_ylabel("Стоимость ($)")
    for bar in bars:
        height = bar.get_height()
        ax2.annotate(f'${int(height):,}', xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 5), textcoords="offset points", ha='center', fontweight='bold')
    chart_bar = figure_to_base64(fig2)

    # CHART 3: Сравнение средних цен по типам недвижимости (Продажа)
    data = Property.objects.filter(deal_type='sale').values('prop_type__name').annotate(avg_price=Avg('price'))

    labels = [i['prop_type__name'] or "Другое" for i in data]
    values = [float(i['avg_price']) for i in data]

    # Увеличиваем высоту фигуры (второй параметр figsize), чтобы было место для длинных подписей
    fig3, ax3 = plt.subplots(figsize=(10, 6))

    bars = ax3.bar(labels, values, color='#227c9d', width=0.6, alpha=0.85)

    ax3.set_title("СРЕДНЯЯ ЦЕНА ПО ТИПАМ ОБЪЕКТОВ (ПРОДАЖА)", fontsize=13, pad=20)
    ax3.set_ylabel("Цена ($)", fontsize=11)

    # ГЛАВНОЕ ИСПРАВЛЕНИЕ: Поворачиваем подписи и выравниваем их
    plt.xticks(rotation=45, ha='right', fontsize=9)

    ax3.grid(axis='y', linestyle=':', alpha=0.6)

    # Аннотации над столбцами
    for bar in bars:
        height = bar.get_height()
        ax3.annotate(f'${int(height):,}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 5), textcoords="offset points",
                     ha='center', va='bottom', fontweight='bold', fontsize=8)

    # Настраиваем отступы, чтобы подписи не обрезались
    plt.tight_layout()

    chart_line = figure_to_base64(fig3)

    return render(request, 'agency/statistics.html', {
        'chart_pie': chart_pie,
        'chart_bar': chart_bar,
        'chart_line': chart_line,
        'usd_rate': usd_rate
    })


# =========================================================================
# ASYNC API ENDPOINTS & TRANSACTIONS
# =========================================================================

def secured_agency_stats_api(request):
    """
    Protected JSON endpoint providing advanced metadata summaries for verified tokens or user sessions.
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'error',
            'error': 'Unauthorized',
            'message': 'Security access denied: Authentication context is missing.'
        }, status=401)

    session_duration = 0
    if request.user.last_login:
        delta = timezone.now() - request.user.last_login
        session_duration = int(delta.total_seconds())

    total_properties = Property.objects.filter(is_active=True).count()
    total_deals = Deal.objects.count()
    sum_usd_data = Deal.objects.aggregate(total_usd=Sum('final_price'))
    total_usd = float(sum_usd_data['total_usd'] or 0.0)

    try:
        res = requests.get('https://api.nbrb.by/exrates/rates/431', timeout=3)
        rate = float(res.json()['Cur_OfficialRate']) if res.status_code == 200 else 3.25
    except Exception:
        rate = 3.25

    total_byn = total_usd * rate
    sales_count = Deal.objects.filter(deal_type='sale').count()
    rent_count = Deal.objects.filter(deal_type='rent').count()

    if sales_count > rent_count:
        market_trend = "High purchaser activity (Seller's market)"
        investment_advice = "Capital investments in primary developments are highly prioritized."
    elif rent_count > sales_count:
        market_trend = "Elevated tenancy requirement (Landlord's market)"
        investment_advice = "Buying target assets for passive commercial flow is profitable."
    else:
        market_trend = "Stable supply-demand equilibrium"
        investment_advice = "Market indexes are firmly aligned."

    return JsonResponse({
        'status': 'success',
        'security_audit': {
            'user_identity': request.user.username,
            'role': 'Сотрудник' if hasattr(request.user, 'employeeprofile') else 'Клиент',
            'session_active_seconds': session_duration,
            'token_status': 'Valid / Verified'
        },
        'market_analytics': {
            'active_listings': total_properties,
            'total_completed_deals': total_deals,
            'gross_volume_usd': f"${total_usd:,.0f}".replace(",", " "),
            'gross_volume_byn': f"{total_byn:,.0f} BYN".replace(",", " "),
            'nbrb_exchange_rate': f"{rate:.4f} BYN/$"
        },
        'ai_recommendation': {
            'current_trend': market_trend,
            'advice': investment_advice
        },
        'server_timestamp': timezone.now().strftime("%d.%m.%Y %H:%M:%S")
    })

@login_required
@require_POST
def create_deal_ajax(request, property_id):
    """
    Processes transaction creation correctly mapping deal type from the property object.
    """
    next_url = request.META.get('HTTP_REFERER', 'property_list')

    if request.user.is_superuser or hasattr(request.user, 'employeeprofile'):
        messages.error(request, 'Критическая ошибка доступа: Сотрудники и администраторы не могут оформлять сделки покупки.')
        return redirect(next_url)

    try:
        client_profile = request.user.clientprofile
    except ClientProfile.DoesNotExist:
        messages.error(request, 'Профиль клиента не инициализирован. Доступ заблокирован.')
        return redirect(next_url)

    employee_id = request.POST.get('employee_id')
    if not employee_id:
        messages.error(request, 'Необходимо выбрать менеджера для оформления сделки.')
        return redirect(next_url)

    employee = get_object_or_404(EmployeeProfile, id=employee_id)
    property_obj = get_object_or_404(Property, id=property_id, is_active=True)

    if Deal.objects.filter(property=property_obj).exists():
        messages.error(request, f'Данная позиция («{property_obj.title}») уже участвует в сделке.')
        return redirect(next_url)

    # ИСПРАВЛЕНИЕ: Берем тип сделки из объекта недвижимости, а не из POST-запроса
    deal_type = property_obj.deal_type

    try:
        Deal.objects.create(
            property=property_obj,
            client=client_profile,
            employee=employee,
            final_price=property_obj.price,
            deal_type=deal_type # Теперь здесь будет либо 'sale', либо 'rent'
        )
        property_obj.is_active = False
        property_obj.save()

        manager_name = employee.user.get_full_name() or employee.user.username
        messages.success(request, f'Заявка на "{property_obj.title}" успешно создана! Назначен менеджер: {manager_name}.')
        return redirect('dashboard')

    except ValidationError as e:
        error_msg = str(e) # Упрощенный вывод ошибки для пользователя
        messages.error(request, f'Ошибка валидации: {error_msg}')
        return redirect(next_url)
    except Exception as e:
        messages.error(request, f'Не удалось сохранить сделку: {str(e)}')
        return redirect(next_url)