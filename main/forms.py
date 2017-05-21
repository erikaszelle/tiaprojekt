from django import forms

from .models import Category

from django.db import connection

class LoginForm(forms.Form):
    email = forms.EmailField(required=True, label="Enter email", max_length=100)
    password = forms.CharField(required=True, label="Enter password", widget=forms.PasswordInput)

class RegisterForm(forms.Form):
    name = forms.CharField(required=True, label="Enter name", min_length=3)
    surname = forms.CharField(required=True, label="Enter surname", min_length=3)
    email = forms.EmailField(required=True, label="Enter email", min_length=6, max_length=100)
    password = forms.CharField(required=True, label="Enter password", widget=forms.PasswordInput, min_length=5)
    confirm_password = forms.CharField(required=True, label="Confirm password", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
    
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
    
        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("The two passwords must be the same.")
        return cleaned_data

class AddCategoryForm(forms.Form):
    category_name = forms.CharField(required=True, min_length=3)

class AddUrlForm(forms.Form):
    url = forms.URLField(required=True)
    category = forms.ChoiceField(widget=forms.Select(), required=True)

    url_title = forms.CharField(min_length=3)
    notes = forms.CharField(widget=forms.Textarea(), required=False)

    def __init__(self, user_id, *args, **kwargs):

        super(AddUrlForm, self).__init__(*args, **kwargs)

        cursor = connection.cursor()
        cursor.execute('''SELECT DISTINCT ON (main_category.id, main_category.name) main_category.id, main_category.name
                FROM main_savedurl RIGHT JOIN main_category ON main_savedurl.category_id=main_category.id 
                WHERE main_category.is_default=TRUE OR main_savedurl.user_id=''' + str(user_id))
        categories = cursor.fetchall()
        cursor.close()
        self.fields['category'].choices = categories

class AddLabelForm(forms.Form):
    label_name = forms.CharField(required=True, min_length=3)



