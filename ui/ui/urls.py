"""ui URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

from StrategyUI import views


urlpatterns = [
    url(r'^user/upload_strategy/$', views.user_upload_strategy, name='user_upload_strategy'),
    url(r'^user/upload_data_handle/$', views.handle_upload_strategy,name='handle_upload_strategy'),
    url(r'^user/run_strategy_handler/$', views.run_strategy_handler,name='run_strategy_handler'),
    url(r'^user/run_test/$', views.user_run_strategy,name='user_run_strategy'),
    url(r'^user/statistics/$', views.user_statistics,name='user_statistics'),
    url(r'^manager/$', views.main_manager_view,name='main_manager_view'),
    url(r'^manager/create_user/$', views.manager_create_user,name='manager_create_user'),
    url(r'^manager/create_user_action/$', views.create_user_action,name='create_user_action'),
    url(r'^manager/create_profile/$', views.manager_create_profile,name='manager_create_profile'),
    url(r'^manager/create_profile_action/$', views.create_profile_action,name='create_profile_action'),
    url(r'^manager/list_users/$', views.list_users,name='list_users'),
    url(r'^manager/list_profiles/$', views.list_profiles,name='list_profiles'),
    url(r'^manager/upload_data/$', views.manager_upload_data,name='manager_upload_data'),
    url(r'^manager/upload_data_handle/$', views.handle_upload_data,name='handle_upload_data'),
    url(r'^manager/statistics/$', views.manager_statistics,name='manager_statistics'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout,name='logout'),
    url(r'^user/$', views.main_user_view,name='user'),
    url(r'^', views.index, name='index'),
]
