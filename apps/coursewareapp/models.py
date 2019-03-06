from django.db import models

# Create your models here.
from Elearn import settings
from userapp.models import *

file_dir = os.path.join(settings.BASE_DIR, 'static/')


class FileCheck():

    def __init__(self):
        self.file_dir = file_dir

    def get_filesize(self, filename):
        u"""
        获取文件大小（M: 兆）
        """
        file_byte = os.path.getsize(filename)
        filesize = FileCheck.sizeConvert(self, file_byte)
        return filesize

    def sizeConvert(self, size):  # 单位换算
        K, M, G = 1024, 1024 ** 2, 1024 ** 3
        if size >= G:
            return str('%.2f' % (size / G)) + 'G'
        elif size >= M:
            return str('%.2f' % (size / M)) + 'M'
        elif size >= K:
            return str('%.2f' % (size / K)) + 'K'
        else:
            return str('%.2f' % size) + 'B'


class Courseware(models.Model):
    courseawre_name = models.CharField(max_length=100, verbose_name='课件名称')
    courseware_upload = models.FileField(upload_to='resources/courseware/%Y%m%d', max_length=200, verbose_name='课件路径')
    courseawre_size = models.CharField(max_length=20, verbose_name='课件大小', editable=False)
    courseware_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', editable=False)
    courseware_download_nums = models.CharField(max_length=10, editable=False, default=0, verbose_name='下载量')
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, verbose_name='老师')

    class Meta:
        db_table = 'courseware'
        verbose_name = '课件'
        verbose_name_plural = verbose_name
        ordering = ['courseware_time']

    def __str__(self):
        return self.courseawre_name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if len(self.courseware_upload.name) < 32:
            uuid_str = str(uuid.uuid4()).replace('-', '')
            self.courseware_upload.name = uuid_str + os.path.splitext(self.courseware_upload.name)[-1]
        super().save()

        # 对上传的视频计算时长
        self.courseawre_size = FileCheck.get_filesize(self, os.path.join(file_dir, str(self.courseware_upload.name)))
        super().save()

    def delete(self, using=None, keep_parents=False):
        Courseware.objects.filter(id=self.id).delete()
        os.remove(os.path.join(file_dir, str(self.courseware_upload.name)))