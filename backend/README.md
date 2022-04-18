# Backend

poetry env use "3.8.6"
poetry install

poetry run python scraper.py dtf list test_setups
poetry run python scraper.py dtf scrape 'test_setups/test_setup_1/test_setup_data'
