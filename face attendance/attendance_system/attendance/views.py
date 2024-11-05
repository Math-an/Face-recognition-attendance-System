# home =============================================================================
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import User
def home(request):
    return render(request, 'index.html')

#=============ADMIN LOGIN ===============================================================
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Admin  # Ensure 'Admin' is correct; if it's named differently, change this line to match the actual model name.

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate admin user
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('admin_dashboard')  # Redirect to the admin dashboard after login
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'admin_login.html')

#======================================ADMIN DASHBOARD ==================================================
from django.contrib.auth.decorators import login_required
from .models import User, Attendance

@login_required
def admin_dashboard(request):
    # Sample context data (You can fetch actual data to display on the dashboard)
   
    total_users = User.objects.count()
    users_present = Attendance.objects.filter(is_present=True).count()
    users_absent = Attendance.objects.filter(is_present=False).count()

    context = {
        'total_users': total_users,
        'users_present': users_present,
        'users_absent': users_absent,
    }

    return render(request, 'admin_dashboard.html', context)

#======================================ADD import random

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail
from .models import User

@csrf_exempt
def add_user(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        role = request.POST.get('role')
        dob = request.POST.get('dob')
        password = request.POST.get('password')

        try:
            # Create the user account using AutoField id
            user = User.objects.create(
                username=email,
                first_name=name,
                email=email,
                password=password,  # Store the password directly, hashing will happen when saving
                # Other fields can be added if needed
            )
            # user.set_password(password)  # Hash the password before saving
            user.save()  # Save the user instance

            # Send email with password to user
            send_mail(
                'Your account password',
                f'Hello {name},\nYour account password is: {password}',
                'your_email@example.com',  # Replace with your sender email
                [email],
                fail_silently=False,
            )

            return JsonResponse({'message': 'User added successfully and email sent!'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return render(request, 'add_user.html')


#===========================================List User================================================
from .forms import AddUserForm
from django.shortcuts import get_object_or_404
  # Assuming this is your form for adding users

def list_users(request):
    users = User.objects.all()  # Retrieve all users from the database
    return render(request, 'list_user.html', {'users': users})

def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = AddUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('list_users')  # Redirect to the user list after saving
    else:
        form = AddUserForm(instance=user)
    return render(request, 'edit_user.html', {'form': form, 'user': user})

def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('list_users')  # Redirect to the user list after deletion
    return render(request, 'delete_user.html', {'user': user})

#===========================================Attendance Report==============================================
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Attendance

# @login_required
def attendance_report(request, user_id):
    print(user_id);
    # Fetch attendance records safely using the AutoField id
    attendance_records = Attendance.objects.filter(user=user_id)
    print(attendance_records)

    # # Pass the username and attendance records to the template
    context = {
        'attendance_records': attendance_records,
        'username': request.user.username,
    }

    print(context);

    return render(request, 'attendance_report.html', context)


from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse

from django.contrib.auth.models import User

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

      
        
        # Authenticate the user
        # user = authenticate(request, username=username, password=password)
        # print(user.password);
        try:
            obj = User.objects.get(first_name = username);
            print(obj.id);
            # Log the authentication attempt
        
            
            if obj.password == password:
                login(request, obj);
            
                # Redirect directly to the attendance report
                return attendance_report(request, obj)  # Use the named URL for redirection
            else:
                    messages.error(request, 'Invalid username or password.')
        except User.DoesNotExist:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')



def face_recognition_view(request):
    return render(request, 'face_recognition.html') 
#=====================================================================================




# Mark Attendance Function ==============================================
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
from .models import User, Attendance

@csrf_exempt
def mark_attendance_view(request, data):

    username = data
    print(username)
    try:
        user = User.objects.get(first_name=username)
        today = datetime.date.today()
        attendance, created = Attendance.objects.get_or_create(user=user, date=today)
        if created:
            attendance.is_present = True
            attendance.save()
            return JsonResponse({'success': True, 'message': 'Attendance marked'})
        return JsonResponse({'success': False, 'message': 'Attendance already marked'})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'})
    #-------------------------------------------------------------------------------------------------------

import csv
from django.http import HttpResponse
from django.shortcuts import render
from .models import Attendance  # Replace AttendanceRecord with Attendance
 # Adjust the model import as needed

def admin_attendance_report(request):
    # Get filter parameters from the request
    date = request.GET.get('date')
    status = request.GET.get('status')
    download = request.GET.get('download')

    # Filter attendance records based on the provided filters
    attendance_records = Attendance.objects.all()

    for i in attendance_records:
        print(i)
    
    if date:
        attendance_records = attendance_records.filter(date=date)
    if status:
        attendance_records = attendance_records.filter(status=status)

    # If 'download' is set to 'csv', export the data
    if download == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['User ID', 'Name', 'Date', 'Status'])
        for record in attendance_records:
            date_str=record.date.strftime('%Y-%m-%d')
            status = "Present" if record.is_present else "Absent"
            writer.writerow([record.user_id, record.user.username,date_str,status])
        
        return response

    # Render the attendance report template with filtered data
    return render(request, 'admin_attendance_report.html', {'attendance_records': attendance_records})
