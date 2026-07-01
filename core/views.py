from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth import logout
from .models import LandUsePlan, Comment, Vote
from django.http import HttpResponse

from reportlab.pdfgen import canvas
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from .models import LandUsePlan # change Plan to your actual model name
# HOME PAGE
def home(request):

    # kama user hajalogin
    if not request.user.is_authenticated:
        return redirect('/login/')
    
    is_officer = (
        request.user.is_superuser
        or request.user.groups.filter(
            name='PlanningOfficer'
        ).exists()
    )

    # COMMENT SYSTEM
    if request.method == "POST" and request.POST.get("text"):

        plan_id = request.POST.get("plan_id")
        text = request.POST.get("text")

        plan = LandUsePlan.objects.get(id=plan_id)

        if plan.status != "Open":
            return redirect('/')

        Comment.objects.create(
            user=request.user,
            plan_id=plan_id,
            text=text
        )

        return redirect('/')

    # VOTING SYSTEM
    if request.method == "POST" and request.POST.get("vote"):

        plan_id = request.POST.get("plan_id")
        choice = request.POST.get("vote")

        plan = LandUsePlan.objects.get(id=plan_id)

        if plan.status != "Open":
            return redirect('/')

        # check kama user tayari amevote
        existing_vote = Vote.objects.filter(
            user=request.user,
            plan_id=plan_id
        ).first()

        # kama hajavote
        if not existing_vote:

            Vote.objects.create(
                user=request.user,
                plan_id=plan_id,
                choice=choice
            )

        return redirect('/')

    search = request.GET.get('search')

    # Admin na Planning Officer wanaona plans zote
    if is_officer:

        if search:

            plans = LandUsePlan.objects.filter(
                title__icontains=search
            )

        else:

            plans = LandUsePlan.objects.all()

    # Citizens hawaoni Draft
    else:

        if search:

            plans = LandUsePlan.objects.filter(
                title__icontains=search
            ).exclude(status='Draft')

        else:

            plans = LandUsePlan.objects.exclude(
                status='Draft'
            )

    for plan in plans:

        plan.approvals = Vote.objects.filter(
            plan=plan,
            choice="Approve"
        ).count()

        plan.rejects = Vote.objects.filter(
            plan=plan,
            choice="Reject"
        ).count()

    comments = Comment.objects.all()

    

    return render(request, 'home.html', {
        'plans': plans,
        'comments': comments,
        'is_officer': is_officer
    })


# REGISTER
def register(request):

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']

        User.objects.create_user(
            username=username,
            password=password
        )

        return redirect('/login/')

    return render(request, 'register.html')


# LOGIN
def login_view(request):

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('/')

    return render(request, 'login.html')

def logout_view(request):

    logout(request)

    return redirect('/login/')

def dashboard(request):
    def dashboard(request):

        if not request.user.is_authenticated:
            return redirect('/login/')

        if not (
            request.user.is_superuser
            or request.user.groups.filter(
                name='PlanningOfficer'
            ).exists()
        ):

            return redirect('/')

    total_plans = LandUsePlan.objects.count()
    total_comments = Comment.objects.count()
    total_votes = Vote.objects.count()
    total_users = User.objects.count()

    return render(request, 'dashboard.html', {
        'total_plans': total_plans,
        'total_comments': total_comments,
        'total_votes': total_votes,
        'total_users': total_users
    })

def generate_pdf(request):

    response = HttpResponse(content_type='application/pdf')

    response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    p = canvas.Canvas(response)

    # title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "Land Use Planning Report")

    # statistics
    p.setFont("Helvetica", 12)

    p.drawString(100, 760,
        f"Total Plans: {LandUsePlan.objects.count()}"
    )

    p.drawString(100, 740,
        f"Total Comments: {Comment.objects.count()}"
    )

    p.drawString(100, 720,
        f"Total Votes: {Vote.objects.count()}"
    )

    # comments section
    y = 680

    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, y, "Citizen Comments")

    y -= 30

    p.setFont("Helvetica", 11)

    comments = Comment.objects.all()

    for comment in comments:

        p.drawString(
            100,
            y,
            f"{comment.user.username}: {comment.text}"
        )

        y -= 20

        # avoid page overflow
        if y < 100:
            p.showPage()
            y = 800

    p.save()

    return response

def add_plan(request):

    if not request.user.is_authenticated:
        return redirect('/login/')

    if not (
        request.user.is_superuser
        or request.user.groups.filter(
            name='PlanningOfficer'
        ).exists()
    ):
        return redirect('/')

    if request.method == 'POST':

        title = request.POST['title']
        description = request.POST['description']

        image = request.FILES.get('image')

        latitude = request.POST.get('latitude')

        longitude = request.POST.get('longitude')

        status = request.POST.get('status')

        LandUsePlan.objects.create(
            title=title,
            description=description,
            image=image,
            latitude=latitude,
            longitude=longitude,
            status=status
        )

        return redirect('/')

    return render(
        request,
        'add_plan.html'
    )

@login_required
def manage_plans(request):

    if not (
        request.user.is_superuser
        or request.user.groups.filter(
            name='PlanningOfficer'
        ).exists()
    ):
        return redirect('/')

    plans = LandUsePlan.objects.all()

    return render(
        request,
        'manage_plans.html',
        {
            'plans': plans
        }
    )

@login_required
def edit_plan(request, plan_id):

    if not (
        request.user.is_superuser
        or request.user.groups.filter(
            name='PlanningOfficer'
        ).exists()
    ):
        return redirect('/')

    plan = LandUsePlan.objects.get(id=plan_id)

    if request.method == 'POST':

        plan.title = request.POST['title']
        plan.description = request.POST['description']
        plan.status = request.POST['status']

        if request.POST.get('latitude'):
            plan.latitude = request.POST['latitude']

        if request.POST.get('longitude'):
            plan.longitude = request.POST['longitude']

        if request.FILES.get('image'):
            plan.image = request.FILES['image']

        plan.save()

        return redirect('/manage-plans/')

    return render(
        request,
        'edit_plan.html',
        {
            'plan': plan
        }
    )

def delete_plan(request, plan_id):
    plan = get_object_or_404(LandUsePlan, id=plan_id)
    plan.delete()
    return redirect('/manage-plans/')