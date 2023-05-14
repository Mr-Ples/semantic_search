import constants
from drive_downloader import main as drive_downloader
from embeddings import main as embeddings

if __name__ == "__main__":
    constants.COLLECTION_NAME = constants.DESIGN_DOCUMENTS_COLLECTION
    constants.COLLECTION_DRIVE_FOLDER_ID = constants.DESIGN_DOCUMENTS_DRIVE_FOLDER_ID
    drive_downloader()
    embeddings()
