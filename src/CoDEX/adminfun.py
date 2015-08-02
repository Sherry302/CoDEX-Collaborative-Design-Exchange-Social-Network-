

def addTag(request):
	tag = Tag(name=request.POST("tag_name"), num_posts=0)
	tag.save()
	tags = Tag.objects.all()
	context = {"tags": tags}
	return render(request, "", context)	

