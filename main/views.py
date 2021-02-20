from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist 
from django.template.loader import get_template
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView
from django.contrib.messages.views import SuccessMessageMixin 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.signing import BadSignature
from django.core.paginator import Paginator
from django.db.models import Q

from .utilities import signer
from .forms import *
from .models import *


def other_page(request, page):
    try:
        template = get_template(f'{page}.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))


class BulBoardLoginView(LoginView):
    template_name = 'login.html' 
    authentication_form = LoginForm


class BulBoardLogoutView(LogoutView):
    template_name = 'logout.html'


class ChangeUserProfileView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser
    template_name = 'change_user_profile.html'
    form_class = ChangeUserProfileForm
    success_url = reverse_lazy('profile')
    success_message = 'Your profile was changed'

    def dispatch(self, request, *args, **kwargs): 
        self.user_id = request.user.pk 
        return super().dispatch(request, *args, **kwargs)


    def get_object(self, queryset=None): 
        if not queryset: 
            queryset = self.get_queryset() 
        return get_object_or_404(queryset, pk=self.user_id)


class BulBoardPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'password_change.html'
    form_class = ChangeUserPasswordForm
    success_url = reverse_lazy('profile')
    success_message = 'Your password was changed'


class RegistrateUserView(CreateView):
    model = AdvUser
    template_name = 'registrate_user.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('registration_done')


class RegistrationDoneView(TemplateView):
    template_name = 'registration_done.html'


def user_activate(request, sign): 
    try: 
        username = signer.unsign(sign) 
    except BadSignature: 
        return render(request, 'bad_signature.html') 
    user = get_object_or_404(AdvUser, username=username) 
    if user.is_activated: 
        template = 'user_is_activated.html'
    else: 
        template = 'activation_done.html' 
        user.is_active = True 
        user.is_activated = True 
        user.save() 
        return render(request, template)


class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = AdvUser
    template_name = 'delete_user.html'
    success_url = reverse_lazy('index')

    def dispatch(self, request, *args, **kwargs): 
        self.user_id = request.user.pk 
        return super().dispatch(request, *args, **kwargs)


    def post(self, request, *args, **kwargs): 
        logout(request) 
        messages.add_message(request, messages.SUCCESS, f'User {request.user.username} was deleted') 
        return super().post(request, *args, **kwargs)


    def get_object(self, queryset=None): 
        if not queryset: 
            queryset = self.get_queryset() 
        return get_object_or_404(queryset, pk=self.user_id)


class ResetUserPasswordView(PasswordResetView):
    template_name = 'reset_password.html'
    subject_template_name = 'email/reset_password_subject.txt'
    email_template_name = 'email/reset_password_body.txt'
    form_class = UserPasswordResetForm
    from_email = 'liderdrev@ukr.net'


class UserProfileView(LoginRequiredMixin ,TemplateView):
    template_name = 'profile.html'

#make as a listview class
def user_adverts(request):
    bulletins = Bulletin.objects.filter(author=request.user.pk)
    return render(request, 'user_adverts.html', {'bulletins': bulletins})


class RubricsListView(ListView):
    model = SubRubric
    template_name = 'index.html'
    context_object_name = 'rubrics'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bulletins'] = Bulletin.objects.filter(is_active=True)[:4]
        return context


def by_rubric(request, pk):
    rubric = get_object_or_404(SubRubric, pk=pk)   
    bulletins = Bulletin.objects.filter(is_active=True, rubric=pk)
    rubrics = SubRubric.objects.all()
    keyword = None

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword)
        bulletins = Bulletin.objects.filter(q)

    form = SearchForm(initial=keyword)
    paginator = Paginator(bulletins, 2)

    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1

    page = paginator.get_page(page_num)
    context = {'rubric': rubric, 'page': page, 'keyword': keyword, 
                'bulletins': page.object_list, 'form': form, 'rubrics': rubrics}

    return render(request, 'by_rubric.html', context) 


def bulletin_detail(request, from_view, pk):
    bulletin = get_object_or_404(Bulletin, pk=pk) 
    ais = bulletin.additionalimage_set.all() 
    comments = bulletin.comment_set.all()
    rubrics = SubRubric.objects.all()

    initial = {'bulletin': bulletin.pk, 'author': request.user.pk}
    form = CommentForm(initial=initial)

    if request.method == 'POST':
        post_form = CommentForm(request.POST)
        if post_form.is_valid():
            post_form.save()
            messages.add_message(request, messages.SUCCESS, 'Comment was added.')
        else:
            form = post_form
            messages.add_message(request, messages.WARNING, 'Comment was not added.')

    context = {'bulletin': bulletin, 'ais': ais, 'rubrics': rubrics, 
                            'from_view': from_view, 'form': form, 'comments': comments}
    return render(request, 'detail.html', context)               


@login_required
def add_bulletin(request):
    if request.method == 'POST':
        form = BulletinForm(request.POST, request.FILES)
        formset = AdditionalImagesFormSet(request.POST, request.FILES, instance=bulletin)

        if form.is_valid():
            bulletin = form.save()
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Bulletin was added')
                return redirect('profile')
    else:
        form = BulletinForm(initial={'author': request.user.pk})
        formset = AdditionalImagesFormSet()
    context = {'form': form, 'formset': formset}
    return render(request, 'add_bulletin.html', context)


@login_required
def update_bulletin(request, pk):
    bulletin = get_object_or_404(Bulletin, pk=pk)
    if request.method == 'POST':
        form = BulletinForm(request.POST, request.FILES, instance=bulletin)
        formset = AdditionalImagesFormSet(request.POST, request.FILES, instance=bulletin)
        if form.is_valid():
            form.save()
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Bulletin was updated')
                return redirect('profile')
    else:
        form = BulletinForm(instance=bulletin)
        formset = AdditionalImagesFormSet(instance=bulletin)
        context = {'form': form, 'formset': formset}
    return render(request, 'add_bulletin.html', context)


class BulletinDeleteView(LoginRequiredMixin, DeleteView):
    model = Bulletin
    template_name = 'delete_bulletin.html'
    success_url = reverse_lazy('profile')