import uvicorn
import os
if __name__ =="__main__":
    port = int(os.environ.get("PORT", 8000))  # Use the PORT environment variable or default to 8000
    uvicorn.run("src:app", host="0.0.0.0", port=port, reload=True)