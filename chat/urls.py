from django.urls import path
from . import views

urlpatterns = [
    path('callback/', views.callback, name='callback'),
    path('test_predict/', views.TestPredictView.as_view(), name='test_predict'),
    path('test_result/', views.TestResultView.as_view(), name='test_result'),
]