from django.conf.urls.defaults import *
import views

urlpatterns = patterns('',
    url(r'^$', views.overview, name="badges_overview"),
    url(r'^(?P<slug>[A-Za-z0-9_-]+)/$', views.detail, name="badge_detail"),
    )