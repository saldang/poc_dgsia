FROM ollama/ollama:latest
COPY ./ollama-serve.sh /ollama-serve.sh
RUN chmod +x /ollama-serve.sh
RUN ./ollama-serve.sh

# Run the application
CMD [ "ollama","serve"]