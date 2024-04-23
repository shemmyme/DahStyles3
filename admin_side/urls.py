from django.urls import path,include
from .import views
urlpatterns = [
    
    # path('admins/',views.admin_panel,name='admin_panel'),
    path('dashboard/',views.admin_panel,name='dashboard'),
    path('prodects/',views.products,name='prodects'),
    path('sales/',views.sales,name='sales'),
    path('list_users/',views.list_users,name='list_users'),
    path('admins/',views.admin_login,name='admin_login'),
    path('',views.admin_logout,name='admin_logout'),
    path('<int:id>/blockuser/', views.blockuser, name='blockuser'),
    path('admin_profile/', views.adminprofile, name='adminprofile'),
    path('manage_order', views.manage_order, name='manage_order'),
    path('manage_order_con/', views.manage_order, name="manage_order_con"),
    path('orderdetails/<int:id>/',views.orderdetails, name="orderdetails"),
    path('searchorder/', views.searchorder, name="searchorder"),
    path('update_order/<int:id>/', views.update_order, name="update_order"),
    path('admincancelOrder/<int:id>/',views.admincancelOrder, name='admincancelOrder'),
    # path('searchUser/',views.searchUser,name="searchuser"),
    # path('addbrand/',views.addbrand,name='addbrand'),
    # path('addcolor/',views.addcolor,name='addcolor'),
    # path('adminproductedit/<int:product_id>',views.adminproductedit,name='adminproductedit'),
    # path('deleteproduct/<int:product_id>/',views.deleteprodect,name='deleteproduct'),
    # path('admincategory/',views.admincategory,name='admincategory'),
    # path('editcategory/<int:id>',views.editcategory,name='editcategory'),
    # path('deletecategory/<int:id>/',views.deletecategory,name='deletecategory'),
    path('variants/',views.variantsselection,name='variants'),
    path('product_variations/',views.product_variations,name='product_variations'),
    path('add_variations/',views.add_product_variation,name='add_product_variation'),
    path('products/product_variations/<int:id>/edit_variation', views.edit_product_variation, name='edit_product_variation'),
    path('products/product_variations/<int:id>/delete_variation', views.delete_product_variation, name='delete_product_variation'),
    path('admincategory/', views.admincategory, name='admincategory'),
    path('admincategory',views.cat_search,name='catsearch'),
    path('addCategory/', views.addCategory, name='addCategory'),
    path('<slug:category_slug>/editCategory/', views.editCategory, name='editCategory'),
    path('<str:slug>/deleteCategory/', views.deleteCategory, name='deleteCategory'),
    path('adminupdate/', views.adminupdate, name='adminupdate'),
    path('addaddress/', views.addaddress, name='addaddress'),
    path('adminmanage/', views.adminmanage, name='adminmanage'),
    path('deletead/<int:id>/',views.deletead,name='deleteaddress'),
    path('editad/<int:id>/', views.editad, name='editaddress'),
    
    

    # path('subCategories/', views.subCategories, name='subCategories'),
    # path('<str:category_slug>/addSubCategory/', views.addSubCategory, name='addSubCategory'),
    # path('<str:slug>/editSubCategory/', views.editSubCategory, name='editSubCategory'),
    # path('<str:slug>/deleteSubCategory/', views.deleteSubCategory, name='deleteSubCategory'),

    path('products/', views.products, name='products'),
    path('addProduct/', views.addProduct, name='addProduct'),
    path('<int:id>/editProduct/', views.editProduct, name='editProduct'),
    path('<int:id>/deleteProduct/', views.deleteProduct, name='deleteProduct'),
    # path('<str:category_slug>/subcategorychoose/',views.subcatogorychoose,name='subcategorychoose'),
    
    
    
    

    




]