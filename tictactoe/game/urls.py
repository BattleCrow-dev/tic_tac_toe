from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('lobby/', views.lobby, name='lobby'),
    path('leave_lobby/', views.leave_lobby, name='leave_lobby'),
    path('game/<int:game_id>/', views.game_view, name='game_view'),
    path('game/<int:game_id>/state/', views.game_state, name='game_state'),
    path('game/<int:game_id>/move/', views.make_move, name='make_move'),
    path('game/<int:game_id>/leave/', views.leave_game, name='leave_game'),
    path('game/<int:game_id>/send_message/', views.send_message, name='send_message'),
    path('game/<int:game_id>/get_messages/', views.get_messages, name='get_messages'),
    path('game/<int:game_id>/upload_voice_message/', views.upload_voice_message, name='upload_voice_message'),
]
