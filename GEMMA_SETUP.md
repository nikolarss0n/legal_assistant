# Setting Up Gemma 3 for Legal Assistant

This guide explains how to set up Gemma 3 to work with the Bulgarian Legal Assistant.

## Prerequisites

Before setting up Gemma 3, make sure you have:

1. A Hugging Face account (https://huggingface.co/join)
2. Access to the Gemma 3 model (you need to accept the license on Hugging Face)
3. Python 3.8+ and pip installed

## Installation Steps

### 1. Install Core Dependencies

First, install the core dependencies:

```bash
pip install -r requirements.txt
```

### 2. Install Gemma 3 Support

Uncomment and run the Gemma-specific dependencies in requirements.txt:

```bash
pip install git+https://github.com/huggingface/transformers@v4.49.0-Gemma-3
pip install torch
```

### 3. Get Hugging Face Access Token

1. Go to https://huggingface.co/settings/tokens
2. Create a new token with "read" access
3. Copy your token

### 4. Configure Environment

Create a `.env` file in the project root with your token:

```
HUGGINGFACE_TOKEN=your_token_here
```

Or set it as an environment variable:

```bash
export HUGGINGFACE_TOKEN=your_token_here
```

### 5. Accept Gemma 3 Model License

Before you can use Gemma 3, you need to accept its license:

1. Go to https://huggingface.co/google/gemma-3-12b-it
2. Click "Access repository" or "Accept license"
3. Review and accept the terms

## Running with Gemma 3

### Using Hugging Face-hosted Model

After installation, use the legal assistant with the Hugging Face-hosted Gemma 3:

```bash
python legal_query.py --model google/gemma-3-12b-it --api-key your_token_here
```

Or use the smaller model if you have limited resources:

```bash
python legal_query.py --model google/gemma-3-8b-it
```

### Using a Locally Downloaded Model

#### 1. Download the model

Download the model using the Hugging Face CLI:

```bash
# Install the Hugging Face CLI
pip install huggingface_hub

# Log in to Hugging Face (you'll need to accept the model license first)
huggingface-cli login

# Download the model (replace with desired version)
huggingface-cli download google/gemma-3-12b-it --local-dir ./gemma-3-model
```

Or download using Python:

```python
from huggingface_hub import snapshot_download

# Download the model
snapshot_download(
    repo_id="google/gemma-3-12b-it",
    local_dir="./gemma-3-model",
    token="your_hf_token_here"
)
```

#### 2. Use the locally downloaded model

Specify the local model path when running the assistant:

```bash
python legal_query.py --model-path ./gemma-3-model
```

### Using Quantized Models for Low-Resource Devices

For computers with limited RAM/VRAM, you can use quantized models:

#### 1. Install bitsandbytes

```bash
pip install bitsandbytes
```

#### 2. Load 4-bit quantized model

Update the `initialize_model` method in `model/gemma_interface.py`:

```python
# Add quantization parameters
model = Gemma3ForConditionalGeneration.from_pretrained(
    model_path, 
    device_map="auto",
    token=self.api_key,
    load_in_4bit=True,             # Enable 4-bit quantization
    quantization_config={
        "bnb_4bit_compute_dtype": torch.float16
    }
).eval()
```

Or run with the `--quantize` flag (if you add this option to `legal_query.py`):

```bash
python legal_query.py --model-path ./gemma-3-model --quantize 4bit
```

#### 3. Memory requirements for different configurations

| Model Size | Format    | RAM Required | VRAM Required |
|------------|-----------|--------------|--------------|
| 12B        | Full      | 24+ GB       | 24+ GB       |
| 12B        | 8-bit     | 12+ GB       | 12+ GB       |
| 12B        | 4-bit     | 6+ GB        | 6+ GB        |
| 8B         | Full      | 16+ GB       | 16+ GB       |
| 8B         | 8-bit     | 8+ GB        | 8+ GB        |
| 8B         | 4-bit     | 4+ GB        | 4+ GB        |

## Troubleshooting

### Model Loading Issues

If you encounter errors loading the model:

1. Check that you've accepted the license on Hugging Face
2. Verify your API token is correct
3. Ensure you have enough disk space and RAM
4. Try using a smaller model like gemma-3-8b-it

### GPU Memory Issues

If you run into GPU memory errors:

1. Use a smaller model
2. Set `device_map="auto"` to use CPU offloading
3. Try running with CPU only (slower but works with less memory)

### Import Errors

If you see import errors related to Gemma3:

1. Make sure you installed the correct version of transformers with Gemma 3 support
2. Check that torch is installed correctly

## Using Gemma 3 with CPU Only

To run on systems without a GPU:

```python
# In code, modify model loading to use CPU
model = Gemma3ForConditionalGeneration.from_pretrained(
    model_path, 
    device_map="cpu",
    torch_dtype=torch.float32
).eval()
```

Or specify CPU usage in the command line:

```bash
CUDA_VISIBLE_DEVICES="" python legal_query.py
```