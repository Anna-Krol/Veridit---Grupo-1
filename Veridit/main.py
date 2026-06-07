import uvicorn

if __name__ == "__main__":
    print("Iniciando o servidor da plataforma Veridit...")
    # Executa o FastAPI contido dentro do pacote 'interface.web_ui'
    uvicorn.run("interface.web_ui:app", host="127.0.0.1", port=8000, reload=True)