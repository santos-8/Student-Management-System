from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class LoginCheckMiddleWare(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user
        
        # Allow logout to pass through without redirect
        if request.path == reverse("logout"):
            return None

        # Allow Django to serve media/static files in DEBUG without redirecting.
        # Some settings may define STATIC_URL without a leading slash, handle both.
        try:
            media_url = settings.MEDIA_URL or "/media/"
        except Exception:
            media_url = "/media/"
        try:
            static_url = settings.STATIC_URL or "/static/"
        except Exception:
            static_url = "/static/"
        if not media_url.startswith("/"):
            media_url = f"/{media_url}"
        if not static_url.startswith("/"):
            static_url = f"/{static_url}"

        if request.path.startswith(media_url) or request.path.startswith(static_url):
            return None
        
        if user.is_authenticated:
            if user.user_type == "1":
                if modulename == "student_management_app.HodViews":
                    return None
                elif modulename == "student_management_app.views":
                    return None
                else:
                    return HttpResponseRedirect(reverse("admin_home"))
            elif user.user_type == "2":
                if modulename == "student_management_app.StaffViews":
                    return None
                elif modulename == "student_management_app.views":
                    return None
                else:
                    return HttpResponseRedirect(reverse("staff_home"))
            elif user.user_type == "3":
                if modulename == "student_management_app.StudentViews":
                    return None
                elif modulename == "student_management_app.views":
                    return None
                else:
                    return HttpResponseRedirect(reverse("student_home"))
            else:
                return HttpResponseRedirect(reverse("show_login"))
        else:
            if request.path == reverse("show_login") or request.path == reverse("do_login") or modulename == "django.contrib.auth.views":
                return None
            else:
                return HttpResponseRedirect(reverse("show_login"))