import sys

sys.path.append("../app/back-end")
from services.file import extract_text_from_filepath
import warnings
from pydantic_schemas.document import Document
import os

warnings.filterwarnings("ignore")


if __name__ == "main":
    files = os.listdir("../data/")
    docs = []
    for i, file in enumerate(files):
        metadata = {
            "source_id": "test:" + file,
            "source": "file",
            "url": file,
            "author": "EMC" + str(i),
        }
        extracted_text = extract_text_from_filepath("../data/" + file)
        doc = Document(text=extracted_text, metadata=metadata)
        docs.append(doc)
    datastore = await get_datastore()
    await datastore.delete(delete_all=True)
    await datastore.upsert(docs)
