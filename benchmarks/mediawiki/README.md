# MediaWiki Benchmark

This benchmark implements a small MediaWiki wiki containing a few pages downloaded from Wikipedia.
The benchmark uses PHP-FPM (FastCGI Process Manager) to process PHP requests, Nginx as web server and MySQL as database.
Everything is fully containerized using docker.

## Starting the website

Use `docker-compose` to start the benchmark.
```bash
docker compose -f docker-compose.yaml up
```
The website will be served on at port 9999. Thus, to access the content open `localhost:9999` in your browser.

## Invoking the website

There are two options to stress the website. Either using [siege](https://linux.die.net/man/1/siege) or the [http-client](./../../client/) provided with this repo.

#### Using siege

After installing siege you can use the `siege_bm.urls` file invoke different webpages of the Wiki.
Refer to the siege documentation for additional configurations like concurrency.

```bash
siege -f siege_bm.urls
```

#### Using http-client

Build the client and invoke it using the provided `urls.tmpl` file.
Refer to the [README](./../../client/README.md) for additional information to use the client.

```bash
./http-client -url localhost -port 9999 -f urls.tmpl
```



## Useful resources

In the following some links that where useful in building this benchmark.

Some general info about mediawiki in docker
https://kindalame.com/2020/11/25/self-hosting-mediawiki-with-docker/


Download all images from a wikipedia webpage.
https://how-to.fandom.com/wiki/How_to_download_all_image_files_in_a_Wikimedia_Commons_page_or_directory


```bash
# Get all content links and stores them in `commons.wikimedia.org` folder
wget -r -l 1 -e robots=off -w 1 http://commons.wikimedia.org/wiki/<SITE>

# Extract image links
WIKI_LINKS=`grep fullImageLink commons.wikimedia.org/wiki/File\:* | sed 's/^.*><a href="//'| sed 's/".*$//'`

## Download each file into downloaded_wiki_images
wget -nc -w 1 -e robots=off -P downloaded_wiki_images $WIKI_LINKS

```


After adding extentions or other stuff reload the database
https://www.mediawiki.org/wiki/Manual:Upgrading


```bash
# Login to container
sudo docker exec -it wiki bash
# Go into maintainance folder
cd /var/www/html/maintenance

php update.php
```


### Create a database dump

Once done with your website you can build a database dump that can be uses in the docker file to populate the database with content. 

```bash
# Create the dump
sudo docker exec -t database mysqldump -u wikiuser -ppassword wiki | gzip > wiki.sql.gz

```