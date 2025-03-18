from django import forms

# Slot choices
INTEGER_CHOICES= [

    1,2,3,4,5,6
]
# Plant choices
# TODO: Need to update this to reflect the actual plants in the database
PLANT_CHOICES= [

    1,2,3
]

# Form for adding a plant to a slot
class plantForm(forms.Form):
    slot= forms.CharField(widget=forms.Select(choices=INTEGER_CHOICES))
    plant= forms.CharField(widget=forms.Select(choices=PLANT_CHOICES))
