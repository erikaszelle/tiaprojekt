from django.shortcuts import render, get_object_or_404

from main.models import Category, SavedUrl, User, Url, Label
from .forms import LoginForm, RegisterForm, AddCategoryForm, AddUrlForm, AddLabelForm

from django.contrib import auth
from django.db.models import Count
from django.db import connection, IntegrityError
from django.http import Http404, HttpResponseRedirect
from django.db.models import Q

import hashlib

# Create your views here.

def auth(hashed_value):
    users = User.objects.all()
    for user in users:
        if hashlib.sha224(user.email.encode()).hexdigest() == hashed_value:
            return user
    return None

def index(request):
    saved_urls = []
    categories = []
    default_categories = []
    current_user = None
    cursor = connection.cursor()

    if 'user_email' in request.session:
        current_user = auth(request.session['user_email'])
        #try:
        #    current_user = User.objects.get(email = request.session['user_email'])
        #except User.DoesNotExist:
        #    current_user = None

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

            request.session['user_email'] = hashlib.sha224(user_email.encode()).hexdigest()
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

    if 'user_email' in request.session:
        current_user = auth(request.session['user_email'])
        if not current_user:
            raise Http404
    else:
        return HttpResponseRedirect("/")

    category = get_object_or_404(Category, id=id)

    urls = SavedUrl.objects.filter(user=current_user, category=id).exclude(url__isnull=True)
    saved_urls = [(url, Label.objects.filter(saved_url=url.id)) for url in urls]

    context = {'category': category, 'saved_urls' : saved_urls, 'user': current_user }

    return render(request, 'savedurls.html', context)

def view_all_categories(request):

    if 'user_email' in request.session:
        current_user = auth(request.session['user_email'])
        if not current_user:
            raise Http404
    else:
        return HttpResponseRedirect("/")

    urls = SavedUrl.objects.filter(user=current_user).exclude(url__isnull=True)
    saved_urls = [(url, Label.objects.filter(saved_url=url.id)) for url in urls]

    context = {'saved_urls' : saved_urls }

    return render(request, 'savedurls.html', context)

def add_category(request):

    if 'user_email' in request.session:
        current_user = auth(request.session['user_email'])
        if not current_user:
            raise Http404
    else:
        return HttpResponseRedirect("/")

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

    if 'user_email' in request.session:
        current_user = auth(request.session['user_email'])
        if not current_user:
            raise Http404
    else:
        return HttpResponseRedirect("/")

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

    if 'user_email' in request.session:
        current_user = auth(request.session['user_email'])
        if not current_user:
            raise Http404
    else:
        return HttpResponseRedirect("/login/")

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

    if 'user_email' in request.session:
        current_user = auth(request.session['user_email'])
        if not current_user:
            raise Http404
    else:
        return HttpResponseRedirect("/")

    if request.method == "POST":
        savedurl = get_object_or_404(SavedUrl, id=id, user_id=current_user.id)
        savedurl.delete()
        return render(request, 'delete_url_success.html')
    else:
        return render(request, 'delete_url.html')

def edit_url(request, id):

    if 'user_email' in request.session:
        current_user = auth(request.session['user_email'])
        if not current_user:
            raise Http404
    else:
        return HttpResponseRedirect("/")

    if request.method == "POST":
        form = AddUrlForm(current_user.id, request.POST)
        if form.is_valid():
            savedurl = get_object_or_404(SavedUrl, id=id, user_id=current_user.id)
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
        labels = Label.objects.filter(saved_url=url.id)
        form = AddUrlForm(current_user.id, 
                {'url': url.url, 'category': category.id, 
                    'url_title': savedurl.url_title, 'notes': savedurl.notes})
        return render(request, 'add_url.html', {'form': form, 'labels': labels})

def add_label(request, id):

    if 'user_email' in request.session:
        current_user = auth(request.session['user_email'])
        if not current_user:
            raise Http404
    else:
        return HttpResponseRedirect("/")

    if request.method == 'POST':
        form = AddLabelForm(request.POST)
        if form.is_valid():
            url = get_object_or_404(SavedUrl, id=id)
            label_name = form.cleaned_data['label_name']
            try:
                (label, created) = Label.objects.get_or_create(name=label_name)
                label.saved_url.add(url)
                label.save()
            except IntegrityError as e:
                return render(request, 'add_label.html', {'form': form, 'reason': e})
            return render(request, 'add_label_success.html', {'form': form})

        return render(request, 'add_label.html', {'form': form, 'error': form.errors})
    else:
        return render(request, 'add_label.html', {'form': AddLabelForm})

def search(request):

    if 'user_email' in request.session:
        current_user = auth(request.session['user_email'])
        if not current_user:
            raise Http404
    else:
        return HttpResponseRedirect("/")

    if request.method == "POST":
        raise Http404

    query = request.GET['q'].split()
    if len(query) == 0:
        return render(request, 'savedurls.html', {'saved_urls': []})

    q = Q(url__url__icontains=query[0]) | Q(category__name__icontains=query[0]) | Q(url_title__icontains=query[0])
    for elem in query:
        q.add(Q(url__url__icontains=elem) | Q(category__name__icontains=elem) | Q(url_title__icontains=elem), q.connector)

    urls = SavedUrl.objects.filter(q, user=current_user).exclude(url__isnull=True)
    saved_urls = [(url, Label.objects.filter(saved_url=url.id)) for url in urls]

    context = {'saved_urls' : saved_urls }

    return render(request, 'savedurls.html', context)

def search_label(request, id):

    if 'user_email' in request.session:
        current_user = auth(request.session['user_email'])
        if not current_user:
            raise Http404
    else:
        return HttpResponseRedirect("/")

    label = Label.objects.get(id=id)
    d = {}
    for url in label.saved_url.all():
        try:
            url = SavedUrl.objects.get(id=url.id, user=current_user)
        except:
            continue

        labels = Label.objects.filter(saved_url=url.id)

        if url.id not in d:
            d.update({url.id : (url, labels)})
        else:
            d[url.id][1] += [label]

    saved_urls = list(d.values())

    context = {'saved_urls' : saved_urls , 'label': label}

    return render(request, 'savedurls.html', context)


def delete_label(request, url_id, label_id):

    if 'user_email' in request.session:
        current_user = auth(request.session['user_email'])
        if not current_user:
            raise Http404
    else:
        return HttpResponseRedirect("/")

    if request.method == 'POST':
        saved_url = get_object_or_404(SavedUrl, id=url_id)
        label = get_object_or_404(Label, id=label_id)
        try:
            label.saved_url.remove(saved_url)
            label.save()
        except IntegrityError as e:
            return render(request, 'delete_label.html', {'reason': e})
        return render(request, 'delete_label_success.html')
    else:
        return render(request, 'delete_label.html')
