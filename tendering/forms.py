from django import forms
from tendering.models import Comment, Bid, Lot
from django.utils import timezone


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]


class BidForm(forms.ModelForm):

    class Meta:
        model = Bid
        fields = ["amount"]

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        lot_id = self.data.get("lot_id")

        if lot_id:
            lot = Lot.objects.filter(id=lot_id).first()
            if lot:
                if lot.end_date <= timezone.now():
                    raise forms.ValidationError("Sorry, this lot has expired")
                current_price = lot.current_price or lot.start_price
                if amount <= current_price:
                    raise forms.ValidationError("Your bid must be higher than the current price.")
        return amount