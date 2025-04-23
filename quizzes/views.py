from django.shortcuts import render, get_object_or_404, redirect
from .models import Quiz, Question, Option, StudentQuizResult, OTP
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

# Extra imports for webcam
import base64
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from PIL import Image
import io
import cv2
import numpy as np
import json
import os
import random
print("TEST RANDOM:", random.randint(1000, 9999))

# ✅ Signup View
from .forms import CustomUserCreationForm
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('quiz_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

# ✅ Quiz List View
def quiz_list(request):
    quizzes = Quiz.objects.all()
    return render(request, 'quizzes/quiz_list.html', {'quizzes': quizzes})

# ✅ Take Quiz View (Login Required)
@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.question_set.all()

    if request.method == 'POST':
        score = 0
        total = questions.count()

        for q in questions:
            selected = request.POST.get(str(q.id))
            correct = q.option_set.filter(is_correct=True).first()
            if correct and selected == str(correct.id):
                score += 1

        percentage = (score / total) * 100

        StudentQuizResult.objects.create(
            student=request.user,
            quiz=quiz,
            score=percentage,
        )
        return render(request, 'quizzes/quiz_result.html', {
            'score': percentage,
            'quiz': quiz
        })

    return render(request, 'quizzes/take_quiz.html', {
        'quiz': quiz,
        'questions': questions,
    })

# ✅ Score History View
@login_required
def score_history(request):
    results = StudentQuizResult.objects.filter(student=request.user).order_by('-taken_at')
    return render(request, 'quizzes/score_history.html', {'results': results})

# ✅ Webcam Upload API
@csrf_exempt
def upload_frame(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_data = data.get('image')

            if not image_data:
                return JsonResponse({'error': 'No image data'}, status=400)

            image_data = image_data.split(',')[1]
            img_bytes = base64.b64decode(image_data)
            img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

            cascade_path = os.path.join(os.path.dirname(__file__), 'haarcascade_frontalface_default.xml')
            face_cascade = cv2.CascadeClassifier(cascade_path)

            if face_cascade.empty():
                return JsonResponse({'error': 'Failed to load face cascade XML'}, status=500)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

            return JsonResponse({
                'faces_detected': len(faces),
                'cheating_flag': len(faces) != 1
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

# ✅ Send OTP View
def send_otp_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            messages.error(request, "Email is required.")
            return redirect('send_otp')

        otp = random.randint(100000, 999999)
        OTP.objects.create(email=email, code=str(otp), created_at=timezone.now())

        send_mail(
            subject="Quiz System - Your OTP Code",
            message=f"Your OTP is: {otp}",
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )

        request.session['reset_email'] = email
        return redirect('verify_otp')

    return render(request, 'registration/send_otp.html')


# ✅ Verify OTP View
def verify_otp_view(request):
    if request.method == 'POST':
        input_code = request.POST.get('otp')
        email = request.session.get('reset_email')

        if not email:
            messages.error(request, "Session expired. Try again.")
            return redirect('send_otp')

        try:
            otp_obj = OTP.objects.filter(email=email).latest('created_at')
            if otp_obj.code == input_code:
                request.session['verified_email'] = email
                return redirect('set_new_password')
            else:
                messages.error(request, "Incorrect OTP.")
        except OTP.DoesNotExist:
            messages.error(request, "OTP expired or not found.")

    return render(request, 'registration/verify_otp.html')


# ✅ New Password Set View
from django.contrib.auth.hashers import make_password

def set_new_password_view(request):
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        email = request.session.get('verified_email')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('set_new_password')

        try:
            user = User.objects.get(email=email)
            user.password = make_password(password1)
            user.save()
            messages.success(request, "Password reset successfully.")
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, "User not found.")

    return render(request, 'registration/set_new_password.html')

from django.contrib.auth import authenticate, login
from django.contrib import messages

def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('/admin/')
        else:
            messages.error(request, 'Invalid admin credentials.')
    return render(request, 'registration/admin_login.html')
