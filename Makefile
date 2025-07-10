elastic-search:
	@docker pull docker.elastic.co/elasticsearch/elasticsearch:8.7.0
	@-docker network create elastic
	@-docker run -d --name es-eastern-religion-chatbot --net elastic -p 9200:9200 -it --memory=4g --cpus=1 docker.elastic.co/elasticsearch/elasticsearch:8.7.0
