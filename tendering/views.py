from http.client import HTTPResponse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.shortcuts import render
from django.views import generic

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


class InactiveLotListView(LoginRequiredMixin, generic.ListView):
    model = Lot
    paginate_by = 5
    queryset = Lot.objects.filter(is_active=False)
    context_object_name = "inactive_lot_list"
    template_name = "tendering/inactive_list.html"


class ActiveLotListView(LoginRequiredMixin, generic.ListView):
    model = Lot
    paginate_by = 5
    queryset = Lot.objects.filter(is_active=True)
    context_object_name = "active_lot_list"
    template_name = "tendering/active_list.html"


class UserListView(LoginRequiredMixin, generic.ListView):
    model = User
    template_name = "tendering/user_list.html"
    paginate_by = 5

class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = User