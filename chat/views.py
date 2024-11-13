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
    """
    Affiche la liste des conversations de l'utilisateur connecté.
    
    Cette vue:
    1. Récupère toutes les conversations où l'utilisateur est participant
    2. Récupère tous les contacts potentiels (autres utilisateurs)
    3. Affiche la page principale avec la liste des conversations
    """
    conversations = Conversation.objects.filter(participants=request.user)
    contacts = User.objects.exclude(id=request.user.id)
    return render(request, 'chat/conversation_list.html', {
        'conversations': conversations,
        'contacts': contacts
    })

@login_required
def conversation_detail(request, conversation_id):
    """
    Affiche le détail d'une conversation et ses messages.
    
    Paramètres:
    - conversation_id: ID de la conversation à afficher
    
    Sécurité:
    - Vérifie que l'utilisateur est bien participant de la conversation
    - Filtre les messages avec fichiers manquants
    """
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    messages = conversation.messages.all()
    
    # Gestion des messages avec fichiers manquants
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
    """
    Gère l'envoi des messages (texte, image, vocal).
    
    Méthode: POST uniquement
    Types de messages supportés:
    - text: message texte simple
    - image: fichier image
    - voice: message vocal
    
    Retourne:
    - JSON avec statut 'success' et URLs des fichiers si nécessaire
    - JSON avec statut 'error' en cas d'échec
    """
    if request.method == 'POST':
        conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
        message_type = request.POST.get('message_type', 'text')
        
        message_data = {
            'conversation': conversation,
            'sender': request.user,
            'message_type': message_type
        }

        # Gestion des différents types de messages
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
    """
    Démarre ou récupère une conversation avec un utilisateur.
    
    Logique:
    1. Vérifie si une conversation existe déjà entre les deux utilisateurs
    2. Si non, crée une nouvelle conversation
    3. Redirige vers la conversation
    
    Paramètres:
    - user_id: ID de l'utilisateur avec qui démarrer la conversation
    """
    other_user = get_object_or_404(User, id=user_id)
    
    # Recherche d'une conversation existante
    conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()
    
    # Création d'une nouvelle conversation si nécessaire
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)
    
    return redirect('chat:conversation_detail', conversation_id=conversation.id)
