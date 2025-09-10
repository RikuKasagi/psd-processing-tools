# PSD Processing Tools

🎨 **Python utilities for PSD file processing** - Extract layers from PSD files and create PSD files from PNG images with ease.

## ✨ Features

### 🔧 PSD Layer Extraction (`psd_split.py`)
- **Extract all layers** from PSD files as individual PNG images
- **Support for hidden layers** - extract both visible and hidden layers
- **Preserve canvas size** - all extracted images maintain original PSD dimensions
- **Alpha channel support** - full transparency preservation
- **Group layer support** - hierarchical layer extraction
- **Position preservation** - layers maintain their original positions

### 🏗️ PSD Creation (`psd_maker.py`)
- **Create PSD files** from multiple PNG images
- **Layer management** - automatic layer naming and ordering
- **Size validation** - ensures all input images have consistent dimensions
- **Transparency support** - full RGBA channel support

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/RikuKasagi/psd-processing-tools.git
cd psd-processing-tools

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

#### Extract layers from PSD

```python
from psd_split import extract_layers_from_psd

# Extract all layers (including hidden ones)
layers = extract_layers_from_psd(\"artwork.psd\", include_hidden=True)

# Save each layer as PNG
for layer_name, image in layers.items():
    image.save(f\"{layer_name}.png\")
```

#### Create PSD from PNG images

```python
from psd_maker import save_images_as_psd

# Create PSD from PNG files (bottom to top order)
save_images_as_psd(
    image_paths=[\"background.png\", \"character.png\", \"effects.png\"],
    layer_names=[\"Background\", \"Character\", \"Effects\"],
    save_path=\"output.psd\"
)
```

## 📖 API Reference

### `extract_layers_from_psd(psd_path, include_hidden=True)`

Extract layers from a PSD file.

**Parameters:**
- `psd_path` (str): Path to the PSD file
- `include_hidden` (bool): Whether to include hidden layers (default: True)

**Returns:**
- `Dict[str, Image.Image]`: Dictionary with layer names as keys and PIL Images as values

### `save_images_as_psd(image_paths, layer_names, save_path)`

Create a PSD file from PNG images.

**Parameters:**
- `image_paths` (List[str]): List of PNG file paths (bottom to top order)
- `layer_names` (List[str]): List of layer names
- `save_path` (str): Output PSD file path

## 📁 Project Structure

```
psd-processing-tools/
├── psd_split.py       # PSD layer extraction
├── psd_maker.py       # PSD creation from PNGs
├── requirements.txt   # Python dependencies
├── LICENSE           # MIT License
└── README.md         # This file
```

## 🔧 Dependencies

- **psd-tools** >= 1.9.0 - For reading PSD files
- **pytoshop** >= 1.2.0 - For writing PSD files  
- **Pillow** >= 9.0.0 - Image processing
- **numpy** >= 1.21.0 - Numerical operations

## 💡 Use Cases

- **Digital Art Workflows** - Extract artwork layers for further editing
- **Game Development** - Separate game assets from layered designs
- **Web Development** - Extract UI elements from design files
- **Automation** - Batch process PSD files in production pipelines
- **Asset Management** - Organize and manage design resources

## 🐛 Troubleshooting

### Common Issues

- **FileNotFoundError**: Check if the PSD file path is correct
- **ValueError: PNG以外が含まれています**: Ensure all input files are PNG format
- **ValueError: 画像サイズが一致していません**: All PNG images must have the same dimensions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [psd-tools](https://github.com/psd-tools/psd-tools) for robust PSD reading
- Uses [pytoshop](https://github.com/mdboom/pytoshop) for reliable PSD writing
- Powered by [Pillow](https://pillow.readthedocs.io/) for image processing

---

**Made with ❤️ for the digital art and development community**