from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()


class EmailLoginForm(AuthenticationForm):
    username = "email"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Email"
        self.fields["password"].label = "Пароль"
        self.fields["username"].widget.attrs.update(
            {"class": "w-full rounded-lg border px-3 py-2 text-sm", "placeholder": "you@example.com"}
        )
        self.fields["password"].widget.attrs.update(
            {"class": "w-full rounded-lg border px-3 py-2 text-sm", "placeholder": "••••••••"}
        )


class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "first_name", "last_name", "school", "city")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({"class": "w-full rounded-lg border px-3 py-2 text-sm"})
            if name != "school" and name != "city":
                field.widget.attrs["required"] = "required"