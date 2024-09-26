from http.client import HTTPResponse

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Sum, Avg, Count, Max, QuerySet
from django.http import HttpRequest, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic

from tendering.forms import (
    CommentForm,
    BidForm,
    LotForm,
    LotUpdateForm,
    UserCreateForm,
    UserUpdateForm,
    LotSearchForm,
)
from tendering.models import (
    Category,
    User,
    Lot,
    Comment,
    Bid
)


def index(request: HttpRequest) -> HTTPResponse:
    num_categories = Category.objects.count()
    num_users = User.objects.count()
    num_lots = Lot.objects.count()
    num_active_lots = Lot.objects.filter(is_active=True).count()
    num_bids = Bid.objects.count()
    sum_lots = Lot.objects.aggregate(total=Sum("current_price"))["total"] or 0
    avg_bids = Lot.objects.annotate(
        participant_count=Count("participant")
    ).aggregate(
        avg=Avg("participant_count")
    )["avg"]

    recent_bids = Bid.objects.select_related("lot", "user").order_by("-created_time")[:5]

    bid_data = [
        {
            "bid_lot": bid.lot.name,
            "bid_id": bid.id,
            "amount": bid.amount,
            "percentage": int(bid.lot.get_progress_percentage()),
            "bidders": bid.lot.participant.count(),
        }
        for bid in recent_bids
    ]

    context = {
        "num_categories": num_categories,
        "num_users": num_users,
        "num_lots": num_lots,
        "num_active_lots": num_active_lots,
        "num_bids": num_bids,
        "sum_lots": sum_lots,
        "avg_bids": round(avg_bids, 2),
        "bids": bid_data,
    }

    return render(request, "pages/index.html", context=context)


def register(request) -> HTTPResponse:
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("tendering:index")
    else:
        form = UserCreateForm()

    return render(
        request,
        "admin_soft/accounts/register.html",
        {"form": form}
    )


class InactiveLotListView(LoginRequiredMixin, generic.ListView):
    model = Lot
    paginate_by = 5
    context_object_name = "inactive_lot_list"
    template_name = "tendering/inactive_list.html"

    def get_context_data(self, *, object_list=None, **kwargs) -> dict:
        context = super(
            InactiveLotListView,
            self
        ).get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = LotSearchForm(initial={"name": name})
        return context

    def get_queryset(self) -> QuerySet:
        queryset = (
            Lot.objects.filter(is_active=False)
            .select_related("category", "owner")
            .prefetch_related("bids__user")
            .order_by("-start_date")
        )
        form = LotSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(
                name__icontains=form.cleaned_data["name"]
            )
        return queryset


def close_expired_lots():
    now = timezone.now()
    expired_lots = Lot.objects.filter(is_active=True, end_date__lte=now)
    for lot in expired_lots:
        lot.is_active = False
        highest_bid = lot.bids.order_by("-amount").first()
        if highest_bid:
            lot.owner = highest_bid.user
        lot.save()


class ActiveLotListView(LoginRequiredMixin, generic.ListView):
    model = Lot
    paginate_by = 5
    context_object_name = "active_lot_list"
    template_name = "tendering/active_list.html"

    def get_context_data(
            self,
            *,
            object_list=None,
            **kwargs
    ) -> dict:
        context = super(
            ActiveLotListView,
            self
        ).get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = LotSearchForm(initial={"name": name})
        return context

    def get_queryset(self) -> QuerySet:
        close_expired_lots()
        queryset = (
            Lot.objects.filter(is_active=True)
            .select_related("category", "owner")
            .prefetch_related("bids__user")
        )
        form = LotSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(
                name__icontains=form.cleaned_data["name"]
            )
        return queryset


class UserListView(LoginRequiredMixin, generic.ListView):
    model = User
    template_name = "tendering/tables.html"
    paginate_by = 8

    def get_queryset(self) -> QuerySet:
        queryset = User.objects.prefetch_related("lots")
        queryset = queryset.annotate(
            bids_count=Count("bids")
        )
        queryset = queryset.annotate(
            last_bid=Max("bids__created_time")
        )
        return queryset


class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = User
    template_name = "pages/profile.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        user = self.object
        lots = (
            Lot.objects.filter(owner=user)
            .select_related("category", "owner")
            .prefetch_related("bids__user")
            .order_by("is_active", "-start_date")
        )
        participating_lots = (
            Lot.objects.filter(bids__user=user, is_active=True)
            .select_related("owner", "category")
            .prefetch_related("bids__user")
        )
        lots_num = lots.count()
        context["my_lots"] = lots
        context["participating_lots"] = participating_lots
        context["lots_num"] = lots_num
        return context


class LotDetailView(LoginRequiredMixin, generic.DetailView):
    model = Lot

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["bid_form"] = BidForm()
        return context


class CommentCreateView(LoginRequiredMixin, generic.CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form) -> HttpResponseRedirect:
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

    def form_valid(self, form) -> HttpResponseRedirect:
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

    def form_invalid(self, form) -> HTTPResponse:
        lot_id = self.kwargs.get("pk")
        lot = get_object_or_404(Lot, id=lot_id)
        context = {
            "lot": lot,
            "bid_form": form,
        }
        return render(
            self.request,
            "tendering/lot_detail.html",
            context
        )


class LotCreateView(LoginRequiredMixin, generic.CreateView):
    model = Lot
    template_name = "tendering/lot_form.html"
    form_class = LotForm
    success_url = reverse_lazy("tendering:lot-list-active")

    def form_valid(self, form) -> None:
        lot = form.save(commit=False)
        lot.current_price = None
        lot.owner = self.request.user
        lot.save()
        return super().form_valid(form)


class LotUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Lot
    template_name = "tendering/lot_form.html"
    form_class = LotUpdateForm

    def get_success_url(self) -> HTTPResponse:
        return reverse_lazy(
            "tendering:lot-detail",
            kwargs={"pk": self.object.id}
        )

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().owner.pk != request.user.pk and not request.user.is_superuser:
            messages.info(request, "This is not your lot")
            return redirect("tendering:index")
        return super().dispatch(request, *args, **kwargs)


class LotDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Lot
    success_url = reverse_lazy("tendering:lot-list-active")
    template_name = "tendering/lot_confirm_delete.html"

    def delete(
            self,
            request,
            *args,
            **kwargs
    ) -> HttpResponseForbidden | None:
        obj = self.get_object()
        if not self.has_permission_to_delete(request, obj):
            return HttpResponseForbidden(
                "You do not have permission to delete this lot."
            )
        return super().delete(request, *args, **kwargs)

    def has_permission_to_delete(self, request, obj) -> bool:
        return request.user == obj.owner or request.user.is_superuser


class UserCreateView(generic.CreateView):
    model = User
    template_name = "tendering/user_form.html"
    success_url = reverse_lazy("tendering:user-list")
    form_class = UserCreateForm


class UserUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = User
    template_name = "tendering/user_update.html"
    form_class = UserUpdateForm

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().pk != request.user.pk and not request.user.is_superuser:
            messages.info(request, "This is not your profile")
            return redirect("tendering:index")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> HTTPResponse:
        return self.object.get_absolute_url()


class UserDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = User
    template_name = "tendering/user_confirm_delete.html"
    success_url = reverse_lazy("tendering:user-list")

    def delete(
            self,
            request,
            *args,
            **kwargs
    ) -> HttpResponseForbidden | None:
        obj = self.get_object()
        if not self.has_permission_to_delete(request, obj):
            return HttpResponseForbidden(
                "You do not have permission to delete this user."
            )
        return super().delete(request, *args, **kwargs)

    def has_permission_to_delete(self, request, obj) -> bool:
        return request.user == obj or request.user.is_superuser


def rules(request: HttpRequest) -> HTTPResponse:
    return render(request, "tendering/rules.html")
