


from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Document, ShareDocument

class DocumentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Document
        fields = ('title', 'description', 'format', 'upload_date','owner','file')

    def validate_file(self, file):
        file_format = ('.txt','.pdf','.docx')
        allowed_size = 5 * 1024 * 1024 

        if not file.name.lower().endswith(file_format):
            raise serializers.ValidationError("Invalid file format. Allowed formats: txt, pdf, docx.")
        if file.size > allowed_size:
            raise serializers.ValidationError("File size exceeds the allowed limit (5 MB).")

        return file


class DocumentListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    file = serializers.SerializerMethodField()
    owner=serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ('id', 'title', 'description', 'owner','file')

    def get_file(self, document):
        return document.file.name.split('/')[-1]
    
    def get_owner(self,document):
        user=User.objects.get(id=document.owner.id)
        return user.email

    
class ShareDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShareDocument
        fields = ('document', 'owner', 'sharedwith')