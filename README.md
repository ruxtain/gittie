# gittie

## server
receive files uploaded by the client

## client
scan changed files and upload them to the server

## how to use?

1. write your host, port, and url path in config.json:

```json
{
	"url": "http://127.0.0.1:6061",
	"path": "/push"
}
```

2. put the code on your server and your local machine.

3. run client:

```shell
# run status to check what have changed
python client.py ./test /tmp/remote status

# run push to push your code to the server 
python client.py ./test /tmp/remote push

# if something goes wrong, you can do a full overwrite
python client.py ./test /tmp/remote reset
python client.py ./test /tmp/remote push
```
