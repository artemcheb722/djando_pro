import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from Book.models import Order

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    total_price = 100.00
    post_office_number = '12345'
    payment_method = 'card'
    payment_status = 'unpaid'
    status = 'pending'