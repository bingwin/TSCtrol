import oss2
from PyQt5.Qt import *
import os
import sys
from PyQt5.QtCore import pyqtSignal

class OSS(QObject):
    access_key_id = os.getenv('OSS_TEST_ACCESS_KEY_ID', 'LTAIQQ7KYIkJui5Q')
    access_key_secret = os.getenv('OSS_TEST_ACCESS_KEY_SECRET', 'Q8kcKGUNuoW2fpg7uxpgEFkMRd9Js2')
    endpoint = os.getenv('OSS_TEST_ENDPOINT', 'http://oss-cn-shenzhen.aliyuncs.com')
    path = os.path.abspath('.')
    dir_path = os.path.abspath('')
    dirs = os.listdir(path)
    bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name="code-55331")
    def showBucket(cls):
        print("**********   获取bucket信息  *******")
        service = oss2.Service(oss2.Auth(access_key_id, access_key_secret), endpoint)
        print("*****************************")
        print("     现有bucket有：      ")
        print('\n'.join(info.name for info in oss2.BucketIterator(service)))
        print("*****************************")


    def createBucket(cls):
        print("**********   创建  *******")
        bucket_input = input("请输入想创建的bucket名：   ")
        # 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
        bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name=bucket_input)

        # 带权限与存储类型创建bucket
        bucket.create_bucket(permission=oss2.BUCKET_ACL_PRIVATE,
                             input=oss2.models.BucketCreateConfig(oss2.BUCKET_STORAGE_CLASS_STANDARD))
        if oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name=bucket_input):
            print("     成功创建%s" %bucket_input)

        print("***************************")

    def bucketInfo(cls):
        print("**********   获取bucket_info  *******")
        bucket_input = input('请输入bucket名：   ')
        # 获取bucket相关信息
        bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name=bucket_input)
        bucket_info = bucket.get_bucket_info()
        print("     bucket_info:")
        print(' name: ' + bucket_info.name)
        print(' storage class: ' + bucket_info.storage_class)
        print(' creation date: ' + bucket_info.creation_date)
        print("*******************************")

        print("*******************************")
        print("     bucket_stat:")
        bucket_stat = bucket.get_bucket_stat()
        print(' storage: ' + str(bucket_stat.storage_size_in_bytes))
        print(' object count: ' + str(bucket_stat.object_count))
        print(' multi part upload count: ' + str(bucket_stat.multi_part_upload_count))
        print("********************************")








    def download(cls):
        print("**********   下载  *******")
        bucket_input = input('请输入bucket名：')
        bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name=bucket_input)
        print("     %s下有如下文件：" %bucket_input)
        for i in oss2.ObjectIterator(bucket):
            print(i.key)
        print("***************************")
        cloud_name = input('请输入要下载的文件名：')
        file_name = input('请输入保存至本地文件名：')
        bucket.get_object_to_file(cloud_name, file_name)
        print(file_name[4:])
        if file_name[4:] in os.listdir(dir_path):
            print("     成功下载%s" %cloud_name)
        print("**************************")
        print("     当前目录下所有文件：")
        for file in os.listdir(dir_path):
            print(file)
        print("***************************")



    def remove(cls):
        print("**********   删除  *******")
        bucket_input = input('请输入bucket名：'  )
        bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name=bucket_input)
        print("     %s下有如下文件(删除前)：" % bucket_input)
        for i in oss2.ObjectIterator(bucket):
            print(i.key)
        print("***************************")
        file_name = input('请输入要删除的文件名：'  )

        # 删除名为motto.txt的Object
        bucket.delete_object(file_name)
        print("     成功删除%s" %file_name)
        print("     %s下有如下文件(删除后)：" % bucket_input)
        for i in oss2.ObjectIterator(bucket):
            print(i.key)

    @classmethod
    def getdirectory(cls,folder):
            ret = {}
            i = 0
            for obj in oss2.ObjectIterator(OSS.bucket,prefix=folder, delimiter='/'):
                if i ==0:
                    ret.update({obj.key: "root"})
                else:
                    if obj.is_prefix():  # 文件夹
                        ret.update({obj.key:"directory"})
                    else:  # 文件
                        ret.update({obj.key:"file"})
                i+=1
            return ret

    # 上传下载进度



    def downloadFile(self,cloud_name,file_name,):
        print("**********   下载  *******")
        def percentage(consumed_bytes, total_bytes):
            if total_bytes:
                rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
                self.communicate_2.emit(rate)

        OSS.bucket.get_object_to_file(cloud_name, file_name,progress_callback=percentage)
        if file_name[4:] in os.listdir(OSS.dir_path):
            return True
        else:
            return False

    def uploadFile(self,cloud_name,filename):
        def percentage(consumed_bytes, total_bytes):
            if total_bytes:
                rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
                self.communicate_2.emit(rate)
                print('\r{0}% '.format(rate), end='')

        with open(oss2.to_unicode(filename), 'rb') as f:
            OSS.bucket.put_object(cloud_name, f,progress_callback=percentage)
        meta =  OSS.bucket.get_object_meta(cloud_name)
        if meta:
            return True
        else:
            return False
    def deleteFile(cls,filename):
        OSS.bucket.delete_object(filename)

#OSS.getdirectory("root/插件/")


