import gradio as gr

from src.agent.core import agent
from src.agent.state import STATES
from src.config.settings import GRADIO_SHARE, GRADIO_SERVER_NAME, GRADIO_SERVER_PORT


USER_ID = "demo_user"


def ensure_started(language_code: str):
    if USER_ID not in agent.sessions:
        return agent.start(USER_ID, language_code)
    return None


def send(message, history, lang_choice, uploaded_files):
    language_code = "am" if "አማርኛ" in lang_choice else "en"

    if history is None:
        history = []

    ensure_started(language_code)

    # Convert Gradio file list to list of file paths
    # Gradio Files component returns list of file paths (strings)
    files = None
    if uploaded_files:
        files = [str(f) for f in uploaded_files if f]

    # Check current state before processing
    session = agent.sessions.get(USER_ID, {})
    state_before = session.get("state")
    
    result = agent.process(USER_ID, message, language_code, files=files)
    
    # Only append to history if there's a message or response
    if message or result.get("response"):
        history.append((message or "(uploaded files)", result["response"]))
    
    # Get PDF path if available
    pdf_path = result.get("pdf_path")
    
    # Determine if file upload should be visible
    session_after = agent.sessions.get(USER_ID, {})
    show_upload = session_after.get("state") == STATES.BIRTH_DOCUMENTS
    
    # Show PDF download if available
    pdf_update = gr.update(value=pdf_path, visible=pdf_path is not None) if pdf_path else gr.update(visible=False)
    
    return history, "", gr.update(visible=show_upload), pdf_update


def quick(choice, history, lang_choice, uploaded_files):
    return send(choice, history, lang_choice, uploaded_files)


def reset(lang_choice):
    if USER_ID in agent.sessions:
        del agent.sessions[USER_ID]
    return [], "", gr.update(visible=False), gr.update(visible=False)


def build_app():
    with gr.Blocks(title="🇪🇹 Kebele Service Agent") as demo:
        gr.Markdown("# 🇪🇹 Kebele Service Agent MVP")
        gr.Markdown("Birth Certificate Registration + Digital ID Appointment Booking (Hackathon demo).")

        lang = gr.Radio(["አማርኛ (Amharic)", "English"], value="አማርኛ (Amharic)", label="Language")

        chatbot = gr.Chatbot(height=480, label="Chat")
        msg = gr.Textbox(placeholder="Type here (or click A/B/C/D)...", label="Message")
        
        # File upload widget (initially hidden)
        file_upload = gr.Files(
            label="Upload documents (1-3 files: images or PDF)",
            file_types=["image", "pdf"],
            visible=False
        )
        
        # PDF download output
        pdf_download = gr.File(
            label="📄 Download Generated Birth Certificate PDF",
            visible=False
        )

        with gr.Row():
            btn_send = gr.Button("Send")
            btn_reset = gr.Button("Reset")

        with gr.Row():
            a = gr.Button("A")
            b = gr.Button("B")
            c = gr.Button("C")
            d = gr.Button("D")

        btn_send.click(
            send, 
            inputs=[msg, chatbot, lang, file_upload], 
            outputs=[chatbot, msg, file_upload, pdf_download]
        )
        msg.submit(
            send, 
            inputs=[msg, chatbot, lang, file_upload], 
            outputs=[chatbot, msg, file_upload, pdf_download]
        )

        a.click(
            quick, 
            inputs=[gr.State("A"), chatbot, lang, file_upload], 
            outputs=[chatbot, msg, file_upload, pdf_download]
        )
        b.click(
            quick, 
            inputs=[gr.State("B"), chatbot, lang, file_upload], 
            outputs=[chatbot, msg, file_upload, pdf_download]
        )
        c.click(
            quick, 
            inputs=[gr.State("C"), chatbot, lang, file_upload], 
            outputs=[chatbot, msg, file_upload, pdf_download]
        )
        d.click(
            quick, 
            inputs=[gr.State("D"), chatbot, lang, file_upload], 
            outputs=[chatbot, msg, file_upload, pdf_download]
        )

        btn_reset.click(
            reset, 
            inputs=[lang], 
            outputs=[chatbot, msg, file_upload, pdf_download]
        )

        return demo


def launch():
    demo = build_app()
    # server_name="0.0.0.0" makes it reachable on your LAN; server_port controls the port. [web:27]
    demo.launch(share=GRADIO_SHARE, server_name=GRADIO_SERVER_NAME, server_port=GRADIO_SERVER_PORT)


if __name__ == "__main__":
    launch()
