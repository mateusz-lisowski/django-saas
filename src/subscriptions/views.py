from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def subscription_details(request):
    return None
