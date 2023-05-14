# gittie

## The server
Receive files uploaded by the client

## The client
Scan changed files and upload them to the server

## How to use?

1. Write your host, port, and url path in config.json:

```json
{
	"url": "http://127.0.0.1:6061",
	"path": "/push",
	"ignores": [
		".DS_Store", 
		"env/",
		"/path/to/project/some_path"
	]
}
```

The `ignores` in `config.json` only supports 3 kinds of elements currently.
1) relative file path
2) relative directory path with a trailing slash
3) absolute file or directory

The special `.git` and `.gittie` are ignored by default.

2. Put the code on your server and your local machine.

3. Run client:

```shell
# run status to check what have changed
python client.py ./test /tmp/remote status

# run push to push your code to the server 
python client.py ./test /tmp/remote push

# if something goes wrong, you can do a full overwrite
python client.py ./test /tmp/remote reset
python client.py ./test /tmp/remote push
```