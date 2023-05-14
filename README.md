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

# TODO
- deal with files too large to be exported
- add spreadsheet support
- add more file types
- add chat bot
- add upload document on front end + memory of uploaded docs
- add links to download
- add website scraping via links to summarize websites

visit: https://semantic-search.jprq.live/
