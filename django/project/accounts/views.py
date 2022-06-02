from functools import total_ordering
from multiprocessing import context
from operator import truediv
from sre_constants import ANY
from urllib.robotparser import RequestRate
from django.shortcuts import render,redirect
from django.http import HttpResponse

from django.core.paginator import Paginator
from .filters import historyfilter
from accounts.decorator import *
from .models import *
from .forms import * 
from django.forms import formset_factory
from django.contrib import messages
import datetime

#login page

# Go through decorator.py，already_login function
@already_login
def login(request):
    #load form when loading the page
    form = loginform()
    #if submit
    if request.method =='POST':
        #retrieve login information
        useremail = request.POST.get('useremail')
        password = request.POST.get('password')
        #matching email input with database, if successfully, copy user info into e
        if employee.objects.filter(employeeEmail=useremail).exists() == True:
            e=employee.objects.get(employeeEmail=useremail)
            #validate password, if correct，session user information and redirect to home page
            if password == e.employeePassword:
                request.session['employeeid'] = e.id
                request.session['employeeName'] = e.employeeName
                request.session['employeeEmail'] = e.employeeEmail
                request.session['employeePassword'] = e.employeePassword
                request.session['accountLevel'] = e.accountLevel
                request.session['employeeDepartment'] = e.employeeDepartment
                request.session['employeeNotes'] = e.employeeNotes
                request.session.set_expiry(1000)
                return redirect('home')
            #if password input is wrong, error message.
            else:
                messages.error(request,'User email or user password is wrong.')
        #if email is not exist in databse, error message.
        else:
            messages.error(request,'EmployeeID does not exist.')

    context={'form':form,}
    return render(request,'accounts/login.html',context)


#home page

#check whether login using is_login decorator.
@is_login
#another decorator
@can_login
def home(request):
    #for navbar info
    navname = request.session['employeeName']
    accountlevel = request.session['accountLevel']
    location = 'home'


    context = {'filter':filter,
               'navname':navname,
               'accountlevel':accountlevel,
               'home':location,
    }
    return render(request,'accounts/home.html',context)


#change password page
#check whether login using decorator is_login
@is_login
def changepassword(request):
    #for navbar info
    navname = request.session['employeeName']
    accountlevel = request.session['accountLevel']

    #loading form when loading page
    form = changepasswordform()
    #if submit
    if request.method =='POST':
        #if is update request，validate old password
        if request.POST.get('Update') == 'Update':
            if request.POST.get('oldpassword') == request.session['employeePassword']:
                #verify confirm password is same as new password, if yes, store new password into database
                if request.POST.get('confirmpassword') == request.POST.get('employeePassword'):
                    e = employee.objects.get(employeeEmail = request.session['employeeEmail'])
                    form = changepasswordform(request.POST,instance = e )
                    form.save()
                    #if save successfully, print success message
                    messages.success(request,'Password updated.')
                    #if change password successfully, auto logout
                    return redirect('logout')
                #if confirm password not same as new password
                else:
                    messages.error(request,'Confirm Password does not match.')
            #if old password is wrong, error message
            else:
                messages.error(request,'Old password is wrong.')
        #if request is back, redirect to home page
        else:
            return redirect('home')

    context = {'form':form,
               'navname':navname,
               'accountlevel':accountlevel,
    }
    return render(request,'accounts/changepassword.html',context)

#logout function
def logout(request):
    #delete all sessions and redirect to login page
    request.session.clear()
    return redirect('login')


#manage access page
#check whether is login using is_login decorator
@is_login
#only admin is allowed to access this page, ensure this using admin_only decorator
@admin_only
def manageaccess(request):
    #for navbar info
    navname = request.session['employeeName']
    accountlevel = request.session['accountLevel']
    location = 'manageAccess'
    #loading form when loading page
    form = editaccessform()

    #if request is get
    if request.method == 'GET':
        #if request is back, redirect to home
        if request.GET.get('Back') == 'Back':
            return redirect('home')

    #if request is post
    if request.method =='POST':
        if request.POST.get('Submit') == 'Update':
            #if request is update, retrieve inputs, and validate
            form = editaccessform(request.POST)
            if form.is_valid:
                #if access not blank
                if request.POST.get('accessName') != '':
                    #if action is create, check whether access is already exist
                    if request.POST.get('action') == 'Create':
                        if access.objects.filter(accessName=request.POST.get('accessName')).exists() == False:
                            #if not exist, adding access to database, and give success message
                            form.save()
                            change = request.POST.get('accessName')
                            messages.success(request,'New access '+change+' is successfully added.')
                        #if exist, error message
                        else:
                            change = request.POST.get('accessName')
                            messages.error(request,'AccessName '+change+' already exists.')
                    #if action is delete, check whether accessname is exist
                    elif request.POST.get('action') == 'Delete':
                        #if access name not exist, error message
                        if access.objects.filter(accessName=request.POST.get('accessName')).exists() == False:
                            change = request.POST.get('accessName')
                            messages.error(request,'Access '+change+' does not exist.')
                        #if accessname exist, delete from database, and show success message
                        else:
                            change = access.objects.get(accessName = request.POST.get('accessName'))
                            change.delete()
                            changename = request.POST.get('accessName')
                            messages.success(request,'Access '+changename+' is successfully deleted.')
                    #if action is blank, error message
                    else:
                        messages.error(request,'Please choose an action.')
                #if accessname is blank, error message
                else:
                    messages.error(request,'Please enter accessName.')
        #if request is post and not update, redirect to home
        else:
            return redirect('home')
    context = {'form':form,
               'navname':navname,
               'accountlevel':accountlevel,
               'manageAccess':location,
            
    }
    return render(request,'accounts/manageaccess.html',context)


#search user page before manage user page
#check whether is login with is_login decorator
@is_login
#only admin is allowed to access, using admin_only decorator to check
@admin_only
def searchuser(request):
    #for navbar info
    navname = request.session['employeeName']
    accountlevel = request.session['accountLevel']
    location = 'manageUser'

    #retrieve all employee for input dropdown list
    em = employee.objects.all()

    #loading form when loading page
    form = findemployee()

    #if submit, if request is get, redirect to home
    if request.method == 'GET':
        if request.GET.get('Back') == 'Back':
            return redirect('home')

    #if request is post,
    if request.method =="POST":
        #if submit request is search,
        if request.POST.get('submit') == 'Search':
            try:
                #matching input employeeid with database, if exist, retrieve user info to e, redirect to manageuser page with searchid
                if employee.objects.filter(id=request.POST.get('employeename')).exists() == True: 
                    searchid=request.POST.get('employeename')
                    return redirect('/manageuser/%s'%searchid)
                #if not matching, error message
                else:
                    messages.error(request,'The employeeID does not exist.')
            except:
                #matching input employeename with database, if exist, retrieve user info to e, redirect to manageuser page with searchid
                if employee.objects.filter(employeeName = request.POST.get('employeename')).exists() == True:
                    e = employee.objects.get(employeeName = request.POST.get('employeename'))
                    searchid = e.id
                    return redirect('/manageuser/%s'%searchid)
                #if not matching, error message
                else:
                    messages.error(request,'The employeeID does not exist.')

        #if request is create new user, redirect to register page
        if request.POST.get('create') == 'Create New User':
            return redirect('/register')

    context = {'form':form,
               'employee':em,
               'navname':navname,
               'accountlevel':accountlevel,
               'manageUser':location,
    }
    return render(request,'accounts/searchuser.html',context)


#manage user page
#check whether is login using is_login decorator
@is_login
#only admin is allowed to access this page, using admin_only decorator to check
@admin_only
def manageuser(request,searchid):
    #for navbar info
    navname = request.session['employeeName']
    accountlevel = request.session['accountLevel']
    location = 'manageUser'
    #matching searchid with database and retrieve user info into e
    e = employee.objects.get(id=searchid)
    #loading form when loading page and fill with info in e
    form = manageuserform(instance = e)
    #if submit
    if request.method == "POST":
        #if request is update
        if request.POST.get('Update') == 'Update':
            #fill form with input
            form = manageuserform(request.POST)
            #validation
            if form.is_valid:
                #if email is unchange or email is not used, update user info with inputs
                if request.POST.get('employeeEmail')==e.employeeEmail or employee.objects.filter(employeeEmail =request.POST.get('employeeEmail')).exists()==False:
                    form = manageuserform(request.POST, instance = e)
                    form.save()
                    #success message, redirect to search user page
                    username = request.POST.get('employeeName')
                    messages.success(request,'User '+username+' infomation updated!')
                    return redirect('searchuser')
                #if email is duplicated, error message
                else:
                    messages.error(request,'employeeEmail cannot be duplicated.')
        #if request is not update, redirect to searchuser page
        else:
            return redirect('searchuser')

    context={'employee':e,
             'form':form,
             'navname':navname,
             'accountlevel':accountlevel,
             'manageUser':location,
    }
    return render(request,'accounts/manageuser.html',context)


#register new user
#check whether login, using is_login decorator
@is_login
#only admin is allowed to access, using admin_only decorator
@admin_only
def register(request):
    #for navbar info
    navname = request.session['employeeName']
    accountlevel = request.session['accountLevel']
    location = 'manageUser'
    #loading form when loading page
    form = registerform()
    #if submit is post,
    if request.method =="POST":
        #if request is create, fill form with input
        if request.POST.get('Create') == 'Create':
            form = registerform(request.POST)
            if form.is_valid:
                #check everything is filled, and check if email is already exist
                if request.POST.get('employeeName')!='' and request.POST.get('employeeEmail')!='' and request.POST.get('employeePassword')!='':
                    check = employee.objects.filter(employeeEmail = request.POST.get('employeeEmail')).exists()
                    #if yes, error message
                    if check == True:
                        messages.error(request,'Email is exist.')
                    #if not exist, add into database
                    else:
                        form.save()
                        #success message, redirect to search user page
                        username = request.POST.get('employeeName')
                        messages.success(request,'New employee '+username+' is created')
                        return redirect('searchuser')
                #if form is not complete, error message
                else:
                    messages.error(request,'Please fill in form properly.')
            #if form not valid, error message
            else:
                messages.error(request,'Please fill in form properly.')
        #if not request is not post, redirect to search user page
        else:
            return redirect('searchuser')

    context = {'form':form,
               'navname':navname,
               'accountlevel':accountlevel,
               'manageUser':location,
    }
    return render(request,'accounts/register.html',context)

#userportal page
#check whether login using is_login decorator
@is_login
#only user are allowed to access, using user_only decorator
@user_only
def userportal(request):
    #for navbar info
    navname = request.session['employeeName']
    accountlevel = request.session['accountLevel']
    location = 'userPortal'

    #for html to retrieve employee info
    employ = employee.objects.all()
    acceess = access.objects.all()

    dic = {}
    dictionary=dic.items()
    e = {}

    #loading forms when loading page
    form = findemployee()
    grantaccessformset = formset_factory(grantaccessform, extra = 1)
    formset = grantaccessformset()
    

    #if request is get, redirect to home
    if request.method == 'GET':
        if request.GET.get('Back') == 'Back':
            return redirect('home')

    #if request is post, if submit request is search
    if request.method == 'POST':
        if request.POST.get('submit') == 'Search':
            # try if input is number, if yes, using id to retrieve employee
            try:
                #check whether id in database
                if employee.objects.filter(id=request.POST.get('employeename')).exists() == True:
                    #if id exist in database, retrieve selected employee info put into e
                    e = employee.objects.get(id=request.POST.get('employeename'))
                    #for html to print current access
                    currentaccess = e.access_set.all()
                    for Access in currentaccess:
                        grant = Grant.objects.get(employee = e, access = Access)
                        dic[Access.accessName]=grant.rights
                #if id not exist, error message
                else:
                    messages.error(request,'The employee does not exist.')
            #if input is not number, then treat input as employeeName
            except:
                #if employeename in database retrieve employee infomation into e
                if employee.objects.filter(employeeName = request.POST.get('employeename')).exists() == True:
                    e = employee.objects.get(employeeName=request.POST.get('employeename'))
                    #for html to print current access
                    currentaccess = e.access_set.all()
                    for Access in currentaccess:
                        grant = Grant.objects.get(employee = e, access = Access)
                        if grant.rights =='readOnly':
                            dic[Access.accessName]=grant.rights
                        else:
                            dic[Access.accessName]=''
                #if employeename not in database, error message
                else:
                    messages.error(request,'The employee does not exist.')

        #if request is update
        if request.POST.get('submit') == 'Update':
            #fill formset with inputs
            formset = grantaccessform(request.POST)
            if formset.is_valid:
                #if actiondate not blank, loop all accessinput
                if request.POST.get('actiondate') !='':
                    for accessInput in request.POST.getlist('accessName'):
                        #if accessinput is not blank,check whether accessinput can match with database
                        if accessInput !='':
                            if access.objects.filter(accessName = accessInput).exists() == True:
                                #if accessinput match in database, retrieve access into a
                                a = access.objects.get(accessName = accessInput)

                                #if action input is write, loop all employeeinput
                                if request.POST.get('action') == 'Write':
                                    for employeeInput in request.POST.getlist('grantTo'):
                                        #if employeeInput not blank
                                        if employeeInput !='':
                                            #if employeeinput is number, treat as employeeid
                                            try:
                                                #if employeeid exist in database, check whether access is already granted to the employee
                                                if employee.objects.filter(id = employeeInput).exists() == True:
                                                    #if access already granted to the employee, retrieve the relationship infomation into grant
                                                    if a.grantTo.filter(id = employeeInput).exists() == True:
                                                        grant = Grant.objects.get(employee = employee.objects.get(id = employeeInput), 
                                                                                access = access.objects.get(accessName=accessInput))
                                                        #if relationship between the access and the employee is write, error message
                                                        if grant.rights =='write':
                                                            messageEmployee = str(employeeInput)
                                                            messageAccess = str(accessInput)
                                                            messages.error(request, messageEmployee+' already has '+messageAccess)
                                                        #if relationship is not write, then upgrade to write
                                                        else:
                                                            #targetAccess store selected access info
                                                            #targetEmployee store selected employee info
                                                            targetAccess = access.objects.get(accessName=accessInput)
                                                            targetEmployee = employee.objects.get(id = employeeInput)
                                                            #remove readonly relationship and grant write access, save
                                                            targetAccess.grantTo.remove(targetEmployee)
                                                            targetAccess.save()
                                                            grant = Grant(employee = targetEmployee, access = targetAccess, rights = 'write')
                                                            grant.save()
                                                            #record into history
                                                            record = history(
                                                                accessName = accessInput,
                                                                action = request.POST.get('action'),
                                                                actTo = targetEmployee.employeeName,
                                                                actBy = request.session['employeeName'],
                                                                actionDate = request.POST.get('actiondate'),
                                                            )
                                                            record.save()
                                                            #success message
                                                            messageAccess = str(accessInput)
                                                            messageEmployee = str(employeeInput)
                                                            messages.success(request,messageAccess+' has successfully granted to '+messageEmployee)
                                                    #if the employee has no relationship with the access, grant write access
                                                    else:
                                                        #targetAccess store selected access info
                                                        #targetEmployee store selected employee info
                                                        targetAccess = access.objects.get(accessName=accessInput)
                                                        targetEmployee = employee.objects.get(id = employeeInput)
                                                        #grant write access and save
                                                        grant = Grant(employee = targetEmployee, access = targetAccess, rights = 'write')
                                                        grant.save()
                                                        #record into history
                                                        record = history(
                                                            accessName = accessInput,
                                                            action = request.POST.get('action'),
                                                            actTo = targetEmployee.employeeName,
                                                            actBy = request.session['employeeName'],
                                                            actionDate = request.POST.get('actiondate'),
                                                        )
                                                        record.save()
                                                        #success message
                                                        messageAccess = str(accessInput)
                                                        messageEmployee = str(employeeInput)
                                                        messages.success(request,messageAccess+' has successfully granted to '+messageEmployee)
                                                #if employee does not exist in database, error message
                                                else:
                                                    messages.error(request, 'employee does not exist.')

                                            #if employeeinput is not number, treat as employeename
                                            except:
                                                #if employeename in database
                                                if employee.objects.filter(employeeName = employeeInput).exists() == True:
                                                    #if the access has relationship with  the employee, retrieve relationship info into grant
                                                    if a.grantTo.filter(employeeName = employeeInput).exists() == True:
                                                        grant = Grant.objects.get(employee = employee.objects.get(employeeName = employeeInput), 
                                                                                access = access.objects.get(accessName=accessInput))
                                                        #if relationship is write, error message
                                                        if grant.rights =='write':
                                                            messageEmployee = str(employeeInput)
                                                            messageAccess = str(accessInput)
                                                            messages.error(request, messageEmployee+' already has '+messageAccess)
                                                        #if relationship is not write, upgrade to write
                                                        else:
                                                            #targetaccess store selected access info
                                                            #targetemployee store selected employee info
                                                            targetAccess = access.objects.get(accessName=accessInput)
                                                            targetEmployee = employee.objects.get(employeeName = employeeInput)
                                                            #remove readonly access and grant write access
                                                            targetAccess.grantTo.remove(targetEmployee)
                                                            targetAccess.save()
                                                            grant = Grant(employee = targetEmployee, access = targetAccess, rights = 'write')
                                                            grant.save()
                                                            #record history
                                                            record = history(
                                                                accessName = accessInput,
                                                                action = request.POST.get('action'),
                                                                actTo = targetEmployee.employeeName,
                                                                actBy = request.session['employeeName'],
                                                                actionDate = request.POST.get('actiondate'),
                                                            )
                                                            record.save()
                                                            #success message
                                                            messageAccess = str(accessInput)
                                                            messageEmployee = str(employeeInput)
                                                            messages.success(request,messageAccess+' has successfully granted to '+messageEmployee)
                                                    #if the access has no relationship with the employee
                                                    else:
                                                        #targetaccess store selected access info
                                                        #targetemployee store selected employee info
                                                        targetAccess = access.objects.get(accessName=accessInput)
                                                        targetEmployee = employee.objects.get(employeeName = employeeInput)
                                                        #grant and save
                                                        grant = Grant(employee = targetEmployee, access = targetAccess, rights = 'write')
                                                        grant.save()
                                                        #record history
                                                        record = history(
                                                            accessName = accessInput,
                                                            action = request.POST.get('action'),
                                                            actTo = targetEmployee.employeeName,
                                                            actBy = request.session['employeeName'],
                                                            actionDate = request.POST.get('actiondate'),
                                                        )
                                                        record.save()
                                                        #success message
                                                        messageAccess = str(accessInput)
                                                        messageEmployee = str(employeeInput)
                                                        messages.success(request,messageAccess+' has successfully granted to '+messageEmployee)
                                                #if employee does not exist in database, error message
                                                else:
                                                    messages.error(request, 'employee does not exist.')
                                #if accessinput is readonly
                                elif request.POST.get('action') == 'ReadOnly':
                                    #loop all employee input
                                    for employeeInput in request.POST.getlist('grantTo'):
                                        #if employeeinput is not blank
                                        if employeeInput !='':
                                            #if employeeinput is number, treat as employeeid
                                            try:
                                                #if employeeid exist in database
                                                if employee.objects.filter(id = employeeInput).exists() == True:
                                                    #if the access has relationship with employee, error message
                                                    if a.grantTo.filter(id = employeeInput).exists() == True:
                                                        messageEmployee = str(employeeInput)
                                                        messageAccess = str(accessInput)
                                                        messages.error(request, messageEmployee+' already has '+messageAccess)
                                                    else:
                                                    #targetAccess store selected access info
                                                    #targetEmployee store selected employee info
                                                        targetAccess = access.objects.get(accessName=accessInput)
                                                        targetEmployee = employee.objects.get(id = employeeInput)
                                                        #grant and save
                                                        grant = Grant(employee = targetEmployee, access = targetAccess, rights = 'readOnly')
                                                        grant.save()
                                                        #record history
                                                        record = history(
                                                            accessName = accessInput,
                                                            action = request.POST.get('action'),
                                                            actTo = targetEmployee.employeeName,
                                                            actBy = request.session['employeeName'],
                                                            actionDate = request.POST.get('actiondate'),
                                                        )
                                                        record.save()
                                                        #success message
                                                        messageAccess = str(accessInput)
                                                        messageEmployee = str(employeeInput)
                                                        messages.success(request,messageAccess+' has successfully granted to '+messageEmployee)
                                                #if employee not in database
                                                else:
                                                    messages.error(request, 'employee act to does not exist.')
                                            #if employee input is not number, treat as employeename 
                                            except:
                                                #if employeename exist in database,
                                                if employee.objects.filter(employeeName = employeeInput).exists() == True:
                                                    #if the access has relationship with the employee
                                                    if a.grantTo.filter(employeeName = employeeInput).exists() == True:
                                                        #error message
                                                        messageEmployee = str(employeeInput)
                                                        messageAccess = str(accessInput)
                                                        messages.error(request, messageEmployee+' already has '+messageAccess)
                                                    #if the access has no relationship with the employee
                                                    else:
                                                        #targetaccess store selected access info
                                                        #targetemployee store selected employee info
                                                        targetAccess = access.objects.get(accessName=accessInput)
                                                        targetEmployee = employee.objects.get(employeeName = employeeInput)
                                                        #grant and save
                                                        grant = Grant(employee = targetEmployee, access = targetAccess, rights = 'readOnly')
                                                        grant.save()
                                                        #record history
                                                        record = history(
                                                            accessName = accessInput,
                                                            action = request.POST.get('action'),
                                                            actTo = targetEmployee.employeeName,
                                                            actBy = request.session['employeeName'],
                                                            actionDate = request.POST.get('actiondate'),
                                                        )
                                                        record.save()
                                                        #success message
                                                        messageAccess = str(accessInput)
                                                        messageEmployee = str(employeeInput)
                                                        messages.success(request,messageAccess+' has successfully granted to '+messageEmployee)
                                                #if employee does not exist in databse, error message
                                                else:
                                                    messages.error(request, 'employee act to does not exist.')
                                #if action is expire or revoke
                                elif request.POST.get('action') == 'Expire' or request.POST.get('action') == 'Revoke':
                                    #loop all employeeinput
                                    for employeeInput in request.POST.getlist('grantTo'):
                                        #if employee is not blank
                                        if employeeInput !='':
                                            #if employeeinput is number, treat as id
                                            try:
                                                #if employeeid exist
                                                if employee.objects.filter(id = employeeInput).exists() == True:
                                                    #if the access has relationship with the employee
                                                    if a.grantTo.filter(id = employeeInput).exists() == True:
                                                        #targetAccess store selected access info
                                                        #targetEmployee store selected employee info
                                                        targetAccess = access.objects.get(accessName=accessInput)
                                                        targetEmployee = employee.objects.get(id = employeeInput)
                                                        #expire access and save
                                                        targetAccess.grantTo.remove(targetEmployee)
                                                        targetAccess.save()
                                                        #record history
                                                        record = history(
                                                            accessName = accessInput,
                                                            action = request.POST.get('action'),
                                                            actTo = targetEmployee.employeeName,
                                                            actBy = request.session['employeeName'],
                                                            actionDate = request.POST.get('actiondate'),
                                                        )
                                                        record.save()
                                                        #success message
                                                        messageAccess = str(accessInput)
                                                        messageEmployee = str(employeeInput)
                                                        messages.success(request,messageAccess+' of '+messageEmployee+' has successfully deleted ')
                                                    #if access has no relationship with the employee, error message
                                                    else:
                                                        messageEmployee = str(employeeInput)
                                                        messageAccess = str(accessInput)
                                                        messages.error(request, messageEmployee+' does not have '+messageAccess)
                                                #if employeeinput not in database, error message
                                                else:
                                                    messages.error(request, 'employee does not exist.')
                                            #if employeeinput not number, treat as employeename
                                            except:
                                                #if employee name in database
                                                if employee.objects.filter(employeeName = employeeInput).exists() == True:
                                                    #if access has relationship with the employee
                                                    if a.grantTo.filter(employeeName = employeeInput).exists() == True:
                                                        #targetAccess store selected access info
                                                        #targetEmployee store selected employee info
                                                        targetAccess = access.objects.get(accessName=accessInput)
                                                        targetEmployee = employee.objects.get(employeeName = employeeInput)
                                                        #expire access and save
                                                        targetAccess.grantTo.remove(targetEmployee)
                                                        targetAccess.save()
                                                        #record history
                                                        record = history(
                                                            accessName = accessInput,
                                                            action = request.POST.get('action'),
                                                            actTo = targetEmployee.employeeName,
                                                            actBy = request.session['employeeName'],
                                                            actionDate = request.POST.get('actiondate'),
                                                        )
                                                        record.save()
                                                        #success message
                                                        messageAccess = str(accessInput)
                                                        messageEmployee = str(employeeInput)
                                                        messages.success(request,messageAccess+' of '+messageEmployee+' has successfully deleted ')
                                                    #if access has no relationship with the employee, error message
                                                    else:
                                                        messageEmployee = str(employeeInput)
                                                        messageAccess = str(accessInput)
                                                        messages.error(request, messageEmployee+' does not have '+messageAccess)
                                                #if employeeinput not found in database, error message
                                                else:
                                                    messages.error(request, 'employee does not exist.')
                                #if action is blank, error message
                                else:
                                    messages.error(request,'Please select an action.')
                            #if access not in database, error message
                            else:
                                messages.error(request,'The access does not exist.')
                #if actiondate not filled, error message
                else:
                    messages.error(request,'Action date cannot be blank')


    context = {'formset':formset,
               'navname':navname,
               'accountlevel':accountlevel,
               'employees':employ,
               'access':acceess,
               'userPortal':location,

               'form':form,
               'employee':e,
               'dic':dictionary,
    }
    return render(request,'accounts/userportal.html',context)


#history page
#check whether login using is_login decorator
@is_login
def viewhistory(request):
    #for navbar info
    navname = request.session['employeeName']
    accountlevel = request.session['accountLevel']
    location = 'history'
    # for html retrieve all employee info into e
    e = employee.objects.all()

    #for html retrieve all history
    hist = (history.objects.all().order_by('-recordTime'))
    
    #for html to retrieve access filter
    accessname = []
    for values in hist:
        if values.accessName not in accessname:
            accessname.append(values.accessName)
    #for html to retrieve employee filter
    actby = []
    for values in hist:
        if values.actBy not in actby:
            actby.append(values.actBy)
    actto = []
    for values in hist:
        if values.actTo not in actto:
            actby.append(values.actTo)

    #combine filter and history
    filter = historyfilter(request.GET, queryset=hist)
    hist = filter.qs

    #if request is refresh, refresh page
    if request.GET.get('refresh')=='refresh':
        return redirect('newhistory')
    #pagination
    paginator = Paginator(hist,20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'employee':e,
               'history':hist,
               'filter':filter,
               'access':accessname,
               'actby':actby,
               'actto':actto,
               'page_obj':page_obj,
               'navname':navname,
               'accountlevel':accountlevel,
               'history':location,
    }
    return render(request,'accounts/history.html',context)