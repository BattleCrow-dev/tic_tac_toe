from django.db import models
from django.contrib.auth.models import User

class Game(models.Model):
    STATUS_CHOICES = [
        ('WAITING', 'Waiting for another player'),
        ('IN_PROGRESS', 'Game in progress'),
        ('FINISHED', 'Game finished')
    ]

    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player1')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player2', null=True, blank=True)
    board = models.CharField(max_length=9, default=' ' * 9)
    turn = models.ForeignKey(User, on_delete=models.CASCADE, related_name='turn', null=True, blank=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='winner', null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='WAITING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Game {self.id}: {self.player1} vs {self.player2}'


class Message(models.Model):
    game = models.ForeignKey(Game, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message {self.id} by {self.sender} in game {self.game.id}'


class VoiceMessage(models.Model):
    game = models.ForeignKey(Game, related_name="voice_messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    audio_file = models.FileField(upload_to='voice_messages/')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'VoiceMessage {self.id} by {self.sender} in game {self.game.id}'
