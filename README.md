# Simple Flask AWS S3 Uploader
Simple and quick AWS S3 upload capability for Flask using Boto3 &amp; env variables

## Download and install locally
1. `git clone git@github.com:jelmerdejong/simple-flask-s3-uploader.git`
2. `cd simple-flask-s3-uploader`
3. `mkvirtualenv simple-flask-s3-uploader`
4. `pip install -r requirements.txt`

## Set local environment variables
Open your environments postactive file (`nano $VIRTUAL_ENV/bin/postactivate`) and add the following lines:
```
cd ~/Projects/simple-flask-s3-uploader
export APP_SETTINGS="config.DevelopmentConfig"
export SECRET_KEY="your-random-secret-key"
export S3_BUCKET="your-bucket-name"
export S3_KEY="your-aws-secret-key"
export S3_SECRET_ACCESS_KEY="your-aws-secret-access-key"
```

## Run it!
1. `export FLASK_APP=app.py`
2. `flask run`
