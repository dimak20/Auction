from django import forms
from django.contrib.auth.forms import UserCreationForm

from tendering.models import Comment, Bid, Lot, User
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
                    raise forms.ValidationError("Your bid must be higher than current price.")
        return amount


class LotForm(forms.ModelForm):
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )
    start_price = forms.DecimalField()


    class Meta:
        model = Lot
        fields = ("name", "description", "category", "end_date", "start_price", )


    def clean(self):
        cleaned_data = super().clean()
        end_date = cleaned_data.get("end_date")
        start_price = cleaned_data.get("start_price")
        if end_date <= timezone.now():
            raise forms.ValidationError("You must set end_date higher than current time")
        if start_price <= 0:
            raise forms.ValidationError("Your start price must be higher than 0")
        return cleaned_data


class LotUpdateForm(forms.ModelForm):
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )


    class Meta:
        model = Lot
        fields = ("description", "end_date", )

    def clean(self):
        cleaned_data = super().clean()
        end_date = cleaned_data.get("end_date")
        if end_date <= timezone.now():
            raise forms.ValidationError("You must set end_date higher than current time")
        return cleaned_data


class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        label="Password",
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm Password",
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserUpdateForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date-local', 'class': 'form-control'})
    )
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "date_of_birth",
            "location",
            "bio",
            "avatar"
        )


class LotSearchForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "placeholder": "search by name"
            }
        )
    )