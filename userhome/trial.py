# # anshad code 

# def wishlist(request):
#     wishlist_items = WishlistItem.objects.filter(wishlist__user=request.user)
#     context = {
#         'wishlist_items': wishlist_items
#     }
#     return render(request, 'main/wishlist.html', context)

# @login_required(login_url='login')
# def add_to_wishlist(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     wishlist, created = Wishlist.objects.get_or_create(user=request.user)
#     wishlist_items = wishlist.wishlistitem_set.all()
#     for item in wishlist_items:
#         if item.product == product:
#             messages.warning(request, 'This product is already in your wishlist')
#             return redirect('home')
#     wishlist_item = WishlistItem.objects.create(wishlist=wishlist, product=product)
#     messages.success(request, 'Product added to your wishlist')
#     return redirect('home')

# def remove_from_wishlist(request, item_id):
#     wishlist_item = WishlistItem.objects.get(id=item_id)
#     wishlist_item.delete()
#     return redirect('wishlist')

# # my code

 
# # @login_required(login_url='login')
# def wishlist(request):
#     user_id = request.user.id
#     current_user = Customer.objects.get(id=user_id)
#     wish = Wishlist.objects.filter(user=current_user)
#     context = {'wish': wish}
#     return render(request, 'wishlist.html', context)

    
# # @login_required(login_url='login')
# # def add_to_wishlist(request, product_id):
# #     user_Id =request.user.id
# #     user = Customer.objects.get(id=user_Id)
# #     product=Product.objects.get(id=product_id)
# #     try:
# #         Wishlist.objects.get(user=user, product=product)
# #     except:
# #         Wishlist(user=user,product=product).save()
# #         return redirect(wishlist)
# #     else:
# #         messages.error(request,'Item already in your cart')
# #     return redirect(home)

# def add_to_wishlist(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     wishlist, created = Wishlist.objects.get_or_create(user=request.user)
#     wishlist_items = wishlist.wishlistitem_set.all()
#     print("added")
#     for item in wishlist_items:
#         if item.product == product:
#             messages.warning(request, 'This product is already in your wishlist')
#             return redirect('home')
#     wishlist_item = WishlistItem.objects.create(wishlist=wishlist, product=product)
#     messages.success(request, 'Product added to your wishlist')
#     return redirect('home')


# def remove_from_wishlist(request, item_id):
#     wishlist_item = WishlistItem.objects.get(id=item_id)
#     wishlist_item.delete()
#     return redirect('wishlist')
