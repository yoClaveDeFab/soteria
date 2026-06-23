import asyncio
import os
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

async def main():
    print("Initializing McpToolset...")
    env = os.environ.copy()
    env["GOOGLE_ACCESS_TOKEN"] = "ya29.dummy"
    
    toolset = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command='npx',
                args=["-y", "google-sheets-mcp"],
                env=env,
            )
        )
    )
    try:
        tools = await toolset.get_tools()
        for t in tools:
            if t.name == "values_append":
                print("Tool Name:", t.name)
                print("Tool Description:", t.description)
                print("Tool Declaration Parameters Schema:")
                import json
                print(json.dumps(t._get_declaration().parameters_json_schema, indent=2))
    except Exception as e:
        import traceback
        print("Error:")
        traceback.print_exc()
    finally:
        await toolset.close()

if __name__ == "__main__":
    asyncio.run(main())
