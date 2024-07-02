from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from langchain.chains import LLMChain
import asyncio
from langchain.prompts import PromptTemplate
import redis
from config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_PASSWORD,
)
from .prompting import EMI_SUMMARY_PROMPT_TEMPLATE


class SourceChain:
    def __init__(self, llm, docs):
        self.llm = llm
        self.docs = docs

    def build_chain(self):
        llm = self.llm

        class SourceSummary(BaseModel):
            summary: str = Field(description="summary of context")
            root_cause: str | None = Field(description="root cause in context")
            solution: str | None = Field(description="solution in context")
            side_effect: str | None = Field(description="side effect in context")

        parser = PydanticOutputParser(pydantic_object=SourceSummary)
        prompt = PromptTemplate(
            template=EMI_SUMMARY_PROMPT_TEMPLATE,
            input_variables=["context", "question"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = LLMChain(llm=llm, prompt=prompt)
        redis_conn = _get_redis_conn()
        dic = redis_conn.json().get("rdexpert-mapping")

        return chain, parser, dic

    async def async_generate(self, chain, parser, query, doc, dic):
        if len(doc) == 1:
            res = await chain.arun(context=doc.page_content, question=query)
            r = doc.metadata.copy()
        else:
            r = doc[0].metadata.copy()
            res = await chain.arun(context=doc[0].page_content, question=query)
            r["similarity"] = doc[1]
            if doc[1] > 0.18:
                return
        res = res.replace("null", '"unknown"')
        r["detail"] = parser.parse(res).dict()
        contact_person = _get_keys_from_value(dic, r["source"].split("/")[-1])
        r["contact_person"] = ""
        if len(contact_person) > 0:
            r["contact_person"] = _get_keys_from_value(dic, r["source"].split("/")[-1])[
                0
            ]
        fileid = "-".join(r["id"].split(":")[-1].split("-")[:-1])
        r["screenshot_url"] = (
            "https://liteonrdexpert.blob.core.windows.net/rd-expert/screenshot/"
            + fileid
            + ".png"
        )
        r["url"] = (
            "https://liteon.sharepoint.com/sites/EIP_Data/Shared Documents/Forms/AllItems.aspx?id=/sites/EIP_data/Shared Documents/"
            + "/".join(r["source"].split("/")[4:])
            + "&parent=/sites/EIP_data/Shared Documents/"
            + "/".join(r["source"].split("/")[4 : len(r["source"].split("/")) - 1])
        )
        return r

    async def generate_concurrently(self, query):
        docs = self.docs
        chain, parser, dic = self.build_chain()
        tasks = []
        for doc in docs:
            tasks.append(self.async_generate(chain, parser, query, doc, dic))

        results = await asyncio.gather(*tasks)
        return results


def _get_keys_from_value(dic, val):
    return [
        v["contact"]
        for k, v in dic.items()
        if k != "Update_Time" and val == v["filename"]
    ]


def _get_redis_conn():
    conn = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        encoding="utf-8",
        decode_responses=True,
    )
    return conn
