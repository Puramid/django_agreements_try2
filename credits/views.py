from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Agreement, Portfolio
from .forms import AgreementForm, PortfolioForm


def dashboard_view(request):
    """Dashboard view showing agreements and portfolios"""
    # Redirect to first agreement if none selected
    if not request.GET.get('agreement'):
        first = Agreement.objects.order_by('id').first()
        if first:
            return redirect(f"{reverse('credits:dashboard')}?agreement={first.pk}")
    
    # Get sorting parameters
    sort = request.GET.get('sort', 'id')
    direction = request.GET.get('dir', 'asc')
    
    # Build ordering
    allowed = {'id', 'agreement_code', 'agreement_date', 'total_sum'}
    if sort == 'creditor':
        order = f"{'-' if direction == 'desc' else ''}creditor__name"
    elif sort == 'agreement_type':
        order = f"{'-' if direction == 'desc' else ''}agreement_type"
    elif sort in allowed:
        order = f"{'-' if direction == 'desc' else ''}{sort}"
    else:
        order = 'id'
    
    # Get agreements with sorting
    agreements = Agreement.objects.select_related('creditor').order_by(order)
    
    # Get current agreement
    aid = request.GET.get('agreement')
    current_agreement = None
    if aid and aid.isdigit():
        current_agreement = Agreement.objects.filter(pk=aid).first()
    
    context = {
        'agreements': agreements,
        'current_agreement': current_agreement,
        'current_sort': sort,
        'current_dir': direction,
        'rev_dir': 'desc' if direction == 'asc' else 'asc',
    }
    
    return render(request, 'credits/dashboard.html', context)


def agreement_create_view(request):
    """Create new agreement"""
    if request.method == 'POST':
        form = AgreementForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Договор создан.")
            return redirect('credits:dashboard')
    else:
        form = AgreementForm()
    
    context = {
        'form': form,
        'view': type('View', (), {'object': None})(),
    }
    return render(request, 'credits/agreement_form.html', context)


def agreement_update_view(request, pk):
    """Update existing agreement"""
    agreement = get_object_or_404(Agreement, pk=pk)
    
    if request.method == 'POST':
        form = AgreementForm(request.POST, request.FILES, instance=agreement)
        if form.is_valid():
            # Update fields manually to handle date logic
            agreement.creditor = form.cleaned_data['creditor']
            agreement.creditor_first = form.cleaned_data['creditor_first']
            agreement.agreement_code = form.cleaned_data['agreement_code']
            agreement.agreement_date = form.cleaned_data['agreement_date'] or agreement.agreement_date
            agreement.agreement_type = form.cleaned_data['agreement_type']
            agreement.total_sum = form.cleaned_data['total_sum']
            agreement.total_amount = form.cleaned_data['total_amount']
            
            # Update document if uploaded
            if 'agreement_doc' in form.cleaned_data and form.cleaned_data['agreement_doc']:
                agreement.agreement_doc = form.cleaned_data['agreement_doc']
            
            agreement.save()
            messages.success(request, f"Договор №{agreement.id} обновлен")
            return redirect('credits:dashboard')
    else:
        # Set initial values for dates
        initial = {}
        if agreement.agreement_date:
            initial['agreement_date'] = agreement.agreement_date.strftime('%Y-%m-%d')
        form = AgreementForm(instance=agreement, initial=initial)
    
    context = {
        'form': form,
        'view': type('View', (), {'object': agreement})(),
    }
    return render(request, 'credits/agreement_form.html', context)


def agreement_delete_view(request, pk):
    """Delete agreement"""
    agreement = get_object_or_404(Agreement, pk=pk)
    
    if request.method == 'POST':
        agreement_id = agreement.id
        agreement.delete()
        messages.success(request, f"Договор №{agreement_id} удалён.")
        return redirect('credits:dashboard')
    
    context = {
        'object': agreement,
    }
    return render(request, 'credits/generic_confirm_delete.html', context)


def portfolio_create_view(request, agreement_pk):
    """Create new portfolio for specific agreement"""
    agreement = get_object_or_404(Agreement, pk=agreement_pk)
    
    if request.method == 'POST':
        form = PortfolioForm(request.POST, agreement=agreement)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.agreement = agreement
            portfolio.save()
            messages.success(request, "Портфель создан.")
            return redirect(f"{reverse('credits:dashboard')}?agreement={agreement.pk}")
    else:
        form = PortfolioForm(agreement=agreement)
    
    context = {
        'form': form,
        'agreement': agreement,
        'view': type('View', (), {'object': None, 'kwargs': {'agreement_pk': agreement_pk}})(),
    }
    return render(request, 'credits/portfolio_form.html', context)


def portfolio_update_view(request, pk):
    """Update existing portfolio"""
    portfolio = get_object_or_404(Portfolio, pk=pk)
    
    if request.method == 'POST':
        form = PortfolioForm(request.POST, instance=portfolio, agreement=portfolio.agreement)
        if form.is_valid():
            # Update fields manually to handle date logic
            portfolio.type = form.cleaned_data['type']
            portfolio.process_type = form.cleaned_data['process_type']
            portfolio.total_sum = form.cleaned_data['total_sum']
            portfolio.date_placement = form.cleaned_data['date_placement'] or portfolio.date_placement
            portfolio.date_finish = form.cleaned_data['date_finish'] or portfolio.date_finish
            portfolio.cession_date = form.cleaned_data['cession_date'] or portfolio.cession_date
            
            # Update label based on new data
            portfolio.label = (
                f"{portfolio.agreement.creditor}_"
                f"{portfolio.agreement.get_agreement_type_display()}_"
                f"{portfolio.date_placement.strftime('%d.%m.%Y')}_"
                f"{portfolio.get_process_type_display()}"
            )
            
            portfolio.save()
            messages.success(request, f"Портфель «{portfolio.label}» обновлен")
            return redirect('credits:dashboard')
    else:
        # Set initial values for dates
        initial = {}
        if portfolio.date_placement:
            initial['date_placement'] = portfolio.date_placement.strftime('%Y-%m-%d')
        if portfolio.date_finish:
            initial['date_finish'] = portfolio.date_finish.strftime('%Y-%m-%d')
        if portfolio.cession_date:
            initial['cession_date'] = portfolio.cession_date.strftime('%Y-%m-%d')
        form = PortfolioForm(instance=portfolio, initial=initial, agreement=portfolio.agreement)
    
    context = {
        'form': form,
        'agreement': portfolio.agreement,
        'view': type('View', (), {'object': portfolio})(),
    }
    return render(request, 'credits/portfolio_form.html', context)


def portfolio_delete_view(request, pk):
    """Delete portfolio"""
    portfolio = get_object_or_404(Portfolio, pk=pk)
    
    if request.method == 'POST':
        portfolio_label = portfolio.label
        agreement_pk = portfolio.agreement.pk
        portfolio.delete()
        messages.success(request, f"Портфель «{portfolio_label}» удалён.")
        return redirect(f"{reverse('credits:dashboard')}?agreement={agreement_pk}")
    
    context = {
        'object': portfolio,
    }
    return render(request, 'credits/generic_confirm_delete.html', context)