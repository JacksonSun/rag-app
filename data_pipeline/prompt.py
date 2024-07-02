#!/usr/bin/env python
# -*- encoding: utf-8 -*-


SUMMARY_SYSTEM_PROMPT = """
I want you to act as a text summarizer and provide a concise summary of a given R&D lesson learned document.
Your summary should be structured, preferably in bullet points.
Must include:
MODEL: The model of the product
CONTEXT: The context, background of the problem
PROBLEM: The problem
SOLUTION: The solution
RESULT: The result
Do not include your opinions or interpretations, just the key information. Ready to start? Please Summarize the text surroded by triple backticks.
"""

SUMMARY_USER_PROMPT = """
```{input_text}```
"""

GENERATE_QA_PAIR_PROMPT_TEMPLATE = """
        You are a R&D expert in electronic product ODM company.
        Given the text input, generate a few questions from it along with the correct answer. \n{user_prompt}\n{format_instructions}
        """
# GENERATE_QA_PAIR_PROMPT_TEMPLATE = """
#         Given the text input, generate a few questions from it along with the correct answer. \n{user_prompt}\n{format_instructions}
#         """
