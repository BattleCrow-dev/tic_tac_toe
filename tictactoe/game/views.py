from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from .models import Game, Message
from .forms import VoiceMessageForm, SimpleRegistrationForm

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect

import json

def home(request):
    return render(request, 'game/home.html')



def signup(request):
    if request.method == 'POST':
        form = SimpleRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('lobby')
    else:
        form = SimpleRegistrationForm()
    return render(request, 'game/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('lobby')
    else:
        form = AuthenticationForm()
    return render(request, 'game/login.html', {'form': form})

@login_required
@csrf_exempt
def lobby(request):
    if request.method == 'POST':
        game = Game.objects.filter(status='WAITING').exclude(player1=request.user).first()
        if game:
            game.player2 = request.user
            game.turn = game.player1
            game.status = 'IN_PROGRESS'
            game.save()
            return JsonResponse({'status': 'ok', 'redirect_url': f'/game/{game.id}/'})
        else:
            game, created = Game.objects.get_or_create(player1=request.user, status='WAITING')
            return JsonResponse({'status': 'waiting', 'game_id': game.id})
    else:
        users = User.objects.all()
        leaderboard_data = []

        for user in users:
            wins = Game.objects.filter(winner=user).count()
            leaderboard_data.append({'username': user.username, 'wins': wins})

        leaderboard_data.sort(key=lambda x: x['wins'], reverse=True)

        return render(request, 'game/lobby.html', {'leaderboard_data': leaderboard_data})


@login_required
@csrf_exempt
def game_view(request, game_id):
    game = Game.objects.get(id=game_id)
    return render(request, 'game/game.html', {'game': game, 'range_three': range(3), 'range_nine': range(9)})

@login_required
@csrf_exempt
def game_state(request, game_id):
    game = Game.objects.get(id=game_id)
    if request.method == 'GET':
        return JsonResponse({
            'board': game.board,
            'turn': game.turn.username if game.turn else '',
            'winner': game.winner.username if game.winner else '',
            'status': game.status,
            'player1': game.player1.username,
            'player2': game.player2.username if game.player2 else ''
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
@csrf_exempt
def make_move(request, game_id):
    game = Game.objects.get(id=game_id)
    if request.method == 'POST':
        data = json.loads(request.body)
        move = data.get('move')
        if move is not None and game.turn == request.user and game.board[move] == ' ':
            board = list(game.board)
            board[move] = 'X' if game.turn == game.player1 else 'O'
            game.board = ''.join(board)
            if check_winner(game.board):
                game.winner = request.user
                game.status = 'FINISHED'
            elif ' ' not in game.board:
                game.winner = None  # Draw
                game.status = 'FINISHED'
            else:
                game.turn = game.player2 if game.turn == game.player1 else game.player1
            game.save()
            return JsonResponse({'status': 'ok', 'board': game.board, 'turn': game.turn.username if game.turn else '', 'winner': game.winner.username if game.winner else None})
        return JsonResponse({'status': 'error', 'message': 'Invalid move or game state'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
@csrf_exempt
def leave_game(request, game_id):
    game = Game.objects.get(id=game_id)
    if game.status != 'FINISHED':
        winner = game.player1 if game.player1 != request.user else game.player2
        message = f'Я вышел из игры :( {winner.username} победил!'
        Message.objects.create(game=game, sender=request.user, content=message)
        game.winner = winner
        game.status = 'FINISHED'
        game.save()
    else:
        message = f'Я вышел, удачи тебе!'
        Message.objects.create(game=game, sender=request.user, content=message)
    return JsonResponse({'status': 'closed'})

def check_winner(board):
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
        [0, 4, 8], [2, 4, 6]              # diagonals
    ]
    for combo in winning_combinations:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != ' ':
            return True
    return False


@login_required
@csrf_exempt
def leave_lobby(request):
    if request.method == 'POST':
        Game.objects.filter(player1=request.user, player2__isnull=True).delete()
        return JsonResponse({'status': 'ok'})

@login_required
@csrf_exempt
def send_message(request, game_id):
    if request.method == 'POST':
        game = Game.objects.get(id=game_id)
        content = request.POST.get('content')
        Message.objects.create(game=game, sender=request.user, content=content)
        return JsonResponse({'status': 'ok'})

@login_required
def get_messages(request, game_id):
    game = Game.objects.get(id=game_id)
    since_timestamp = request.GET.get('since_timestamp')
    messages = game.messages.order_by('timestamp')
    voice_messages = game.voice_messages.order_by('timestamp')

    if since_timestamp:
        messages = messages.filter(timestamp__gt=since_timestamp)
        voice_messages = voice_messages.filter(timestamp__gt=since_timestamp)

    message_data = [{'id': msg.id, 'sender': msg.sender.username, 'content': msg.content, 'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'), 'type': 'text'} for msg in messages]
    voice_message_data = [{'id': msg.id, 'sender': msg.sender.username, 'audio_file_url': msg.audio_file.url, 'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'), 'type': 'voice'} for msg in voice_messages]

    all_messages = sorted(message_data + voice_message_data, key=lambda x: x['timestamp'])
    return JsonResponse(all_messages, safe=False)



@login_required
@csrf_exempt
@require_http_methods(["POST"])
def upload_voice_message(request, game_id):
    game = Game.objects.get(id=game_id)
    form = VoiceMessageForm(request.POST, request.FILES)
    if form.is_valid():
        voice_message = form.save(commit=False)
        voice_message.sender = request.user
        voice_message.game = game
        voice_message.save()
        return JsonResponse({'status': 'ok', 'id': voice_message.id, 'timestamp': voice_message.timestamp.strftime('%Y-%m-%d %H:%M:%S'), 'audio_file_url': voice_message.audio_file.url})
    return JsonResponse({'status': 'error', 'message': 'Invalid form'}, status=400)
