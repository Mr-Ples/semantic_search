import json
import os
import traceback

import aspose.words as aw
import chromadb
import pdfplumber
from aspose.words import (
    Document,
    NodeType,
    SaveFormat,
)
from chromadb.config import Settings
from docx import Document
from sentence_transformers import SentenceTransformer

import constants
from drive_downloader import (
    get_header_data,
    find_document_id,
)


def main():
    print()
    print('Getting document datas')
    embeddings_data = []
    # convert docxs to plain text
    docx_files = []
    # convert docx to pdf
    for root, dirs, files in os.walk('./data'):
        for file in files:
            if file.endswith('.docx'):
                print()
                print(file)
                if os.path.isfile(os.path.join(root, file.replace(".docx", ".pdf"))):
                    print('exists')
                    continue

                doc = aw.Document(os.path.join(root, file))

                # Remove all comments
                comments = doc.get_child_nodes(NodeType.COMMENT, True)
                comments.clear()

                # Remove revision marks (edit suggestions)
                doc.accept_all_revisions()

                doc.save(os.path.join(root, file.replace('.docx', '.pdf')), SaveFormat.PDF)
                # docid = find_document_id(file.replace(".docx", "").replace(".pdf", ""))
                # docx_files.append((os.path.join(root, file.replace('.docx', '.pdf')), docid))

    pdf_files = []
    for root, dirs, files in os.walk('./data'):
        for file in files:
            if file.endswith('.pdf'):
                print(os.path.join(root, file))
                pdf_files.append(os.path.join(root, file))

    for indexx, file in enumerate(pdf_files):
        print()
        doc_id = None
        try:
            name = file.split("/")[-1]
            if name.endswith('(1).pdf'):
                continue
            doc_type = 'document'

            if not doc_id:
                doc_id = find_document_id(name.replace(".docx", "").replace(".pdf", ""), constants.REALTALKS_DRIVE_FOLDER_ID)
                print('https://docs.google.com/document/d/' + doc_id)
                if not doc_id:
                    raise SystemExit("=======Couldn't find", indexx, "", file)

            print("full_name:", file)
            print("name:", name)
            print("doc_type:", doc_type)
            print("doc_id:", doc_id)

            header_data = None
            if doc_type == 'document':
                header_data = get_header_data(doc_id)
                context = ""
                for url, dataz in header_data.items():
                    if 'linked topics' in dataz['name'].lower():
                        for line in dataz['context'].split("***")[-1].split("] "):
                            context += line[:-9] + ", "
                        break
                if not context:
                    for url, dataz in header_data.items():
                        if 'transcript' in dataz['name'].lower():
                            for line in dataz['context'].split("***")[-1].split("] "):
                                context += line[:-9] + ", "
                                print(line[:-9])
                    context = context[250:]
                print(context)
            else:
                continue

            meta = {'doc_name': name, 'doc_type': doc_type, 'doc_id': doc_id, 'doc_path': file}
            with pdfplumber.open(file) as docx:
                for page_num in range(len(docx.pages)):
                    # do all this effort to get the most relevant link
                    link = f'https://docs.google.com/{doc_type}/d/' + doc_id
                    if doc_type == 'document':
                        print("num:", page_num + 1)
                        docx_text = docx.pages[page_num].extract_text()
                        fulltext = ""
                        for elem in docx_text.split('] '):
                            fulltext += elem[:-9]
                        fulltext = fulltext.replace("\n", " ").replace('Evaluation Only.', '').replace('Created with Aspose.Words', '').replace('Copyright 2003-2023 Aspose Pty Ltd.', '').replace("Evaluation Mode.", "").replace('Created with an evaluation copy of Aspose.Words.', '').replace(
                            'To discover the full versions of our APIs please visit: https://products.aspose.c', ''
                        ).replace('To discover the full versions of our APIs please visit: https://products.aspose.com/words/', "").strip()
                        # print(fulltext)
                        docx_text = fulltext
                        temp_contest = ""
                        for elem in docx_text.split('] '):
                            # print(elem[:-9])
                            temp_contest += elem[:-9]
                        if temp_contest:
                            context = temp_contest.replace("\n", " ")[:1000]
                        # print(docx_text)
                    # Generate embedding
                    # embedding = model.encode(docx_text)
                    embedding = []
                    # set metadata
                    metas = {}
                    metas.update(meta)
                    metas.update({'page_num': page_num + 1, 'header': 'Page ' + str(page_num + 1), 'link': link, 'context': context})
                    # pack chromadb tuple
                    embeddings_data.append((embedding, docx_text, metas, doc_id + '-' + str(page_num + 1)))
                    # print(metas)
        except Exception as err:
            traceback.print_exc()
            continue

    # recreate collection with new data
    print("Creating database")
    os.makedirs(constants.CHROMA_PERSIST_DIR, exist_ok=True)
    client = chromadb.Client(
        Settings(
            chroma_db_impl=constants.CHROMA_DB_IMPL,
            persist_directory=constants.CHROMA_PERSIST_DIR
        )
    )
    model = SentenceTransformer(constants.EMBEDDING_MODEL)
    # client.delete_collection('realtalks')
    collection = client.get_or_create_collection(name='realtalks', embedding_function=lambda text: model.encode(text))
    print("BEFORE: ", collection.count())
    collection.upsert(
        # embeddings=[elem[0] for elem in embeddings_data],
        documents=[elem[1] for elem in embeddings_data],
        metadatas=[elem[2] for elem in embeddings_data],
        ids=[elem[3] for elem in embeddings_data]
    )
    print("AFTER: ", collection.count())


def get_new_podcast_links():
    client = chromadb.Client(
        Settings(
            chroma_db_impl=constants.CHROMA_DB_IMPL,
            persist_directory=constants.CHROMA_PERSIST_DIR
        )
    )
    model = SentenceTransformer(constants.EMBEDDING_MODEL)
    collection = client.get_collection(name='realtalks', embedding_function=lambda text: model.encode(text))
    metass = collection.get()['metadatas']
    chroma_realtalks = list(set([meta['doc_name'] for meta in metass]))
    print("Collection realtalks=", chroma_realtalks)
    print()
    info_fjson_output = '/home/simonl/bin/realtalk_infos'
    os.makedirs(info_fjson_output, exist_ok=True)

    _ = input(f"Run this command and come back and tap enter (requires pip install --upgrade youtube-dl):\n\n\t\t\tyoutube-dl --write-info-json --no-overwrites --skip-download -o '{info_fjson_output}/%(title)s-%(id)s' 'https://soundcloud.com/athenepodcast/'\n\nPress any key to continue")
    home_realtalks = ["".join(elem.replace('.info.json', '').split('-')[:-1]) for elem in os.listdir("/home/simonl/") if elem.endswith('.info.json')]
    print("Soundcloud realtalks=", home_realtalks)
    print()
    missing_realtalks = list(set(home_realtalks) - set(chroma_realtalks))
    print("Missing realtalks=", missing_realtalks)
    print()
    links = []
    for info_file in os.listdir(info_fjson_output):
        if info_file.endswith('.info.json') and "".join(info_file.replace('.info.json', '').split('-')[:-1]) in missing_realtalks:
            with open(os.path.join(info_fjson_output, info_file), 'r') as json_file:
                info = json.load(json_file)
                links.append(info['webpage_url'])
    print("Missing podcast links=", links)
    print()
    print("Use the following command in the podcasts notebook (found here: https://colab.research.google.com/drive/13H634_YzqIUPZg7cOyb9YMDTU62GfUm0?usp=sharing):"
        "\n\n\t\t\t!youtube-dl --playlist-end 2 --write-info-json --no-overwrites -c --ignore-errors --output 'drive/MyDrive/podcasts/%(id)s_%(title)s.mp3' " + " ".join(links))


def clean_everything():
    client = chromadb.Client(
        Settings(
            chroma_db_impl=constants.CHROMA_DB_IMPL,
            persist_directory=constants.CHROMA_PERSIST_DIR
        )
    )
    model = SentenceTransformer(constants.EMBEDDING_MODEL)
    for collectio in [
        # 'docs',
        'realtalks'
    ]:
        collection = client.get_collection(name=collectio, embedding_function=lambda text: model.encode(text))
        ids = collection.get()['ids']
        documents = collection.get()['documents']
        metass = collection.get()['metadatas']
        metas_new = []
        print([meta['doc_name'] for meta in metass])

        for idss, meta, docus in zip(ids, metass, documents):
            # meta.update({'context': ''})

            # if meta['page_num'] > 1 and not meta['context']:
            #     print(meta['link'])

            print(meta['context'])
            if meta['context'].startswith(". "):
                print('removing something')
                meta['context'] = meta['context'][3:]
                print(meta['context'])

            doc_name = meta['doc_name']

            removes = ['Evaluation Only. Created with Aspose.Words. Copyright 2003-2023 Aspose Pty',
                       'Created with an evaluation copy of Aspose.Words. To discover the full versions',
                       'of our APIs please visit: https://products.aspose.com/words/',
                       'our APIs please visit: https://products.aspose.com/words/',
                       'Created with an evaluation copy of Aspose.Words. To discover the full',
                       'This document was truncated here because it was created in the Evaluation Mode.',
                       'This document was truncated here because it was created in the Evaluation']
            if any([elem in docus for elem in removes]):
                print("remove aspose")
                for remove in removes:
                    docus = docus.replace(remove, '')

            if docus.startswith('.  '):
                print('remove garbase')
                docus = docus[3:]

            if meta['page_num'] == 1 and ''.join(e for e in doc_name if e.isalnum()).lower() not in ''.join(e for e in docus if e.isalnum()).lower():
                print("add doc name")
                docus = doc_name + ' ' + docus

            if '.pdf' in doc_name:
                print("Remove pdf")
                meta['doc_name'] = meta['doc_name'].replace('.pdf', '')

            print('https://docs.google.com/document/d/' + idss)
            # print(meta['doc_name'])
            # print(docus)
            # print(collection.get(ids=[idss]))
            collection.update(ids=[idss], documents=[docus], metadatas=[meta])
            # print(docus)
            # print(collection.get(ids=[idss]))
            # exit()
        # print([elem['doc_name'] for elem in collection.get(include=["metadatas"])])


if __name__ == "__main__":
    # get_new_podcast_links()
    main()
    clean_everything()
