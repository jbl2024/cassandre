docker:
		docker-compose up

runserver_dev:
		export DJANGO_SETTINGS_MODULE=cassandre.dev_settings; \
		python manage.py runserver

migrate_dev:
		export DJANGO_SETTINGS_MODULE=cassandre.dev_settings; \
		python manage.py migrate

install_dev:
		pip install -r requirements/dev.txt

install_prod:
		pip install -r requirements/prod.txt

manage_dev:
		export DJANGO_SETTINGS_MODULE=cassandre.dev_settings; \
		python manage.py $(filter-out $@,$(MAKECMDGOALS))
%:
		@true	

create_db_dev:
	docker-compose exec -T db createdb -U postgres -O postgres cassandre_dev
