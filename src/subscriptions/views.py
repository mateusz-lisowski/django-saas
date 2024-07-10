from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def subscription_details(request):

    if request.user.has_perm("subscriptions.basic"):
        return render(request, "basic.html")

    if request.user.has_perm("subscriptions.pro"):
        return render(request, "pro.html")

    return render(request, "free.html")
