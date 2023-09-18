from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
# Не забываем импортировать нужные функции и пакеты
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


class IndexView(LoginRequiredMixin, TemplateView):
   template_name = 'protect/index.html'


   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)

       return context




# Create your views here.
