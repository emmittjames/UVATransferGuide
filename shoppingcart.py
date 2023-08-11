from django.shortcuts import get_object_or_404
from transferguideapp.models import InternalCourse, ExternalCourse

# ShoppingCart = [InternalCourse.id, ExternalCourse.id]
class ShoppingCart:
    def __init__(self, request):
        self.session = request.session
        # https://stackoverflow.com/questions/69016487/cart-session-in-django
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = [None, None]
        self.cart = cart

    def __str__(self):
        items = [None,None]
        if self.cart[0] != None: 
            items[0] = get_object_or_404(InternalCourse, id=self.cart[0].id)
        if self.cart[1] != None:
            print("here")
            items[1] = get_object_or_404(ExternalCourse, id=self.cart[1].id)

        return f"{items[0]}\n{items[1]}"

    def get_ic(self):
        return InternalCourse.objects.get(id=self.cart[0])

    def get_ec(self):
        return ExternalCourse.objects.get(id=self.cart[1])  

    def add(self, course):
        if type(course) == InternalCourse:
            self.cart[0] = course.id
            print(f"{InternalCourse.objects.get(id=self.cart[0])} added to cart")
        else: 
            print(self.cart[1])
            self.cart[1] = course.id
            print(f"{ExternalCourse.objects.get(id=self.cart[1])} added to cart")
        


        self.session['cart'] = self.cart
        self.session.modified = True

