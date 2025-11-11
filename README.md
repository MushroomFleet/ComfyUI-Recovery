# ComfyUI Recovery System

A complete system for automated recovery and setup of ComfyUI Portable Windows installations. This tool allows you to quickly rebuild ComfyUI with your custom configuration after a system failure or when setting up a new environment.

![ComfyUI Logo](https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/web/favicon.ico)

## 🔍 Overview

The ComfyUI Recovery System automates the process of downloading, installing, and configuring ComfyUI. It handles creating symbolic links to your model storage and installing custom nodes from a repository list. This allows you to quickly recover from a system failure or create a clean installation with minimal effort.

### How It Works

The recovery system follows a carefully orchestrated workflow:

1. **Download Management** - Downloads ComfyUI from GitHub or uses a cached copy (saves 1.7GB on subsequent runs)
2. **Intelligent Extraction** - Extracts the archive with automatic path detection for different structures
3. **First-Run Initialization** - Automatically launches ComfyUI to create the embedded Python environment
4. **Smart Symlink Creation** - Links your model storage after initialization (prevents conflicts)
5. **Custom Node Installation** - Installs nodes using the embedded Python environment

All steps include comprehensive error handling with clear, actionable guidance if issues occur.

## ✨ Features

- 🔄 **Automated Downloads** - Fetches ComfyUI Portable Windows release from GitHub
- 💾 **Smart Caching** - Reuses downloaded archives to save bandwidth and time (1.7GB saved per run!)
- 🔔 **Version Detection** - Automatically checks for and notifies you of new ComfyUI releases
- 📦 **Intelligent Extraction** - Handles different archive structures automatically
- 🔍 **Flexible Path Detection** - Works with various ComfyUI installation directory structures
- 🚀 **Automatic First-Run Initialization** - Sets up ComfyUI's embedded Python environment before installing custom nodes
- 🔗 **Smart Symlink Management** - Creates symbolic links to your model storage (after initialization to prevent conflicts)
- 🛡️ **Privilege Detection** - Provides clear, actionable guidance for Windows symbolic link permissions
- 🧩 **Custom Node Installation** - Installs nodes from a configurable list of GitHub repositories
- ⚙️ **Configuration Persistence** - Saves your settings for easy reuse
- 📋 **Comprehensive Logging** - Detailed logs of all operations for troubleshooting
- 🎯 **Flexible CLI** - Command-line interface with various options for customization

## 📋 Requirements

- Windows operating system
- Python 3.6 or higher
- Internet connection for downloading ComfyUI and custom nodes
- **Administrator privileges or Developer Mode enabled** (required for symbolic link creation)
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

## 🔑 Running with Administrator Privileges

On Windows, creating symbolic links requires either administrator privileges or Developer Mode to be enabled. You have two options:

### Option 1: Run as Administrator (Recommended for one-time use)

1. Open PowerShell or Command Prompt as Administrator:
   - Press `Win + X` and select "Windows PowerShell (Admin)" or "Command Prompt (Admin)"
   - Or right-click on PowerShell/Command Prompt and select "Run as administrator"

2. Navigate to the ComfyUI-Recovery directory:
```powershell
cd C:\Path\To\ComfyUI-Recovery
```

3. Run the script:
```powershell
python comfyui_recovery.py
```

### Option 2: Enable Developer Mode (Recommended for frequent use)

**Windows 10:**
1. Open Settings (Win + I)
2. Go to "Update & Security" → "For developers"
3. Enable "Developer Mode"
4. Restart your computer (may not be required, but recommended)

**Windows 11:**
1. Open Settings (Win + I)
2. Go to "Privacy & Security" → "For developers"
3. Enable "Developer Mode"
4. Restart your computer (may not be required, but recommended)

Once Developer Mode is enabled, you can run the script normally without administrator privileges:
```bash
python comfyui_recovery.py
```

**Note:** If you encounter a symlink creation error, the script will provide detailed instructions on how to resolve it.

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
| `--latest` | Download the latest version from GitHub (bypass cache) |
| `--skip-download` | Skip downloading ComfyUI (use existing archive) |
| `--skip-extract` | Skip extracting ComfyUI (use existing directory) |
| `--skip-symlink` | Skip creating symbolic links |
| `--skip-first-run` | Skip first-run initialization (use if embedded Python already exists) |
| `--skip-nodes` | Skip installing custom nodes |

## 📖 Example Scenarios

### Scenario 1: Full Recovery After System Failure

```bash
python comfyui_recovery.py --install-path "D:\AI\ComfyUI" --models-path "E:\AI\Models"
```

This will:
1. Download ComfyUI Portable Windows (or use cached version)
2. Extract it to `D:\AI\ComfyUI`
3. **Run first-time initialization** to set up the embedded Python environment
4. Create a symbolic link from the ComfyUI models directory to `E:\AI\Models`
5. Install custom nodes from the default repository list

**Note:** The first-run initialization step automatically launches ComfyUI, waits for it to complete setup, then gracefully shuts it down. This creates the embedded Python environment and default directory structure. The symlink is then created after initialization to replace the default models folder with your existing model storage. This process typically takes 1-3 minutes depending on your system.

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

### Scenario 4: Updating to the Latest Version

To download and install the latest version of ComfyUI from GitHub (bypassing the cached archive):

```bash
python comfyui_recovery.py --latest
```

The script will automatically:
1. Check GitHub for the latest ComfyUI release
2. Download the newest version
3. Update your installation with the latest files
4. Update the cached version information

**Note:** By default, the script uses cached archives to save bandwidth and time. The cached archive will be used on subsequent runs unless you use the `--latest` flag. If a newer version is available, the script will notify you and suggest using `--latest` to update.

## 🔧 Troubleshooting

### Common Issues

1. **Symbolic Link Creation Fails**
   - Ensure you're running the script with administrator privileges
   - Check that both source and destination paths exist
   - Verify Windows Developer Mode is enabled or you have the appropriate permissions
   - The script provides detailed guidance on how to resolve privilege issues

2. **Custom Node Installation Fails**
   - Ensure Git is installed and in your PATH
   - Check internet connectivity
   - Verify the GitHub repository URLs are correct and accessible
   - Ensure first-run initialization completed successfully (embedded Python must exist)

3. **Extraction Fails**
   - Ensure py7zr is installed or 7-Zip is available on your system
   - Check that the destination path is writable
   - Verify the downloaded archive is not corrupted

4. **Path Detection Issues**
   - The system automatically detects both nested and direct extraction structures
   - No manual configuration needed - works with various ComfyUI archive formats
   - If paths aren't detected, check that extraction completed successfully

### System Compatibility

The recovery system intelligently handles different ComfyUI extraction structures:
- **Nested structure**: `install_path/ComfyUI_windows_portable_nvidia/ComfyUI_windows_portable/...`
- **Direct structure**: `install_path/ComfyUI_windows_portable/...`

All path detection is automatic - the system will find the correct directories regardless of how the archive was extracted.

### Log Files

Detailed logs are saved in the `logs` directory. If you encounter issues, check the latest log file for more information.

## 📂 Project Structure

```
ComfyUI-Recovery/
├── comfyui_recovery.py      # Main script
├── settings.py              # Settings management
├── downloader.py            # Download functionality
├── extractor.py             # Archive extraction
├── symlink_manager.py       # Symbolic link management
├── first_run_initializer.py # First-run initialization handler
├── node_installer.py        # Custom node installation
├── RepoLists/               # Repository list storage
│   └── default.txt          # Default repository list
├── settings.json            # User settings (created on first run)
├── logs/                    # Log files
└── README.md                # This documentation
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgements

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) - The awesome stable diffusion GUI
- All custom node developers who extend ComfyUI functionality

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues or pull requests to improve the functionality or documentation.
