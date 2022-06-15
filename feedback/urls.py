from django.urls import re_path as url
from . import views
from .views import index

urlpatterns = [
    url(r'^$',index,name='list'),
    url(r'^thanks/$',views.thanks),
    url(r'^create/$',views.create_company),
    url(r'^(?P<company_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^reviews/(?P<company_id>[0-9]+)/$', views.review, name='review'),
    url(r'^reviews/create_review/(?P<company_id>[0-9]+)/$', views.create_review, name='review'),
]