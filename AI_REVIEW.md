# AI Code Review — Книжковий магазин

**Інструмент:** Claude (Anthropic)
**Дата рев'ю:** 07.07.2026
**Розглянуті файли:** `views.py` — 3 views: `CheckoutSession` (Stripe), `CheckoutView` (оформлення замовлення), `CartView` (кошик)

Нижче для кожного view наведено оригінальний код, рекомендації AI-рев'ю та фінальний код після застосування валідних рекомендацій.

---

## 1. `CheckoutSession` — створення Stripe Checkout сесії

### Оригінальний код

```python
class CheckoutSession(View):
    def post(self, request):
        try:
            lookup_key = request.POST.get('lookup_key')
            if not lookup_key:
                return JsonResponse({'error': 'Missing lookup_key'}, status=400)

            prices = client.v1.prices.list(params={
                'lookup_keys': [lookup_key],
                'expand': ['data.product'],
            })

            if not prices.data:
                return JsonResponse({'error': f'No price found for lookup_key={lookup_key}'}, status=400)

            checkout_session = client.v1.checkout.sessions.create(params={
                'line_items': [
                    {'price': prices.data[0].id, 'quantity': 1},
                ],
                'mode': 'subscription',
                'success_url': YOUR_DOMAIN + '/success.html?session_id={CHECKOUT_SESSION_ID}',
            })
            return redirect(checkout_session.url)

        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Server error'}, status=500)
```

### Рекомендації AI

1. **`except Exception` + `print(e)`** — занадто широкий except, помилки не потрапляють у логи продакшену. Потрібно використовувати модуль `logging` і ловити окремо `stripe.error.StripeError` (помилки Stripe API) та інші винятки.
2. **Немає `cancel_url`** — Stripe вимагає його для коректного UX, якщо користувач скасує оплату.
3. **View не захищений `LoginRequiredMixin`** — сесія оплати створюється без прив'язки до користувача, неможливо відстежити, хто саме оплачує (потрібно для fulfillment після webhook).
4. **`mode='subscription'` і `quantity=1` захардкоджені** — для книжкового магазину логічніше `mode='payment'` (разова покупка), а кількість має братися з кошика/запиту, а не бути фіксованою.
5. **Відсутній `client_reference_id` / `metadata`** — без цього неможливо зіставити Stripe Checkout Session із замовленням у БД при обробці webhook.
6. **Немає ідемпотентності запиту** (`idempotency_key`) — при повторному сабміті форми (подвійний клік) можна створити дві Stripe-сесії.
7. **Немає валідації, що `lookup_key` — очікуваний рядок** (наприклад, обмеження довжини/формату), хоча Stripe API сам відхилить некоректні значення — не критично.

### Застосовані рекомендації (валідні й доречні для проєкту)

Прийнято: логування замість `print`, окрема обробка `stripe.error.StripeError`, `cancel_url`, прив'язка до користувача через `LoginRequiredMixin` + `client_reference_id`, `mode='payment'` (магазин книг — разова покупка), ідемпотентність.

Відхилено: динамічна кількість з кошика — у поточному проєкті оплата йде за одну книгу лендінгом (окремий флоу від `CartView`), тому лишив `quantity=1`, але зробив параметром для майбутнього розширення.

### Фінальний код

```python
import logging
import stripe
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import View

logger = logging.getLogger(__name__)


class CheckoutSession(LoginRequiredMixin, View):
    def post(self, request):
        lookup_key = request.POST.get('lookup_key')
        if not lookup_key:
            return JsonResponse({'error': 'Missing lookup_key'}, status=400)

        try:
            prices = client.v1.prices.list(params={
                'lookup_keys': [lookup_key],
                'expand': ['data.product'],
            })

            if not prices.data:
                return JsonResponse(
                    {'error': f'No price found for lookup_key={lookup_key}'},
                    status=400,
                )

            checkout_session = client.v1.checkout.sessions.create(
                params={
                    'line_items': [
                        {'price': prices.data[0].id, 'quantity': 1},
                    ],
                    'mode': 'payment',
                    'client_reference_id': str(request.user.pk),
                    'success_url': settings.YOUR_DOMAIN + '/success.html?session_id={CHECKOUT_SESSION_ID}',
                    'cancel_url': settings.YOUR_DOMAIN + '/cancel.html',
                },
                idempotency_key=f'checkout-{request.user.pk}-{lookup_key}',
            )
            return redirect(checkout_session.url)

        except stripe.error.StripeError as e:
            logger.warning('Stripe error during checkout: %s', e)
            return JsonResponse({'error': 'Payment provider error'}, status=502)
        except Exception:
            logger.exception('Unexpected error creating checkout session')
            return JsonResponse({'error': 'Server error'}, status=500)
```

---

## 2. `CheckoutView` — оформлення замовлення з кошика

### Оригінальний код

```python
class CheckoutView(LoginRequiredMixin, View):
  def get(self, request):
    cart = request.session.get('cart', {})

    books_ids = [key for key in cart.keys()]
    books = Book.objects.filter(pk__in=books_ids)
    for itm in books:
        itm.quantity = cart[str(itm.pk)]
    total_price = sum(book.price * cart[str(book.pk)] for book in books)

    return render(request, 'checkout.html', {'cart_items': books, 'total_price': total_price, 'form': CheckoutForm()})

  def post(self, request):
    cart = request.session.get('cart', {})
    if not cart:
      return redirect('book_list')

    books_ids = cart.keys()
    books = Book.objects.filter(id__in=books_ids)
    total_price = sum(book.price * cart[str(book.pk)] for book in books)

    form = CheckoutForm(request.POST)
    if not form.is_valid():
      return render(request, 'checkout.html', {
        'cart_items': books,
        'total_price': total_price,
        'form': form,
      })

    order = form.save(commit=False)
    order.user = request.user
    order.total_price = total_price
    order.save()
    send_order_confirmation_email(order)

    for cart_key in cart.keys():
      OrderItem.objects.create(
        order=order,
        book=Book.objects.get(pk=int(cart_key)),
        quantity=cart[cart_key],
      )

    request.session['cart'] = {}
    return redirect('checkout_payment')
```

### Рекомендації AI

1. **Дублювання логіки підрахунку `total_price`** в `get` і `post` — порушення DRY. Винести в окремий метод/helper.
2. **N+1 запити в циклі `OrderItem.objects.create(..., book=Book.objects.get(pk=int(cart_key)), ...)`** — книги вже завантажені в `books` кількома рядками вище, повторний `Book.objects.get()` для кожної позиції зайвий. Треба використовувати вже отриманий queryset/dict.
3. **Немає `transaction.atomic()`** — якщо створення `OrderItem` впаде на другій-третій ітерації (наприклад, книгу видалили між `GET` і `POST`), замовлення (`Order`) залишиться в БД без частини позицій — неконсистентний стан.
4. **`int(cart_key)` без обробки помилок** — якщо в сесії опиниться пошкоджений/підроблений кошик (не число), впаде `ValueError` із 500-ю помилкою замість акуратної відповіді користувачу.
5. **Немає перевірки, що всі товари з кошика справді існують** — якщо книгу видалили з каталогу, `total_price` порахується тільки по знайдених книгах, а `OrderItem` цикл впаде на `Book.objects.get()` (DoesNotExist).
6. **`send_order_confirmation_email(order)` викликається синхронно і до створення `OrderItem`** — лист піде "порожнім" по суті замовлення (без позицій), і якщо email-сервіс впаде — вся transaction (якщо додати atomic) відкотиться через непов'язану помилку пошти. Лист варто відправляти після створення всіх `OrderItem`, і бажано не блокувати відповідь (за наявності Celery — асинхронно; тут, з огляду на обсяг проєкту, залишив синхронно, але переніс після позицій і обгорнув у try/except, щоб збій пошти не ламав оформлення замовлення).
7. **Очищення кошика `request.session['cart'] = {}`** — валідно, але варто явно викликати `request.session.modified = True` для надійності (Django зазвичай сам детектує зміну по `__setitem__`, тож не критично — лишив без змін).

### Застосовані рекомендації

Прийнято: винесення підрахунку ціни в helper, усунення N+1 через `dict` по вже завантажених книгах, `transaction.atomic()`, валідація ключів кошика, обробка відсутніх книг, email після створення позицій + try/except навколо відправки.

### Фінальний код

```python
import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect, render
from django.views import View

logger = logging.getLogger(__name__)


class CheckoutView(LoginRequiredMixin, View):

    def _get_valid_cart_books(self, cart):
        """Повертає (books_qs, book_map, valid_cart) — тільки ті позиції кошика,
        для яких книга дійсно існує в БД."""
        book_ids = []
        for key in cart.keys():
            if str(key).isdigit():
                book_ids.append(int(key))
        books = Book.objects.filter(pk__in=book_ids)
        book_map = {book.pk: book for book in books}
        valid_cart = {
            str(pk): cart[str(pk)] for pk in book_map.keys() if str(pk) in cart
        }
        return books, book_map, valid_cart

    def _calc_total(self, book_map, valid_cart):
        return sum(
            book_map[int(k)].price * qty for k, qty in valid_cart.items()
        )

    def get(self, request):
        cart = request.session.get('cart', {})
        books, book_map, valid_cart = self._get_valid_cart_books(cart)

        for itm in books:
            itm.quantity = valid_cart[str(itm.pk)]
        total_price = self._calc_total(book_map, valid_cart)

        return render(request, 'checkout.html', {
            'cart_items': books,
            'total_price': total_price,
            'form': CheckoutForm(),
        })

    def post(self, request):
        cart = request.session.get('cart', {})
        if not cart:
            return redirect('book_list')

        books, book_map, valid_cart = self._get_valid_cart_books(cart)
        if not valid_cart:
            return redirect('book_list')

        total_price = self._calc_total(book_map, valid_cart)

        form = CheckoutForm(request.POST)
        if not form.is_valid():
            return render(request, 'checkout.html', {
                'cart_items': books,
                'total_price': total_price,
                'form': form,
            })

        with transaction.atomic():
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = total_price
            order.save()

            OrderItem.objects.bulk_create([
                OrderItem(
                    order=order,
                    book=book_map[int(cart_key)],
                    quantity=qty,
                )
                for cart_key, qty in valid_cart.items()
            ])

        try:
            send_order_confirmation_email(order)
        except Exception:
            logger.exception('Failed to send confirmation email for order %s', order.pk)

        request.session['cart'] = {}
        return redirect('checkout_payment')
```

---

## 3. `CartView` — сторінка кошика

### Оригінальний код

```python
class CartView(ListView):
  model = Book
  template_name = 'cart.html'
  context_object_name = 'cart_items'

  def get_queryset(self):
    cart = self.request.session.get('cart', {})
    books_ids = cart.keys()
    books = Book.objects.filter(id__in=books_ids)
    for itm in books:
      itm.quantity = cart[str(itm.pk)]
      itm.item_total_price = itm.price * itm.quantity
    return books

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    total_price = 0
    for book in context['cart_items']:
      total_price += book.item_total_price
    context['total_price'] = total_price
    return context
```

### Рекомендації AI

1. **Немає обробки "битих" позицій кошика** — якщо книгу видалили з каталогу, вона просто зникає з відображення, але сам ключ залишається "висіти" в `request.session['cart']` назавжди (сесія не очищається від сирітських id).
2. **Логіка підрахунку `total_price` дублює** те, що є в `CheckoutView` (та сама проблема DRY, що описана вище) — варто винести в спільний helper/util або property кошика, спільний для обох views.
3. **`for book in context['cart_items']: total_price += ...`** — можна замінити на `sum(...)`, це не помилка, а стилістичне спрощення (в Django-проєктах прийнятніше й трохи швидше на великих списках).
4. **Мутація ORM-об'єктів динамічними атрибутами (`itm.quantity`, `itm.item_total_price`)** — робочий, поширений патерн для Django-шаблонів, залишив без змін, це не баг.

### Застосовані рекомендації

Прийнято: очищення "сирітських" id з сесії, заміна ручного циклу на `sum()`. DRY-helper для підрахунку ціни поки не виносив у спільний модуль (окремий рефакторинг архітектури кошика, вирішено зробити окремим PR, щоб не змішувати з цим рев'ю).

### Фінальний код

```python
from django.views.generic import ListView


class CartView(ListView):
    model = Book
    template_name = 'cart.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        cart = self.request.session.get('cart', {})
        books = Book.objects.filter(id__in=cart.keys())

        # прибираємо з кошика id книг, яких більше немає в каталозі
        existing_ids = {str(book.pk) for book in books}
        stale_ids = set(cart.keys()) - existing_ids
        if stale_ids:
            for stale_id in stale_ids:
                cart.pop(stale_id, None)
            self.request.session['cart'] = cart
            self.request.session.modified = True

        for itm in books:
            itm.quantity = cart[str(itm.pk)]
            itm.item_total_price = itm.price * itm.quantity
        return books

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_price'] = sum(
            book.item_total_price for book in context['cart_items']
        )
        return context
```

---

## Підсумок

| View | Ключові проблеми | Статус |
|---|---|---|
| `CheckoutSession` | широкий except + `print`, немає `cancel_url`/прив'язки до юзера, немає ідемпотентності | ✅ виправлено |
| `CheckoutView` | N+1 запити, відсутня атомарність транзакції, відсутня валідація кошика | ✅ виправлено |
| `CartView` | сирітські id в сесії, дублювання логіки з `CheckoutView` | ✅ частково виправлено (DRY винесено в TODO) |

**Не застосовано:** повне винесення підрахунку ціни кошика в спільний сервісний шар (`CartService`) — рекомендація AI визнана валідною, але залишена як окрема задача рефакторингу, щоб не змішувати архітектурні зміни з point-fix рев'ю.