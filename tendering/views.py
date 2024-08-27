from audioop import reverse
from http.client import HTTPResponse

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpRequest, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic

from tendering.forms import CommentForm, BidForm, LotForm, LotUpdateForm, UserCreateForm, UserUpdateForm
from tendering.models import Category, User, Lot, Comment, Bid


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["bid_form"] = BidForm()
        return context


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


class BidCreateView(LoginRequiredMixin, generic.CreateView):
    model = Bid
    form_class = BidForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["lot_id"] = self.request.POST.get("lot_id")
        return kwargs

    def form_valid(self, form):
        lot_id = self.request.POST.get("lot_id")
        lot = get_object_or_404(Lot, id=lot_id)
        bid = form.save(commit=False)
        bid.lot = lot
        bid.user = self.request.user
        with transaction.atomic():
            bid.save()
            lot.current_price = bid.amount
            lot.save()
        return redirect("tendering:lot-detail", pk=lot.id)


class LotCreateView(LoginRequiredMixin, generic.CreateView):
    model = Lot
    template_name = "tendering/lot_form.html"
    form_class = LotForm
    success_url = reverse_lazy("tendering:lot-list-active")


class LotUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Lot
    success_url = reverse_lazy("tendering:lot-list-active")
    template_name = "tendering/lot_form.html"
    form_class = LotUpdateForm


class LotDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Lot
    success_url = reverse_lazy("tendering:lot-list-active")
    template_name = "tendering/lot_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        obj = self.object
        if not self.has_permission_to_delete(request, obj):
            return HttpResponseForbidden("You do not have permission to delete this lot.")
        return super().delete(request,*args, **kwargs)


    def has_permission_to_delete(self, request, obj):
        return request.user == obj.owner


class UserCreateView(LoginRequiredMixin, generic.CreateView):
    model = User
    template_name = "tendering/user_form.html"
    success_url = reverse_lazy("tendering:user-list")
    form_class = UserCreateForm


class UserUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = User
    template_name = "tendering/user_update.html"
    form_class = UserUpdateForm

    def get_success_url(self):
        return self.object.get_absolute_url()


class UserDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = User
    template_name = "tendering/user_confirm_delete.html"
    success_url = reverse_lazy("tendering:user-list")