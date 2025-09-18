from pydantic import BaseModel, Field

class ErrorSchema(BaseModel):
    """Define como uma mensagem de erro será representada"""
    message: str = Field(..., example="Ocorreu um erro inesperado.", description="Mensagem de erro detalhada")