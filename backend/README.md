# Custom UI Demo - Backend

poetry env use "3.8.6"
poetry install

## DTF

```sh
poetry run python api.py \
    dtf \
    list \
    test_setups
```

```sh
poetry run python api.py \
    dtf \
    scrape \
    test_setups/dvt/milan/testbed1.json \
    > outputs/dtf/dvt__milan__testbed1.json
```

## TG

```sh
poetry run python api.py \
    tg_test_runner \
    list \
    test_actions
```

```sh
poetry run python api.py \
    tg_test_runner \
    scrape \
    tests/test_e2e/test_data/test_scenario_1.json \
    > outputs/tg_test_runner/test_e2e__test_data__test_scenario_1.json
```

```sh
poetry run python api.py \
    tg_test_runner \
    scrape \
    tests/test_e2e/test_data/test_scenario_2.json \
    > outputs/tg_test_runner/test_e2e__test_data__test_scenario_2.json
```
