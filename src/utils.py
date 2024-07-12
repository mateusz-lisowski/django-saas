from typing import Literal

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


def create_stripe_product(name: str, metadata: dict) -> str:
    response = stripe.Product.create(
        name=name,
        metadata=metadata
    )
    return response.id


def create_stripe_price(
        currency: str,
        product: str,
        metadata: dict,
        unit_amount: int = 0,
        interval: Literal["month", "year"] = "month"
) -> str:
    response = stripe.Price.create(
        currency=currency,
        unit_amount=unit_amount,
        recurring={"interval": interval},
        product=product,
        metadata=metadata
    )
    return response.id
