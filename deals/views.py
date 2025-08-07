from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from .models import Agreement, Portfolio
from .forms import AgreementForm, PortfolioForm


class DashboardView(TemplateView):
    template_name = 'deals/dashboard.html'

    def get(self, request, *args, **kwargs):
        if not request.GET.get('agreement'):
            first = Agreement.objects.order_by('-id').first()
            if first:
                return redirect(f"{reverse_lazy('deals:dashboard')}?agreement={first.pk}")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # параметры сортировки
        sort = self.request.GET.get('sort', 'id')
        direction = self.request.GET.get('dir', 'desc')

        allowed = {'id', 'agreement_code', 'agreement_date', 'total_sum'}
        if sort == 'creditor':
            order = f"{'-' if direction == 'desc' else ''}creditor__name"
        elif sort == 'agreement_type':
            order = f"{'-' if direction == 'desc' else ''}agreement_type"
        elif sort in allowed:
            order = f"{'-' if direction == 'desc' else ''}{sort}"
        else:
            order = '-id'

        ctx['agreements'] = Agreement.objects.select_related('creditor').order_by(order)
        ctx['current_sort'] = sort
        ctx['current_dir'] = direction
        ctx['rev_dir'] = 'desc' if direction == 'asc' else 'asc'

        aid = self.request.GET.get('agreement')
        if aid and aid.isdigit():
            ctx['current_agreement'] = Agreement.objects.filter(pk=aid).first()
        else:
            ctx['current_agreement'] = None
        return ctx


class AgreementCreateView(CreateView):
    model = Agreement
    form_class = AgreementForm
    template_name = 'deals/generic_form.html'
    success_url = reverse_lazy('deals:dashboard')


class AgreementUpdateView(UpdateView):
    model = Agreement
    form_class = AgreementForm
    template_name = 'deals/generic_form.html'
    success_url = reverse_lazy('deals:dashboard')


class AgreementDeleteView(DeleteView):
    model = Agreement
    template_name = 'deals/generic_confirm_delete.html'
    success_url = reverse_lazy('deals:dashboard')

    def delete(self, request, *args, **kwargs):
        messages.success(request, f"Договор №{self.get_object().id} удалён.")
        return super().delete(request, *args, **kwargs)


class PortfolioCreateView(CreateView):
    model = Portfolio
    form_class = PortfolioForm
    template_name = 'deals/generic_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.agreement = get_object_or_404(Agreement, pk=kwargs['agreement_pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.agreement = self.agreement
        return super().form_valid(form)

    def get_success_url(self):
        return "{}?agreement={}".format(
            reverse_lazy('deals:dashboard'),
            self.agreement.pk
        )


class PortfolioUpdateView(UpdateView):
    model = Portfolio
    form_class = PortfolioForm
    template_name = 'deals/generic_form.html'

    def get_success_url(self):
        return "{}?agreement={}".format(
            reverse_lazy('deals:dashboard'),
            self.object.agreement.pk
        )


class PortfolioDeleteView(DeleteView):
    model = Portfolio
    template_name = 'deals/generic_confirm_delete.html'

    def get_success_url(self):
        return "{}?agreement={}".format(
            reverse_lazy('deals:dashboard'),
            self.object.agreement.pk
        )

    def delete(self, request, *args, **kwargs):
        messages.success(request, f"Портфель «{self.get_object().label}» удалён.")
        return super().delete(request, *args, **kwargs)