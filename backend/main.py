from fastapi import FastAPI, UploadFile, HTTPException, Depends, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from unstructured.partition.auto import partition
from transformers import T5ForConditionalGeneration, T5Tokenizer
import mimetypes
import pdfplumber
import uuid, os
from pathlib import Path

from dotenv import load_dotenv
from passlib.context import CryptContext
import datetime

# Load environment variables
load_dotenv()

# Retrieve the SECRET_KEY from environment variables


# Initialize password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

# Function to extract text from PDF using PyMuPDF
def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            # Iterate through all pages in the PDF
            for page in pdf.pages:
                text += page.extract_text()  # Extract text from each page
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

# Initialize FastAPI app
app = FastAPI()

origins = [
    "http://frontend:3000",  # The frontend container
    "http://localhost:3000",  # If testing on localhost
]

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
# DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    file_path = Column(String)
    doc_metadata = Column(Text)
    user = relationship("User", back_populates="documents")

User.documents = relationship("Document", cascade="all, delete-orphan", back_populates="user", order_by="Document.id")
Base.metadata.create_all(bind=engine)

# Dependency to get database session
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# T5 Initialization
model_name = "t5-small"  # Change to "t5-base" or "t5-large" if needed
model = T5ForConditionalGeneration.from_pretrained(model_name, torch_dtype="auto", device_map="auto")
tokenizer = T5Tokenizer.from_pretrained("t5-small", legacy=False)

# Helper function for T5 query
def query_with_t5(query: str, document_text: str) -> str:
    """Uses T5 model for question answering."""
    try:
        input_text = f"question: {query} context: {document_text}"
        inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
        outputs = model.generate(inputs["input_ids"], max_length=50, num_beams=5, early_stopping=True)
        answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return answer.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying with T5: {str(e)}")





# API Routes

@app.post("/upload/")
async def upload_document(file: UploadFile = File(...), db: SessionLocal = Depends(get_db)):
    """Upload a document, store locally, and extract metadata."""
    try:
        # Check MIME type for file
        file_type, _ = mimetypes.guess_type(file.filename)
        if file_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed.")

        # Ensure upload directory exists
        upload_dir = Path("uploaded_files")
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Save the uploaded file
        file_path = upload_dir / f"{uuid.uuid4()}-{file.filename}"

        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        # # Validate file size (10 MB limit)
        # if file.spool_max_size and file.spool_max_size > 10 * 1024 * 1024:
        #     raise HTTPException(status_code=400, detail="File size exceeds 10 MB limit")

        # # Read the file content and validate its size (10 MB limit)
        # content = await file.read()
        # if len(content) > 10 * 1024 * 1024:  # 10 MB
        #     raise HTTPException(status_code=400, detail="File size exceeds 10 MB limit")

        # Validate file size (10 MB limit) by checking file size without consuming the content
        # Use file.file (the actual file object) to get the size
        file_size = file.file.seek(0, os.SEEK_END)  # Move to the end to check the size
        if file_size > 10 * 1024 * 1024:  # 10 MB
            raise HTTPException(status_code=400, detail="File size exceeds 10 MB limit")

        # Reset file pointer to the beginning for further operations
        file.file.seek(0)

        with file_path.open("wb") as f:
            while chunk := file.file.read(1024 * 1024):  # Read in chunks of 1 MB
                f.write(chunk)

        # Extract text from PDF
        doc_metadata = extract_text_from_pdf(str(file_path))

        # Save document to DB
        document = Document(
            filename=file.filename,
            file_path=str(file_path),
            doc_metadata=doc_metadata,

        )
        db.add(document)
        db.commit()
        db.refresh(document)

        return {"message": "File uploaded successfully", "file_path": str(file_path)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/")
async def search_documents(query: str, db: SessionLocal = Depends(get_db)):
    """Search documents using T5 for question answering."""
    try:
        documents = db.query(Document).order_by(Document.id.desc()).first()
        if not documents:
            raise HTTPException(status_code=404, detail="No documents found")


        answer = query_with_t5(query, documents.doc_metadata)
        return {
            "document_id": documents.id,
            "filename": documents.filename,
            "results": answer
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/register/")
async def register_user(username: str, password: str, db: SessionLocal = Depends(get_db)):
    """Register a new user."""
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = hash_password(password)  # Hash the password before saving
    user = User(username=username, password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User registered successfully"}

@app.post("/login/")
async def login_user(username: str, password: str, db: SessionLocal = Depends(get_db)):
    """Login user."""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")



    return {"message": "Login successful"}

from fastapi.responses import HTMLResponse

# @app.get("/", response_class=HTMLResponse)
# async def serve_frontend():
#     # Ensure the frontend.html is in the correct directory
#     with open(os.path.join('frontend', 'frontend.html'), 'r') as f:
#         return f.read()

from fastapi.responses import FileResponse
import os

@app.get("/")
def serve_root():
    return FileResponse(os.path.join("frontend", "public", "index.html"))



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
