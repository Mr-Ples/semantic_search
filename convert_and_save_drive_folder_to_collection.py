import constants
from drive_downloader import main as drive_downloader
from embeddings import main as embeddings

if __name__ == "__main__":
    # TODO deal with files too large to be exported
    # TODO add spreadsheet support
    # TODO add more file types
    # TODO add chat bot
    # TODO add upload document on front end + memory of uploaded docs
    # TODO add links to download
    # TODO add website scraping via links to summarize websites
    constants.COLLECTION_NAME = constants.DESIGN_DOCUMENTS_COLLECTION
    constants.COLLECTION_DRIVE_FOLDER_ID = constants.DESIGN_DOCUMENTS_DRIVE_FOLDER_ID
    drive_downloader()
    embeddings()
