import asyncio

from mcp.server.models import InitializationOptions
from mcp.server import Server
from mcp.common import models as types
import mcp.server.stdio

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

server = Server("physics-solver-vis")

llm = None
physics_chain = None

async def initialize_langchain():
    global llm, physics_chain
    try:
        llm = ChatOpenAI(
            base_url="http://localhost:1234/v1",
            api_key="not-needed",
            temperature=0.7,
        )

        prompt_template = """Solve the following physics problem step-by-step, showing all calculations and reasoning.

Then, provide C code for a simulator that models the physics described in the problem. The C code should be a complete, runnable program that prints relevant results to standard output. Mark the beginning of the C code with `### C Code ###`.

Finally, provide Python code for a Manim scene that visualizes the physics problem or its solution. The Manim code should be a complete script that can be run to generate a visualization. Mark the beginning of the Manim code with `### Manim Code ###`.

Physics Problem:
{question}

Solution:"""
        prompt = PromptTemplate(template=prompt_template, input_variables=["question"])

        physics_chain = LLMChain(prompt=prompt, llm=llm)

    except Exception as e:
        print(f"Error initializing Langchain model: {e}")
        llm = None
        physics_chain = None

@server.initialize()
async def handle_initialize(options: InitializationOptions):
    await initialize_langchain()
    print(f"Server initialized with options: {options}")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="solve-physics-question",
            description="Solves a physics problem and provides a C simulation and a Manim visualization.",
            arguments={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The physics question to solve.",
                    },
                },
                "required": ["question"],
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    if name == "solve-physics-question":
        if not physics_chain:
            raise ValueError("Physics chain is not initialized.")
        if not arguments or "question" not in arguments:
            raise ValueError("Missing 'question' argument.")

        question = arguments["question"]
        response_text = await physics_chain.arun(question=question)

        solution_part = response_text
        c_code_part = ""
        manim_code_part = ""

        if "### C Code ###" in response_text:
            parts = response_text.split("### C Code ###")
            solution_part = parts[0].strip()
            remaining = parts[1]
            if "### Manim Code ###" in remaining:
                c_parts = remaining.split("### Manim Code ###")
                c_code_part = c_parts[0].strip()
                manim_code_part = c_parts[1].strip()
            else:
                c_code_part = remaining.strip()
        elif "### Manim Code ###" in response_text:
            parts = response_text.split("### Manim Code ###")
            solution_part = parts[0].strip()
            manim_code_part = parts[1].strip()

        return [
            types.TextContent(type="text", text=solution_part, name="solution"),
            types.TextContent(type="text", text=c_code_part, name="c_code", mimeType="text/x-c"),
            types.TextContent(type="text", text=manim_code_part, name="manim_code", mimeType="text/x-python"),
        ]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    asyncio.run(main())