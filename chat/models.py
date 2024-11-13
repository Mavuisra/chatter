from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Conversation(models.Model):
    """
    Modèle représentant une conversation entre utilisateurs.
    
    Attributs:
        participants (ManyToManyField): Les utilisateurs participant à la conversation
        created_at (DateTimeField): Date de création de la conversation
        updated_at (DateTimeField): Date de dernière mise à jour
    
    Note: Une conversation peut avoir plusieurs participants (extensible pour les groupes)
    """
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']  # Conversations les plus récentes en premier

class Message(models.Model):
    """
    Modèle représentant un message dans une conversation.
    
    Types de messages supportés:
        - text: Message texte simple
        - image: Fichier image
        - voice: Message vocal
    
    Attributs:
        conversation (ForeignKey): Lien vers la conversation parente
        sender (ForeignKey): Utilisateur ayant envoyé le message
        content (TextField): Contenu texte du message
        image (ImageField): Fichier image (optionnel)
        voice (FileField): Fichier audio (optionnel)
        message_type (CharField): Type du message
        timestamp (DateTimeField): Date et heure d'envoi
        read (BooleanField): Statut de lecture du message
    """
    TYPE_CHOICES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('voice', 'Voice'),
    )
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='chat_images/', null=True, blank=True)
    voice = models.FileField(upload_to='voice_messages/', null=True, blank=True)
    message_type = models.CharField(max_length=5, choices=TYPE_CHOICES, default='text')
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']  # Messages ordonnés chronologiquement
