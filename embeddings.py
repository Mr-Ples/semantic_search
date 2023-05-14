import os
import traceback

import chromadb
import pdfplumber
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

import constants
from drive_downloader import get_header_data


def get_file_name(peth):
    current_path = ''
    for index, part in enumerate(peth.split('/')):
        if not index:
            current_path = os.path.join(current_path, part)
            continue
        if os.path.exists(os.path.join(current_path, part)) and '.pdf' not in part:
            current_path = os.path.join(current_path, part)
            continue
        else:
            return peth.replace(current_path + '/', '').replace('.pdf', '')


def get_page_links(pdf_text, header_data):
    for url, data in header_data.items():
        clean_context = ''.join(e for e in data['context'].lower() if e.isalnum())
        clean_text = ''.join(e for e in pdf_text.lower() if e.isalnum())
        if clean_context in clean_text:
            # print(pdf_text)
            print(data['context'])
            print()
            print(clean_context)
            print()
            print(data['name'])
            print(url)
            return url, data['context'], data['name']
    return None, None, None


def main():
    print()
    print('Getting document datas')
    embeddings_data = []
    # convert pdfs to plain text
    pdf_files = []

    for root, dirs, files in os.walk('./data'):
        for file in files:
            if file.endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))

    # print(pdf_files)
    for file in pdf_files:
        if len(file.split("--")) > 2:
            print("Likey an exported google doc!")
            try:
                print(get_file_name(file))

                name = get_file_name(file).split('--')[0]
                doc_type = get_file_name(file).split('--')[-1]
                doc_id = get_file_name(file).replace(name + '--', '').replace('--' + doc_type, '')

                header_data = None
                if doc_type == 'document':
                    header_data = get_header_data(doc_id)
                else:
                    continue

                meta = {'doc_name': name, 'doc_type': doc_type, 'doc_id': doc_id, 'doc_path': file}
                with pdfplumber.open(file) as pdf:
                    for page_num in range(len(pdf.pages)):
                        # do all this effort to get the most relevant link
                        link = f'https://docs.google.com/{doc_type}/d/' + doc_id
                        header = 'Design Document'
                        context = None
                        headers = {}
                        if doc_type == 'document':
                            print("num:", page_num + 1)
                            pdf_text = pdf.pages[page_num].extract_text()
                            temp_link, context, header = get_page_links(pdf_text, header_data)
                            if temp_link:
                                link = temp_link
                            if (not temp_link) and page_num > 0:
                                # print("Didn't find link!")
                                # print(pdf_text)
                                for pageindex in range(page_num - 1, -1, -1):
                                    if pageindex < 0:
                                        break
                                    newtext = pdf.pages[pageindex].extract_text()
                                    # print("newnum:", pageindex)
                                    # print(newtext)
                                    temp_link, context, header = get_page_links(newtext, header_data)
                                    if temp_link:
                                        link = temp_link
                                        break

                        # Generate embedding
                        # embedding = model.encode(pdf_text)
                        embedding = []
                        # set metadata
                        metas = {}
                        metas.update(meta)
                        metas.update({'page_num': page_num + 1, 'header': header if header else 'Design Document', 'link': link, 'context': context.split('***')[-1] if context else ""})
                        # pack chromadb tuple
                        embeddings_data.append((embedding, pdf_text, metas, doc_id + '-' + str(page_num + 1)))
                        # print(metas)
            except:
                traceback.print_exc()
                continue
        else:
            with pdfplumber.open(file) as pdf:
                file_name = get_file_name(file)
                meta = {'doc_name': file_name, 'doc_type': 'pdf', 'doc_id': file_name, 'doc_path': file}
                for page_num in range(len(pdf.pages)):
                    # do all this effort to get the most relevant link
                    print("num:", page_num + 1)
                    pdf_text = pdf.pages[page_num].extract_text()
                    context = pdf_text[:200]
                    # Generate embedding
                    # embedding = model.encode(pdf_text)
                    embedding = []
                    # TODO: upload to s3 maybe and link it
                    link = file
                    # set metadata
                    metas = {}
                    metas.update(meta)
                    metas.update({'page_num': page_num + 1, 'header': 'PDF Document', 'link': link, 'context': context})
                    # pack chromadb tuple
                    embeddings_data.append((embedding, pdf_text, metas, file + '-' + str(page_num + 1)))
                    # print(metas)
    # recreate collection with new data
    print("Creating database")
    os.makedirs(constants.CHROMA_PERSIST_DIR, exist_ok=True)
    client = chromadb.Client(
        Settings(
            chroma_db_impl=constants.CHROMA_DB_IMPL,
            persist_directory=constants.CHROMA_PERSIST_DIR
        )
    )
    client.reset()
    model = SentenceTransformer(constants.EMBEDDING_MODEL)
    collection = client.create_collection(name=constants.COLLECTION_NAME, embedding_function=lambda text: model.encode(text))
    collection.add(
        # embeddings=[elem[0] for elem in embeddings_data],
        documents=[elem[1] for elem in embeddings_data],
        metadatas=[elem[2] for elem in embeddings_data],
        ids=[elem[3] for elem in embeddings_data]
    )


if __name__ == "__main__":
    main()
