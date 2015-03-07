from datetime import datetime
from django.core.urlresolvers import reverse
from django.test import TestCase
import pytz
from rango.models import Category, Page


def add_cat(name, views=0, likes=0):
    """Helper method to create a new category."""
    c = Category.objects.get_or_create(name=name)[0]
    c.views = views
    c.likes = likes
    c.save()
    return c


def add_page(category, title, url):
    """Helper method to create a new page."""
    p = Page.objects.get_or_create(
        category=category,
        title=title,
        url=url)[0]
    p.save()
    return p


class CategoryMethodTests(TestCase):

    def test_ensure_views_are_positive(self):
        """Should result in True for categories where views are zero
        or positive.
        """
        cat = add_cat(name='test', views=-1, likes=0)
        self.assertTrue(cat.views >= 0)

    def test_slug_line_creation(self):
        """Checks to make sure that when we add a category an
        appropriate slug line is created.
        """
        cat = add_cat(name='Random Category String')
        self.assertEqual(cat.slug, 'random-category-string')

    def test_slug_does_not_change_on_category_name_change(self):
        """Checks to make sure that the slug line does not change when
        the category name is changed.
        """
        cat = add_cat(name='Random Category')
        category = Category.objects.get(name='Random Category')
        slug_before = category.slug
        category.name = 'Another Category Name'
        category.save()
        self.assertEqual(category.slug, slug_before)

    def test_index_view_with_no_categories(self):
        """If not categories exist, an appropriate message should be
        displayed on the page.
        """
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are not categories currently.")
        self.assertQuerysetEqual(response.context['categories'], [])

    def test_index_view_with_categories(self):
        """If categories exist, their names should be displayed."""
        add_cat('test', 1, 1)
        add_cat('temp', 1, 1)
        add_cat('tmp', 1, 1)
        add_cat('a temporary category', 1, 1)

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "a temporary category")

        self.assertEqual(len(response.context['categories']), 4)

    def test_ensure_first_visit_is_not_future(self):
        """Ensure that first page visit is not in the future."""
        cat = add_cat(name='A new Category')
        page = add_page(
            category=cat,
            title='python.org',
            url='http://python.org')

        # 'Visit' the webpage
        response = self.client.get(reverse('goto'), {'page_id': page.id})

        page = Page.objects.get(id=page.id)
        self.assertTrue(datetime.now(pytz.utc) > page.first_visit)

    def test_ensure_last_visit_is_past(self):
        """Ensure that the last page visit is not in the future."""
        cat = add_cat(name='B new Category')
        page = add_page(
            category=cat,
            title='montypython.com',
            url='http://montypython.com/')

        # 'Visit' the webpage
        response = self.client.get(reverse('goto'), {'page_id': page.id})

        page = Page.objects.get(id=page.id)
        self.assertTrue(datetime.now(pytz.utc) > page.last_visit)


    def test_ensure_first_visit_is_before_last_visit(self):
        """Ensure that the first page visit is before the last page
        visit.
        """
        cat = add_cat(name='And Eggs')
        page = add_page(
            category=cat,
            title='spam.com',
            url='http://spam.com/')

        # 'Visit' the webpage
        response = self.client.get(reverse('goto'), {'page_id': page.id})

        page = Page.objects.get(id=page.id)
        self.assertTrue(page.first_visit < page.last_visit)
