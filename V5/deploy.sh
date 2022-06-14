source "/Users/$(whoami)/.zshrc"

ENVIRONMENT=${1:-dev} # this variable will be used for docker tag and environment
LAMBDA_NAME=suggestedv5function # must be equals into template.yaml in lower case
PROJECT_NAME=${LAMBDA_NAME}-${ENVIRONMENT}
REGION=us-west-2
BUCKET=$PROJECT_NAME-1

echo "Building image in $ENVIRONMENT environment"

sam build --use-container --parameter-overrides DockerTag=$ENVIRONMENT

# make the bucket deployment
aws s3 ls | grep $BUCKET
if [[ $? != '0' ]]; then
    echo "making the bucket ${BUCKET} for deployment.."
    aws s3 mb s3://$BUCKET --region $REGION
    echo "uploading models, data and codifiers.."
    aws s3 sync outputs s3://$BUCKET/outputs
fi

echo "Validate if exists repository $LAMBDA_NAME"
aws ecr describe-repositories --repository-name $LAMBDA_NAME/$ENVIRONMENT --max-items 1  > /dev/null 2>&1
if [[ $? -ne 0 ]]; then
    echo "Repository not found"
    echo "Creating repository...."
    aws ecr create-repository --repository-name $LAMBDA_NAME/$ENVIRONMENT
fi

echo "Describe respository"
aws ecr describe-repositories --repository-name "$LAMBDA_NAME/$ENVIRONMENT" --max-items 1 > ecr_output.json

REPOSITORY_URI=$(python -c "import json; print(json.load(open('ecr_output.json'))['repositories'][0]['repositoryUri'])")

echo "Login repository $REPOSITORY_URI"
aws ecr get-login-password --region $REGION | docker login -u AWS --password-stdin $REPOSITORY_URI

echo "Pushing docker image $LAMBDA_NAME to aws"
docker tag $LAMBDA_NAME:$ENVIRONMENT $REPOSITORY_URI:latest
docker push $REPOSITORY_URI:latest

echo "Deploying $LAMBDA_NAME lambda function to aws"
sam deploy --stack-name $PROJECT_NAME --region $REGION --capabilities CAPABILITY_IAM --image-repository $REPOSITORY_URI \
    --parameter-overrides Environment=$ENVIRONMENT BucketApp=$BUCKET
