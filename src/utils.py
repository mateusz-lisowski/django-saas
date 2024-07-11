import stripe
from decouple import config


DJANGO_DEBUG = config("DJANGO_DEBUG", default=False, cast=bool)
STRIPE_API_KEY = config("STRIPE_API_KEY", default="", cast=str)

if "sk_test" in STRIPE_API_KEY and not DJANGO_DEBUG:
    raise ValueError("Invalid stripe api key value. Should be production one.")


stripe.api_key = STRIPE_API_KEY


def create_stripe_customer(name: str, email: str, metadata: dict) -> str:
    response = stripe.Customer.create(
        name=name,
        email=email,
        metadata=metadata
    )
    return response.id
