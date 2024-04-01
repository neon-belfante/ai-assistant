# Ella - AI Assistant
Ella is a local Ai assistant that comes with her own gui.
<br> This project serves as a showcase for integrating different GenAI models and frameworks.

## features
1. She has a personality of her own `Llama2 model with cutom modelFile`
2. She talks using a text-to-speech ai `SpeechT5Processor`
3. She has both short-term and long-term memory with options to save and load the conversation `Use of Retrieval Augmented Generation`
4. She can react to images `LLava model`


## Installation
As of now Ella runs only on Debian/Ubuntu based distros
<br> Run on a terminal:
```
sudo curl -sSL https://raw.githubusercontent.com/neon-belfante/ai-assistant/master/installation.sh | bash
```

## Running
Run on a new terminal:
```
cd ai-assistant && ./run_app.sh
```

### Warning
First run will take longer since `Ollama` needs to download the models