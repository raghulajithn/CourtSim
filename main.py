from fastapi import FastAPI, UploadFile, File, Form
from typing import List
from io import BytesIO
from utils.read_file import extract_text_from_file
from scripts.process_documents import process_document, get_retriever_from_chroma
from agents.agent import get_opponent_response, get_judge_response
import os
import shutil

app = FastAPI()


@app.post("/upload/")
async def upload(session_id: str = Form(...),opposition: UploadFile = File(...), laws: UploadFile = File(...)):
    results = []
    folder_path = os.path.join("data", session_id)
    os.makedirs(folder_path, exist_ok=True)

    with open(os.path.join(folder_path, "opposition.pdf"), "wb") as f:
        shutil.copyfileobj(opposition.file, f)
    with open(os.path.join(folder_path, "laws.pdf"), "wb") as f:
        shutil.copyfileobj(laws.file, f)

    filename = f"{session_id}_opposition"
    file_content = BytesIO(await opposition.read())
    text = extract_text_from_file(filename, file_content)
    chunks = process_document(filename, text, persist_directory="db")
    results.append({"filename": opposition.filename, "num_chunks": len(chunks)})

    filename = f"{session_id}_laws"
    file_content = BytesIO(await laws.read())
    text = extract_text_from_file(filename, file_content)
    chunks = process_document(filename, text, persist_directory="db")
    results.append({"filename": laws.filename, "num_chunks": len(chunks)})

    return results

@app.post("/trial/")
async def trial(session_id: str, user_msg: str):
    context = get_retriever_from_chroma(
        user_msg, f"{session_id}_opposition", persist_directory="db"
    )
    reply = get_opponent_response(user_msg, context)
    
    return {"reply":reply}


@app.post("/verdict/")
async def get_verdict(session_id: str, history):
    context = get_retriever_from_chroma(
        history, f"{session_id}_laws", persist_directory="db"
    )
    verdict = get_judge_response(history, context)
    return {"verdict": verdict}
