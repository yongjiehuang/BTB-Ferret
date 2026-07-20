

all: nodeapp

nodeapp-todo:
	docker build \
	--target nodeapp-todo \
	--tag davidschall/nodeapp-todo:latest \
	-f ./Dockerfile \
	.


nodeapp-cart:
	docker build \
	--target nodeapp-cart \
	--tag davidschall/nodeapp-cart:latest \
	-f ./Dockerfile \
	.

nodeapp-nginx:
	docker build \
	--target nodeapp-nginx \
	--tag davidschall/nodeapp-nginx:latest \
	-f ./Dockerfile \
	.
