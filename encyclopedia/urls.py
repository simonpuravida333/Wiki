from django.urls import path, re_path
from . import views, util
import re

app_name = "wiki"
urlpatterns = [
	path("", views.goIndex, name="goIndex"), # user types no address
    path("wiki/", views.index, name="index"),
    path("wiki/createEntry/", views.createEntry, name="createEntry"),
    path("wiki/editEntry/<id>/", views.editEntry, name="editEntry"),
    path("wiki/randomArticle/", views.randomArticle, name="randomArticle"),
]

newurl = ""
for article in util.list_entries():
	newurl = app_name+"/"+article
	urlpatterns.append(path(newurl, views.article, name=article))

urlpatterns.append(re_path(r'^(?P<path>.*)/$', views.notFound))

# articles must be inserted at the beginning as the not-found page in the line just upper must come last as a fall-through option to catch urls that don't exist.
def insertArticleAtBeginning(articleName): 
		urlpatterns.insert(0, path("wiki/"+articleName, views.article, name=articleName))