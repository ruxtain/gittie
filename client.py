# 检测文件修改情况，只找出修改过的文件
# 只需要一个参数：文件目录
# 只有一个操作：识别修改的文件，如果是第一次调用，则记录当前的文件情况

import os
import sys
import json
import urllib
import requests
from pprint import pprint


class Config:

	def __init__(self, config: dict):
		for i in config:
			self.__setattr__(i, config[i])


class File(str):
	# 继承str，只是增加了一个type，用来表示是 file 还是 dir
	# 对于文件有新增、修改、删除，改名等于是删除后心中
	# 但是对于目录，只有新增和删除，改名字等于是删除后新增
	def __new__(cls, value, type):
		obj = super().__new__(cls, value)
		obj.type = type
		return obj


class Client:

	"""
	client.py add /path
		更新目录下所有文件的修改时间
	client.py status /path
		返回发生修改的文件和操作 {file: action} 格式
		action 枚举值: add, modify, remove
	"""

	def __init__(self, root):
		if os.path.isdir(root):
			self.root = os.path.abspath(root)
			self.gittie = os.path.abspath(os.path.join(root, '.gittie'))
			self.modifications = {}
			with open('config.json') as f:
				self.config = Config(json.loads(f.read()))
		else:
			raise FileNotFoundError(f'{root} is not a directory')

	def is_ignore(self, file):
		for ignore in self.config.ignores:
			if file.type == 'dir':
				if ignore in file or '.git/' in file:
					return True
			elif file.type == 'file':
				if ('/' + file).endswith(ignore) or '.gitte' in file:
					return True
		return False

	@property
	def files(self):
		for i, ds, fs in os.walk(self.root, topdown=True):
			for d in ds:
				dire = os.path.abspath(os.path.join(i, d)) 
				dire = File(dire + '/', 'dir') # 为了明显区分目录和文件，目录的结尾加斜杠
				if self.is_ignore(dire):
					ds.remove(d) # 必须直接删除要跳过的目录，否则在更深一层的递归中还是会访问里面的子目录
					break        # 里面的文件也无需访问了
				else:
					for f in fs:
						file = os.path.abspath(os.path.join(i, f))
						file = File(file, 'file')
						if not self.is_ignore(file):
							yield file				
				yield dire



	def reset(self):
		# 删除掉.gittie文件，从而使得所有文件视为心中，于是会同步所有文件
		# 注意reset只处理本地文件，远程文件还是需要手动删除（安全起见）
		if os.path.exists(self.gittie):
			os.remove(self.gittie)

	def status(self):
		# 根据更新时间的变化，找出有修改的文件
		last_info = {} # 之前的文件信息
		info = {}      # 当前的文件信息
		modifications = {}
		if not os.path.exists(self.gittie):
			os.system(f'touch {self.gittie}')

		with open(self.gittie) as f:
			for line in f.readlines():
				last_file, last_type, last_mtime = line.strip().split('\t')
				last_info[File(last_file, last_type)] = last_mtime

		for file in self.files:
			mtime = os.path.getmtime(file)
			info[file] = str(mtime)

		for file in set(info) - set(last_info):
			modifications[file] = 'add_' + file.type
		for file in set(last_info) - set(info):
			modifications[file] = 'remove_' + file.type
		for file in set(last_info) & set(info):
			if file.type == 'file' and last_info[file] != info[file]:
				modifications[file] = 'modify_' + file.type
		self.modifications = modifications
		return modifications

	def update(self):
		# 更新文件的更新时间
		with open(self.gittie, 'w') as f:
			for file in self.files:
				mtime = os.path.getmtime(file)
				print(f'{file}\t{file.type}\t{mtime}', file=f)

	def push(self, remote_root):
		# 推送给server端，考虑到文件都是脚本比较小，就一次性推送了
		modifications = self.status()
		config = self.config

		files = {}
		for file in modifications:
			if modifications[file] in ('modify_file', 'add_file'):
				files[file] = open(file, 'rb')

		data = {
			'local_root': self.root,
			'remote_root': remote_root,
			'modifications': json.dumps(modifications)
		}

		url = urllib.parse.urljoin(config.url, config.path)
		requests.post(url, data=data, files=files)

		self.update() # push之后容易忘记，所以必须自动update


def main():
	args = sys.argv[1:]
	if len(args) == 0:
		print('usage: python client.py local_root remote_root [reset|status|push|update]')
	elif len(args) == 3:
		local_root, remote_root, cmd = sys.argv[1:]
		client = Client(local_root)
		if cmd == 'reset':
			client.reset()
		elif cmd == 'status':
			pprint(client.status())
		elif cmd == 'push':
			client.push(remote_root)
		elif cmd == 'update':   # push后自动执行，几乎不需要手动执行
			client.update()
	
if __name__ == '__main__':
	main()