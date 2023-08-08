from django.db import models

# Create your models here.


from django.contrib.auth.models import User

class Document(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    format = models.CharField(max_length=10)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    #file=models.FileField(upload_to="documents/user_{instance.owner.id}/{instance.format}")
    file=models.FileField(upload_to="documents/")

    def __str__(self):
        return self.title
    

class ShareDocument(models.Model):
    document=models.ForeignKey(Document,on_delete=models.CASCADE)
    # owner=models.ForeignKey(User,on_delete=models.CASCADE,related_name='owned')
    sharedwith=models.ForeignKey(User,on_delete=models.CASCADE,related_name='shared_with')



