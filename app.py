from src.ui.gradio_app import launch
import gradio as gr

def greet(name):
    return "Hello " + name + "!!"

demo = gr.Interface(fn=greet, inputs="text", outputs="text")
demo.launch()

if __name__ == "__main__":
    launch()
