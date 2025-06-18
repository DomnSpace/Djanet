# physics-solver-vis MCP server

An MCP tool that solves physics questions, generates C code for simulation, and Python code for Manim visualization.

## Functionality

This MCP server uses an integrated language model (via LM Studio) to:
1. Provide a step-by-step solution to a given physics problem.
2. Generate C code for a simulator related to the problem.
3. Generate Python code for a Manim visualization of the problem or solution.

The generated C and Manim code are provided as output for manual execution and visualization.

## Configuration

To use this tool, ensure your LM Studio server is running and accessible at `http://localhost:1234/v1`.

## Quickstart

### Install

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  ```json
  "mcpServers": {
    "physics-solver-vis": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\Dominik\\Downloads\\djanet",
        "run",
        "wolfram-alpha-tool" # TODO: Update this to the new package name if changed
      ]
    }
  }
  ```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  ```json
  "mcpServers": {
    "physics-solver-vis": {
      "command": "uvx",
      "args": [
        "wolfram-alpha-tool" # TODO: Update this to the new package name if changed
      ]
    }
  }
  ```
</details>

## Development

### Building and Publishing

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

2. Build package distributions:
```bash
uv build
```

This will create source and wheel distributions in the `dist/` directory.

3. Publish to PyPI:
```bash
uv publish
```

Note: You'll need to set PyPI credentials via environment variables or command flags:
- Token: `--token` or `UV_PUBLISH_TOKEN`
- Or username/password: `--username`/`UV_PUBLISH_USERNAME` and `--password`/`UV_PUBLISH_PASSWORD`

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory C:\Users\Dominik\Downloads\djanet run wolfram-alpha-tool # TODO: Update this to the new package name if changed
```


Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.