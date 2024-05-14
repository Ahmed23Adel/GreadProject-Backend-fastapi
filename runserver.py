import uvicorn

if __name__ =="__main__":
    uvicorn.run(app="src:app", port=8000, reload=True)