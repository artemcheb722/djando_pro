
import os
from django.shortcuts import render, redirect
import json
import stripe
from django.views import View
from django.http import JsonResponse
from mysite import settings
client = stripe.StripeClient(settings.STRIPE_SECRET_KEY)

YOUR_DOMAIN = 'http://localhost:8000'


class CheckoutPaymentPage(View):
    def get(self, request):
        return render(request, 'checkout-payment.html')

def checkout_success_page(request):
    session_id = request.GET.get('session_id')
    return render(request, 'success.html', {'session_id': session_id})

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

class CustomerPortalView(View):
    def post(self, request):
        checkout_session_id = request.POST.get('session_id')
        checkout_session = settings.PAYMENT_CLIENT.v1.checkout.sessions.retrieve(checkout_session_id)
        return_url = YOUR_DOMAIN

        portalSession = client.v1.billing_portal.sessions.create(params={
            'customer': checkout_session.customer,
            'return_url': return_url,
        })
        return redirect(portalSession.url, code=303)


class WebhookView(View):
    def post(self, request):
        webhook_secret = 'whsec_12345'
        request_data = json.loads(request.data)

        if webhook_secret:
            signature = request.headers.get('stripe-signature')
            try:
                event = client.construct_event(
                    payload=request.data, sig_header=signature, secret=webhook_secret)
                data = event['data']
            except Exception as e:
                return e

            event_type = event['type']
        else:
            data = request_data['data']
            event_type = request_data['type']
        data_object = data['object']

        print('event ' + event_type)

        if event_type == 'checkout.session.completed':
            print('🔔 Payment succeeded!')
        elif event_type == 'customer.subscription.trial_will_end':
            print('Subscription trial will end')
        elif event_type == 'customer.subscription.created':
            print('Subscription created %s', event.id)
        elif event_type == 'customer.subscription.updated':
            print('Subscription created %s', event.id)
        elif event_type == 'customer.subscription.deleted':
            print('Subscription canceled: %s', event.id)
        elif event_type == 'entitlements.active_entitlement_summary.updated':
            print('Active entitlement summary updated: %s', event.id)

        return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(port=4242)
