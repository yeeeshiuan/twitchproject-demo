#!/bin/sh

if [ -z "$TRAVIS_PULL_REQUEST" ] || [ "$TRAVIS_PULL_REQUEST" == "false" ]
then

  if [[ "$TRAVIS_BRANCH" == "staging" ]]; then
    export DOCKER_ENV=stage
    export NODE_ENV=production
    export REACT_APP_DOMAIN_NAME_URL="http://twitchproject-staging-alb-640128092.us-east-1.elb.amazonaws.com"
    export REACT_APP_CSRF_TOKEN="c3ab8aa609ea11e793ae92361f002672"
    export REACT_APP_TWITCH_OAUTH_LINK="https://id.twitch.tv/oauth2/authorize"
    export REACT_APP_TWITCH_TOP_STREAM_API_URL="https://api.twitch.tv/kraken/streams/?language=zh-tw&limit=1"
    export REACT_APP_TWITCH_CALLBACK_URL="http://twitchproject-staging-alb-640128092.us-east-1.elb.amazonaws.com/authByTwitch/"
    export REACT_APP_TWITCH_CLIENT_ID="k5vlxcnpyhddnyo3l2kjfcpovg46yr"
    export REACT_APP_TWITCH_USER_NAME="yeeeshiuandev"
    export REACT_APP_TWITCH_OAUTH_TOKEN="oauth:htapnx7reqlfmb1c4lrzk3l58ue73y"

  elif [[ "$TRAVIS_BRANCH" == "production" ]]; then
    export DOCKER_ENV=prod
    export NODE_ENV=production
    export REACT_APP_DOMAIN_NAME_URL=""
    export REACT_APP_CSRF_TOKEN=""
    export REACT_APP_TWITCH_OAUTH_LINK=""
    export REACT_APP_TWITCH_TOP_STREAM_API_URL=""
    export REACT_APP_TWITCH_CALLBACK_URL=""
    export REACT_APP_TWITCH_CLIENT_ID=""
    export REACT_APP_TWITCH_USER_NAME=""
    export REACT_APP_TWITCH_OAUTH_TOKEN=""

    export DATABASE_URL="$AWS_RDS_URI"
    export SECRET_KEY="$PRODUCTION_SECRET_KEY"
  fi

  if [ "$TRAVIS_BRANCH" == "staging" ] || \
     [ "$TRAVIS_BRANCH" == "production" ]
  then
    curl "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip" -o "awscli-bundle.zip"
    unzip awscli-bundle.zip
    ./awscli-bundle/install -b ~/bin/aws
    export PATH=~/bin:$PATH
    # add AWS_ACCOUNT_ID, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY env vars
    eval $(aws ecr get-login --region us-east-1 --no-include-email)
    export TAG=$TRAVIS_BRANCH
    export REPO=$AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
  fi

  if [ "$TRAVIS_BRANCH" == "staging" ] || \
      [ "$TRAVIS_BRANCH" == "production" ]
  then
    # users
    docker build $USERS_REPO -t $USERS:$COMMIT -f Dockerfile-$DOCKER_ENV
    docker tag $USERS:$COMMIT $REPO/$USERS:$TAG
    docker push $REPO/$USERS:$TAG

    # users db
    docker build $USERS_DB_REPO -t $USERS_DB:$COMMIT -f Dockerfile
    docker tag $USERS_DB:$COMMIT $REPO/$USERS_DB:$TAG
    docker push $REPO/$USERS_DB:$TAG

    # client
    docker build $CLIENT_REPO -t $CLIENT:$COMMIT -f Dockerfile-$DOCKER_ENV --build-arg NODE_ENV=$NODE_ENV --build-arg REACT_APP_DOMAIN_NAME_URL=$REACT_APP_DOMAIN_NAME_URL --build-arg REACT_APP_CSRF_TOKEN=$REACT_APP_CSRF_TOKEN --build-arg REACT_APP_TWITCH_OAUTH_LINK=$REACT_APP_TWITCH_OAUTH_LINK --build-arg REACT_APP_TWITCH_TOP_STREAM_API_URL=$REACT_APP_TWITCH_TOP_STREAM_API_URL --build-arg REACT_APP_TWITCH_CALLBACK_URL=$REACT_APP_TWITCH_CALLBACK_URL --build-arg REACT_APP_TWITCH_USER_NAME=$REACT_APP_TWITCH_USER_NAME --build-arg REACT_APP_TWITCH_CLIENT_ID=$REACT_APP_TWITCH_CLIENT_ID  --build-arg REACT_APP_TWITCH_OAUTH_TOKEN=$REACT_APP_TWITCH_OAUTH_TOKEN
    docker tag $CLIENT:$COMMIT $REPO/$CLIENT:$TAG
    docker push $REPO/$CLIENT:$TAG

    # lexical
    docker build $LEXICAL_REPO -t $LEXICAL:$COMMIT -f Dockerfile-$DOCKER_ENV
    docker tag $LEXICAL:$COMMIT $REPO/$LEXICAL:$TAG
    docker push $REPO/$LEXICAL:$TAG

    # repository
    docker build $REPOSITORY_REPO -t $REPOSITORY:$COMMIT -f Dockerfile-$DOCKER_ENV
    docker tag $REPOSITORY:$COMMIT $REPO/$REPOSITORY:$TAG
    docker push $REPO/$REPOSITORY:$TAG

    # repository db
    docker build $REPOSITORY_DB_REPO -t $REPOSITORY_DB:$COMMIT -f Dockerfile
    docker tag $REPOSITORY_DB:$COMMIT $REPO/$REPOSITORY_DB:$TAG
    docker push $REPO/$REPOSITORY_DB:$TAG
  fi
fi
