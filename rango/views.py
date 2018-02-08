from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm

def index(request):
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by no. likes in descending order
    # Retrieve the top 5 only - or all if less than 5
    # Place the list in our context_dict dictionary
    # that will be passed to the template engine.
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = { 'categories' : category_list,
                    'pages' : page_list}
    return render(request, 'rango/index.html', context_dict)

def about(request):
    context_dict = { 'user' : "Martin Ganly"}
    return render(request, 'rango/about.html', context=context_dict)

def polls(request):
    context_dict = { }
    return render(request, 'rango/poll.html', context=context_dict)

def tests(request):
    context_dict = { }
    return render(request, 'rango/tests.html', context=context_dict)

def show_category(request, category_name_slug):
    # Create a context dictonary which we can passed
    # to the template rendering engime.
    context_dict = {}

    try:
        # Can we find a category ane mslut with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception
        # So the .get() method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)

        # Retrieve all of the associated pages.
        # Note that filter() will return a list of page objects or an empty lists
        pages = Page.objects.filter(category=category)

        # Adds our results list to the template context under name other_pages
        context_dict['pages'] = pages
        # We also add the category object from
        # the database to the context dictionary
        # We'll use this in the template to verify that the category exists
        context_dict['category'] = category
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category
        # Don't do anything - the template will display 'no category' for us
        context_dict['category'] = None
        context_dict['pages'] = None

    # Go render the response and return it to the client
    return render(request, 'rango/category.html', context_dict)

def add_category(request):
    form = CategoryForm()

    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database
            form.save(commit=True)
            # Now that the category is saved we could give a confirmation message
            # But since the most recent category added is on the index page then we can direct the user back to the index page
            return index(request)
        else:
            print(form.errors)
        # Will handle the bad form, new form or no form supplied cases.
        # Render the form with error messages (if any)
    return render(request, 'rango/add_category.html', {'form' : form})

def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)

    context_dict = {'form':form, 'category':category}
    return render(request, 'rango/add_page.html', context_dict)