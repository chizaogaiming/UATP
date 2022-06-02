from operator import mod
from tkinter import CASCADE
from xml.etree.ElementInclude import DEFAULT_MAX_INCLUSION_DEPTH
from django.db import models
from django.forms import CharField
from django.test import tag


class employee(models.Model):
	employeeName = models.CharField(max_length=100, null=True)
	employeeEmail = models.CharField(max_length=100, null=True)
	employeePassword = models.CharField(max_length=100, null=True)

	#这块是account level
	admin = 'admin'
	user = 'user'
	employee = 'employee'
	dimission = 'dimission'

	ACCOUNT_LEVEL_CHOICE = [
		(admin,'admin'),
		(user,'user'),
		(employee,'employee'),
		(dimission,'dimission'),
	]
	accountLevel = models.CharField(
		max_length = 10,
		choices = ACCOUNT_LEVEL_CHOICE,
		default = employee
	)

	#这块是department
	IT = 'IT'
	HR = 'HR'
	EMPLOYEE_DEPARTMENT_CHOICE = [
		(IT,'Information Technology'),
		(HR,'Human Resources'),
	]
	employeeDepartment = models.CharField(
		max_length = 10,
		choices = EMPLOYEE_DEPARTMENT_CHOICE,
		default = IT
	)

	employeeNotes = models.CharField(max_length=1000, null=True, blank=True)

	def __str__(self):
		return str(self.employeeName)


class access(models.Model):
	accessName = models.CharField(max_length=100, null=True)
	grantTo = models.ManyToManyField(employee, through='Grant')
	notes = models.CharField(max_length=100, null=True,blank=True)
	

	def __str__(self):
		return str(self.accessName)


class history(models.Model):
	accessName = models.CharField(max_length= 100, null=True)
	action = models.CharField(max_length= 100, null=True)
	actTo = models.CharField(max_length= 100, null=True)
	actBy = models.CharField(max_length= 100, null=True)
	actionDate = models.DateField(auto_now=False,auto_now_add=False, null=True)
	recordTime = models.DateTimeField(auto_now_add=True, null=True)

	
#可能没什么用
class Grant(models.Model):
	employee = models.ForeignKey(employee, on_delete=models.CASCADE)
	access = models.ForeignKey(access, on_delete=models.CASCADE)
	rights = models.CharField(max_length=10, null = True)

	def __str__(self):
		return str(self.employee)

