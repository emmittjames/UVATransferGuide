from django.forms import ModelChoiceField, Form, CharField 


# temporary solution, the form should be more dynamic to accept both already register courses as well as new courses
# Likely will need javacript to make this function correctly
class TransferRequestForm(Form):
        external_course_name = CharField()
        external_course_college = CharField()
        external_course_mnemonic = CharField()
        external_course_number = CharField()
        internal_course_id = CharField() 
        internal_course_name = CharField()
        internal_course_mnemonic = CharField()
        internal_course_number = CharField()


class SisSearchForm(Form):
    mnemonic = CharField(required=False)
#    course_name = CharField(required=False)
    course_number = CharField(required=False)
    page = CharField()
