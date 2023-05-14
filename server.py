#! /usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request
import json
import os

app = Flask(__name__)

@app.route('/push', methods=['GET', 'POST'])
def push():

    if request.method == 'POST':
    	files = request.files
    	local_root = request.form['local_root']
    	remote_root = request.form['remote_root']
    	modifications = json.loads(request.form['modifications'])

    	print('modifications:', modifications)

    	for file, modification in modifications.items():

    		path = file.replace(local_root, remote_root)

    		if modification in ('add_file', 'modify_file'):
    			os.makedirs(os.path.dirname(path), exist_ok=True)
    			files[file].save(path)
    		elif modification == 'remove_file':
    			os.remove(path)
    		elif modification in ('add_dir'):
    			os.makedirs(path, exist_ok=True)
    		elif modification in ('remove_dir'):
    			os.removedirs(path)

    	return 'the push is successful'
        #f = request.files['file']
        #root = request.form['root'] # 对应 client.py 传入的 root
        # path = os.path.join("/home/cdodev/tancheng/jars", f.filename)
        # f.save(path)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=6061)