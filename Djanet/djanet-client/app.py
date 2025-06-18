# app.py

import asyncio
import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import mcp_client

# Placeholder for MCP client connection
# You will need to implement the connection logic here

class PhysicsSolverClient(tk.Tk):
    def __init__(self):
        super().__init__()

        self.mcp_client = None
        self.asyncio_loop = None

        self.title("Physics Solver Client")
        self.geometry("1000x800")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Create main panes
        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left pane for input, C code, and simulation output
        self.left_pane = ttk.PanedWindow(self.paned_window, orient=tk.VERTICAL)
        self.paned_window.add(self.left_pane, weight=1)

        # Right pane for Manim visualization (using a placeholder for now)
        self.right_pane = ttk.Frame(self.paned_window)
        self.paned_window.add(self.right_pane, weight=1)

        # --- Left Pane Widgets ---
        # Input Frame
        self.input_frame = ttk.LabelFrame(self.left_pane, text="Physics Problem Input")
        self.left_pane.add(self.input_frame, weight=1)

        self.prompt_input = scrolledtext.ScrolledText(self.input_frame, wrap=tk.WORD, height=10)
        self.prompt_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.solve_button = ttk.Button(self.input_frame, text="Solve Problem", command=self.solve_problem_threaded)
        self.solve_button.pack(pady=5)

        # C Code Display Frame
        self.c_code_frame = ttk.LabelFrame(self.left_pane, text="Generated C Code")
        self.left_pane.add(self.c_code_frame, weight=1)

        self.c_code_display = scrolledtext.ScrolledText(self.c_code_frame, wrap=tk.WORD, height=10, state=tk.DISABLED)
        self.c_code_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Simulation Output Frame
        self.sim_output_frame = ttk.LabelFrame(self.left_pane, text="Simulation Output (NetCDF Placeholder)")
        self.left_pane.add(self.sim_output_frame, weight=1)

        self.sim_output_display = scrolledtext.ScrolledText(self.sim_output_frame, wrap=tk.WORD, height=10, state=tk.DISABLED)
        self.sim_output_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Right Pane Widgets ---
        # Manim Visualization Frame (Placeholder for Jupyter Notebook like display)
        self.manim_frame = ttk.LabelFrame(self.right_pane, text="Manim Visualization (Jupyter Notebook Placeholder)")
        self.manim_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.manim_display = scrolledtext.ScrolledText(self.manim_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.manim_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def solve_problem_threaded(self):
        if not self.mcp_client or not self.asyncio_loop or not self.mcp_client.is_connected():
            print("MCP client not connected.")
            # You might want to show a user-friendly dialog here
            return

        question = self.prompt_input.get("1.0", tk.END).strip()
        if not question:
            print("Please enter a physics problem.")
            return

        print(f"Scheduling question for server: {question}")
        # Schedule the async solve_problem to run in the asyncio thread
        asyncio.run_coroutine_threadsafe(self.solve_problem(question), self.asyncio_loop)

    async def solve_problem(self, question):
        print(f"Sending question to server: {question}")
        try:
            response = await self.mcp_client.call_tool('solve-physics-question', question=question)
            
            solution = response.get('solution', 'No solution found.')
            c_code = response.get('c_code', 'No C code generated.')
            manim_code = response.get('manim_code', 'No Manim code generated.')

            # Schedule the GUI update on the main (Tkinter) thread
            self.after(0, self.update_displays, solution, c_code, manim_code)

        except Exception as e:
            print(f"An error occurred: {e}")
            self.after(0, self.update_displays, f"Error: {e}", "", "")

    def update_displays(self, solution, c_code, manim_code):
        # Enable the widgets to update them
        for display in [self.c_code_display, self.sim_output_display, self.manim_display]:
            display.config(state=tk.NORMAL)
            display.delete("1.0", tk.END)

        # Insert new content
        self.c_code_display.insert(tk.END, c_code)
        self.sim_output_display.insert(tk.END, solution) # Displaying text solution here
        self.manim_display.insert(tk.END, manim_code)

        # Disable the widgets again
        for display in [self.c_code_display, self.sim_output_display, self.manim_display]:
            display.config(state=tk.DISABLED)

    def on_closing(self):
        if self.asyncio_loop and self.asyncio_loop.is_running():
            print("Stopping asyncio loop.")
            self.asyncio_loop.call_soon_threadsafe(self.asyncio_loop.stop)
        self.destroy()


if __name__ == "__main__":
    app = PhysicsSolverClient()

    def start_asyncio_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        app.asyncio_loop = loop

        async def connect_client():
            server_command = ["python", "-m", "src.wolfram_alpha_tool.server"]
            server_cwd = "c:\\Users\\Dominik\\Downloads\\djanet"
            
            print("Attempting to connect to MCP server...")
            try:
                async with mcp_client.process_client(server_command, cwd=server_cwd) as client:
                    print("MCP Client connected.")
                    app.mcp_client = client
                    await client.wait_closed()
                print("MCP Client disconnected.")
            except Exception as e:
                print(f"Failed to connect or run MCP client: {e}")
            finally:
                app.mcp_client = None
                if loop.is_running():
                    loop.call_soon_threadsafe(loop.stop)

        loop.create_task(connect_client())
        loop.run_forever()
        print("Asyncio loop has stopped.")

    thread = threading.Thread(target=start_asyncio_loop)
    thread.daemon = True
    thread.start()

    app.mainloop()
