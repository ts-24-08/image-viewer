from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
import boto3
from botocore.config import Config

import os

app = FastAPI()

# S3-Bucket-Name aus Umgebungsvariable lesen
S3_BUCKET = os.environ.get('S3_BUCKET_NAME')

my_config = Config(
    region_name='eu-central-1',
    signature_version='v4',
)

# Erstelle eine S3-Client-Instanz
s3_client = boto3.client('s3', config=my_config)

# Jinja2-Template-Umgebung einrichten
templates = Environment(loader=FileSystemLoader('templates'))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Liste alle Objekte im Bucket auf
    objects = s3_client.list_objects_v2(Bucket=S3_BUCKET)

    # Filtere nur Bilddateien
    image_files = []
    if 'Contents' in objects:
        for obj in objects['Contents']:
            if obj['Key'].lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                # Generiere eine vorab signierte URL
                url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': S3_BUCKET, 'Key': obj['Key']},
                    ExpiresIn=3600  # URL gültig für 1 Stunde
                )
                image_files.append(url)

    template = templates.get_template('index.html')
    HTMLcontent = template.render(images=image_files)
    return HTMLResponse(content=HTMLcontent)
