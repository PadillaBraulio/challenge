
import redis

def lambda_handler(event, context):
    try:
        redisClient = redis.StrictRedis(host='localstack',
                                port=4510,
                                db=0)
        bucket_name     =event["Records"][0]["s3"]["bucket"]["name"]
        file_name       =event["Records"][0]["s3"]["object"]["key"]
        print(bucket_name)
        print(file_name)
        redisClient.lpush(bucket_name, file_name)
        
        return { "message": "Successfully added {} file into the list {}. There are {} files in the list".format(file_name, bucket_name,str(redisClient.llen(bucket_name)))}
    except:
        return { "message": "There was an ERROR while saving the file, check the logs for more information" }
        



    
    