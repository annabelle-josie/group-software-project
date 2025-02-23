from django.shortcuts import redirect, render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import UserGarden, Plant
from django.http import HttpResponseRedirect
from user_management.models import CustomUser
from .serializers import UserGardenSerializer, PlantSerializer
from django.contrib.auth.decorators import login_required


@login_required(login_url="/auth/login")
def garden_view(request):
    """View to display the garden on the main page"""
    user_garden = UserGarden.objects.get(user=request.user)
    users = CustomUser.objects.get(username= request.user)
    avalible = users.owned_plants.all().values()
    plant_slots = []
    if user_garden:
        for slot in range(1, 7):  # Loop through all 6 slots
            plant = getattr(user_garden, f"plant{slot}Id", None)  # Get Plant object directly
            #print(f"Plant Slot {slot}: {plant}")  # Debugging line
            plant_slots.append(plant)
    print("Final Plant Slots:", plant_slots)  # Debugging line
    return render(request, "garden/garden.html", {"plant_slots": plant_slots,"avalible":avalible})

@api_view(["GET"])
def get_garden(request, user_id):
    """API used to display garden on the main page"""
    try:
        garden = userGarden.objects.get(user__id=user_id)
        serializer = GardenSerializer(garden)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except userGarden.DoesNotExist:
        return Response({"error": "Garden not found"}, status=status.HTTP_404_NOT_FOUND)
    
def update_garden(request):
    """View to updte the user's garden with a new plant"""
    # print("hello")
    plantname = request.POST.get('plantname')
    slot = request.POST.get('slot')
    print(slot)
    if not plantname:
        return redirect("garden")
    try:
        plant= Plant.objects.get(name=plantname)
        # print(plant)
        plantslots = UserGarden.objects.get(user=request.user)
        plantslot = setattr(plantslots, f"plant{slot}Id",plant)
        plantslots.save()
        # get right plant list and plant ID 
    except Plant.DoesNotExist:
        return Response({"error": "no "}, status=status.HTTP_404_NOT_FOUND)
    return HttpResponseRedirect(redirect_to="/garden")

# @login_required(login_url="/auth/login")
# def market_view(request):
#     plants = Plant.objects.filter(onMarket=True)   # Fetch all plants from DB that are allowed to be on market
    
#     current_leaves = 80  # Need to replace with a method to get that users leaves
    
#     context = {
#         "plants": plants,
#         "leaves": current_leaves
#     }
#     return render(request, "market.html", context)

