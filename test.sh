#!/bin/bash

type=$1
fails=""

inspect() {
  if [ $1 -ne 0 ]; then
    fails="${fails} $2"
  fi
}

nowDoing() {
  if [ "$1" = "start" ]; then
    echo "*******************************************************************"
    echo "Build and run docker-compose!"
    echo "*******************************************************************"
  else
    echo "*******************************************************************"
    echo "Run $1 $2"
    echo "*******************************************************************"
  fi
}

# run server-side tests
server() {
  nowDoing start
  docker-compose -f docker-compose-dev.yml up -d --build

  nowDoing users test
  docker-compose -f docker-compose-dev.yml exec users python manage.py test
  inspect $? users
  nowDoing users lint
  docker-compose -f docker-compose-dev.yml exec users flake8 project
  inspect $? users-project-lint
  docker-compose -f docker-compose-dev.yml exec users flake8 tests
  inspect $? users-tests-lint

  nowDoing lexical test
  docker-compose -f docker-compose-dev.yml exec lexical python manage.py test
  inspect $? lexical
  nowDoing lexical lint
  docker-compose -f docker-compose-dev.yml exec lexical flake8 project
  inspect $? lexical-lint

  nowDoing repository test
  docker-compose -f docker-compose-dev.yml exec repository python manage.py test
  inspect $? repository
  nowDoing repository lint
  docker-compose -f docker-compose-dev.yml exec repository flake8 project
  inspect $? repository-lint

  docker-compose -f docker-compose-dev.yml down
}

# run client-side tests
client() {
  nowDoing start
  docker-compose -f docker-compose-dev.yml up -d --build

  nowDoing client test
  docker-compose -f docker-compose-dev.yml exec client npm test -- --coverage
  inspect $? client

  docker-compose -f docker-compose-dev.yml down
}

# run e2e tests
e2e() {
  nowDoing start
  docker-compose -f docker-compose-dev.yml up -d --build

  nowDoing database seeding
  docker-compose -f docker-compose-dev.yml exec users python manage.py recreate-db
  docker-compose -f docker-compose-dev.yml exec users python manage.py seed-db
  docker-compose -f docker-compose-dev.yml exec repository python manage.py create-user
  docker-compose -f docker-compose-dev.yml exec repository python manage.py seed-db

  nowDoing cypress test
  ./node_modules/.bin/cypress run --config baseUrl=http://localhost
  inspect $? e2e

  docker-compose -f docker-compose-dev.yml down
}

# run all tests
all() {
  nowDoing start
  docker-compose -f docker-compose-dev.yml up -d --build

  nowDoing users test
  docker-compose -f docker-compose-dev.yml exec users python manage.py test
  inspect $? users
  nowDoing users lint
  docker-compose -f docker-compose-dev.yml exec users flake8 project
  inspect $? users-project-lint
  docker-compose -f docker-compose-dev.yml exec users flake8 tests
  inspect $? users-tests-lint

  nowDoing lexical test
  docker-compose -f docker-compose-dev.yml exec lexical python manage.py test
  inspect $? lexical
  nowDoing lexical lint
  docker-compose -f docker-compose-dev.yml exec lexical flake8 project
  inspect $? lexical-lint

  nowDoing repository test
  docker-compose -f docker-compose-dev.yml exec repository python manage.py test
  inspect $? repository
  nowDoing repository lint
  docker-compose -f docker-compose-dev.yml exec repository flake8 project
  inspect $? repository-lint

  nowDoing client test
  docker-compose -f docker-compose-dev.yml exec client npm test -- --coverage
  inspect $? client
  docker-compose -f docker-compose-dev.yml down

  nowDoing e2e test
  e2e
}

# run appropriate tests
if [[ "${type}" == "server" ]]; then
  echo "*******************************************************************"
  echo "Running server-side tests!"
  server
elif [[ "${type}" == "client" ]]; then
  echo "*******************************************************************"
  echo "Running client-side tests!"
  client
elif [[ "${type}" == "e2e" ]]; then
  echo "*******************************************************************"
  echo "Running e2e tests!"
  e2e
else
  echo "*******************************************************************"
  echo "Running all tests!"
  all
fi

# return proper code
if [ -n "${fails}" ]; then
  echo "*******************************************************************"
  echo "Tests failed: ${fails}"
  echo "*******************************************************************"
  exit 1
else
  echo "*******************************************************************"
  echo "Tests passed!"
  echo "*******************************************************************"
  exit 0
fi

echo ""
