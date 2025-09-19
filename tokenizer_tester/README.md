# Batch Ingest Tokenizer Template Tester

A modern Qt-based GUI application for testing and validating tokenizer templates used in batch ingest workflows. This tool helps users preview how file paths will be tokenized using custom templates and immediately see which tokens are resolved successfully.

## Features

- **Real-time Preview**: Instantly see token resolution as you type
- **Error Detection**: Visual feedback for unresolvable tokens with red error cells
- **Dark Theme**: Modern dark UI with clean, edge-less styling
- **Responsive Design**: 400x500px window with proper spacing and scrollable content
- **Template Validation**: Support for multiple token formats (`{token}`, `<token>`, `${token}`)
- **Mock Data Generation**: Built-in mock tokenizer for UI testing (to be replaced with actual tokenizer)

## Installation

### Prerequisites

- Python 3.8+
- Qt bindings (PySide6 or PyQt5/6)
- qtpy wrapper (included in `.venv`)

### Setup

1. Navigate to the tokenizer_tester directory:
   ```bash
   cd tokenizer_tester
   ```

2. Activate the provided virtual environment:
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Usage

### Basic Operation

1. **Testing Path**: Enter the file path you want to analyze in the top input field
2. **Template**: Enter your tokenizer template in the second input field
3. **Results**: View the resolved tokens in the table below

### Template Formats Supported

- `{token}` - Standard curly brace format
- `<token>` - Angle bracket format  
- `${token}` - Environment variable style

### Example

**Testing Path:**
```
/project/sequence_001/shot_010/lighting/master_v001.exr
```

**Template:**
```
{project}/{sequence}/{shot}/{department}/{task}_v{version}.{extension}
```

**Result:**
| Token      | Value        |
|------------|-------------|
| project    | TestProject |
| sequence   | 001_intro   |
| shot       | shot_010    |
| department | lighting    |
| task       | master      |
| version    | v001        |
| extension  | exr         |

### Error Indication

- **Red cells**: Indicate tokens that cannot be resolved
- **Normal cells**: Successfully resolved tokens
- **Warning message**: Displayed when no tokens are found

## File Structure

```
tokenizer_tester/
├── main.py              # Application entry point
├── controller.py        # Data processing and mock tokenizer
├── styles.css          # Dark theme styling
├── README.md           # This documentation
├── test_app.py         # Validation and testing script
├── __init__.py         # Package initialization
└── ui/                 # User interface components
    ├── __init__.py     # UI package initialization
    ├── ui.py           # Main application window
    ├── view.py         # Custom table view component
    ├── model.py        # Table data model
    └── delegate.py     # Custom item delegates
```

## UI Components

### Main Window
- **Size**: 400px × 500px fixed
- **Margins**: 10px internal spacing
- **Theme**: Dark theme with rounded corners
- **Title**: "Batch Ingest tokenizer template tester"

### Input Fields
- **Path Input**: Full width, top position, placeholder text
- **Template Input**: Full width, 20px below path input
- **Styling**: 10% brighter than window background, no borders

### Token Table
- **Headers**: "Token" and "Value"
- **Scrollable**: Vertical and horizontal scrolling when needed
- **Alternating rows**: Every second row slightly dimmed
- **Token column**: 10% darker background
- **Grid lines**: Horizontal only, no vertical lines
- **Error cells**: Red tinted background for unresolved tokens

## Development

### Architecture

- **MVC Pattern**: Separated model, view, and controller logic
- **Qt Framework**: Using qtpy wrapper for Qt binding flexibility
- **Type Safety**: Full type annotations throughout
- **Documentation**: Google-style docstrings for all functions

### Key Classes

- `TokenizerTesterApp`: Main application window
- `TokenTableModel`: Data model for token display
- `TokenTableView`: Custom table view with warning support
- `TokenTableDelegate`: Custom styling for table cells

### Mock Tokenizer

The current `parse_tokens()` function in `controller.py` is a mockup that generates random test data. This includes:

- 10-12 sample tokens with realistic names
- Randomly removed tokens to test error handling
- None values for some tokens to test error display

**Future Implementation**: Replace `parse_tokens()` with actual tokenizer logic that:
- Parses real file paths against templates
- Extracts actual token values
- Handles various file path formats and naming conventions

## Testing

Run the comprehensive test suite:

```bash
python test_app.py
```

This includes:
- Controller function validation
- UI component testing
- Interactive visual testing with sample data
- Error handling verification

## Styling

The application uses a comprehensive CSS file (`styles.css`) with:

- **Colors**: Dark theme (#2b2b2b base, #353535 inputs, #1e1e1e table)
- **Fonts**: Segoe UI, Arial fallbacks
- **Borders**: No edges style, rounded corners where appropriate
- **Scrollbars**: Custom styled to match dark theme
- **Focus indicators**: Blue outline for accessibility

## Future Enhancements

### Planned Features
- [ ] Real tokenizer integration
- [ ] Template syntax highlighting
- [ ] Path validation indicators
- [ ] Export token results
- [ ] Multiple template testing
- [ ] Token statistics and analytics
- [ ] Drag & drop file path input
- [ ] Recent templates history
- [ ] Custom token format definitions

### Integration Points
- Replace `parse_tokens()` in `controller.py`
- Add actual path validation logic
- Implement template syntax validation
- Add file system browsing capabilities

## License

Internal tool for Ynput batch ingest workflows.

## Support

For issues or feature requests, contact the development team or create an issue in the project repository.