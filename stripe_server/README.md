
# Django Stripe Shop

Простое и расширяемое приложение интернет-магазина на Django с интеграцией Stripe для проведения онлайн-платежей.

## Особенности

- **Stripe Checkout** для оплаты как отдельных товаров, так и всей корзины целиком
- **Корзина заказов** с поддержкой объединения одинаковых товаров
- **Скидки (Coupons)** и **налоги (Taxes)**, отображаемые непосредственно в форме Stripe
- **Поддержка мультивалютности (USD / EUR)** с автоматическим выбором ключей Stripe
- **Управление товарами, заказами, скидками и налогами через Django Admin**
- **Контейнеризация с Docker + Docker Compose**
- **Stripe test mode** с готовыми тестовыми картами
- Альтернативная оплата через **Stripe Payment Intent** для отдельных товаров

## Требования

- Docker
- Docker Compose
- Аккаунт в Stripe с активированным test mode и двумя парами ключей (USD и EUR)

## Быстрый запуск

1. Создайте файл `.env` в корне проекта (рядом с файлом docker-compose.yml) и заполните его необходимыми переменными окружения. Пример содержимого:

```env
# PostgreSQL
POSTGRES_DB=stripe_server
POSTGRES_USER=admin
POSTGRES_PASSWORD=your_strong_password
POSTGRES_PORT=5432

# Django
SECRET_KEY='your_django_secret_key'
DEBUG=True
ALLOWED_HOSTS=*
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=your_strong_password

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=stripe_server
DB_USER=admin
DB_PASSWORD=your_strong_password
DB_HOST=db
DB_PORT=5432

# Stripe
STRIPE_PUBLIC_KEY_USD='your_stripe_public_key_usd'
STRIPE_SECRET_KEY_USD='your_stripe_secret_key_usd'
STRIPE_PUBLIC_KEY_EUR='your_stripe_public_key_eur'
STRIPE_SECRET_KEY_EUR='your_stripe_secret_key_eur'

# Site URL
SITE_URL='http://localhost:8000'
````

2. Соберите и запустите проект:

```bash
docker-compose up --build
```

3. Создайте суперпользователя:

```bash
docker-compose exec web python manage.py createsuperuser
```

4. Перейдите по адресу [http://localhost:8000](http://localhost:8000)

## Основные URL-адреса

| Путь                       | Назначение                                        |
| -------------------------- | ------------------------------------------------- |
| `/`                        | Список всех товаров                               |
| `/item/<id>/`              | Страница отдельного товара с кнопкой "Купить"     |
| `/buy/<id>/`               | Создание Stripe Checkout сессии для одного товара |
| `/order/`                  | Просмотр корзины                                  |
| `/add_to_order/<item_id>/` | Добавление товара в корзину                       |
| `/buy_order/`              | Покупка всех товаров в корзине через Stripe       |
| `/add_discount/`           | Применение скидки по имени                        |
| `/add_tax/`                | Применение налога по имени                        |
| `/clear_order/`            | Очистка корзины                                   |
| `/admin/`                  | Django админ-панель                               |

## Stripe тестовые карты

Используйте следующие данные для проверки оплаты через Stripe:

*  **Успешная оплата:** `4242424242424242`
*  **Отклонённая оплата:** `4000000000000002`

Подходят **любые данные для имени, любой CVC (например, 123) и любая дата в будущем**.

## Возможности админ-панели

После входа в админку вы можете:

* Добавлять/редактировать **товары**
* Создавать **скидки**, которые автоматически синхронизируются с купонами Stripe
* Создавать **налоги**, синхронизируемые с налоговыми ставками Stripe
* Создавать и удалять **корзины и содержимое заказов**

При удалении купонов или налогов происходит их деактивация/удаление в Stripe API.

## Пример сценария использования

1. Пользователь заходит на главную страницу и просматривает товары.
2. Он может либо сразу оплатить конкретный товар через Stripe Sessions или с помощью Stripe Intent, либо добавить один или несколько товаров в корзину.
3. В корзине он может применить скидку и налог, если такие предусмотрены.
4. При оплате формируется сессия Stripe, и пользователь переходит на защищённую платежную страницу.
5. После успешной оплаты отображается страница благодарности.

## Дополнительно

* Реализовано с использованием **Django REST Framework** + **TemplateHTMLRenderer**.
* Поддерживаются сессии корзины без необходимости авторизации пользователя.
* Каждая единица товара имеет свою валюту, валюта корзины должна быть единой.
* Stripe ключи разделены по валютам и автоматически выбираются.


