from django.shortcuts import render, get_object_or_404

from main.models import Category, SavedUrl, User, Url
from .forms import LoginForm, RegisterForm, AddCategoryForm, AddUrlForm

from django.contrib import auth
from django.db.models import Count
from django.db import connection, IntegrityError

# Create your views here.

def index(request):
    saved_urls = []
    categories = []
    default_categories = []
    current_user = None
    cursor = connection.cursor()

    if 'user_email' in request.session:
        try:
            current_user = User.objects.get(email = request.session['user_email'])
        except User.DoesNotExist:
            current_user = None

        cursor.execute('''
        SELECT main_category.id AS id, main_category.name AS name, count(main_savedurl.url_id) AS count 
        FROM main_savedurl RIGHT JOIN main_category 
        ON main_savedurl.category_id=main_category.id AND main_savedurl.user_id=''' + str(current_user.id) + '''
        WHERE main_category.is_default=TRUE 
        GROUP BY main_category.id
        ORDER BY count DESC''')
        default_categories = cursor.fetchall()

        cursor.execute('''SELECT main_category.id AS id, main_category.name AS name, count(main_savedurl.url_id) AS count 
                FROM main_savedurl RIGHT JOIN main_category ON main_savedurl.category_id=main_category.id 
                WHERE main_category.is_default=FALSE AND main_savedurl.user_id=''' + str(current_user.id) + ''' 
                GROUP BY main_category.id''')
        categories = cursor.fetchall()
        cursor.close()


    context = {'categories' : categories, 'default_categories': default_categories, 'user': current_user }

    return render(request, 'index.html', context)



def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            user_password = form.cleaned_data['password']
            try:
                user = User.objects.get(email = user_email, password = user_password)
            except User.DoesNotExist:
                return render(request, 'login.html', {'form': form, 'reason': 'Email or password not correct.'})

            request.session['user_email'] = user_email
            return render(request, 'login_success.html', {'user': user})
        else:
            return render(request, 'login.html', {'form': form, 'error': form.errors})
    else:
        return render(request, 'login.html', {'form': LoginForm})

def logout(request):
    if request.method == "POST":
        if 'user_email' in request.session:
            del request.session['user_email']
            request.session.flush() # delete session data
        return render(request, 'logout_success.html')
    else:
        return render(request, 'logout.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user_name = form.cleaned_data['name']
            user_surname = form.cleaned_data['surname']
            user_email = form.cleaned_data['email']
            user_password = form.cleaned_data['password']
            try:
                user = User(name=user_name, surname=user_surname, email = user_email, password = user_password)
                user.save()
            except IntegrityError as e:
                return render(request, 'register.html', {'form': form, 'reason': 'User with that email already exists!'})

            return render(request, 'register_success.html', {'user': user})
        else:
            return render(request, 'register.html', {'form': form, 'error': form.errors})
    else:
        return render(request, 'register.html', {'form': RegisterForm})

def view_category(request, id):
    saved_urls = []
    current_user = None
    category = get_object_or_404(Category, id=id)

    if 'user_email' in request.session:
        try:
            current_user = User.objects.get(email = request.session['user_email'])
        except User.DoesNotExist:
            current_user = None

        saved_urls = SavedUrl.objects.filter(user=current_user, category=id).exclude(url__isnull=True)

    context = {'category': category, 'saved_urls' : saved_urls, 'user': current_user }

    return render(request, 'savedurls.html', context)

def view_all_categories(request):
    saved_urls = []
    current_user = None

    if 'user_email' in request.session:
        try:
            current_user = User.objects.get(email = request.session['user_email'])
        except User.DoesNotExist:
            current_user = None

        saved_urls = SavedUrl.objects.filter(user=current_user).exclude(url__isnull=True)

    context = {'saved_urls' : saved_urls }

    return render(request, 'savedurls.html', context)

def add_category(request):
    user_email = None
    if 'user_email' in request.session:
        user_email = request.session['user_email']

    current_user = get_object_or_404(User, email = user_email)

    if request.method == 'POST':
        form = AddCategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            (new_category, created) = Category.objects.get_or_create(name=category_name)
            try:
                new_saved_url = SavedUrl(user=current_user, category=new_category)
                new_saved_url.save()
            except IntegrityError as e:
                return render(request, 'add_category.html', {'form': form, 'reason': e})
            return render(request, 'add_category_success.html', {'form': form})

        return render(request, 'add_category.html', {'form': form, 'error': form.errors})
    else:
        return render(request, 'add_category.html', {'form': AddCategoryForm})


def delete_category(request, id):
    user_email = None
    if 'user_email' in request.session:
        user_email = request.session['user_email']

    current_user = get_object_or_404(User, email = user_email)

    if request.method == 'POST':
        category = get_object_or_404(Category, id=id)
        undefined_category = Category.objects.filter(name='Undefined')[0]
        saved_urls = SavedUrl.objects.filter(category_id=category.id)
        try:
            for s_u in saved_urls:
                s_u.category_id = undefined_category.id
                s_u.save()
            category.delete()
        except IntegrityError as e:
            return render(request, 'delete_category.html', {'reason': e})
        return render(request, 'delete_category_success.html')
    else:
        return render(request, 'delete_category.html')

def add_url(request):
    user_email = None
    if 'user_email' in request.session:
        user_email = request.session['user_email']

    current_user = get_object_or_404(User, email = user_email)

    if request.method == 'POST':
        form = AddUrlForm(current_user.id, request.POST)
        if form.is_valid():
            
            (new_url, created) = Url.objects.get_or_create(url=form.cleaned_data['url'])
            (new_cat, created) = Category.objects.get_or_create(id=form.cleaned_data['category'])

            new_title = form.cleaned_data['url_title']
            new_notes = form.cleaned_data['notes']

            try:
                savedurl = SavedUrl(user=current_user, url=new_url, 
                        category=new_cat, url_title=new_title, notes=new_notes)
                savedurl.save()
            except IntegrityError as e:
                return render(request, 'add_url.html', {'form': form, 'reason': 'There is already an entry with that url.'})
            return render(request, 'add_url_success.html')
        return render(request, 'add_url.html', { 'error': form.errors })
    else:
        return render(request, 'add_url.html', {'form': AddUrlForm(current_user.id)})

def delete_url(request, id):
    user_email = None
    if 'user_email' in request.session:
        user_email = request.session['user_email']

    current_user = get_object_or_404(User, email = user_email)

    if request.method == "POST":
        savedurl = get_object_or_404(SavedUrl, id=id, user_id=current_user.id)
        savedurl.delete()
        return render(request, 'delete_url_success.html')
    else:
        return render(request, 'delete_url.html')

def edit_url(request, id):
    user_email = None
    if 'user_email' in request.session:
        user_email = request.session['user_email']

    current_user = get_object_or_404(User, email = user_email)

    if request.method == "POST":
        form = AddUrlForm(current_user.id, request.POST)
        if form.is_valid():
            savedurl = get_object_or_404(SavedUrl, id=id)
            (savedurl.url, created) = Url.objects.get_or_create(url = form.cleaned_data['url'])
            savedurl.category = get_object_or_404(Category, id=form.cleaned_data['category'])
            savedurl.url_title = form.cleaned_data['url_title']
            savedurl.notes = form.cleaned_data['notes']
            try:
                savedurl.save()
            except IntegrityError as e:
                return render(request, 'add_url.html', 
                        {'form': form, 'reason': 'There were some problems with the data. Maybe you want to add an existing url?'})
            return render(request, 'add_url_success.html')
        return render(request, 'add_url.html', { 'form': form, 'error': form.errors })
    else:
        savedurl = get_object_or_404(SavedUrl, id=id)
        url = get_object_or_404(Url, id=savedurl.url_id)
        category = get_object_or_404(Category, id=savedurl.category_id)
        form = AddUrlForm(current_user.id, 
                {'url': url.url, 'category': category.id, 
                    'url_title': savedurl.url_title, 'notes': savedurl.notes})
        return render(request, 'add_url.html', {'form': form})




