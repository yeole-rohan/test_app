# chat/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message, UserProfile, ChatRoom
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm


@login_required
def home(request):
    # Fetch all rooms involving the logged-in user
    chat_rooms = ChatRoom.objects.filter(user1=request.user) | ChatRoom.objects.filter(user2=request.user)
    print(chat_rooms)
    return render(request, 'chat/home.html', {'chat_rooms': chat_rooms})

@login_required
def chat_room(request, username):
    receiver = get_object_or_404(User, username=username)
    
    # Get or create a chat room for the two users
    room, created = ChatRoom.objects.get_or_create(
        user1=request.user,
        user2=receiver
    ) if not ChatRoom.get_room(request.user, receiver) else (ChatRoom.get_room(request.user, receiver), False)
    
    # Get existing messages
    messages = Message.objects.filter(sender__in=[request.user, receiver], receiver__in=[request.user, receiver])
    is_online = UserProfile.objects.get(user=receiver).is_online

    return render(request, 'chat/room.html', {
        'receiver': receiver,
        'messages': messages,
        'is_online': is_online,
        'room_name': room.id,
    })

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat:home')
    else:
        form = SignUpForm()
    return render(request, 'chat/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('chat:home')
    else:
        form = AuthenticationForm()
    return render(request, 'chat/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('chat:login')