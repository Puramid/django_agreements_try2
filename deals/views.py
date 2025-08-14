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
            first = Agreement.objects.order_by('id').first()
            if first:
                return redirect(f"{reverse_lazy('deals:dashboard')}?agreement={first.pk}")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Параметры сортировки
        sort = self.request.GET.get('sort', 'id')
        direction = self.request.GET.get('dir', 'asc')

        allowed = {'id', 'agreement_code', 'agreement_date', 'total_sum'}
        if sort == 'creditor':
            order = f"{'-' if direction == 'desc' else ''}creditor__name"
        elif sort == 'agreement_type':
            order = f"{'-' if direction == 'desc' else ''}agreement_type"
        elif sort in allowed:
            order = f"{'-' if direction == 'desc' else ''}{sort}"
        else:
            order = 'id'

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
    template_name = 'deals/agreement_form.html'
    success_url = reverse_lazy('deals:dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Договор №{self.object.id} создан")
        return response


class AgreementUpdateView(UpdateView):
    model = Agreement
    form_class = AgreementForm
    template_name = 'deals/agreement_form.html'
    success_url = reverse_lazy('deals:dashboard')

    def get_initial(self):
        initial = super().get_initial()
        if self.object.agreement_date:
            initial['agreement_date'] = self.object.agreement_date.strftime('%Y-%m-%d')
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Договор №{self.object.id} обновлен")
        return response


class AgreementDeleteView(DeleteView):
    model = Agreement
    template_name = 'deals/generic_confirm_delete.html'
    success_url = reverse_lazy('deals:dashboard')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f"Договор №{obj.id} удалён.")
        return super().delete(request, *args, **kwargs)


class PortfolioCreateView(CreateView):
    model = Portfolio
    form_class = PortfolioForm
    template_name = 'deals/portfolio_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.agreement = get_object_or_404(Agreement, pk=kwargs['agreement_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['agreement'] = self.agreement
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['agreement'] = self.agreement
        return ctx

    def form_valid(self, form):
        form.instance.agreement = self.agreement
        response = super().form_valid(form)
        messages.success(self.request, "Портфель создан.")
        return response

    def get_success_url(self):
        return "{}?agreement={}".format(
            reverse_lazy('deals:dashboard'),
            self.agreement.pk
        )


class PortfolioUpdateView(UpdateView):
    model = Portfolio
    form_class = PortfolioForm
    template_name = 'deals/portfolio_form.html'

    def get_initial(self):
        initial = super().get_initial()
        if self.object.date_placement:
            initial['date_placement'] = self.object.date_placement.strftime('%Y-%m-%d')
        if self.object.date_finish:
            initial['date_finish'] = self.object.date_finish.strftime('%Y-%m-%d')
        if self.object.cession_date:
            initial['cession_date'] = self.object.cession_date.strftime('%Y-%m-%d')
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['agreement'] = self.object.agreement
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['agreement'] = self.object.agreement
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Портфель «{self.object.label}» обновлен")
        return response

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
        obj = self.get_object()
        messages.success(request, f"Портфель «{obj.label}» удалён.")
        return super().delete(request, *args, **kwargs)