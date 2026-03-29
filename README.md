# 🌸 Flora Luxe — Premium Flower Shop

Django-приложение для интернет-магазина цветов с поддержкой мобильных устройств.

## 🚀 Деплой на Railway (шаг за шагом)

### 1. Создайте аккаунт на [railway.app](https://railway.app)

### 2. Загрузите проект
```bash
# Инициализируйте git если ещё не сделали
git init
git add .
git commit -m "Initial commit"
```

### 3. На Railway: New Project → Deploy from GitHub repo

### 4. Добавьте переменные окружения в Railway → Variables:
```
SECRET_KEY=your-secret-key-50-chars-min
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourapp.up.railway.app
CSRF_TRUSTED_ORIGINS=https://yourapp.up.railway.app
```

### 5. Добавьте PostgreSQL
Railway → New → Database → Add PostgreSQL  
`DATABASE_URL` добавится автоматически.

### 6. Создайте суперпользователя
В Railway → Shell:
```bash
python manage.py createsuperuser
```

### 7. Откройте сайт
Перейдите на `https://yourapp.up.railway.app`  
Админка: `https://yourapp.up.railway.app/admin/`

---

## ⚙️ Локальная разработка

```bash
# Создайте .env из примера
cp .env.example .env
# Заполните .env значениями

# Установите зависимости
pip install -r requirements.txt

# Примените миграции
python manage.py migrate

# Создайте суперпользователя
python manage.py createsuperuser

# Запустите сервер
python manage.py runserver
```

---

## 🔑 Переменные окружения

| Переменная | Описание | Обязательна |
|---|---|---|
| `SECRET_KEY` | Django secret key | ✅ |
| `DJANGO_DEBUG` | True/False | ✅ |
| `DJANGO_ALLOWED_HOSTS` | Хосты через запятую | ✅ |
| `CSRF_TRUSTED_ORIGINS` | CSRF origins (https://...) | ✅ |
| `DATABASE_URL` | PostgreSQL URL | Railway авто |
| `GOOGLE_CLIENT_ID` | Google OAuth | Опционально |
| `GOOGLE_CLIENT_SECRET` | Google OAuth | Опционально |
| `PAYME_SECRET` | Payme ключ | Опционально |
| `CLICK_SERVICE_ID` | Click ID | Опционально |
| `CLICK_MERCHANT_ID` | Click Merchant | Опционально |
| `OPENAI_API_KEY` | ChatGPT для AI-чата | Опционально |

---

## 📱 Функциональность

- **Каталог цветов** с поиском и фильтрацией по категориям
- **Корзина** (session-based)
- **Оформление заказа** с уникальным кодом чека
- **Онлайн-оплата** через Payme и Click
- **Google OAuth** авторизация
- **AI-чат** помощник Flora (rule-based + OpenAI опционально)
- **Мобильное приложение** — нижняя навигация, PWA-ready
- **Мультиязычность** — RU / UZ / EN
- **Отзывы** с модерацией
- **Профиль пользователя** с историей заказов
- **Проверка чека** по коду

---

## 🛡️ Исправленные баги

1. ✅ `Order.STATUS_CHOICES` и поле `status` теперь совпадают (добавлены `processing`, `delivered`)
2. ✅ `PAYME_SECRET` вынесен в переменные окружения
3. ✅ `OPENAI_API_KEY` берётся из env, не хардкодится
4. ✅ `ALLOWED_HOSTS` настраивается через `DJANGO_ALLOWED_HOSTS`
5. ✅ `CSRF_TRUSTED_ORIGINS` настраивается через env
6. ✅ `Product` (неиспользуемая модель) — удалена
7. ✅ Payme webhook — добавлена обработка `DoesNotExist`
8. ✅ `save_user_profile` — исправлен `AttributeError` при отсутствии профиля
9. ✅ `SESSION_COOKIE_SECURE` работает корректно в dev и prod
10. ✅ `add_to_cart` — возврат на страницу откуда добавляли
