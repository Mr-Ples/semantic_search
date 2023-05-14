# semantic-search
- Free Vector DB: chromadb
- Free embeddings: SBERT
- Free hosting: tirmux + idle mobile device + jprq

## setup
- change `COLLECTION_NAME` and `COLLECTION_DRIVE_FOLDER_ID` in `constants.py`
- add Google service account to the folder that has all the files you want to store
- save service account credentials as `service_creds.json` in repo root
- run script `convert_and_save_drive_folder_to_collection.py`

## serve
- install and configure `jprq`: https://github.com/azimjohn/jprq
- run `chmod +x serve.sh`
- run `./serve.sh`

visit: https://mr-ples.jprq.live/