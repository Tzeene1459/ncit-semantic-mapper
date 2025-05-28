import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.base import Runnable
load_dotenv()


class DefnGenerator(Runnable):
    """
    This a langchain Runnable that will ask the given llm to create a short
    biomedical definition of an input term. This can be used to bootstrap
    context for short terms before performing a vector store semantic search.

    llm: langchain chat model (defaults to ChatOpenAI)
    instructions: system prompt for generating a biomedical definition (has default)
    TOO_LONG: integer value (default 25) - if the input string is more than TOO_LONG
              words long, llm will not be called and the string '<term too long>' is returned.
    """
    
    llm: ChatOpenAI = ChatOpenAI(
        openai_api_key=os.getenv('OPENAI_API_KEY'), 
        temperature=0
    )
    instructions : str = """
    Return a 25- to 50-word definition for the input term, triple-quoted below.
    Perform the following steps to do this:

    Step 1: Review the term for misspellings and phonetic spellings. If the term requires
    correction, the correction will be refered to as <correction> in subsequent steps.

    Step 2: If <correction> is identified, write one line as follows:

     Corrected term: <correction>
    
    If no correction is found, do not mention that fact.

    Step 3. Write a 25-50 word definition of term or its correction.
    The definition should be written from the standpoint of an experienced 
    subject matter expert in the areas of biomedical clinical and research data.
    Use a formal dictionary style, not a conversational style. Do not use the term
    in the definition. Do not "speak to the user". Do not refer to yourself.

    Input term: '''{term}'''
    """

    filter_instructions: str = """

    Consider the input statement, triple-quoted below.

    Your viewpoint is as an biomedical data subject matter expert.
    If the statement appears to contain the definition of a biomedical concept, 
    write exactly the input statement, without enclosing quotes of any kind.

    If the statement  states
    "no definition can be provided", "undefinable", "irrelevant", or similar
    sentiments, write the following verbatim: Unable to define.

    Input statement: '''{statement}'''
    """
    
    TOO_LONG: int = 25

    def invoke(self, input) -> str:
        if len(input.split()) >= self.TOO_LONG:
            return "<term too long>"
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.instructions),
                ("human", "{term}")
            ]
        )
        filter_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.filter_instructions),
                ("human", "{statement}")
            ]
        )
        chain = prompt | self.llm | StrOutputParser() | filter_prompt | self.llm | StrOutputParser()
        return chain.invoke(input)
    
