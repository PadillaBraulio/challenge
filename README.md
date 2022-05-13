# challenge

This repository goes through the creation of a lambda function that gets triggered by an s3 object creation event, after the lambda is triggered it saves the name of the file in a list inside an elasticache server, all of that is done using terraform with localstack.

## Prerrequisites

Before we start make sure you have installed the following tools

1. [docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/install/)
2. [awscli](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
3. [terraform](https://www.terraform.io/downloads)
4. [Python3.7](https://www.python.org/downloads/)
5. [tflocal](https://docs.localstack.cloud/integrations/terraform/#using-the-tflocal-script)


## Getting started
Follow the steps provided in each of the following sections to get the environment up and ready.


.
### LocalStack:

From the [Documentation](https://localstack.cloud/):

LocalStack provides an easy-to-use test/mocking framework for developing Cloud applications. It spins up a testing environment on your local machine that provides the same functionality and APIs as the real AWS cloud environment.

---

There are multiples way to install localstack but for this case we used [docker-compose](https://docs.localstack.cloud/get-started/#docker-compose) approach.

In order to start localstack please run the following commands:

```
export LOCALSTACK_API_KEY=XXXXXXX
docker-compose up -d
```

After running above commands you will have localstack ready in your computer, you can check the logs using 

```
docker-compose logs
```

#### **Warning**:

**To get the LOCALSTACK_API_KEY you will have to create an account in https://app.localstack.cloud/ and get a subscription or use the free trail for 14 days without charge [Billing plans](https://localstack.cloud/pricing/)
This is needed because of the [elasticache](https://docs.localstack.cloud/aws/elasticache/) server is a PRO feature.**


.


----

### Lambda function

The code is in the **main.py** file inside the **lambda** folder, since redis package is not included in the lambda container we had to add that dependency into the zip file so there is a script called **createzip.sh** that will create the **lambda.zip** file with all the dependecies for the redis package.

To run that script you need to do the following:

```
cd lambda
bash createzip.sh
```

After that you will have your lambda.zip package updated with your latest changes.

.

----

### Terraform

To run terraform you need to do the following steps:

```
tflocal init
tflocal apply -auto-approve
```

tflocal is a wrap script that takes care of all the configuration needed for running terraform into a localstack container.

After you run the above commands all the infrastructure will be all set up and you will be able to test the functionality.

---
.

## Testing 


After you ran both docker-compose and the terraform scripts you, do the following to verify its working.


```
export AWS_ACCESS_KEY_ID="test"
export AWS_SECRET_ACCESS_KEY="test"
export AWS_DEFAULT_REGION="us-east-1"
echo "Hola" > test
echo "Hola2" > test2
echo "Hola3" > test3
aws --endpoint-url=http://localhost:4566 s3 cp test s3://files-bucket/
aws --endpoint-url=http://localhost:4566 s3 cp test2 s3://files-bucket/
aws --endpoint-url=http://localhost:4566 s3 cp test3 s3://files-bucket/

```

Above code will upload 3 files to the s3 bucket, so the lambda should be triggered and updated the redis server.

### Validating

#### Checking Lambda Function worked

First validation is to make sure the lambda was created and ran sucessfully.

Run the following:

```
docker-compose logs
```

and you should see this message 3 times:

```
localstack  | {"message":"Successfully added test file into the list files-bucket. There are 1 files in the list"}
localstack  | >tail: unrecognized file system type 0x794c7630 for ‘/tmp/__daemons.out’. please report this to bug-coreutils@gnu.org. reverting to polling
localstack  | > START RequestId: 64211ed6-34f3-1a79-de51-8dd8c9d17ffb Version: $LATEST
localstack  | > files-bucket
localstack  | > test
localstack  | > END RequestId: 64211ed6-34f3-1a79-de51-8dd8c9d17ffb
localstack  | > REPORT RequestId: 64211ed6-34f3-1a79-de51-8dd8c9d17ffb  Init Duration: 359.12 ms      Duration: 6.07 ms       Billed Duration: 7 ms   Memory Size: 1536 MB  Max Memory Used: 39 MB
```

The main difference would be that the number of files should increase in each time the message appear.

```{"message":"Successfully added test file into the list files-bucket. There are 1 files in the list"}```

#### Checking redis directly

For this we need redis-cli, we will use docker to get a redis-cli

```
docker run --name redis -it --rm --net=host --entrypoint /bin/bash bitnami/redis:latest

redis-cli -p 4510 LINDEX files-bucket 0
redis-cli -p 4510 LINDEX files-bucket 1
redis-cli -p 4510 LINDEX files-bucket 2

```

You should see something like this

```
[root@ip-10-0-11-141 ec2-user]# docker run --name redis3 -it --rm --net=host --entrypoint /bin/bash bitnami/redis:latest
I have no name!@ip-10-0-11-141:/$ redis-cli -p 4510 LINDEX files-bucket 0
"test3"
I have no name!@ip-10-0-11-141:/$ redis-cli -p 4510 LINDEX files-bucket 1
"test2"
I have no name!@ip-10-0-11-141:/$ redis-cli -p 4510 LINDEX files-bucket 2
"test"
I have no name!@ip-10-0-11-141:/$ 

```



