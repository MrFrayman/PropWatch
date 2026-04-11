import os
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = lambda: None

# Load environment variables from .env file
load_dotenv()

class Config:
    # Database configuration
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # API keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # File paths
    PDF_STORAGE_PATH = os.getenv('PDF_STORAGE_PATH', './pdfs')
    REPORT_OUTPUT_PATH = os.getenv('REPORT_OUTPUT_PATH', './reports')
    
    # Runtime flags
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() in ('true', '1', 't')
    
    # Add more configuration variables as needed
    @staticmethod
    def validate():
        missing_vars = []
        if not Config.DATABASE_URL:
            missing_vars.append('DATABASE_URL')
        if not Config.OPENAI_API_KEY:
            missing_vars.append('OPENAI_API_KEY')
        if not Config.REPORT_OUTPUT_PATH:
            missing_vars.append('REPORT_OUTPUT_PATH')
        if missing_vars:
            raise ValueError(f'Missing required environment variables: {", ".join(missing_vars)}')