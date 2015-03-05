from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import redirect, render

from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from rango.models import Category, Page


def index(request):
    """Returns the main page of the Rango app."""

    # List of all categories, ordered by likes
    category_list = Category.objects.order_by('-likes')

    # Top 5 pages by likes
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}

    # Get site visit count for session, default to 1 if it doesn't exist
    visits = request.session.get('visits', 1)

    reset_last_visit_time = False
    last_visit = request.session.get('last_visit')
    datetime_format = "%Y-%m-%d %H:%M:%S"

    if last_visit:
        last_visit_time = datetime.strptime(last_visit, datetime_format)

        # More than a day since the last visit
        if (datetime.now() - last_visit_time).days > 1:
            visits += 1
            reset_last_visit_time = True
    else:
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = datetime.strftime(
            datetime.now(), datetime_format)
        request.session['visits'] = visits
    context_dict['visits'] = visits

    return render(request, 'rango/index.html', context_dict)


def about(request):

    # Get index visit count, default to 0 if it does not exist
    visits = request.session.get('visits', 0)

    return render(request, 'rango/about.html', {'visits': visits})


def category(request, category_name_slug):
    context_dict = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        context_dict['category'] = category
        context_dict['category_name_slug'] = category_name_slug
    except Category.DoesNotExist:
        pass

    return render(request, 'rango/category.html', context_dict)


@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            try:
                form.save(commit=True)
                return redirect('index')

            # Database error, slug is not unique
            # (i.e. 'Python'.slug == 'python'.slug)
            except IntegrityError:
                form.add_error('name',
                    "That Category is to similar to one that already exists!")
        else:
            print form.errors
    # Not a HTTP POST, prep blank form for render
    else:
        form = CategoryForm()

    # Bad form, form details, no form supplied... Render with any errors
    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                return redirect('category',
                                category_name_slug=category_name_slug)
        else:
            print form.errors
    # Not a HTTP POST, prep blank form for render
    else:
        form = PageForm()

    context_dict = {'form': form, 'category': cat}
    return render(request, 'rango/add_page.html', context_dict)


def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()
            registered = True
        else:
            print user_form.errors, profile_form.errors
    # Not a HTTP POST, so prep blank forms for render
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render template depending on the context
    return render(
        request,
        'rango/register.html',
        {'user_form': user_form, 'profile_form': profile_form,
            'registered': registered}
        )


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Have Django attempt to see if username/password is valid
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect('/rango/')
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # Request is not a HTTP POST, display the login form
    else:
        return render(request, 'rango/login.html', {})


@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})


@login_required
def user_logout(request):
    logout(request)
    return redirect('/rango/')
