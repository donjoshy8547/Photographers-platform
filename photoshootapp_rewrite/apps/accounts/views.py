"""
Authentication Views - Login, Register, Logout, Profile Management
Clean, class-based views with proper separation of concerns
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.paginator import Paginator

from apps.accounts.models import CustomUser, UserRole
from apps.accounts.services import AuthenticationService, ProfileService
from apps.accounts.forms import (
    UserRegistrationForm, 
    PhotographerProfileForm, 
    UserProfileForm
)


# ============== Authentication Views ==============

class RegisterView(CreateView):
    """User registration view"""
    template_name = 'accounts/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('accounts:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Register'
        return context
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')
        role = form.cleaned_data.get('role')
        
        user, error = AuthenticationService.register_user(
            username=username,
            email=email,
            password=password,
            role=role,
            first_name=form.cleaned_data.get('first_name', ''),
            last_name=form.cleaned_data.get('last_name', ''),
        )
        
        if user:
            messages.success(
                self.request,
                f'Account created successfully! Please login.'
            )
            return redirect(self.success_url)
        else:
            messages.error(self.request, error)
            return self.form_invalid(form)


class CustomLoginView(auth_views.LoginView):
    """Custom login view"""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Login'
        return context
    
    def form_valid(self, form):
        user, error = AuthenticationService.login_user(
            self.request,
            form.cleaned_data.get('username'),
            form.cleaned_data.get('password')
        )
        
        if user:
            return redirect('accounts:dashboard')
        else:
            messages.error(self.request, error)
            return self.form_invalid(form)


class CustomLogoutView(auth_views.LogoutView):
    """Custom logout view"""
    next_page = 'accounts:login'


class DashboardView(DetailView):
    """User dashboard - role-specific"""
    model = CustomUser
    template_name = 'accounts/dashboard.html'
    context_object_name = 'user'
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context['page_title'] = 'Dashboard'
        
        # Role-specific data
        if user.is_photographer:
            profile = ProfileService.get_photographer_profile(user)
            context['profile'] = profile
            context['events_count'] = user.events_hosted.count() if hasattr(user, 'events_hosted') else 0
            context['template'] = 'accounts/photographer_dashboard.html'
        elif user.is_client:
            profile = ProfileService.get_client_profile(user)
            context['profile'] = profile
            context['bookings_count'] = user.bookings.count() if hasattr(user, 'bookings') else 0
            context['template'] = 'accounts/client_dashboard.html'
        elif user.is_assistant:
            profile = user.assistant_profile if hasattr(user, 'assistant_profile') else None
            context['profile'] = profile
            context['template'] = 'accounts/assistant_dashboard.html'
        else:
            context['template'] = 'accounts/admin_dashboard.html'
        
        return context


# ============== Profile Views ==============

@login_required
def profile_view(request):
    """View current user profile"""
    user = request.user
    template_name = 'accounts/profile.html'
    
    context = {
        'page_title': 'My Profile',
        'user': user,
    }
    
    if user.is_photographer:
        context['profile'] = ProfileService.get_photographer_profile(user)
    
    return render(request, template_name, context)


@login_required
def edit_profile_view(request):
    """Edit user profile"""
    user = request.user
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        
        if form.is_valid():
            ProfileService.update_user_profile(
                user,
                **form.cleaned_data
            )
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=user)
    
    return render(request, 'accounts/edit_profile.html', {
        'page_title': 'Edit Profile',
        'form': form,
    })


@login_required
def edit_photographer_profile_view(request):
    """Edit photographer-specific profile"""
    if not request.user.is_photographer:
        messages.error(request, 'Access denied')
        return redirect('accounts:dashboard')
    
    profile = ProfileService.get_photographer_profile(request.user)
    
    if request.method == 'POST':
        form = PhotographerProfileForm(request.POST, instance=profile)
        
        if form.is_valid():
            ProfileService.update_photographer_profile(
                request.user,
                **form.cleaned_data
            )
            messages.success(request, 'Photographer profile updated!')
            return redirect('accounts:profile')
    else:
        form = PhotographerProfileForm(instance=profile)
    
    return render(request, 'accounts/edit_photographer_profile.html', {
        'page_title': 'Edit Photographer Profile',
        'form': form,
    })


# ============== Password Reset Views ==============

class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/emails/password_reset_email.txt'
    subject_template_name = 'accounts/emails/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')


class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'


# ============== Photographer Directory ==============

def photographer_list_view(request):
    """List all available photographers"""
    city = request.GET.get('city')
    specialty = request.GET.get('specialty')
    
    photographers = ProfileService.get_available_photographers(
        city=city,
        specialty=specialty
    )
    
    # Pagination
    paginator = Paginator(photographers, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/photographer_list.html', {
        'page_title': 'Find Photographers',
        'page_obj': page_obj,
        'cities': CustomUser.objects.filter(
            role=UserRole.PHOTOGRAPHER,
            city__isnull=False
        ).values_list('city', flat=True).distinct(),
    })


def photographer_detail_view(request, username):
    """View photographer public profile"""
    photographer = get_object_or_404(
        CustomUser,
        username=username,
        role=UserRole.PHOTOGRAPHER
    )
    
    profile = ProfileService.get_photographer_profile(photographer)
    
    return render(request, 'accounts/photographer_detail.html', {
        'page_title': photographer.full_name,
        'photographer': photographer,
        'profile': profile,
    })