
from .models import ExternalCollege, ExternalCourse, InternalCourse, CourseTransfer, Favorites, TransferRequest
from django.db.models import Q, F, Func, Count, Case, When, Value, CharField, BooleanField
from django.db.models.functions import Concat

# Originally, all of this code was placed in the templates themselves, but
# as the complexity grew, I decided to move everything to get_context_data().
# However, views.py was getting cluttered, so I put everything in separate methods.

########################################################################################
# In order for us to reuse templates, the context dictionary entries of
# InternalCoursePage and ExternalCoursePage must match
########################################################################################

def context_course(context, course, request):
    context['isAdmin'] = True if (request.user.groups.filter(name='admins').exists()) else False
    context['foreign'] = set_foreign(course)
    context['credits'] = set_credits(course)
    context["disabled"] = set_disabled(course, request.session)
    context['tab'], collegeQ = handle_tab(course, request.session)

    if "course_tab" not in request.session:
        request.session["course_tab"] = "all"
    context["all_tab"] = "show active" if (request.session["course_tab"] == "all") else ""
    context["specific_tab"] = "show active" if (request.session["course_tab"] == "specific") else ""


    unspecific, specific = favorite_filters(course, request.user)

    equivalents = course.get_equivalent().annotate(
        totallikes=Count('coursetransfer__favorites', filter=unspecific),

        pagelikes=Count('coursetransfer__favorites', filter=specific),

        color=Case(When(totallikes=0, then=Value('light')),
                   When(Q(totallikes__gte=1, pagelikes=0), then=Value('warning')),
                   When(Q(totallikes__gte=1, pagelikes__gte=1), then=Value('success')),
                   output_field=CharField()),

        action=Case(When(pagelikes=0, then=Value('Favorite')),
                    When(pagelikes__gte=1, then=Value('Unfavorite')),
                    output_field=CharField())
    )

    context["equivalents"] = equivalents
    context["equivalents_specific"] = equivalents.filter(collegeQ)

########################################################################################

def handle_tab(course, session):
    if "user_college_id" in session and course.get_model() == "internalcourse":
        tab = True
        collegeQ = Q(college__id=session["user_college_id"])
    else:
        tab = False
        collegeQ = ~Q(id=-1)
    return tab, collegeQ

def favorite_filters(course, user):
    unspecific = Q(coursetransfer__favorites__user=user)
    if course.get_model() == "internalcourse":
        specific = unspecific & Q(coursetransfer__internal_course=course)
    else:
        specific = unspecific & Q(coursetransfer__external_course=course)
    return unspecific, specific

def set_foreign(course):
    if course.get_model() == "externalcourse":
        if not course.college.domestic_college:
            return "(Foreign)"
    return ""

def set_credits(course):
    if course.get_model() == "internalcourse":
        if int(course.credits) >= 0:
            return course.credits
    return ""

def set_disabled(course, session):
    disabled = False
    if "SC" in session:
        if course.get_model() == "internalcourse":
            if session["SC"]["internalID"] == course.id:
                disabled = True
        else:
            if session["SC"]["externalID"] == course.id:
                disabled = True
    return disabled

########################################################################################
# In order for us to reuse templates, the context dictionary entries of
# CourseRequest, UpdateInternal, UpdateExternal, and UpdateCourses must match
########################################################################################

# define context for CourseRequest view
def context_course_request(context, course, session):
    if "user_college" in session:
        collegeID = session["user_college_id"]
        college = session["user_college"]
        q = Q(id=collegeID)
    else:
        collegeID = ""
        college = ""
        q = Q()

    context['colleges'] = ExternalCollege.objects.filter(~q).order_by('college_name')
    context['collegeID'] = collegeID
    context['college'] = college
    context['action'] = 'make_request'
    context['course'] = InternalCourse.objects.none()
    context['courseID'] = course.id
    context['title'] = "Course Transfer Request"
    context['link'] = True
    context['comment'] = True
    context['credits'] = False

# define context for UpdateInternal view
def context_update_internal(context, course):
    context['colleges'] = ExternalCollege.objects.none()
    context['collegeID'] = ""
    context['college'] = "University of Virginia"
    context['action'] = 'submit_update'
    context['course'] = course
    context['courseID'] = course.id
    context['title'] = "Edit UVA Course"
    context['link'] = False
    context['comment'] = False
    context['credits'] = True

# define context for UpdateExternal view
def context_update_external(context, course):
    q = Q(id=course.college.id)
    context['colleges'] = ExternalCollege.objects.filter(~q).order_by('college_name')
    context['collegeID'] = course.college.id
    context['college'] = course.college.college_name
    context['action'] = 'submit_update'
    context['course'] = course
    context['courseID'] = course.id
    context['title'] = "Edit External Course"
    context['link'] = False
    context['comment'] = False
    context['credits'] = False

# define context for UpdateCourses view
def context_update_course(context):
    context['colleges'] = ExternalCollege.objects.order_by('college_name')
    context['collegeID'] = ""
    context['college'] = "University of Virginia"
    context['action'] = 'submit_update'
    context['course'] = InternalCourse.objects.none()
    context['courseID'] = ""
    context['title'] = "Add Course"
    context['link'] = False
    context['comment'] = False
    context['credits'] = True

########################################################################################
# Context for ViewRequests view
########################################################################################


def context_view_requests(context, user, session):
    # control which elements are visible for admins vs. common users
    if user.groups.filter(name='admins').exists():
        context["isAdmin"] = True
        user_specific = Q()
    else:
        context["isAdmin"] = False
        user_specific = Q(user=user)

    # set which tab is active
    if "request_tab" not in session:
        session["request_tab"] = "pending"
    context["pending_tab"] = "show active" if (session["request_tab"] == "pending") else ""
    context["accepted_tab"] = "show active" if (session["request_tab"] == "accepted") else ""
    context["rejected_tab"] = "show active" if (session["request_tab"] == "rejected") else ""
    context["all_tab"] = "show active" if (session["request_tab"] == "all") else ""

    # annotate transfer requests with relevant attributes
    requests = TransferRequest.objects.filter(user_specific).annotate(
        color=Case(When(Q(condition=TransferRequest.pending), then=Value('light')),
                   When(Q(condition=TransferRequest.accepted), then=Value('success')),
                   When(Q(condition=TransferRequest.rejected), then=Value('danger')),
                   output_field=CharField()),
        btn=Case(When(Q(condition=TransferRequest.pending), then=Value('outline-dark')),
                 When(Q(condition=TransferRequest.accepted), then=Value('outline-success')),
                 When(Q(condition=TransferRequest.rejected), then=Value('outline-danger')),
                 output_field=CharField()),

        visibility=Case(When(Q(condition=TransferRequest.pending), then=Value("none")),
                        When(~Q(condition=TransferRequest.pending), then=Value("block")),
                        output_field=CharField()),
    )

    # filter which transfer requests are under each tab
    context["all"] = requests.order_by('-created_at')
    context["pending"] = requests.filter(condition=TransferRequest.pending).order_by('-created_at')
    context["accepted"] = requests.filter(condition=TransferRequest.accepted).order_by('-updated_at')
    context["rejected"] = requests.filter(condition=TransferRequest.rejected).order_by('-updated_at')

    # count how many of user's transfer requests are under each tab
    myRequests = TransferRequest.objects.filter(user=user).aggregate(
        pending_cnt=Count('pk', filter=Q(condition=TransferRequest.pending)),
        accepted_cnt=Count('pk', filter=Q(condition=TransferRequest.accepted)),
        rejected_cnt=Count('pk', filter=Q(condition=TransferRequest.rejected)),
        total_cnt=Count('pk'),
    )

    # set percentage of user's transfer requests for each condition
    total = myRequests["total_cnt"]
    if total != 0:
        context["pending_pct"] = 100 * myRequests["pending_cnt"] / total
        context["accepted_pct"] = 100 * myRequests["accepted_cnt"] / total
        context["rejected_pct"] = 100 * myRequests["rejected_cnt"] / total
    else:
        context["pending_pct"] = 0
        context["accepted_pct"] = 0
        context["rejected_pct"] = 0


def context_profile_page(context, user, session, profile):
    # set name
    context['name'] = f"{profile.first_name} {profile.last_name}"

    # control which elements are visible for admins vs. common users
    context["isAdmin"] = True if (user.groups.filter(name='admins').exists()) else False

    # set which tab is active
    if "request_tab" not in session:
        session["request_tab"] = "pending"
    context["pending_tab"] = "show active" if (session["request_tab"] == "pending") else ""
    context["accepted_tab"] = "show active" if (session["request_tab"] == "accepted") else ""
    context["rejected_tab"] = "show active" if (session["request_tab"] == "rejected") else ""
    context["all_tab"] = "show active" if (session["request_tab"] == "all") else ""

    # annotate transfer requests with relevant attributes
    requests = TransferRequest.objects.filter(user=profile).annotate(
        color=Case(When(Q(condition=TransferRequest.pending), then=Value('light')),
                   When(Q(condition=TransferRequest.accepted), then=Value('success')),
                   When(Q(condition=TransferRequest.rejected), then=Value('danger')),
                   output_field=CharField()),
        btn=Case(When(Q(condition=TransferRequest.pending), then=Value('outline-dark')),
                 When(Q(condition=TransferRequest.accepted), then=Value('outline-success')),
                 When(Q(condition=TransferRequest.rejected), then=Value('outline-danger')),
                 output_field=CharField()),

        visibility=Case(When(Q(condition=TransferRequest.pending), then=Value("none")),
                        When(~Q(condition=TransferRequest.pending), then=Value("block")),
                        output_field=CharField()),
    )

    # filter which transfer requests are under each tab
    context["all"] = requests.order_by('-created_at')
    context["pending"] = requests.filter(condition=TransferRequest.pending).order_by('-created_at')
    context["accepted"] = requests.filter(condition=TransferRequest.accepted).order_by('-updated_at')
    context["rejected"] = requests.filter(condition=TransferRequest.rejected).order_by('-updated_at')

########################################################################################




