from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.basic, name='basic'),
    url(r'upload/$', views.check, name='checks'),
    # url(r'error/(?P<error>\w+)/$', views.error, name='error'),

]