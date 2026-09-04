from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from datetime import date
# Стало (добавь через запятую модель Article):
from .models import Property, Review, Article


# =========================================================
# ВАЛИДАТОР ДЛЯ БГУИР (Валидация ДР по введенной дате)
# =========================================================
def validate_birth_date(value):
    if value > date.today():
        raise ValidationError("Дата рождения не может быть в будущем!")

    age = date.today().year - value.year - ((date.today().month, date.today().day) < (value.month, value.day))
    if age > 120:
        raise ValidationError("Указан неправдоподобный возраст (более 120 лет).")
    if age < 18:
        raise ValidationError("Регистрация доступна только лицам старше 18 лет.")


# =========================================================
# ТВОЯ ФОРМА НЕДВИЖИМОСТИ (Все поля и виджеты сохранены)
# =========================================================
class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        # Добавляем 'deal_type' в список отображаемых полей формы
        fields = ['title', 'prop_type', 'owner', 'price', 'description', 'is_active', 'image', 'deal_type']

        # Если ты используешь виджеты для стилизации (например, добавления классов Bootstrap или кастомных стилей):
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'prop_type': forms.Select(attrs={'class': 'form-control'}),
            'owner': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'deal_type': forms.Select(attrs={'class': 'form-control'}),  # Добавляем класс селекту
        }

    # Валидация на уровне моделей/форм (Бэк)
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError("Цена недвижимости должна быть больше нуля!")
        return price


# =========================================================
# ТВОЯ ФОРМА ОТЗЫВОВ (Все поля и виджеты сохранены)
# =========================================================
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['property', 'rating', 'comment'] # Автора и дату заполним сами во вьюхе
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'property': forms.Select(attrs={'class': 'form-control'}),
        }

    # Валидация отзыва на уровне бэка (Цензура)
    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        bad_words = ['спам', 'реклама', 'купить диплом']
        for word in bad_words:
            if word in comment.lower():
                raise forms.ValidationError(f"Текст содержит недопустимое слово: '{word}'.")
        return comment


# =========================================================
# ТВОЯ ФОРМА РЕГИСТРАЦИИ (Добавлено только поле ДР для лабы)
# =========================================================
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Пароль")
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                                       label="Подтвердите пароль")

    # Добавлено поле ДР для выполнения требования преподавателя
    birth_date = forms.DateField(
        label="Дата рождения",
        validators=[validate_birth_date],
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Это имя пользователя уже занято.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Пароли не совпадают.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


# =========================================================
# ТВОЯ ФОРМА АВТОРИЗАЦИИ (Все плейсхолдеры сохранены)
# =========================================================
class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логин'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}))

# Не забудь добавить Article в импорт моделей из .models в начале файла!
# пример: from .models import Property, Review, Article

# =========================================================
# НОВАЯ ФОРМА ДЛЯ НОВОСТЕЙ (CRUD СТАТЕЙ)
# =========================================================
class ArticleForm(forms.ModelForm):
    class Meta:
        # Убедись, что модель в models.py называется именно Article
        model = Article
        fields = ['title', 'content', 'image']
        labels = {
            'title': 'Заголовок новости',
            'content': 'Текст публикации',
            'image': 'Изображение / Обложка',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите заголовок...'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Напишите текст новости...'}),
            # Виджет для файла стилизуется стандартным браузерным инпутом
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    # Небольшая валидация на уровне бэка, чтобы заголовки не были слишком короткими
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title and len(title) < 5:
            raise forms.ValidationError("Заголовок новости должен содержать минимум 5 символов!")
        return title