from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import redirect, render

from rango import bing_search
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from rango.models import Category, Page, UserProfile


def index(request):
    """Returns the main page of the Rango app."""

    # List of top 5 categories, ordered by likes
    category_list = Category.objects.order_by('-likes')[:5]

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

    # If HTTP POST, then search and display results
    if request.method == 'POST':
        query = request.POST['query'].strip()

        # TODO: Emplement site search and return results to context_dict

    # Load all pages for category if they exist
    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        context_dict['category'] = category
        context_dict['category_name_slug'] = category_name_slug
    except Category.DoesNotExist:
        print "Category: {0} not found.".format(category_name_slug)

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
                form.add_error(
                    'name',
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


@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})


def search(request):
    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            result_list = bing_search.run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})


def track_url(request):
    if request.method == "GET" and 'page_id' in request.GET:
        page_id = request.GET['page_id']

        try:
            page = Page.objects.get(id=page_id)
            page.views += 1
            page.save()
            return redirect(page.url)
        except ObjectDoesNotExist:
            print "Page ID: {0} not found.".format(page_id)

    # No page_id or page_id not found, return to homepage
    return redirect('index')

@login_required
def register_profile(request):
    if request.method == 'POST':

        # New or current user can user this form, attach to the
        # UserProfile of the logged in User
        user, _ = UserProfile.objects.get_or_create(user=request.user)
        form = UserProfileForm(request.POST, instance=user)

        if form.is_valid():
            user_profile = form.save(commit=False)

            # Save profile picture if it was selected
            if 'picture' in request.FILES:
                user_profile.picture = request.FILES['picture']

            user_profile.save()
            return redirect('index')
        else:
            print form.errors()

    # Not an HTTP POST, prep blank form for render
    else:
        form = UserProfileForm()

    return render(
        request, 'rango/profile_registration.html', {'form': form})


@login_required
def profile(request):
    user = request.user
    context_dict = {}
    try:
        user_profile = UserProfile.objects.get(user=user)
    except ObjectDoesNotExist:
        user_profile = {}

    return render(request, 'rango/profile.html',
                  {'user': user, 'user_profile': user_profile})
