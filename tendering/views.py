from http.client import HTTPResponse
from lib2to3.fixes.fix_input import context

from django.http import HttpRequest
from django.shortcuts import render

from tendering.models import Category, User, Lot, Comment


def index(request: HttpRequest) -> HTTPResponse:
    num_categories = Category.objects.count()
    num_users = User.objects.count()
    num_lots = Lot.objects.count()
    num_active_lots = Lot.objects.filter(is_active=True).count()
    context = {
        "num_categories": num_categories,
        "num_users": num_users,
        "num_lots": num_lots,
        "num_active_lots": num_active_lots
    }
    return render(request, "tendering/index.html", context=context)
