from django.contrib.auth.hashers import check_password
from django.db import IntegrityError
from django.urls import reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden
from django.contrib.auth.models import Group, User
from django.views import generic
from transferguideapp.forms import SisSearchForm, TransferRequestForm
from .models import AdminKey, ExternalCourse, InternalCourse, ExternalCollege, CourseTransfer, Favorites, Notification, TransferRequest
from .sis import request_data, unique_id
from django.db.models import Q
from .searchfilters import search
from .context import context_course, context_course_request, context_update_internal, context_update_external, context_update_course, context_view_requests, context_profile_page
from .viewhelper import update_favorites_helper, update_course_helper, request_course_helper, handle_request_helper, sis_lookup_helper, sc_request_helper, add_college_helper
from django.contrib import messages
from helpermethods import course_title_format
from django.db.models import CharField, Value, Max, Count, Sum, IntegerField
from django.db.models.functions import Concat, Cast
from shoppingcart import ShoppingCart
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


def admin_check(user):
    return user.groups.filter(name='admins').exists()


def error_404(request, exception):
    context = {"message": "404: Page Not Found"}
    return render(request, "error.html", context)


@login_required(login_url="home")
def cart_TR(request):
    # comment = request.POST['comment']
    # ec_mnemonic = request.POST['external_course_mnemonic']
    # ec_college = request.POST['external_course_college']
    # ec_name = request.POST['external_course_name']
    # ec_number = request.POST['external_course_number']
    ec_id = request.POST['external_course_id']
    ic_id = request.POST['internal_course_id']
    # ic_number = request.POST['internal_course_number']
    # ic_mnemonic = request.POST['internal_course_mnemonic']
    # ic_name = request.POST['internal_course_name']

    ic = InternalCourse.objects.get(id = ic_id)
    ec = ExternalCourse.objects.get(id = ec_id)


    ct, created = CourseTransfer.objects.get_or_create(external_course = ec, internal_course = ic)
    if created:
        ct.save()

    tr, created = TransferRequest.objects.get_or_create(user=request.user, transfer = ct)
    if created:
        tr.save()
        print(tr)

    return redirect('/handle_request')


@login_required(login_url="home")
def add_to_cart(request):
    if 'college' in request.POST:
        college = request.POST['college']
    else:
       college = 'University of Virginia'

    course_id = request.POST['item_id']

    if college == 'University of Virginia':
        print("uva course detected")
        course = InternalCourse.objects.get(pk=course_id)
    else:
        course = ExternalCourse.objects.get(pk=course_id)

    cart = ShoppingCart(request)
    cart.add(course)
    request.session['cart'] = cart.cart
    request.session.modified = True

    context = {
        'cart': cart
    }

    return render(request, 'index.html', context=context)


@login_required(login_url="home")
def sc_request(request):
    if request.method == "POST":
        try:
            url = request.POST["url"]
            comment = request.POST["comment"]
            internalID = int(request.session["SC"]["internalID"])
            externalID = int(request.session["SC"]["externalID"])
            user = request.user
        except Exception as e:
            message = f"An error occurred: {e}"
            messages.add_message(request, messages.WARNING, message)
        else:
            redirect, type, message = sc_request_helper(user, internalID, externalID, url, comment)
            if message:
                messages.add_message(request, type, message)
                if type == messages.SUCCESS:
                    request.session["SC"] = {"internalID": -1, "externalID": -1}
            return redirect
    return HttpResponseRedirect(reverse('submit_search'))


@login_required(login_url="home")
def cart_add(request):
    cartURL = reverse("submit_search")
    if request.method == "POST":
        try:
            url = request.META.get('HTTP_REFERER')
            model = request.POST["model"]
            courseID = int(request.POST["courseID"])
        except Exception as e:
            message = f"An error occurred: {e}"
            messages.add_message(request, messages.WARNING, message)
        else:
            SC = request.session["SC"] if ("SC" in request.session) else {"internalID": -1, "externalID": -1}
            if model == "internalcourse":
                SC["internalID"] = courseID
            else:
                SC["externalID"] = courseID
            request.session["SC"] = SC
            message = f"Course successfully added to <a href='{cartURL}' class='alert-link'>shopping cart</a>."
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(url)
    return HttpResponseRedirect(cartURL)


@login_required(login_url="home")
def favorite_request(request, favorite_id):
    favorite = get_object_or_404(Favorites, id=favorite_id, user=request.user)

    tr, created = TransferRequest.objects.get_or_create(user=request.user, transfer = favorite.transfer)
    if created:
        tr.save()

    return redirect('/handle_request')


@login_required(login_url="home")
def add_college(request):
    if request.method == "POST":
        try:
            url = request.META.get('HTTP_REFERER')
            name = request.POST['college']
            domestic = True if "domestic" in request.POST else False
        except Exception as e:
            message = f"An error occurred: {e}"
            messages.add_message(request, messages.WARNING, message)
        else:
            type, message = add_college_helper(name, domestic, request.session)
            if message:
                messages.add_message(request, type, message)
            return redirect(url)
    return HttpResponseRedirect(reverse('courseSearch'))


@login_required(login_url="home")
def admin_upgrade(request):
    if(request.method == 'POST'):
        key = request.POST['key']
        if(AdminKey.objects.filter(key=make_password(key,'idkthisissomething')).exists()):
            admin_group = Group.objects.get(name='admins')
            request.user.groups.clear()
            request.user.groups.add(admin_group)
            return render(request, 'account_info.html', {'user': request.user, 'permissions':"Admin"})
        else:
            return render(request, 'account_info.html', {'user': request.user,'permissions':"User"})
    return redirect('home')


@login_required(login_url="home")
def account_info(request):
    user = request.user
    permissions = "User"
    if(user.groups.filter(name='admins').exists()):
        permissions = "Admin"
    if user.is_authenticated:
        return render(request, 'account_info.html', {'user': user, 'permissions': permissions})
    else:
        return redirect('home')


@login_required(login_url="home")
def set_group(request, user_id):
    if(request.method == 'POST'):
        group = request.POST.get('usertype', None)
        g = Group.objects.get(name=group)
        user = User.objects.get(id=user_id)
        user.groups.add(g)
        user.save()
    return redirect('home')


class ProfilePage(LoginRequiredMixin, generic.DetailView):
    login_url = "home"
    redirect_field_name = "redirect_to"
    template_name = "handleRequests.html"
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"
    context_object_name = "profile"

    def get(self, request, *args, **kwargs):
        if admin_check(request.user):
            return super(ProfilePage, self).get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('handleRequests'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context_profile_page(context, self.request.user, self.request.session, self.object)
        return context


class InternalCoursePage(LoginRequiredMixin, generic.DetailView):
    login_url = "home"
    redirect_field_name = "redirect_to"
    template_name = 'course.html'
    model = InternalCourse
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context_course(context, self.object, self.request)
        return context


class ExternalCoursePage(LoginRequiredMixin, generic.DetailView):
    login_url = "home"
    redirect_field_name = "redirect_to"
    template_name = 'course.html'
    model = ExternalCourse
    context_object_name = 'course'

    def get(self, request, *args, **kwargs):
        if self.get_object().admin or self.get_object().coursetransfer_set.filter(accepted=True).exists():
            return super(ExternalCoursePage, self).get(request, *args, **kwargs)
        else:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context_course(context, self.object, self.request)
        return context


class CourseSearch(LoginRequiredMixin, generic.ListView):
    login_url = "home"
    redirect_field_name = "redirect_to"
    template_name = 'search.html'
    model = InternalCourse
    context_object_name = 'course_list'

    def get_queryset(self):
        courses, query = search(self.request.session)
        if query == Q():
            return courses.none()
        else:
            return courses.filter(query).order_by('mnemonic', 'course_number')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['colleges'] = ExternalCollege.objects.values_list('college_name', flat=True).order_by('college_name')
        if "SC" in self.request.session:
            internalID = self.request.session["SC"]["internalID"]
            externalID = self.request.session["SC"]["externalID"]
            context['cart_internal'] = InternalCourse.objects.filter(id=internalID).first()
            context['cart_external'] = ExternalCourse.objects.filter(id=externalID).first()
            context['cart'] = "show" if (context['cart_internal'] or context['cart_external']) else ""
        else:
            context['cart_internal'] = InternalCourse.objects.none()
            context['cart_external'] = ExternalCourse.objects.none()
            context['cart'] = ""
        return context


class UpdateInternal(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
    login_url = "home"
    redirect_field_name = "redirect_to"
    template_name = 'generalForm.html'
    model = InternalCourse
    # context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context_update_internal(context, self.object)
        return context

    def test_func(self):
        return admin_check(self.request.user)

    def handle_no_permission(self):
        return redirect("home")


class UpdateExternal(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
    login_url = "home"
    redirect_field_name = "redirect_to"
    template_name = 'generalForm.html'
    model = ExternalCourse
    # context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context_update_external(context, self.object)
        return context

    def test_func(self):
        return admin_check(self.request.user)

    def handle_no_permission(self):
        return redirect("home")


class UpdateCourses(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    login_url = "home"
    redirect_field_name = "redirect_to"
    template_name = 'generalForm.html'
    queryset = InternalCourse.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context_update_course(context)
        return context

    def test_func(self):
        return admin_check(self.request.user)

    def handle_no_permission(self):
        return redirect("home")


@user_passes_test(admin_check, login_url="home")
@login_required(login_url="home")
def submit_update(request):
    if request.method == "POST":
        try:
            collegeID = request.POST["collegeID"]
            mnemonic = request.POST["mnemonic"]
            number = request.POST["number"]
            name = request.POST["name"]
            courseID = request.POST["id"]
            credits = request.POST["credits"]
        except Exception as e:
            message = f"An error occurred: {e}"
            messages.add_message(request, messages.WARNING, message)
        else:
            collegeID = int(collegeID) if collegeID else -1
            mnemonic = mnemonic.upper()
            number = number.upper()
            courseID = int(courseID) if courseID else -1
            credits = int(credits) if credits else -1

            redirect, type, message = update_course_helper(collegeID, mnemonic, number, name, courseID, credits)
            if message:
                messages.add_message(request, type, message)
            return redirect
    return HttpResponseRedirect(reverse('submit_search'))


@login_required(login_url="home")
def submit_search(request):
    request.session["search"] = {"college": "", "mnemonic": "", "number": "", "name": ""}
    if request.method == "POST":
        try:
            college = request.POST["college"]
            mnemonic = request.POST["mnemonic"]
            number = request.POST["number"]
            name = request.POST["name"]
        except Exception as e:
            message = f"An error occurred: {e}"
            messages.add_message(request, messages.WARNING, message)
        else:
            request.session["search"]["college"] = college
            request.session["search"]["mnemonic"] = mnemonic.upper()
            request.session["search"]["number"] = number.upper()
            request.session["search"]["name"] = name

    return HttpResponseRedirect(reverse('courseSearch'))


@login_required(login_url="home")
def handle_transfer_request(request):
    transfer_form = TransferRequestForm(request.POST)
    if transfer_form.is_valid():
        external_course_name = transfer_form.cleaned_data['external_course_name']
        external_course_college = transfer_form.cleaned_data['external_course_college']
        external_course_mnemonic = transfer_form.cleaned_data['external_course_mnemonic']
        external_course_number = transfer_form.cleaned_data['external_course_number']
        internal_course_id = int(transfer_form.cleaned_data['internal_course_id'])
        internal_course_name = transfer_form.cleaned_data['internal_course_name']
        internal_course_mnemonic = transfer_form.cleaned_data['internal_course_mnemonic']
        internal_course_number = transfer_form.cleaned_data['internal_course_number']
        college = (None, False)
        extern = (None, False)
        intern = (None, False)
        try:
            college = ExternalCollege.objects.update_or_create(college_name = external_course_college)
        except IntegrityError:
            pass
        try:
            extern = ExternalCourse.objects.update_or_create(course_name = external_course_name, college = college[0], mnemonic = external_course_mnemonic, course_number = external_course_number)
        except IntegrityError:
            pass
        try:
            intern = InternalCourse.objects.update_or_create(course_name = internal_course_name, id = internal_course_id, mnemonic = internal_course_mnemonic, course_number = internal_course_number)
        except IntegrityError:
            pass
        try:
            CourseTransfer.objects.update_or_create(external_course = extern[0] , internal_course = intern[0])
        except IntegrityError:
            pass


        return redirect('home')


@login_required(login_url="home")
def handle_sis_request(request):
    sis_form = SisSearchForm(request.GET)
    transfer_form = TransferRequestForm()
    r = [{}]
    if sis_form.is_valid():
        mnemonic = sis_form.cleaned_data['mnemonic']
        course_number = sis_form.cleaned_data['course_number']
        page = sis_form.cleaned_data['page']
        query = {'page' : page}
        if not mnemonic == "":
            query['subject'] = mnemonic
        if not course_number == "":
            query['catalog_nbr'] = course_number
        r = unique_id(request_data(query))
    return render(request, 'request.html', {'transfer_form' : transfer_form , 'sis_form' : sis_form, 'r' : r})


@login_required(login_url="home")
def submit_transfer_request(request):
    r = [{}]
    if request.method == "POST":
        sis_form = SisSearchForm()
        transfer_form = TransferRequestForm(request.POST)
        if 'transfer' in request.POST:
            return handle_transfer_request(request)
    elif request.method == "GET":
        sis_form = SisSearchForm(request.GET)
        transfer_form = TransferRequestForm()
        if 'sis' in request.GET:
            return handle_sis_request(request)
    else:
        transfer_form = TransferRequestForm()
        sis_form = SisSearchForm()
    return render(request, 'request.html', {'transfer_form' : transfer_form , 'sis_form' : sis_form, 'r' : r})


@login_required(login_url="home")
def favorites(request):
    f = Favorites.objects.filter(user=request.user, transfer__accepted=True).order_by('-created_at')
    total = f.values_list('transfer__internal_course', flat=True).distinct().aggregate(total=Sum(Cast('transfer__internal_course__credits', IntegerField())))['total']
    return render(request, 'favorites2.html', {'favorites': f, 'total': total})


#not super sure if this is the best way to do it. need to test on the real database
@login_required(login_url="home")
def add_favorite(request, in_course_mnemonic=None, in_course_number=None, ex_course_mnemonic=None, ex_course_number=None):
    if in_course_mnemonic and in_course_number and ex_course_mnemonic and ex_course_number:
        in_course = get_object_or_404(InternalCourse, mnemonic=in_course_mnemonic, course_number=in_course_number)
        ex_course = get_object_or_404(ExternalCourse, mnemonic=ex_course_mnemonic, course_number=ex_course_number)
        favorite = Favorites(user=request.user, in_course=in_course, ex_course=ex_course)
        favorite.save()
        return redirect('favorites')
    else:
        raise Http404("Missing course information")


@login_required(login_url="home")
def update_favorites(request):
    if request.method == "POST":
        try:
            user = request.user
            pid = request.POST["primary"]
            sid = request.POST["secondary"]
            type = request.POST["type"]
            tab = request.POST["active-tab"]
        except Exception as e:
            message = f"An error occurred: {e}"
            messages.add_message(request, messages.WARNING, message)
        else:
            request.session["course_tab"] = tab
            return update_favorites_helper(user, pid, sid, type)
    return HttpResponseRedirect(reverse('submit_search'))


class CourseRequest(LoginRequiredMixin, generic.DetailView):
    login_url = "home"
    redirect_field_name = "redirect_to"
    model = InternalCourse
    template_name = "generalForm.html"
    # context_object_name = "course"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context_course_request(context, self.object, self.request.session)
        return context


@login_required(login_url="home")
def make_request(request):
    if request.method == "POST":
        try:
            user = request.user
            collegeID = request.POST["collegeID"]
            mnemonic = request.POST["mnemonic"]
            number = request.POST["number"]
            name = request.POST["name"]
            courseID = request.POST["id"]
            url = request.POST["url"]
            comment = request.POST["comment"]
        except Exception as e:
            message = f"An error occurred: {e}"
            messages.add_message(request, messages.WARNING, message)
        else:
            collegeID = int(collegeID) if collegeID else -1
            mnemonic = mnemonic.upper()
            number = number.upper()
            courseID = int(courseID) if courseID else -1

            redirect, type, message = request_course_helper(user, collegeID, mnemonic, number,
                                                            name, courseID, url, comment)
            if message:
                messages.add_message(request, type, message)
            return redirect
    return HttpResponseRedirect(reverse('submit_search'))


@login_required(login_url="home")
def delete_favorite(request, favorite_id):
    favorite = get_object_or_404(Favorites, id=favorite_id, user=request.user)
    favorite.delete()
    return redirect('favorites')


class HandleRequests(LoginRequiredMixin, generic.ListView):
    login_url = "home"
    redirect_field_name = "redirect_to"
    template_name = 'handleRequests.html'
    context_object_name = 'user_list'
    queryset = User.objects\
        .filter(transferrequest__condition=TransferRequest.pending)\
        .annotate(name=Concat('first_name', Value(' '), 'last_name', output_field=CharField()),
                  time=Max('transferrequest__created_at'),
                  count=Count('transferrequest'))\
        .order_by('-time')[:10] # limit at 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context_view_requests(context, self.request.user, self.request.session)
        return context

@login_required(login_url="home")
def refresh_request(request):
    request.session["request_tab"] = "pending"
    return HttpResponseRedirect(reverse('handleRequests'))

@user_passes_test(admin_check, login_url="home")
@login_required(login_url="home")
def accept_request(request):
    request.session["request_tab"] = "pending"
    if request.method == "POST":
        try:
            requestID = request.POST["requestID"]
            adminResponse = request.POST["adminResponse"]
            tab = request.POST["tab"]
            url = request.META.get('HTTP_REFERER')
        except Exception as e:
            message = f"An error occurred: {e}"
            messages.add_message(request, messages.WARNING, message)
        else:
            request.session["request_tab"] = tab
            handle_request_helper(requestID, adminResponse, accepted=True)
            return redirect(url)
    return HttpResponseRedirect(reverse('handleRequests'))


@user_passes_test(admin_check, login_url="home")
@login_required(login_url="home")
def reject_request(request):
    request.session["request_tab"] = "pending"
    if request.method == "POST":
        try:
            requestID = request.POST["requestID"]
            adminResponse = request.POST["adminResponse"]
            tab = request.POST["tab"]
            url = request.META.get('HTTP_REFERER')
        except Exception as e:
            message = f"An error occurred: {e}"
            messages.add_message(request, messages.WARNING, message)
        else:
            request.session["request_tab"] = tab
            handle_request_helper(requestID, adminResponse, accepted=False)
            return redirect(url)
    return HttpResponseRedirect(reverse('handleRequests'))


@user_passes_test(admin_check, login_url="home")
@login_required(login_url="home")
def delete_request(request):
    request.session["request_tab"] = "pending"
    if request.method == "POST":
        try:
            requestID = request.POST["requestID"]
            tab = request.POST["tab"]
            url = request.META.get('HTTP_REFERER')
        except Exception as e:
            message = f"An error occurred: {e}"
            messages.add_message(request, messages.WARNING, message)
        else:
            request.session["request_tab"] = tab
            TransferRequest.objects.filter(id=requestID).delete()
            return redirect(url)
    return HttpResponseRedirect(reverse('handleRequests'))


@login_required(login_url="home")
def sis_lookup(request):
    if request.method == "POST":
        try:
            sisMnemonic = request.POST["sisMnemonic"]
            sisNumber = request.POST["sisNumber"]
        except Exception as e:
            message = f"An error occurred: {e}"
            messages.add_message(request, messages.WARNING, message)
        else:
            redirect, type, message = sis_lookup_helper(sisMnemonic, sisNumber)
            if message:
                messages.add_message(request, type, message)
            return redirect
    return HttpResponseRedirect(reverse('submit_search'))


@login_required(login_url="home")
def auto_accept(request):
    requests = TransferRequest.objects.filter(user=request.user, condition=TransferRequest.pending)
    for r in requests:
        response = "Your transfer request has been accepted by the auto-accept bot."
        handle_request_helper(r.id, response, accepted=True)
    return HttpResponseRedirect(reverse('handleRequests'))


@login_required(login_url="home")
def handle_notifications(request):
    user = request.user;
    Notification.objects.filter(user = user).delete();
    return HttpResponseRedirect(reverse('handleRequests'))
