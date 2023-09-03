from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client, get_tracker_conf
from django.conf import settings


# fastdfs文件存储类
class FDFSStorage(Storage):
    def __init__(self, client_conf=None, base_url=None):
        """初始化"""
        self.client_conf = client_conf or settings.FDFS_CLIENT_CONF
        self.base_url = base_url or settings.FDFS_URL

    def _open(self, name, mode='rb'):
        """打开文件时使用"""
        pass

    def _save(self, name, content):
        """保存文件时使用"""
        tracker_conf = get_tracker_conf(self.client_conf)  # client.conf的具体位置
        client = Fdfs_client(tracker_conf)  # 创建一个client对象

        res = client.upload_by_buffer(content.read())  # 上传文件到fast dfs系统中

        # dict
        # {
        #     'Group name': group_name,
        #     'Remote file_id': remote_file_id,
        #     'Status': 'Upload successed.',
        #     'Local file name': '',
        #     'Uploaded size': upload_size,
        #     'Storage IP': storage_ip
        # }
        if res.get('Status') != 'Upload successed.':
            # 上传失败
            raise Exception('上传文件到fast dfs失败')

        # 获取返回的文件ID
        filename = res.get('Remote file_id').decode()

        return filename

    def exists(self, name):
        """Django判断文件名是否可用"""
        return False

    def url(self, name):
        """返回访问文件的url路径"""
        return self.base_url + name
