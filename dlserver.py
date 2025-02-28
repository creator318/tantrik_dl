#!/usr/bin/env python3
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import nbformat
from nbconvert import MarkdownExporter
from pathlib import Path

app = FastAPI()
UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

@app.post("/upload")
async def upload_and_convert(file: UploadFile = File(...), nb2md: bool = Form(False)):
  if nb2md and file.filename.endswith(".ipynb"):
    # Convert notebook to Markdown without saving .ipynb
    md_path = UPLOAD_FOLDER / (Path(file.filename).stem + ".md")
    try:
      nb_content = nbformat.reads(await file.read(), as_version=4)
      md_exporter = MarkdownExporter()
      md_body, _ = md_exporter.from_notebook_node(nb_content)

      # Save converted Markdown
      with md_path.open("w", encoding="utf-8") as md_file:
        md_file.write(md_body)

      return {
        "message": "Uploaded Notebook converted to Markdown successfully",
      }
    except Exception as e:
      raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

  else:
    # Save the uploaded file as-is
    file_path = UPLOAD_FOLDER / file.filename
    with file_path.open("wb") as f:
      f.write(await file.read())

    return {
      "message": "File uploaded successfully",
    }

if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=5000)
