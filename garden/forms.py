from django import forms


INTEGER_CHOICES= [

    1,2,3,4,5,6
]
PLANT_CHOICES= [

    1,2,3
]


class plantForm(forms.Form):
    slot= forms.CharField(widget=forms.Select(choices=INTEGER_CHOICES))
    plant= forms.CharField(widget=forms.Select(choices=PLANT_CHOICES))
