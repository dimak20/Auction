from http.client import HTTPResponse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic

from tendering.forms import CommentForm
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
    queryset = Lot.objects.filter(
        is_active=False
    ).select_related(
        "category",
        "owner"
    ).prefetch_related(
        "bids__user"
    )
    context_object_name = "inactive_lot_list"
    template_name = "tendering/inactive_list.html"


class ActiveLotListView(LoginRequiredMixin, generic.ListView):
    model = Lot
    paginate_by = 5
    queryset = Lot.objects.filter(
        is_active=True
    ).select_related(
        "category",
        "owner"
    ).prefetch_related(
        "bids__user"
    )
    context_object_name = "active_lot_list"
    template_name = "tendering/active_list.html"


class UserListView(LoginRequiredMixin, generic.ListView):
    model = User
    template_name = "tendering/user_list.html"
    paginate_by = 5

class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        lots = Lot.objects.filter(
            owner=user
        ).select_related(
            "category",
            "owner"
        ).prefetch_related(
            "bids__user"
        )
        my_active_lots = lots.filter(owner=user, is_active=True)
        my_inactive_lots = lots.filter(owner=user, is_active=False)
        participating_lots = Lot.objects.filter(
            bids__user=user, is_active=True
        ).select_related(
            "owner",
            "category"
        ).prefetch_related(
            "bids__user"
        )
        context["my_active_lots"] = my_active_lots
        context["my_inactive_lots"] = my_inactive_lots
        context["participating_lots"] = participating_lots
        return context


class LotDetailView(LoginRequiredMixin, generic.DetailView):
    model = Lot


class CommentCreateView(LoginRequiredMixin, generic.CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        lot_id = self.request.POST.get("lot_id")
        lot = get_object_or_404(Lot, id=lot_id)
        comment = form.save(commit=False)
        comment.lot = lot
        comment.owner = self.request.user
        comment.save()
        return redirect("tendering:lot-detail", pk=lot.id)

