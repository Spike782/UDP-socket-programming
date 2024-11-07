#运行环境：Ubuntu 22.04.5 LTS, Python3
import os #用于处理文件
import socket

#设置服务器ip和端口
serverPort = 12000
serverIP='192.168.1.5'

# 创建 UDP socket 连接
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind((serverIP, serverPort))
print("The server is ready to receive")

def receive_file():
    try:
        #接收文件标志
        dir_flag, clientAddress = serverSocket.recvfrom(3)
        if dir_flag != b'\x01':
            raise ValueError("Invalid file!")

        # 接收文件名长度，并转换为字符串
        file_name_length_data, clientAddress = serverSocket.recvfrom(4)
        file_name_length = int.from_bytes(file_name_length_data, 'big')

        # 接收文件名
        file_name_data, clientAddress = serverSocket.recvfrom(file_name_length)
        file_name = file_name_data.decode()

        # 接收文件大小长度
        file_size_length_data, clientAddress = serverSocket.recvfrom(4)
        file_size_length = int.from_bytes(file_size_length_data, 'big')

        # 接收文件大小
        file_size_data, clientAddress = serverSocket.recvfrom(file_size_length)
        file_size = int(file_size_data.decode())

        #初始化一个空的字节变量，用于储存接收到的文件内容
        received_data = b''
        #将变量remain_size初始化为接收到的文件大小file_size，这个变量用于跟踪还有多少字节的数据需要接收。
        remain_size = file_size
        #当还有数据未接收时：
        while remain_size > 0:
            #从套接字持续接收数据，这里使用min(remain_size, 1024)来确定每次接收的最大数据量，确保不会接收超过剩余需要接收的数据量和 1024 字节中的较小值。
            data, clientAddress = serverSocket.recvfrom(min(remain_size, 1024))
            #将新接收到的数据追加到已接收数据当中
            received_data += data
            #更新剩余需要接收的数据量
            remain_size = remain_size - len(data)

        #将接收到的文件储存，这里储存在linux的用户主目录下的received_files文件夹
        #获取当前用户的主目录路径
        home_dir = os.path.expanduser("~")
        #创建一个路径指向主目录下的received_files文件夹，如果该文件夹不存在就创建一个
        received_files_dir = os.path.join(home_dir, "received_files")
        if not os.path.exists(received_files_dir):
            os.makedirs(received_files_dir)
        #把文件标题和received_files文件夹组成一个完整的文件保存路径
        file_path = os.path.join(received_files_dir, file_name)

        #以二进制写入模式打开文件，将接收到的完整文件内容写入
        with open(file_path, 'wb') as file:
            file.write(received_data)

        print(f"Received file:{file_name}")
    except Exception as err:
        print(f"Error receiving file:{err}")
def receive_dir():
    try:
        #接收目录标志
        dir_flag,clientAddress=serverSocket.recvfrom(3)
        if dir_flag!=b'\x02':
            raise ValueError("Invalid directory!")

        #接收目录名
        dir_name_data,clientAddress=serverSocket.recvfrom(1024)
        dir_name=dir_name_data.decode()

        #如果目录不存在则创建
        #由于Linux和Windows文件路径不同，无法创建，暂未解决该问题
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        #获取当前的工作目录
        current_dir=os.getcwd()
        #切换到接收到的目录名对应的目录
        os.chdir(dir_name)

        # 无限循环，直到遇到 socket.timeout 异常跳出
        while True:
            try:
                # 递归接收文件，调用 receive_file 函数
                receive_file()
            except socket.timeout:
                break
        # 切换回原来的工作目录
        os.chdir(current_dir)
        print("Directory received successfully")
    except Exception as err:
        print(f"Error receiving directory:{err}")
while True:
    try:
        # 设置服务器套接字超时时间为 20 秒
        serverSocket.settimeout(20)
        # 接收文件类型数据和客户端地址
        file_type_data, client_address = serverSocket.recvfrom(1)
        # 将接收到的字节数据转换为整数类型
        file_type = int.from_bytes(file_type_data, 'big')
        # 如果文件类型为 1，则调用 receive_file 函数接收文件
        if file_type == 1:
            receive_file()
        # 如果文件类型为 2，则调用 receive_dir 函数接收目录
        elif file_type == 2:
            receive_dir()
        else:
            # 如果文件类型是其他，则打印无效文件类型标志信息
            print("Invalide file type flag")
    except socket.timeout:
        # 如果发生超时异常，则继续循环等待接收数据
        continue
    except Exception as err:
        # 如果发生其他异常，则打印错误信息
        print(f"Error!{err}")

# 关闭客户端套接字接口
serverSocket.close()