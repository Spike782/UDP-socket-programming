#运行环境：Windows11,Python3
import socket
import sys #用于在终端上处理命令行
import os #用于处理文件


# 命令行输入 ip 地址和端口号
# 如果错误输入命令行参数，示范正确输入
if len(sys.argv) < 3:
    print("Usage: python client.py <server_ip> <server_port>")
    sys.exit(1)

# 输入两个命令行参数：目标服务器地址和端口号
server_ip = sys.argv[1]
server_port = int(sys.argv[2])

# 创建 UDP socket 连接
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_file(file_path):
    try:
        #发送文件标志，此处设为"1"
        client_socket.sendto(b'\x01', (server_ip, server_port))
        # 获取文件名
        file_name = os.path.basename(file_path)
        # 获取文件名长度
        file_name_length = len(file_name.encode())
        #获取文件大小
        file_size = os.path.getsize(file_path)

        #发送文件名长度
        client_socket.sendto(file_name_length.to_bytes(4, byteorder='big'), (server_ip, server_port))
        # 将文件名发送给目标服务器
        client_socket.sendto(file_name.encode(), (server_ip, server_port))
        # 发送文件大小长度
        file_size_length = len(str(file_size).encode())

        client_socket.sendto(file_size_length.to_bytes(4, byteorder='big'), (server_ip, server_port))
        # 将文件大小发送给目标服务器
        client_socket.sendto(str(file_size).encode(), (server_ip, server_port))
        # 将文件内容发送给目标服务器
        with open(file_path, 'rb') as file:
            data = file.read(1024)
            while data:
                client_socket.sendto(data, (server_ip, server_port))
                data = file.read(1024)

        print(f"send file: {file_name}")
    except Exception as error:
        print(f"fail to send: {error}")


def send_dir(dir_path):
    try:
        dir_name = os.path.basename(dir_path)
        # 发送目录标志,此处设为"2"
        client_socket.sendto(b'\x02', (server_ip, server_port))
        # 发送目录名
        client_socket.sendto(dir_name.encode(), (server_ip, server_port))
        # 递归发送目录下的文件
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                send_file(file_path)

        print("send directory successfully")
    except Exception as error:
        print(f"fail to send: {error}")

#用户输入要发送的是文件还是目录，并输入文件或目录的路径
judge = input("please enter the type of content to send（file/dir)")
if judge == "file":
    file_path = input("please enter the file path to send: ")
    send_file(file_path)
elif judge == "dir":
    dir_path = input("please enter the directory path to send: ")
    send_dir(dir_path)
else:
    print("invalid input！")

# 关闭客户端套接字接口
client_socket.close()