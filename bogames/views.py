from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.template import loader
from django.http import HttpResponse


class LandingPage(View):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('bogames/landing.html')
        context = {
            'games': {
                'Borkle': reverse('borkle_dashboard')
            }
        }
        return HttpResponse(template.render(context, request))
