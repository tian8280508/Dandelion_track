import paramiko
import os


def sftp_upload_file(local_path, server_path='/root/neo4j/', host='101.34.159.189', user='root',
                     password='Albert738822655!', ):
    _, file = os.path.split(local_path)
    t = paramiko.Transport((host, 22))
    t.connect(username=user, password=password)
    sftp = paramiko.SFTPClient.from_transport(t)
    sftp.put(local_path, server_path + file)
    t.close()


# 递归这种东西，写在return 里的是要传上来的，写在参数里的是要传下去的

def get_path_file_names(path, if_file_type=False):
    '''
    获取当前路径下面的文件名
    :param path:
    :param if_file_type: 是否包含文件类型
    :return:文件名列表
    '''
    if if_file_type:
        for _, _, files in os.walk(path):
            return files
    if not if_file_type:
        file_list = []
        for _, _, files in os.walk(path):
            for file in files:
                file_list.append(file.split('.')[0])

            return file_list
