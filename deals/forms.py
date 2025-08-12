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
            'agreement_date': forms.DateInput(attrs={  # Изменено с DateTimeInput на DateInput
                'type': 'date',  # Изменено с datetime-local на date
                'class': 'form-control'
            }),
            'total_sum': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'class': 'form-control'
            }),
            'total_amount': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'class': 'form-control'
            }),
            'agreement_code': forms.TextInput(attrs={'class': 'form-control'}),
            'creditor': forms.Select(attrs={'class': 'form-select'}),
            'creditor_first': forms.Select(attrs={'class': 'form-select'}),
            'agreement_type': forms.Select(attrs={'class': 'form-select'}),
            'agreement_doc': forms.FileInput(attrs={'class': 'form-control'}),
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
            'date_placement': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'date_finish': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'cession_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'total_sum': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'class': 'form-control'
            }),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'process_type': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, agreement=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.agreement = agreement
        
        # Если это редактирование, используем существующий объект
        if self.instance and self.instance.pk:
            self.agreement = self.instance.agreement