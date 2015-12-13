from django.http import HttpResponse
from datetime import datetime
from django.template.loader import get_template
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import redirect
import subprocess
import os

from models import User, Profile, Result, Data, Strategy


def index(request):
    if request.session.get("authenticated", False):
        request.session["login_error"] = False
        if request.session.get("role","user") == "user":
            redirect("/user/")
        elif request.session.get("role","user") == "manager":
            redirect("/manager/")

    is_err = request.session.get('login_error',False)
    return render_to_response("login_page.html", {'is_err': is_err})


def login(request):
    #check user password and redirect to page
    try:
        user_name = request.POST["login"]
        password = request.POST["password"]
        if user_name == 'eduard' and password == "pass":
            request.session["authenticated"] = True
            request.session["user_name"] = 'eduard'
            request.session["login_error"] = False
            request.session["role"] = "user"
            return redirect("../user/")
        elif user_name == 'manager' and password == "mpass":
            request.session["authenticated"] = True
            request.session["user_name"] = 'Manager'
            request.session["login_error"] = False
            request.session["role"] = "manager"
            return redirect("../manager/")
    except:
        pass

    request.session.clear()
    request.session["login_error"] = True
    return redirect("../")

def main_user_view(request):
    if not request.session.get("authenticated",False):
        request.session["login_error"] = True
        return redirect("../")
    now = datetime.now()
    return render_to_response('main_client_page.html', {'current_date': now}, context_instance=RequestContext(request))


def main_manager_view(request):
    if not request.session.get("authenticated",False) or request.session.get("role","none") != "manager":
        request.session["login_error"] = True
        return redirect("../")
    now = datetime.now()
    return render_to_response('main_manager_page.html', {'current_date': now}, context_instance=RequestContext(request))


def logout(request):
    request.session.clear()
    return redirect("../")


def user_upload_strategy(request):
    now = datetime.now()
    return render_to_response('user_upload_strategy_page.html', {'current_date': now}, context_instance=RequestContext(request))


def handle_upload_strategy(request):
    f = request.FILES['datafile']
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, 'upload')
    (root, ext) = os.path.splitext(f.name)
    root += ".strategy"
    path = os.path.join(path, root)
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    try:
        Strategy.objects.get(name=root)
    except Strategy.DoesNotExist:
        s = Strategy(name=root,path=path)
        s.save()

    return redirect("/user/upload_strategy/")

def user_run_strategy(request):
    try:
        data_list = Strategy.objects.all()
    except Strategy.DoesNotExist:
        pass

    return render_to_response('run_strategy_page.html', {'data_list': data_list},
                              context_instance=RequestContext(request))

def run_strategy_handler(request):
    try:
        s = Strategy.objects.get(name=request.POST["strategy_name"])[:1]
    except:
        redirect("/user/run_test/")
    strategy_name = s.name
    strategy_path = s.path
    # call strategy tester cmd with path and params
    p = subprocess.Popen('ls', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    results = []
    for line in p.stdout.readlines():
        results.append(line)

    p.wait()
    return render_to_response('user_statistics_page.html', {'results': results},
                              context_instance=RequestContext(request))


def user_statistics(request):
    now = datetime.now()
    t = get_template('user_statistics_page.html')
    html = t.render(RequestContext(request,{'current_date': now}))
    return HttpResponse(html)


def manager_create_user(request):
    now = datetime.now()
    t = get_template('manager_create_user_page.html')
    html = t.render(RequestContext(request,{'current_date': now}))
    return HttpResponse(html)


def manager_create_profile(request):
    if not request.session.get("authenticated",False) or request.session.get("role","none") != "manager":
        request.session["login_error"] = True
        return redirect("../")
    try:
        data=Data.objects.all()
    except Data.DoesNotExist:
        data=[]
        pass

    return render_to_response('manager_create_profile_page.html', {'data_list': list(data)},
                                    context_instance=RequestContext(request))




def manager_upload_data(request):
    now = datetime.now()
    t = get_template('manager_upload_data_page.html')
    html = t.render(RequestContext(request,{'current_date': now}))
    return HttpResponse(html)


def handle_upload_data(request):
    f = request.FILES['datafile']
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, 'upload')
    (root, ext) = os.path.splitext(f.name)
    root += ".data"
    path = os.path.join(path, root)
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    try:
        Data.objects.get(name=root)
    except Data.DoesNotExist:
        p = Data(name=root, path=path)
        p.save()

    return redirect("/manager/upload_data/")


def manager_statistics(request):
    now = datetime.now()
    t = get_template('manager_statistics_page.html')
    html = t.render(RequestContext(request,{'current_date': now}))
    return HttpResponse(html)


def create_user_action(request):
    user_name, password, email, role = ["", "", "", ""]
    try:
        user_name = request.POST["user"]
        password = request.POST["password"]
        email = request.POST["email"]
        role = "user"
    except:
        return redirect("/manager/create_user/")

    try:
        User.objects.get(name=user_name)
    except User.DoesNotExist:
        u = User(name=user_name, password=password, email=email, role=role)
        u.save()
    return redirect("/manager/create_user/")


def list_users(request):
    return render_to_response('manager_userlist_page.html', {'results': list(User.objects.all())},
                              context_instance=RequestContext(request))


def list_profiles(request):
    return render_to_response('manager_profiles_page.html', {'results': list(Profile.objects.all())},
                              context_instance=RequestContext(request))


def create_profile_action(request):
    name, data_name, commission = ["","",""]
    try:
        name = request.POST["profile"]
        data_name = Data.objects.get(name=request.POST["data_name"])
        commission = request.POST["commission"]
    except:
        return redirect("/manager/create_profile/")

    try:
        Profile.objects.get(name=name)
    except Profile.DoesNotExist:
        p = Profile(name=name, data=data_name, commission=float(commission))
        p.save()
    return redirect("/manager/create_profile/")