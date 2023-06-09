from django.shortcuts import render
from django.urls import path
from django.urls import resolve
from django import forms
from . import util, urls
import re
from django.http import HttpResponse
import random
import markdown2


def index(request):
	search = request.GET.get('search')
	if (search):
		return getit(request, search)
	else:
		return render(request, "encyclopedia/index.html", {"entries": util.list_entries()})
		
def article(request):
	search = request.GET.get('search')
	articleTitle = resolve(request.path_info).url_name
	if (search):
		return getit(request, search)
	else:
		return getit(request, articleTitle)
		
def getit(request, search):
	if util.get_entry(search) is not None:
		return render(request, "encyclopedia/article.html",{"content": markdown2.markdown(util.get_entry(search)),"title": search })
		
	listOfEntries = util.list_entries()
	listOfFinds = []
	count = 0
	
	while count < len(listOfEntries): # for-loop wouldn't work, type error (assumes count to be str)
		x = re.search(search.lower(), listOfEntries[count].lower())
		if (x is not None):
			listOfFinds.append(listOfEntries[count])
		count += 1
		
	if len(listOfFinds) > 0:
		return render(request, "encyclopedia/searchResult.html", {"finds": listOfFinds,"title":"Search Results"})
	else:
		return render(request, "encyclopedia/notFound.html",{"content": "No article could be found for your search.","title": "No results found!"})

def notFound(request, path):
	return render(request, "encyclopedia/notFound.html",{"content": "There's no article for the URL you've tried.","title": "Article not found."})
	
def createEntry(request):
	if request.method == "POST":
		form = NewArticle(request.POST)
		if form.is_valid():
			article = form.cleaned_data["article"]
			title = form.cleaned_data["title"]
			
			#check for existing article with same title
			listOfEntries = util.list_entries()
			count = 0
			while count < len(listOfEntries):
				if (title.lower() == listOfEntries[count].lower()):
					return render(request, "encyclopedia/notFound.html",{"content": f"An article with the title {title} already exists.","title": "Entry already exists!" })
				count += 1
			
			util.save_entry(title, article)
			urls.insertArticleAtBeginning(title)
			return getit(request, title)
		
		else:
			return render(request, "encyclopedia/createEntry.html", {
                "form": form})
	
	return render(request, "encyclopedia/createEntry.html", {
        "form": NewArticle()})

def editEntry(request, id):
	title = id
	article = util.get_entry(title)
	
	if request.method == "POST":
		form = NewArticle(request.POST)
		if form.is_valid():
			article = form.cleaned_data["article"]
			title = form.cleaned_data["title"]
			util.save_entry(title, article)
		return getit(request, id)
	return render(request, "encyclopedia/editEntry.html", {
        "form": NewArticle(initial={'title':title,'article':article})})
	
class NewArticle(forms.Form):
	title = forms.CharField()
	article = forms.CharField(widget = forms.Textarea)

def randomArticle(request):
	listOfEntries = util.list_entries()
	article = listOfEntries[(random.randint(0, len(listOfEntries)-1))]
	return getit(request, article)