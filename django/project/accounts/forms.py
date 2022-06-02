from django.forms import ModelForm
from .models import employee,access, history, Grant
from django import forms


#管理用户表
class manageuserform(ModelForm):
    class Meta:
        model = employee
        fields = '__all__'
        exclude = ['employeePassword']

#注册表
class registerform(ModelForm):
    class Meta:
        model = employee
        fields ='__all__'

#找人表
class findemployee(forms.Form):
    employeename = forms.CharField()

#登录表  
class loginform(ModelForm):
    class Meta:
        model = employee
        fields = ['employeeEmail','employeePassword']

#改密码表
class changepasswordform(ModelForm):
    class Meta:
        model = employee
        fields = ['employeePassword']

#授权表
class grantaccessform(ModelForm):
    class Meta:
        model = access
        fields = '__all__'

class editaccessform(ModelForm):
    class Meta:
        model = access
        fields = ['accessName','notes']

class historyform(ModelForm):
    class Meta:
        model = history
        fields = '__all__'