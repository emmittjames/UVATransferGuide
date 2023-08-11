"""transferguide URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from django.conf.urls import handler404, handler500, handler403, handler400

from transferguideapp.views import admin_upgrade, add_college, handle_notifications, set_group, account_info, favorites, update_favorites, CourseSearch, submit_search, InternalCoursePage, ExternalCoursePage, UpdateInternal, UpdateExternal, UpdateCourses, submit_update, make_request, CourseRequest, HandleRequests, accept_request, reject_request, delete_request, ProfilePage, sis_lookup, cart_add, sc_request, auto_accept, refresh_request, error_404

# Out of Date Views ???
from transferguideapp.views import favorite_request, submit_transfer_request, add_favorite, delete_favorite, add_to_cart, cart_TR

urlpatterns = [
    # Login / Logout / Account Info
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name="index.html"), name="home"),
    path('accounts/', include('allauth.urls')),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('set_group/<int:user_id>', set_group , name='set_group'),
    path('account_info/', account_info , name='account_info'),
    path('admin_upgrade', admin_upgrade , name='admin_upgrade'),
    path('handle_notifications', handle_notifications, name='handle_notifications'),

    # Course Search
    path('search/', CourseSearch.as_view(), name='courseSearch'),
    path('search/clear/', submit_search, name='submit_search'), # this is for error handling
    path('search/lookup/', sis_lookup, name="sis_lookup"),

    # Course Pages
    path('internal/<int:pk>', InternalCoursePage.as_view(), name='internalcourse'), # WARNING: hardcoded
    path('external/<int:pk>', ExternalCoursePage.as_view(), name='externalcourse'), # WARNING: hardcoded

    # Add / Edit Course
    path('internal/<int:pk>/update', UpdateInternal.as_view(), name='internalcourseUpdate'), # WARNING: hardcoded
    path('external/<int:pk>/update', UpdateExternal.as_view(), name='externalcourseUpdate'), # WARNING: hardcoded
    path('course/update/', UpdateCourses.as_view(), name='updateCourses'),
    path('course/update/submit', submit_update, name='submit_update'),
    path('course/update/add_college', add_college, name= 'add_college'),
    path('course/shop/', cart_add, name='cart_add'),

    # Favorites
    path('favorites/', favorites, name='favorites'),
    path('favorites/update/', update_favorites, name='update_favorites'),

    # Transfer Requests
    path('internal/<int:pk>/request', CourseRequest.as_view(), name='courseRequest'),
    path('course/request', make_request, name='make_request'),
    path('course/request/cart', sc_request, name="sc_request"),

    # Handle Requests
    path('handle_request', HandleRequests.as_view(), name='handleRequests'),
    path('handle_request/refresh', refresh_request, name='refresh_request'),
    path('handle_request/accept', accept_request, name='accept_request'),
    path('handle_request/reject', reject_request, name='reject_request'),
    path('handle_request/delete', delete_request, name='delete_request'),
    path('handle_request/auto', auto_accept, name='auto_accept'),
    path('handle_request/<str:username>', ProfilePage.as_view(), name='profilePage'), # WARNING: hardcoded

    # Out of Date Views ???
    path('request/', submit_transfer_request, name='request'),
    path('add_favorite/<str:in_course_mnemonic>/<str:in_course_number>/<str:ex_course_mnemonic>/<str:ex_course_number>/', add_favorite, name='add_favorite'),
    path('favorites/delete/<int:favorite_id>/', delete_favorite, name='delete_favorite'),
    path('favorites/<int:favorite_id>/', favorite_request, name='favorite_request'),
    path('add_to_cart/', add_to_cart, name='add_to_cart'),
    path('add_to_cart/submit', cart_TR, name='cart_TR'),

    ]

# handling the 404 error
handler404 = error_404
