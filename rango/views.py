from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime

def index(request):
    request.session.set_test_cookie()
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by no. likes in descending order
    # Retrieve the top 5 only - or all if less than 5
    # Place the list in our context_dict dictionary
    # that will be passed to the template engine.
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = { 'categories' : category_list,
                    'pages' : page_list}

    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']

    response = render(request, 'rango/index.html', context_dict)
    return response

def about(request):
    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()
    context_dict = { 'user' : "Martin Ganly"}

    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']

    response = render(request, 'rango/about.html', context_dict)
    return response

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

@login_required
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

@login_required
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

def register(request):
    # A boolean value for telling the template
    # whether the registration was successful.
    # Set to False initially. Code changes value to
    # True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves,
            # we set commit=False. This delays saving the model
            # until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and
            #put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            # Now we save the UserProfile model instance.
            profile.save()
            # Update our variable to indicate that the template
            # registration was successful.
            registered = True
        else:
            # Invalid form or forms - mistakes or something else?
            # Print problems to the terminal.
            print(user_form.errors, profile_form.errors)
    else:
            # Not a HTTP POST, so we render our form using two ModelForm instances.
            # These forms will be blank, ready for user input.
            user_form = UserForm()
            profile_form = UserProfileForm()

            # Render the template depending on the context.
    return render(request, 'rango/register.html', {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):
    # If form submitted get data
    if request.method =='POST':
        # set account details variables from user input
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check details are correct
        user = authenticate(username = username, password = password)
        if user:
            # Check account is active
            if user.is_active:
                # log user in and redirect to homepage
                login(request,user)
                return HttpResponseRedirect(reverse('index'))
            else:
                # Account disabled
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Incorrect details were provided
            print("Invalid login details: {0}, {1}".format(username,password))
            return HttpResponse("Invalid login details supplied.")
    else:
            # No data submitted to form - reload page
            return render(request,'rango/login.html', {})

# Use the login required to ensure only logged in users can access the view
@login_required
def user_logout(request):
    # Since the user is logged in, log them out
    logout(request)
    # redirect to homepage
    return HttpResponseRedirect(reverse('index'))

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})

def visitor_cookie_handler(request):
    visits = int(request.COOKIES.get('visits', '1'))

    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    if(datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        response.set_cookie('last_visit', str(datetime.now()))
    else:
        visits = 1
        request.session['last_visit'] = last_visit_cookie

    request.session['visits'] = visits

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val
