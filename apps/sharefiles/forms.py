from django import forms

class ChunkFileForm(forms.Form):
    chunk = forms.FileField(label='chunk')
    index = forms.IntegerField(label='index')
    total = forms.IntegerField(label='total_chunk')
    md5 = forms.CharField(label='md5 value for the whole file',max_length=32)
    file_name = forms.CharField(label='file name',max_length=50)

    