from zoneinfo import ZoneInfo
import requests
from PIL.Image import logger
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class PropertyType(models.Model):
    name = models.CharField(max_length=100, verbose_name="Вид недвижимости")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Вид недвижимости"
        verbose_name_plural = "Виды недвижимости"


class Owner(models.Model):
    full_name = models.CharField(max_length=255, verbose_name="ФИО владельца")
    phone = models.CharField(max_length=20, verbose_name="Телефон")

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Владелец"
        verbose_name_plural = "Владельцы"


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Аккаунт")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    promo_codes = models.ManyToManyField(
        'PromoCode',
        blank=True,
        related_name='clients',
        verbose_name="Персональные промокоды"
    )

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Профиль клиента"
        verbose_name_plural = "Профили клиентов"


class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Аккаунт")
    position = models.CharField(max_length=100, verbose_name="Должность")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    photo = models.ImageField(
        upload_to="employees_photos/",
        blank=True,
        null=True,
        verbose_name="Фото сотрудника"
    )
    job_description = models.TextField(
        blank=True,
        verbose_name="Выполняемые работы / Обязанности"
    )

    def __str__(self):
        full_name = self.user.get_full_name()
        return f"{full_name if full_name else self.user.username} ({self.position})"

    class Meta:
        verbose_name = "Профиль сотрудника"
        verbose_name_plural = "Профили сотрудников"


class Property(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название объекта")
    prop_type = models.ForeignKey(PropertyType, on_delete=models.PROTECT, verbose_name="Вид недвижимости")
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, verbose_name="Владелец")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Стоимость")
    description = models.TextField(verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Доступно")
    image = models.ImageField(
        upload_to="property_images/",
        blank=True,
        null=True,
        verbose_name="Фото объекта"
    )

    DEAL_TYPE_CHOICES = [
        ('sale', 'Продажа'),
        ('rent', 'Аренда'),
    ]
    deal_type = models.CharField(
        max_length=10,
        choices=DEAL_TYPE_CHOICES,
        default='sale',
        verbose_name="Тип сделки"
    )

    _cached_usd_rate = None

    class Meta:
        verbose_name = "Объект недвижимости"
        verbose_name_plural = "Объекты недвижимости"

    def __str__(self):
        return f"{self.title} ({self.get_deal_type_display()})"

    @classmethod
    def get_usd_rate(cls):
        if cls._cached_usd_rate is None:
            try:
                res = requests.get('https://api.nbrb.by/exrates/rates/USD?parammode=2', timeout=2)
                if res.status_code == 200:
                    data = res.json()
                    rate_val = data.get('Cur_OfficialRate')
                    if rate_val:
                        cls._cached_usd_rate = float(rate_val)
                        logger.info("Успешно закэширован курс USD с НБРБ: %s", cls._cached_usd_rate)
                    else:
                        cls._cached_usd_rate = 3.25
                else:
                    cls._cached_usd_rate = 3.25
            except Exception as e:
                logger.warning("Не удалось получить курс во время работы модели Property: %s. Используем дефолт.", e)
                cls._cached_usd_rate = 3.25
        return cls._cached_usd_rate

    @property
    def get_price_in_byn(self):
        if not self.price:
            return "0.00"
        rate = self.get_usd_rate()
        total_byn = float(self.price) * rate
        return f"{total_byn:,.2f}".replace(",", " ")


class Deal(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, verbose_name="Недвижимость")
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, verbose_name="Клиент")
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, verbose_name="Менеджер")
    final_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Финальная цена ($)")
    deal_type = models.CharField(max_length=10, choices=[('sale', 'Продажа'), ('rent', 'Аренда')], default='sale')

    created_at_utc = models.DateTimeField(auto_now_add=True, verbose_name="Дата/Время создания (UTC)")
    created_at_local = models.DateTimeField(null=True, blank=True, verbose_name="Дата/Время создания (Локальное)")
    timezone_name = models.CharField(max_length=50, default='Europe/Minsk', verbose_name="Таймзона фиксации")
    date = models.DateField(auto_now_add=True, verbose_name="Дата сделки (для совместимости)")

    class Meta:
        verbose_name = "Сделка"
        verbose_name_plural = "Сделки"

    def __str__(self):
        return f"Сделка #{self.id} — {self.property.title}"

    def clean(self):
        super().clean()
        if self.final_price and self.final_price <= 0:
            raise ValidationError({'final_price': 'Стоимость сделки должна быть строго больше нуля.'})

        if self.property and not self.property.is_active:
            raise ValidationError({'property': 'Выбранный объект недвижимости сейчас неактивен или уже продан.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        self.timezone_name = 'Europe/Minsk'
        now_utc = timezone.now()
        minsk_tz = ZoneInfo(self.timezone_name)

        if not self.created_at_local:
            self.created_at_local = now_utc.astimezone(minsk_tz)

        super().save(*args, **kwargs)


class Review(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, verbose_name="Объект недвижимости")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор", null=True)
    rating = models.PositiveIntegerField(verbose_name="Оценка")
    comment = models.TextField(verbose_name="Отзыв")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отзыва")

    def __str__(self):
        return f"Отзыв на {self.property.title}"

    def get_rating_color(self):
        try:
            rating_val = int(self.rating)
        except (ValueError, TypeError):
            return "#2b8a3e"

        if rating_val in [1, 2]:
            return "#ff6b6b"
        elif rating_val in [3, 4]:
            return "#ffd43b"
        else:
            return "#2b8a3e"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"


class PromoCode(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Код")
    discount = models.PositiveIntegerField(verbose_name="Скидка (%)")
    valid_until = models.DateField(verbose_name="Действует до")

    @property
    def is_active(self):
        return self.valid_until >= timezone.now().date()

    def __str__(self):
        status = "Активен" if self.is_active else "Архив"
        return f"{self.code} (-{self.discount}%) — {status}"

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"


class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    short_description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Краткое содержание (одно предложение)"
    )
    content = models.TextField(verbose_name="Содержание")
    image = models.ImageField(
        upload_to="news_images/",
        blank=True,
        null=True,
        verbose_name="Изображение статьи"
    )
    published_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"


class FAQ(models.Model):
    question = models.CharField(max_length=255, verbose_name="Вопрос / Термин")
    answer = models.TextField(verbose_name="Ответ / Определение")
    date_added = models.DateField(auto_now_add=True, verbose_name="Дата добавления")

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = "Вопрос-ответ (FAQ)"
        verbose_name_plural = "Вопросы-ответы (FAQ)"
        ordering = ['-date_added']


class Vacancy(models.Model):
    title = models.CharField(max_length=100, verbose_name="Название вакансии")
    description = models.TextField(verbose_name="Описание и требования")
    salary = models.PositiveIntegerField(verbose_name="Предлагаемая оплата (BYN)", null=True, blank=True)

    def __str__(self):
        if self.salary:
            return f"{self.title} ({self.salary} BYN)"
        return self.title

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"


class Partner(models.Model):
    name = models.CharField(max_length=150, verbose_name="Название компании")
    logo = models.ImageField(upload_to="partners_logos/", verbose_name="Логотип")
    website_url = models.URLField(verbose_name="Ссылка на сайт компании")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Партнер"
        verbose_name_plural = "Партнеры"


class CompanyInfo(models.Model):
    name = models.CharField(max_length=150, default="EliteEstate", verbose_name="Название компании")
    logo = models.ImageField(upload_to="company_logos/", blank=True, null=True, verbose_name="Логотип компании")
    description = models.TextField(verbose_name="Информация о компании")
    history_by_years = models.TextField(blank=True, verbose_name="История по годам")
    requisites = models.TextField(blank=True, verbose_name="Реквизиты компании")
    certificate_text = models.TextField(blank=True, verbose_name="Текст сертификата")
    video_file = models.FileField(upload_to="company_videos/", blank=True, null=True, verbose_name="Видео о компании (файл)")
    video_url = models.URLField(blank=True, null=True, verbose_name="Ссылка на видео (YouTube/iframe)")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "О компании"
        verbose_name_plural = "О компании"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Корзина {self.user.username}"

    @property
    def total_price(self):
        return sum(item.get_cost for item in self.items.all())

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="Корзина")
    item_property = models.ForeignKey(Property, on_delete=models.CASCADE, verbose_name="Объект недвижимости")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    @property
    def get_cost(self):
        return self.item_property.price * self.quantity

    def __str__(self):
        return f"{self.item_property.title} (x{self.quantity})"

    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"