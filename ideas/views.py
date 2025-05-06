

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import UpdateView
from django.views import generic
from django.views.generic import DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import Q
from .models import Idea, Category
from .forms import SignUpForm, IdeaForm

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('browse_ideas')  # Redirect to homepage after login
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login page after signup
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})

def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('browse_ideas')   
    else:
        return redirect('login')

@login_required
def idea_list(request):
    # Get search query and category filter
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    
    # Start with all ideas
    ideas = Idea.objects.all().order_by('-created_at')
    
    # Apply search if provided
    if query:
        ideas = ideas.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        )
    
    # Apply category filter if provided
    if category_id:
        ideas = ideas.filter(categories__id=category_id)
    
    # Get all categories for the filter dropdown
    categories = Category.objects.all()
    
    return render(request, 'ideas/idea_list.html', {
        'ideas': ideas,
        'categories': categories,
        'query': query,
        'selected_category': int(category_id) if category_id else None
    })

from django.shortcuts import render, get_object_or_404
from .models import Idea
from django.contrib.auth.decorators import login_required

@login_required
def idea_detail(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    print(f"Idea ID: {idea.id}")  # Print the Idea ID
    print(f"Idea Title: {idea.title}")
    print(f"Idea Creator: {idea.created_by}")  # Print the creator (User object or None)
    if idea.created_by:
        print(f"Idea Creator Username: {idea.created_by.username}")
    is_creator = (request.user == idea.created_by)
    print(f"Is Creator: {is_creator}")
    context = {
        'idea': idea,
        'is_creator': is_creator,
    }
    return render(request, 'ideas/idea_detail.html', context)

@login_required
def idea_create(request):
    if request.method == 'POST':
        form = IdeaForm(request.POST)
        if form.is_valid():
            idea = form.save(commit=False)
            idea.created_by = request.user
            idea.save()
            form.save_m2m()  # Save many-to-many relationships
            return redirect('idea_detail', pk=idea.pk)
    else:
        form = IdeaForm()
        return render(request, 'ideas/idea_form.html', {
        'form': form,
        'edit_mode': False,
        'idea': None,
    })

@login_required
def idea_edit(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    
    # Check if the user is the owner of the idea
    if idea.created_by != request.user:
        return redirect('idea_detail', pk=idea.pk)
    
    if request.method == 'POST':
        form = IdeaForm(request.POST, instance=idea)
        if form.is_valid():
            form.save()
            return redirect('idea_detail', pk=idea.pk)
    else:
        form = IdeaForm(instance=idea)
    
    return render(request, 'ideas/idea_form.html', {
        'form': form,
        'edit_mode': True,
        'idea': idea,   # needed for cancel link
    })

@login_required
def dashboard(request):
    ideas         = request.user.ideas.all()
    sent_reqs     = request.user.sent_requests.all()
    received_reqs = request.user.received_requests.filter(status='pending')
    return render(request, 'ideas/dashboard.html', {
        'ideas':          ideas,
        'sent_reqs':      sent_reqs,
        'received_reqs':  received_reqs,
    })

@login_required
def submit_idea(request):
    if request.method == 'POST':
        form = IdeaForm(request.POST)
        if form.is_valid():
            idea = form.save(commit=False)
            idea.created_by = request.user
            idea.save()
            form.save_m2m()
            return redirect('idea_detail', pk=idea.pk)
    else:
        form = IdeaForm()
    categories = Category.objects.all()
    return render(request, 'ideas/submit_idea.html', {
        'form': form,
        'categories': categories,
    })

from django.shortcuts import get_object_or_404


from django.http import HttpResponseForbidden

@login_required
def delete_idea(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    if request.user != idea.created_by:
        return HttpResponseForbidden("You are not allowed to delete this idea.")

    if request.method == 'POST':
        idea.delete()
        return redirect('dashboard')  # or wherever you want to send them after delete

    return render(request, 'ideas/delete_idea_confirm.html', {'idea': idea})

from django.shortcuts import render
from .models import Idea

@login_required
def browse_ideas(request):
    # 1) read the category ID from GET (e.g. /ideas/?category=3)
    category_id = request.GET.get('category', '')

    # 2) get all ideas, then filter if a category was chosen
    ideas = Idea.objects.all().order_by('-created_at')
    if category_id:
        ideas = ideas.filter(categories__id=category_id)

    # 3) pass the full list of categories so the template can build the dropdown
    categories = Category.objects.all()

    return render(request, 'ideas/browse_ideas.html', {
        'ideas': ideas,
        'categories': categories,
    })

from django.shortcuts import render, get_object_or_404, redirect
from .models import Idea, CollaborationRequest, Profile, JoinRequest
from .forms import ProfileForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

@login_required
def request_collab(request, pk):
    # Get the idea to collaborate on
    idea = get_object_or_404(Idea, pk=pk)
    
    # Prevent sending collaboration request to your own idea
    if idea.created_by == request.user:
        return HttpResponseForbidden("You can't request collaboration on your own idea.")

    # Ensure the user has not already requested collaboration
    if CollaborationRequest.objects.filter(idea=idea, sender=request.created_by).exists():
        return redirect('browse_ideas')

    # Create a new collaboration request
    CollaborationRequest.objects.create(
        idea=idea,
        sender=request.created_by,
        receiver=idea.created_by,
        status='pending'  # Default status for new requests
    )

    return redirect('browse_ideas')

@login_required
def profile_view(request):
    user_profile = Profile.objects.get(user=request.user)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        department = request.POST.get('department')
        resume = request.FILES.get('resume')

        user_profile.name = name
        user_profile.department = department
        if resume:
            user_profile.resume = resume
        user_profile.save()

    user_profile.refresh_from_db()

    context = {
        'user_profile': user_profile
    }
    return render(request, 'profile.html', context)


from django.http import HttpResponseNotAllowed

@login_required
def logout_view(request):
    if request.method == 'POST':  # This view should handle POST requests for logout
        logout(request)
        return redirect('login')
    return HttpResponseNotAllowed("Method Not Allowed")

from django.shortcuts import redirect
from django.contrib.auth import logout
from django.http import HttpResponseForbidden

# Custom logout view
def custom_logout(request):
    # Check if the request method is POST
    if request.method == 'POST':
        logout(request)  # Log the user out
        return redirect('login')  # Redirect to the login page after logout
    
    # If it's not a POST request, return HTTP 405 (Method Not Allowed)
    return HttpResponseForbidden("Method Not Allowed")

class IdeaEditView(UpdateView):
    model = Idea
    form_class = IdeaForm
    template_name = 'ideas/idea_edit.html'

    def get_success_url(self):
        return reverse('idea_detail', kwargs={'pk': self.object.pk})
    
class IdeaDeleteView(DeleteView):
    model = Idea
    template_name = 'ideas/idea_confirm_delete.html'
    success_url = reverse_lazy('dashboard')  # Redirect to dashboard after deletion

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Idea, JoinRequest

@login_required
def send_join_request(request, idea_id):
    # Get the idea object, or return 404 if it doesn't exist
    idea = get_object_or_404(Idea, id=idea_id)
    
    # Create the JoinRequest object
    JoinRequest.objects.create(idea=idea, applicant=request.user)
    
    # Redirect to the 'idea_detail' view, passing 'pk' instead of 'idea_id'
    return redirect('idea_detail', pk=idea.id)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Idea, JoinRequest

@login_required
def user_manage_requests(request):  # Renamed to user_manage_requests
    ideas = Idea.objects.filter(created_by=request.user)
    join_requests = JoinRequest.objects.filter(idea__in=ideas) # Changed to JoinRequest
    return render(request, 'ideas/user_manage_requests.html', {
        'join_requests': join_requests,
    })

@login_required
def idea_manage_requests(request, idea_id):  # Renamed to idea_manage_requests
    # Get the idea object
    idea = get_object_or_404(Idea, id=idea_id)

    # Make sure the user is the owner of the idea
    if request.user != idea.owner:
        return redirect('home')  # Or a 'not authorized' page

    # Get all join requests for this idea
    join_requests = JoinRequest.objects.filter(idea=idea)

    return render(request, 'ideas/idea_manage_requests.html', {'idea': idea, 'join_requests': join_requests}) #changed template name

@login_required
def accept_request(request, idea_id, request_id):
    idea = get_object_or_404(Idea, id=idea_id)
    join_request = get_object_or_404(JoinRequest, id=request_id)

    # Ensure the user is the owner of the idea
    if request.user != idea.created_by:
        return redirect('home')

    # Accept the request and change its status
    join_request.status = 'accepted'
    join_request.save()

    # Optionally, add the applicant to the participants of the idea
    idea.collaborators.add(join_request.applicant)

    # Redirect back to the manage requests page
    return redirect('user_manage_requests')


@login_required
def reject_request(request, idea_id, request_id):
    idea = get_object_or_404(Idea, id=idea_id)
    join_request = get_object_or_404(JoinRequest, id=request_id)

    # Ensure the user is the owner of the idea
    if request.user != idea.created_by:
        return redirect('home')

    # Reject the request and change its status
    join_request.status = 'rejected'
    join_request.save()

    # Redirect back to the manage requests page
    return redirect('user_manage_requests', idea_id=idea.id)
