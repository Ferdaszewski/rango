from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.db import IntegrityError

from rango.forms import CategoryForm, PageForm
from rango.models import Category, Page


def index(request):
    """Returns the main page of the Rango app."""

    # Top 5 categories by likes
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict = {'categories': category_list}

    # Top 5 pages by likes
    page_list = Page.objects.order_by('-views')[:5]
    context_dict['pages'] = page_list

    return render(request, 'rango/index.html', context_dict)


def about(request):
    return render(request, 'rango/about.html')


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


def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            try:
                form.save(commit=True)
                return redirect('index')

            # Database error, name and/or slug not unique
            except IntegrityError:
                form.add_error('name', "That Category already exists!")
        else:
            print form.errors
    else:
        form = CategoryForm()

    # Bad form, form details, no form supplied... Render with any errors
    return render(request, 'rango/add_category.html', {'form': form})


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
    else:
        form = PageForm()

    context_dict = {'form': form, 'category': cat}
    return render(request, 'rango/add_page.html', context_dict)
