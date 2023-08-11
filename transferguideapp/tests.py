from django.test import TestCase
from .models import CourseTransfer, ExternalCourse, InternalCourse, ExternalCollege, Favorites
from django.contrib.auth.models import Group, User
from .searchfilters import search, set_user_college, filterCollege, filterMnemonic, filterNumber, filterName
from django.db.models import Q

# This test is just to verify that CI is working
#class TestFail(TestCase):
#    def test_fail(self):
#        self.assertTrue(False)


def clean_data():
    CourseTransfer.objects.all().delete()
    ExternalCourse.objects.all().delete()
    ExternalCollege.objects.all().delete()
    InternalCourse.objects.all().delete()


class TestModelCreation(TestCase):
    def test_course_transfer_create(self):
        inter_course = InternalCourse(course_name = "Advanced Software Development Techniques", course_number = "3240" , mnemonic = "CS")
        inter_course.save()
        exter_college = ExternalCollege(college_name = "Piedmont Valley Community College")
        exter_college.save()
        exter_course = ExternalCourse(course_name = "Software Development", course_number = "123", mnemonic = "CS", college = ExternalCollege.objects.get(college_name = "Piedmont Valley Community College"))
        exter_course.save()
        course_transfer = CourseTransfer(internal_course = InternalCourse.objects.get(course_number = "3240", mnemonic="CS"), external_course = ExternalCourse.objects.get(course_number = "123", mnemonic="CS"))
        course_transfer.save()
        self.assertEqual(str(course_transfer), str(CourseTransfer.objects.get(external_course = ExternalCourse.objects.get(course_number = "123", mnemonic = "CS"))))
        clean_data()

    def test_external_course_create(self):
        exter_college = ExternalCollege(college_name = "Piedmont Valley Community College")
        exter_college.save()
        exter_course = ExternalCourse(course_name = "Software Development", course_number = "123", mnemonic = "CS", college = ExternalCollege.objects.get(college_name = "Piedmont Valley Community College"))
        exter_course.save()
        self.assertEqual(str(exter_course), str(ExternalCourse.objects.get(course_number="123", mnemonic = "CS")))
        clean_data()


    def test_internal_course_create(self):
        inter_course = InternalCourse(course_name = "Advanced Software Development Techniques", course_number = "3240" , mnemonic = "CS")
        inter_course.save()
        self.assertEqual(str(inter_course), str(InternalCourse.objects.get(course_number="3240", mnemonic = "CS")))
        clean_data()



    def test_external_college_create(self):
        exter_college = ExternalCollege(college_name = "Piedmont Valley Community College")
        exter_college.save()
        self.assertEqual(str(exter_college), str(ExternalCollege.objects.get(college_name = "Piedmont Valley Community College")))
        clean_data()

class ModelMethodTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', password='12345')
        self.user2 = User.objects.create_user(username='testuser2', password='12345')
        self.user3 = User.objects.create_user(username='testuser3', password='12345')
        login = self.client.login(username='testuser1', password='12345')

        self.college = ExternalCollege.objects.create(college_name=f"college{1}",
                                                 domestic_college=True)

        self.external = ExternalCourse.objects.create(id=f"{1}",
                                                      college=self.college,
                                                      mnemonic=f"mnemonic{1}",
                                                      course_number=f"number{1}",
                                                      course_name=f"name{1}")
        self.internal = InternalCourse.objects.create(id=f"{1}",
                                                      mnemonic=f"mnemonic{1}",
                                                      course_number=f"number{1}",
                                                      course_name=f"name{1}")
        for i in range(2, 6):
            extern = ExternalCourse.objects.create(id=f"{i}",
                                                   college=self.college,
                                                   mnemonic=f"mnemonic{i}",
                                                   course_number=f"number{i}",
                                                   course_name=f"name{i}")
            intern = InternalCourse.objects.create(id=f"{i}",
                                                   mnemonic=f"mnemonic{i}",
                                                   course_number=f"number{i}",
                                                   course_name=f"name{i}")
            transfer1 = CourseTransfer.objects.create(internal_course=self.internal,
                                                     external_course=extern,
                                                     accepted=True)
            transfer2 = CourseTransfer.objects.create(internal_course=intern,
                                                      external_course=self.external,
                                                      accepted=True)

            favorite1 = Favorites.objects.create(user=self.user1, transfer=transfer1)
            favorite2 = Favorites.objects.create(user=self.user2, transfer=transfer2)
            favorite3 = Favorites.objects.create(user=self.user3, transfer=transfer1)
            favorite4 = Favorites.objects.create(user=self.user3, transfer=transfer2)

        for i in range(6, 8):
            extern = ExternalCourse.objects.create(id=f"{i}",
                                                   college=self.college,
                                                   mnemonic=f"mnemonic{i}",
                                                   course_number=f"number{i}",
                                                   course_name=f"name{i}")
            intern = InternalCourse.objects.create(id=f"{i}",
                                                   mnemonic=f"mnemonic{i}",
                                                   course_number=f"number{i}",
                                                   course_name=f"name{i}")
            transfer = CourseTransfer.objects.create(internal_course=intern,
                                                      external_course=extern,
                                                      accepted=True)
        return

    def test_get_model(self):
        self.assertEqual(self.internal.get_model(), "internalcourse")
        self.assertEqual(self.external.get_model(), "externalcourse")
        return

    def test_get_transfers(self):
        transIDs = [1, 3, 5, 7]
        internalInput = self.internal.get_transfers()
        internalExpected = CourseTransfer.objects.filter(id__in=transIDs)
        self.assertQuerysetEqual(internalInput, internalExpected, ordered=False)

        transIDs = [2, 4, 6, 8]
        externalInput = self.external.get_transfers()
        externalExpected = CourseTransfer.objects.filter(id__in=transIDs)
        self.assertQuerysetEqual(externalInput, externalExpected, ordered=False)
        return

    def test_get_equivalents(self):
        IDs = [2, 3, 4, 5]

        internalInput = self.internal.get_equivalent()
        internalExpected = ExternalCourse.objects.filter(id__in=IDs)
        self.assertQuerysetEqual(internalInput, internalExpected, ordered=False)

        externalInput = self.external.get_equivalent()
        externalExpected = InternalCourse.objects.filter(id__in=IDs)
        self.assertQuerysetEqual(externalInput, externalExpected, ordered=False)
        return

    def test_get_users(self):
        usernames = ["testuser1", "testuser3"]

        internalInput = self.internal.get_users()
        internalExpected = User.objects.filter(username__in=usernames)
        self.assertQuerysetEqual(internalInput, internalExpected, ordered=False)

        usernames = ["testuser2", "testuser3"]

        externalInput = self.external.get_users()
        externalExpected = User.objects.filter(username__in=usernames)
        self.assertQuerysetEqual(externalInput, externalExpected, ordered=False)
        return

    def test_college_name(self):
        self.assertEquals(self.internal.college_name(), "University of Virginia")
        self.assertEquals(self.external.college_name(), self.college.college_name)



class SearchTests(TestCase):
    def setUp(self):
        self.session = {"search": {"college": "", "mnemonic": "", "number": "", "name": ""}}

    def test_empty_search(self):
        courses, query = search(self.session)
        self.assertEquals(query, Q())
        return

    def test_uva_aliases(self):
        q1, courses1, _ = filterCollege("")
        q2, courses2, _ = filterCollege("uva")
        q3, courses3, _ = filterCollege("university of virginia")

        q4, courses4, _ = filterCollege("the university of virginia")
        q5, courses5, _ = filterCollege("virginia")
        q6, courses6, _ = filterCollege("virginia tech")

        self.assertTrue(courses1.model is InternalCourse)
        self.assertTrue(courses2.model is InternalCourse)
        self.assertTrue(courses3.model is InternalCourse)
        self.assertTrue(q1 == q2 == q3 == Q())

        self.assertTrue(courses4.model is ExternalCourse)
        self.assertTrue(courses5.model is ExternalCourse)
        self.assertTrue(courses6.model is ExternalCourse)
        self.assertTrue((q4 and q5 and q6) != Q())
        return

    def test_filter_college(self):
        name = "Virginia Polytechnic Institute"
        _, _, collegeBefore = filterCollege(name)
        college = ExternalCollege.objects.create(college_name=name, domestic_college=True)
        _, _, collegeAfter = filterCollege(name)
        self.assertFalse(collegeBefore)
        self.assertTrue(collegeAfter)
        self.assertEquals(college, collegeAfter)
        return

    def test_set_user_college(self):
        self.assertTrue("user_college" not in self.session)
        self.assertTrue("user_college_id" not in self.session)

        college = ExternalCollege.objects.none()
        set_user_college(self.session, college)
        self.assertTrue("user_college" not in self.session)
        self.assertTrue("user_college_id" not in self.session)

        name = "Virginia Polytechnic Institute"
        college = ExternalCollege.objects.create(college_name=name, domestic_college=True)

        set_user_college(self.session, college)
        self.assertEquals(self.session["user_college_id"], 1)
        self.assertEquals(self.session["user_college"], name)

    def test_filter_mnemonic(self):
        mnemonic = "MATH"
        full = filterMnemonic(mnemonic)
        empty = filterMnemonic("")
        self.assertEquals(str(full), f"(AND: ('mnemonic', '{mnemonic}'))")
        self.assertEquals(str(empty), "(AND: )")
        return

    def test_filter_number(self):
        number = "1234"
        full = filterNumber(number)
        empty = filterNumber("")
        self.assertEquals(str(full), f"(AND: ('course_number__startswith', '{number}'))")
        self.assertEquals(str(empty), "(AND: )")
        return

    def test_filter_name_alphabetic(self):
        word = "word"
        phrase = "this is a sentence"
        dirty = " t,his:is a /&/ (sen?!tence) "

        Qword = Q(course_name__icontains="word")
        Qphrase = Q(course_name__icontains="this") & Q(course_name__icontains="is") &\
                  Q(course_name__icontains="a") & Q(course_name__icontains="sentence")
        Qdirty = Q(course_name__icontains="t") & Q(course_name__icontains="his") &\
                 Q(course_name__icontains="is") & Q(course_name__icontains="a") &\
                 Q(course_name__icontains="sen") & Q(course_name__icontains="tence")

        self.assertEquals(filterName(word), Qword)
        self.assertEquals(filterName(phrase), Qphrase)
        self.assertEquals(filterName(dirty), Qdirty)
        return


class FavoritesTests(TestCase):

    def setUp(self):
        
        self.user = User.objects.create_user(username='testuser', password='12345')
        i=1
        college = ExternalCollege.objects.create(college_name=f"college{i}",
                                                     domestic_college=True)

        external = ExternalCourse.objects.create(college=college,
                                                     mnemonic=f"mnemonic{i}",
                                                     course_number=f"number{i}",
                                                     course_name=f"name{i}")
        internal = InternalCourse.objects.create(mnemonic=f"mnemonic{i}",
                                                     course_number=f"number{i}",
                                                     course_name=f"name{i}")
        ic = InternalCourse.objects.get(id=1)
        
        self.transfer = CourseTransfer.objects.create( 
            external_course = external,
            internal_course = internal,
            accepted = True 
        )

        self.favorite = Favorites.objects.create(
            user = self.user,
            transfer = self.transfer
        )

    def test_quantity(self):
        count = Favorites.objects.filter(user=self.user).count()
        self.assertEquals(count, 1)

    def test_favorite_instance(self):
        self.assertEqual(self.favorite.user, self.user)
        self.assertEqual(self.favorite.transfer, self.transfer)
        
    def tearDown(self):
        self.favorite.delete()
        self.transfer.delete()
        self.user.delete()
