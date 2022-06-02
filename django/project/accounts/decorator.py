from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from .models import employee
from django.shortcuts import render,redirect

#检查是否在线,防二次登录专用
def already_login(view_func):
    def wrapper_func(request, *args, **kwargs):
        #如果有session的话说明在线，不准再登录，禁止卡bug,传送回主页
        if 'employeeName' in request.session:
            return redirect('home')
        #没有session就是没有登录，允许继续去登录页面
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func

#检查是否在线，防零次登录
def is_login(view_func):
    def wrapper_func(request, *args, **kwargs):
        #如果有session的话说明在线，继续
        if 'employeeName' in request.session:
                return view_func(request, *args, **kwargs)
        #没有session就是没有登录，拷走
        else:
            return redirect('login')
    return wrapper_func

#检查账号有没有登录权限
def can_login(view_func):
    def wrapper_func(request, *args, **kwargs):
        #先看看你登录到期没
        if 'employeeName' in request.session:
            #如果你是尊贵的admin，请进
            if request.session['accountLevel'] == 'admin':
                return view_func(request, *args, **kwargs)
            #如果你是不尊贵的user,请进
            elif request.session['accountLevel'] == 'user':
                return view_func(request, *args, **kwargs)
            #user都不是，爬
            else:
                messages.error(request,'You have no access to the system.')
                request.session.clear()
                return redirect('login')
        #到期就请出去
        else:
            return redirect('login')
    return wrapper_func

#检查是不是admin可以去的地方
def admin_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        #照例检查是否登录
        if 'accountLevel' in request.session:
            #如果是尊贵的admin，请进
            if request.session['accountLevel'] == 'admin':
                return view_func(request, *args, **kwargs)
            #不是，警告，滚回主页
            else:
                messages.error(request,'You have no access to this page.')
                return redirect('home')
    return wrapper_func

#检查是不是user可以去的地方
def user_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        #例行检查登录情况
        if 'accountLevel' in request.session:
            #如果是不尊贵的user，那随便进
            if request.session['accountLevel'] == 'user':
                return view_func(request, *args, **kwargs)
            #尊贵的admin别瞎跑
            else:
                messages.error(request,'You have no access to this page.')
                return redirect('home')
    return wrapper_func

