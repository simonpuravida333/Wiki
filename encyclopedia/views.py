from django.shortcuts import render, redirect
from django.urls import path
from django.urls import resolve
from django import forms
from . import util, urls
import re
from django.http import HttpResponse
import random
import markdown


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
		return render(request, "encyclopedia/article.html",{"content": markdown.markdown(util.get_entry(search)),"title": search })
		
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
	#print(article)
	#print(article.encode())
	if request.method == "POST":
		form = NewArticle(request.POST)
		if form.is_valid():
			article = form.cleaned_data["article"]
			title = form.cleaned_data["title"]
			util.save_entry(title, article.encode()) #if it wasn't for .encode() linebreaks would double every time in the textarea window (innerText, not innerHTML), both the \r and \n would double at every save. See it by uncommenting the two prints upper in this function and removing encode() from the parameter of util.save_entry
			# https://stackoverflow.com/questions/69216585/newline-character-n-duplicates-when-writing-a-file-with-python#:~:text=I%20had%20the%20same%20problem%2C%20saving%20markdown%20files,now%20it%20can%20be%20saved%20into%20a%20file
		return getit(request, id)
	return render(request, "encyclopedia/createEntry.html", {
        "form": NewArticle(initial={'title':title,'article':article})})
	
class NewArticle(forms.Form):
	title = forms.CharField(label = '')
	article = forms.CharField(widget = forms.Textarea, label ='')

def randomArticle(request):
	listOfEntries = util.list_entries()
	article = listOfEntries[(random.randint(0, len(listOfEntries)-1))]
	return redirect(f"wiki:{article}")