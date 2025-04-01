# ComfyUI Recovery System

A complete system for automated recovery and setup of ComfyUI Portable Windows installations. This tool allows you to quickly rebuild ComfyUI with your custom configuration after a system failure or when setting up a new environment.

![ComfyUI Logo](https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/web/favicon.ico)

## 🔍 Overview

The ComfyUI Recovery System automates the process of downloading, installing, and configuring ComfyUI. It handles creating symbolic links to your model storage and installing custom nodes from a repository list. This allows you to quickly recover from a system failure or create a clean installation with minimal effort.

## ✨ Features

- 🔄 Downloads ComfyUI Portable Windows release from GitHub
- 📦 Extracts the downloaded archive to a specified location
- 🔗 Creates symbolic links between your model storage and the ComfyUI models directory
- 🧩 Installs custom nodes from a configurable list of GitHub repositories
- ⚙️ Saves your configuration for easy reuse
- 📋 Comprehensive logging of all operations
- 🚀 Command-line interface with various options for customization

## 📋 Requirements

- Windows operating system
- Python 3.6 or higher
- Internet connection for downloading ComfyUI and custom nodes
- Administrator privileges (required for symbolic link creation)
- Git (for custom node installation)
- 7-Zip (optional, py7zr will be used if 7-Zip is not available)

## 🔧 Installation

1. Clone this repository:
```bash
git clone https://github.com/MushroomFleet/ComfyUI-Recovery.git
cd ComfyUI-Recovery
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## 🚀 Usage

### Basic Usage

Run the recovery script:

```bash
python comfyui_recovery.py
```

On first run, you'll be prompted to enter:
- The path where ComfyUI should be installed
- The path to your existing model storage

These settings will be saved to `settings.json` for future use.

### Custom Repository List

By default, the system uses `RepoLists/default.txt` for custom node installation. You can create your own lists in the `RepoLists` directory and specify which one to use:

```bash
python comfyui_recovery.py --repo-list RepoLists/my_custom_list.txt
```

Format for repository list files:
```
# Comments start with #
https://github.com/username/repository1
https://github.com/username/repository2
```

### Command-line Arguments

The following arguments are available:

| Argument | Description |
|----------|-------------|
| `--install-path PATH` | Path where ComfyUI will be installed |
| `--models-path PATH` | Path to your model storage directory |
| `--repo-list PATH` | Path to the repository list file (default: RepoLists/default.txt) |
| `--force` | Force installation even if destination is not empty |
| `--skip-download` | Skip downloading ComfyUI (use existing archive) |
| `--skip-extract` | Skip extracting ComfyUI (use existing directory) |
| `--skip-symlink` | Skip creating symbolic links |
| `--skip-nodes` | Skip installing custom nodes |

## 📖 Example Scenarios

### Scenario 1: Full Recovery After System Failure

```bash
python comfyui_recovery.py --install-path "D:\AI\ComfyUI" --models-path "E:\AI\Models"
```

This will:
1. Download ComfyUI Portable Windows
2. Extract it to `D:\AI\ComfyUI`
3. Create a symbolic link from the ComfyUI models directory to `E:\AI\Models`
4. Install custom nodes from the default repository list

### Scenario 2: Setting Up a New Configuration

```bash
# First, create a custom repository list
echo "https://github.com/ltdrdata/ComfyUI-Manager" > RepoLists/minimal.txt
echo "https://github.com/Fannovel16/comfyui_controlnet_aux" >> RepoLists/minimal.txt

# Then run the recovery with the custom list
python comfyui_recovery.py --install-path "D:\Projects\ComfyUI-Minimal" --models-path "E:\AI\Models" --repo-list RepoLists/minimal.txt
```

This sets up a minimal ComfyUI installation with only specific custom nodes.

### Scenario 3: Quick Recovery Using Existing Files

If you've already downloaded the ComfyUI archive but need to set up everything else:

```bash
python comfyui_recovery.py --skip-download --install-path "D:\AI\ComfyUI" --models-path "E:\AI\Models"
```

## 🔧 Troubleshooting

### Common Issues

1. **Symbolic Link Creation Fails**
   - Ensure you're running the script with administrator privileges
   - Check that both source and destination paths exist
   - Verify Windows Developer Mode is enabled or you have the appropriate permissions

2. **Custom Node Installation Fails**
   - Ensure Git is installed and in your PATH
   - Check internet connectivity
   - Verify the GitHub repository URLs are correct and accessible

3. **Extraction Fails**
   - Ensure py7zr is installed or 7-Zip is available on your system
   - Check that the destination path is writable
   - Verify the downloaded archive is not corrupted

### Log Files

Detailed logs are saved in the `logs` directory. If you encounter issues, check the latest log file for more information.

## 📂 Project Structure

```
ComfyUI-Recovery/
├── comfyui_recovery.py   # Main script
├── settings.py           # Settings management
├── downloader.py         # Download functionality
├── extractor.py          # Archive extraction
├── symlink_manager.py    # Symbolic link management
├── node_installer.py     # Custom node installation
├── RepoLists/            # Repository list storage
│   └── default.txt       # Default repository list
├── settings.json         # User settings (created on first run)
├── logs/                 # Log files
└── README.md             # This documentation
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgements

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) - The awesome stable diffusion GUI
- All custom node developers who extend ComfyUI functionality

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues or pull requests to improve the functionality or documentation.
