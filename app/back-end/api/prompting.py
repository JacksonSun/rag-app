#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# Overall Summary
## Prompt for text-davinci-003 model
OVERALL_RESPONSE_PROMPT = """
You are an smart assistant to help answer question from context.
- Answer the following question using only the data provided in the sources below in Markdown format.
- If the context have a markdown table, please return the table as well.
- Each source has a index followed by colon and the actual information, qoute the source index surrouded by [] for each piece of data you used in the response.
- If you cannot answer using the sources below, say you don't know.

question: {question}

Sources:
{sources}

Answer:
"""

# Prompt for Chat model
SYSTEM_CHAT_TEMPLATE = """
You are an smart assistant to help answer question from context.
- Answer the following question using only the data provided in the sources below.
- If the context have a markdown table, please return the table as well.
- Each source has a index followed by colon and the actual information, qoute the source index surrouded by [] for each piece of data you used in the answer.
- Please answer in bullet points.
- If you cannot answer using the sources below, say you don't know. here is an example:
"""

# shots/sample conversation
EXAMPLE_Q = """
Question: What is the deductible for the employee plan for a visit to Overlake in Bellevue?

Sources:
1: deductibles depend on whether you are in-network or out-of-network. In-network deductibles are $500 for employee and $1000 for family. Out-of-network deductibles are $1000 for employee and $2000 for family.
2: Overlake is in-network for the employee plan.
3: Overlake is the name of the area that includes a park and ride near Bellevue.
4: In-network institutions include Overlake, Swedish and others in the region
"""
EXAMPLE_A = "In-network deductibles are $500 for employee and $1000 for family [1] and Overlake is in-network for the employee plan [2][4]."

QUERY_TEMPLATE = """
Question: {question}

Sources:
{sources}
"""


EMI_SUMMARY_PROMPT_TEMPLATE = """
        Use the context delimited by triple backticks to extract summary, root cause, solution, side effect related to the question
        Context: ```{context}```
        Question:```{question}```

        Output in Json with following key:

        summary
        root cause
        solution
        side effect

        {format_instructions}
        """


QUESTION_ANSWER_PROMPT_TEMPLATE = """
        Given the following extracted parts of a long document and a question, create a final answer.
        If you don't know the answer, just say that you don't know. Don't try to make up an answer.
        Question: {question}
        =========
        {summaries}
        =========
        Answer:
        """


UPLOAD_DOCUMENT_SUMMARY_PROMPT_TEMPLATE = """
        Write a concise and comprehensive summary of the input text.
        Summary should include all details and no longer than 1000 words.
        DO NOT have person name in summary. Have CONTEXT, PROBLEM, SOLUTION and RESULT in summary.

        INPUT TEXT: {input_text}
        """

FILE_SUMMARY_SYSTEM_PROMPT = """
I want you to act as a text summarizer and provide a concise summary of a given article or text.
Your summary should be no more than 3-4 sentences and should accurately capture the main points and ideas of the original text.
Response should be structured, preferably in bullet points.
Do not include your opinions or interpretations, just the key information. Ready to start? Please provide the text you would like summarized.
"""

FILE_SUMMARY_USER_PROMPT = """
Summarize the text surroded by triple backticks.

```{input_text}```
"""
