from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Conversation, Message
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.core.files.base import ContentFile
import base64
import json

@login_required
def conversation_list(request):
    conversations = Conversation.objects.filter(participants=request.user)
    contacts = User.objects.exclude(id=request.user.id)
    return render(request, 'chat/conversation_list.html', {
        'conversations': conversations,
        'contacts': contacts
    })

@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    messages = conversation.messages.all()
    
    # Filtrer les messages pour ne garder que ceux avec des fichiers valides
    for message in messages:
        if message.message_type == 'voice' and not message.voice:
            message.message_type = 'text'
            message.content = "[Message vocal non disponible]"
        elif message.message_type == 'image' and not message.image:
            message.message_type = 'text'
            message.content = "[Image non disponible]"
    
    return render(request, 'chat/conversation_detail.html', {
        'conversation': conversation,
        'messages': messages
    })

@login_required
def send_message(request, conversation_id):
    if request.method == 'POST':
        conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
        message_type = request.POST.get('message_type', 'text')
        
        message_data = {
            'conversation': conversation,
            'sender': request.user,
            'message_type': message_type
        }

        if message_type == 'text':
            content = request.POST.get('content')
            if content:
                message_data['content'] = content
                message = Message.objects.create(**message_data)
                return JsonResponse({'status': 'success'})
        
        elif message_type == 'image':
            image = request.FILES.get('image')
            if image:
                message_data['image'] = image
                message = Message.objects.create(**message_data)
                return JsonResponse({
                    'status': 'success',
                    'image_url': message.image.url
                })
        
        elif message_type == 'voice':
            voice = request.FILES.get('voice')
            if voice:
                message_data['voice'] = voice
                message = Message.objects.create(**message_data)
                return JsonResponse({
                    'status': 'success',
                    'voice_url': message.voice.url
                })

    return JsonResponse({'status': 'error'})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def start_conversation(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    # Vérifier si une conversation existe déjà
    conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()
    
    # Si aucune conversation n'existe, en créer une nouvelle
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)
    
    return redirect('chat:conversation_detail', conversation_id=conversation.id)
