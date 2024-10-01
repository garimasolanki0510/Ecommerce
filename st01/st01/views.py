import random
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
import mysql.connector
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

# Database connection
db = mysql.connector.connect(host='localhost', user='root', passwd='', database='ecommerce')
cr = db.cursor()

def home(request):
    return render(request, 'index.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        cr.execute("SELECT * FROM register WHERE username=%s", (username,))
        user = cr.fetchone()
        if not user:
            messages.error(request, 'Invalid username', extra_tags='username')
            return render(request, 'login.html', {'username': username})
       
        if user and user[6] != password:
            messages.error(request, 'Invalid password', extra_tags='password')
            return render(request, 'login.html', {'username': username})
       
        if user and user[6] == password:
            user_details = {
                'firstname': user[1],
                'lastname': user[2],
                'email': user[3],
                'mobile': user[4],
                'username': user[5]
            }
            return render(request, 'loginhome.html', {'user': user_details})
   
    return render(request, 'login.html')

def signup(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        username = request.POST.get('username')
        password = request.POST.get('password')
        otp = request.POST.get('otp')
        
        # Verify OTP
        if otp != request.session.get('otp'):
            messages.error(request, 'Invalid OTP', extra_tags='otp')
            return render(request, 'register.html', {
                'firstname': firstname,
                'lastname': lastname,
                'email': email,
                'mobile': mobile,
                'username': username
            })
        
        # Perform validations
        if not firstname:
            messages.error(request, 'First name is required', extra_tags='firstname')
        if not lastname:
            messages.error(request, 'Last name is required', extra_tags='lastname')
        if not email:
            messages.error(request, 'Email is required', extra_tags='email')
        elif '@' not in email:
            messages.error(request, 'Invalid email format', extra_tags='email')
        if not mobile:
            messages.error(request, 'Mobile number is required', extra_tags='mobile')
        elif not mobile.isdigit():
            messages.error(request, 'Mobile number should contain only digits', extra_tags='mobile')
        if not username:
            messages.error(request, 'Username is required', extra_tags='username')
        if not password:
            messages.error(request, 'Password is required', extra_tags='password')
        elif len(password) < 8:
            messages.error(request, 'Password should be at least 8 characters long', extra_tags='password')
  
        # Check for existing records
        cr.execute("SELECT * FROM register WHERE email=%s OR mobile=%s OR username=%s", (email, mobile, username))
        existing_records = cr.fetchall()
        
        for record in existing_records:
            if record[3] == email:
                messages.error(request, 'Email already exists', extra_tags='email')
            if record[4] == mobile:
                messages.error(request, 'Mobile number already exists', extra_tags='mobile')
            if record[5] == username:
                messages.error(request, 'Username already exists', extra_tags='username')
        
        # If there are any error messages, re-render the form
        if messages.get_messages(request):
            return render(request, 'register.html', {
                'firstname': firstname,
                'lastname': lastname,
                'email': email,
                'mobile': mobile,
                'username': username
            })
        
        try:
            cr.execute("INSERT INTO register(firstname, lastname, email, mobile, username, password) VALUES (%s, %s, %s, %s, %s, %s)",
                       (firstname, lastname, email, mobile, username, password))
            db.commit()
            
            # Send registration confirmation email
            subject = 'Welcome to Our E-commerce Platform'
            message = f'''
            Dear {firstname} {lastname},

            Thank you for registering on our e-commerce platform. Here are your registration details:

            First Name: {firstname}
            Last Name: {lastname}
            Email: {email}
            Mobile: {mobile}
            Username: {username}

            We're excited to have you on board!

            Best regards,
            The E-commerce Team
            '''
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]
            
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            
            messages.success(request, 'Registration successful! Please check your email for confirmation.')
            return render(request, 'registersuc.html')
        except Exception as e:
            db.rollback()
            messages.error(request, f'Registration failed. Please try again. Error: {str(e)}')
            return render(request, 'register.html')
    
    return render(request, 'register.html')

def send_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            return JsonResponse({'success': False, 'error': 'Email address is required'})

        otp = str(random.randint(100000, 999999))
        request.session['otp'] = otp
        
        subject = 'One-Time Password (OTP) for Your Registration'
        message = f"""
        Dear User,

        We are pleased to inform you that your registration process has begun. 
        To complete your registration, please use the following One-Time Password (OTP):

        OTP: {otp}

        Please enter this OTP in the required field on the registration page to proceed. 
        This OTP is valid for a limited time and can only be used once.

        If you did not request this registration or have any questions, please contact our support team at [garimasolanki875.com.com/9302092796].

        Thank you for choosing our services.

        Best regards,
        [garima solanki]
        [CEO]
        [Ecoomerce retailer]
        [Contact:garimasolanki875.com]
        """
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        
        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        # Compose email
        email_subject = f"New contact form submission: {subject}"
        email_message = f"Name: {name}\nEmail: {email}\nMessage: {message}"
        
        # Send email
        try:
            send_mail(
                email_subject,
                email_message,
                settings.EMAIL_HOST_USER,
                [email],  # Send to the user's email
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')  # Redirect to the same page after submission
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    
    return render(request, 'contact.html')

def product(request, id):
    # Here you would typically fetch the product details based on the id
    # For now, we'll just render the template
    return render(request, 'product.html')
def cart(request):
    return render(request, 'cart.html')