# Deploy a serverless webserver to AWS lambda using Zappa

## Setup AWS Credentials
Must have a `credentials` file in your `~/.aws/` folder.

## Install requirements.txt
```shell
pip install -r requirements.txt
```

## Deploy
```shell
zappa deploy dev
```

## Update
```shell
zappa update dev
```