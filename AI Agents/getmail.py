from flask import Flask, render_template, request
from imap_tools import MailBox
from langchain.llms.base import LLM
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
import requests
import requests
from langchain.llms.base import LLM
from typing import Optional, List, Mapping, Any

class Ollama(LLM):
    model: str = "llama2"
    base_url: str = "http://localhost:11434"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        url = f"{self.base_url}/api/generate"
        response = requests.post(url, json={"model": self.model, "prompt": prompt}, stream=True)
        response.raise_for_status()

        # Collect streamed output
        full_output = ""
        for line in response.iter_lines():
            if line:
                data = line.decode("utf-8")
                if '"response":"' in data:
                    part = data.split('"response":"')[1].split('"')[0]
                    full_output += part
        return full_output.strip()

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model": self.model}

    @property
    def _llm_type(self) -> str:
        return "ollama"

app = Flask(__name__)

import socket
try:
    print(socket.gethostbyname("imap.gmail.com"))
except socket.gaierror as e:
    print("DNS resolution error:", e)


# Email and password (keep safely, or ask user to input)
EMAIL = "jaiaakaash06@gmail.com"
APP_PASSWORD = "fbws ojvw kxco ihej"

def fetch_and_summarize_emails():
    emails = []
    with MailBox("imap.gmail.com").login(EMAIL, APP_PASSWORD, "INBOX") as mailbox:
        for msg in mailbox.fetch(criteria="UNSEEN", limit=5, reverse=True, mark_seen=True):
            text = msg.text or msg.html or "(No content)"
            emails.append(text)

    llm = Ollama(model="llama3.2")
    summarizer = load_summarize_chain(llm, chain_type="stuff")

    summaries = []
    for email_text in emails:
        doc = Document(page_content=email_text)
        result = summarizer.invoke([doc])
        summaries.append(result["output_text"])
    return summaries

@app.route("/", methods=["GET", "POST"])
def home():
    summaries = []
    if request.method == "POST":
        summaries = fetch_and_summarize_emails()
    return render_template("index.html", summaries=summaries)

if __name__ == "__main__":
    app.run(debug=True)
