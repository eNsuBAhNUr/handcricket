from django.shortcuts import render, redirect
import random

def home(request):
    request.session.flush()  # reset everything
    return render(request, "game/home.html")

def toss(request):
    if request.method == 'POST':
        call = request.POST.get('call')
        toss_result = random.choice(['heads', 'tails'])
        request.session['toss_winner'] = 'user' if call == toss_result else 'system'
        return redirect('choose')
    return render(request, "game/toss.html")

def choose(request):
    if request.session.get('toss_winner') == 'user':
        if request.method == 'POST':
            choice = request.POST.get('choice')
            request.session['batting'] = 'user' if choice == 'bat' else 'system'
            request.session['user_score'] = 0
            request.session['system_score'] = 0
            request.session['balls_left'] = 6  # default 1 over
            request.session['current_ball'] = 0
            request.session['game_over'] = False
            return redirect('play')
        return render(request, "game/choose.html")
    else:
        # system won toss
        request.session['batting'] = random.choice(['user', 'system'])
        request.session['user_score'] = 0
        request.session['system_score'] = 0
        request.session['balls_left'] = 6
        request.session['current_ball'] = 0
        request.session['game_over'] = False
        return redirect('play')

def play(request):
    if 'user_score' not in request.session:
        return redirect('home')

    batting = request.session['batting']
    user_score = request.session['user_score']
    system_score = request.session['system_score']
    runs_needed = max(0, user_score - system_score)

    if request.method == 'POST' and not request.session['game_over']:
        user_num = int(request.POST.get('run'))
        system_num = random.randint(1, 6)

        # --- User batting ---
        if batting == 'user':
            if user_num == system_num:
                # Out! switch innings
                request.session['batting'] = 'system'
                request.session['current_ball'] = 0
                request.session['balls_left'] = 6
            else:
                request.session['user_score'] += user_num

        # --- System batting ---
        elif batting == 'system':
            if user_num == system_num:
                # System out → You win
                request.session['game_over'] = True
                request.session['winner'] = 'You Won! 🏆'
            else:
                request.session['system_score'] += system_num
                if request.session['system_score'] >= request.session['user_score']:
                    # System reached/exceeded your score → System wins
                    request.session['game_over'] = True
                    request.session['winner'] = 'System Won! 💻'

        # Update balls
        request.session['current_ball'] += 1
        if request.session['current_ball'] >= request.session['balls_left']:
            if batting == 'user':
                request.session['batting'] = 'system'
                request.session['current_ball'] = 0
            else:
                request.session['game_over'] = True
                if request.session['system_score'] < request.session['user_score']:
                    request.session['winner'] = 'You Won! 🏆'

        context = {
            'user_num': user_num,
            'system_num': system_num,
            'user_score': request.session['user_score'],
            'system_score': request.session['system_score'],
            'batting': request.session['batting'],
            'runs_needed': max(0, request.session['user_score'] - request.session['system_score']),
        }

        return render(request, "game/play.html", context)

    return render(request, "game/play.html", {
        'user_score': request.session['user_score'],
        'system_score': request.session['system_score'],
        'batting': request.session['batting'],
        'runs_needed': runs_needed
    })

def result(request):
    return render(request, "game/result.html", {
        'user_score': request.session.get('user_score', 0),
        'system_score': request.session.get('system_score', 0),
        'winner': request.session.get('winner', '')
    })
