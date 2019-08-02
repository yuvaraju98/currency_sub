from django import forms

class DataForm(forms.Form):
    base= forms.CharField(widget=forms.TextInput(attrs={'class':'special', 'size': '30px','placeholder':'eg: USD'}))
    target = forms.EmailField(widget=forms.TextInput(attrs={'class':'special', 'size': '30px','placeholder':'eg: INR'}))
    date = forms.CharField(widget=forms.TextInput(attrs={'class':'special', 'size': '30px','placeholder':'YYYY-MM-DD'}))
    amount = forms.CharField(widget=forms.TextInput(attrs={'class':'special', 'size': '30px','placeholder':'enter amount'}))
    maxdays = forms.CharField(widget=forms.TextInput(attrs={'class':'special', 'size': '30px','placeholder':'eg: 3'}))





