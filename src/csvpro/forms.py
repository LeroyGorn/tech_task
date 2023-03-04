from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import modelformset_factory

from csvpro.models import DataColumn, DataSchema


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
            }
        )
    )


class SchemaForm(forms.ModelForm):
    class Meta:
        model = DataSchema
        fields = (
            "name",
            "column_separator",
            "string_character",
        )

    def __init__(self, *args, **kwargs):
        super(SchemaForm, self).__init__(*args, **kwargs)
        SEPARATOR_CHOICES = (
            (",", "Comma (,)"),
            (".", "Dot (.)"),
            ("|", "Line (|)"),
            ("/", "Slash (/)"),
        )
        CHAR_CHOICES = (
            ('""', 'Double quote (")'),
            ("'", "Single quote (')"),
        )
        self.fields["name"] = forms.CharField(label="Name")
        self.fields["column_separator"] = forms.ChoiceField(label="Column separator", choices=SEPARATOR_CHOICES)
        self.fields["string_character"] = forms.ChoiceField(label="String character", choices=CHAR_CHOICES)


class SchemaColumnForm(forms.ModelForm):
    prefix = "form"

    class Meta:
        model = DataColumn
        fields = ("column_type", "column_name", "order", "to_value", "from_value")

    def __init__(self, *args, **kwargs):
        super(SchemaColumnForm, self).__init__(*args, **kwargs)
        self.fields['order'] = forms.DecimalField(
            min_value=0, required=True
        )
        self.fields["from_value"] = forms.DecimalField(
            min_value=0, required=False, widget=forms.NumberInput(attrs={
                "disabled": True,
            })
        )
        self.fields["to_value"] = forms.DecimalField(
            min_value=0, required=False, widget=forms.NumberInput(attrs={"disabled": True})
        )


ColumnFormset = forms.formset_factory(
    form=SchemaColumnForm,
)
