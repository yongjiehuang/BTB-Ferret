include .env


all: wiki wiki-memc db

wiki:
	docker build \
	--target mediawiki-wiki \
	--tag davidschall/mediawiki:latest \
	-f ./Dockerfile \
	.

wiki-memc:
	docker build \
	--target wiki-memc \
	--tag davidschall/mediawiki-memc:latest \
	-f ./Dockerfile \
	.

wiki-fpm:
	docker build \
	--build-arg COMPOSER_HASH=$(COMPOSER_HASH) \
	--build-arg MW_VERSION=$(MW_VERSION) \
	--build-arg MW_PATCH_VERSION=$(MW_PATCH_VERSION) \
	--target mediawiki-fpm \
	--tag davidschall/mediawiki-fpm:latest \
	-f ./Dockerfile \
	.

wiki-nginx:
	docker build \
	--target mediawiki-nginx \
	--tag davidschall/mediawiki-nginx:latest \
	-f ./Dockerfile \
	.


db:
	docker build \
	--target mediawiki-db \
	--tag davidschall/mediawiki-db:latest \
	-f ./Dockerfile \
	.

		# --platform=linux/amd64,linux/arm64 \