build:
	docker-compose up -d --build

start:
	docker-compose up -d

stop:
	docker-compose down

cleanup:
	docker-compose down -v --rmi all --remove-orphans
	docker volume prune
	docker images -q --filter "dangling=true" | xargs docker rmi