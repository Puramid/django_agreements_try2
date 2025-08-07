# deals/forms.py
from django import forms
from .models import Agreement, Portfolio


class AgreementForm(forms.ModelForm):
    class Meta:
        model = Agreement
        fields = [
            'creditor',
            'creditor_first',
            'agreement_code',
            'agreement_date',
            'agreement_type',
            'total_sum',
            'total_amount',
            'agreement_doc',
        ]
        widgets = {
            'agreement_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class PortfolioForm(forms.ModelForm):
    label_preview = forms.CharField(
        label='Имя портфеля (итог)',
        required=False,
        widget=forms.TextInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control-plaintext',
            'id': 'id_label_preview',
        })
    )

    class Meta:
        model = Portfolio
        fields = [
            'label_preview',
            'type',
            'process_type',
            'total_sum',
            'date_placement',
            'date_finish',
            'cession_date',
        ]
        widgets = {
            'date_placement': forms.DateInput(attrs={'type': 'date'}),
            'date_finish': forms.DateInput(attrs={'type': 'date'}),
            'cession_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, agreement=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.agreement = agreement