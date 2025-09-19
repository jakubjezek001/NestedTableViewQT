# NestedTableViewQT

A Qt-based application for displaying nested table data with expandable/collapsible rows. This application demonstrates a sophisticated implementation of nested ProductItems and RepresentationItems data in a single table view with advanced features like required column highlighting, disabled cell visualization, and flexible data handling.

## Features

### Core Functionality
- **Nested Table Display**: ProductItems with expandable RepresentationItems underneath
- **Expandable Rows**: Click ▶/▼ or double-click to expand/collapse product items  
- **Universal Column Handling**: Flexible model accommodates different column sets per item
- **Required Column Highlighting**: Columns marked with `<>` are visually distinguished
- **Disabled Cell Visualization**: Cells without relevant data show diagonal pattern
- **Auto-sizing**: Intelligent column width management
- **Full Editing Support**: Edit any applicable cell data

### User Interface
- **Modern Qt Fusion Style**: Clean, professional appearance
- **Keyboard Shortcuts**: Full keyboard navigation support
- **Auto-refresh**: Optional automatic data reloading
- **Status Information**: Live statistics and selection feedback
- **Export/Import**: JSON data file management
- **Responsive Layout**: Adaptive to window resizing

## Requirements

- Python 3.7+
- qtpy
- PySide6 or PyQt5 (via qtpy wrapper)
- JSON data file

## Installation & Setup

1. **Clone or extract the project**:
   ```bash
   cd NestedTableViewQT
   ```

2. **Activate the virtual environment**:
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac  
   source .venv/bin/activate
   ```

3. **Install dependencies** (if not already installed):
   ```bash
   pip install qtpy PySide6
   ```

4. **Verify installation**:
   ```bash
   python test_app.py
   ```

5. **Run the application**:
   ```bash
   python main.py
   ```

## File Structure

```
NestedTableViewQT/
├── main.py              # Application entry point
├── controller.py        # Data management and business logic
├── data.json           # Sample data file
├── test_app.py         # Test suite for verification
├── README.md           # This documentation
├── .venv/              # Virtual environment
└── ui/                 # User interface components
    ├── __init__.py     # Package initialization
    ├── ui.py           # Main window and application UI
    ├── view.py         # Table view components
    ├── model.py        # Data models for Qt MVC
    └── delegate.py     # Custom cell rendering and editing
```

## Data Format

The application reads data from `data.json` with the following structure:

```json
{
  "ProductItems": [
    {
      "id": "ProdItem0",
      "data": {
        "<Folder Path>": "/path/to/folder",
        "Task Name": "Compositing", 
        "<Product Type>": "render",
        "Version": "v003",
        "Width": 1920,
        "Height": 1080
      },
      "RepresentationItems": [
        {
          "id": "ReprItem0",
          "data": {
            "<File Path>": "/path/to/file.exr",
            "Name": "beauty_main",
            "Extension": "exr",
            "Tags": "beauty,final"
          }
        }
      ]
    }
  ]
}
```

### Data Rules
- **Required Columns**: Marked with `<column name>` (e.g., `<File Path>`)
- **Flexible Schema**: Each item can have different columns
- **Missing Data**: Items without specific column data show as disabled cells

## Usage Instructions

### Basic Navigation
- **Expand/Collapse**: Click ▶ arrow or double-click any cell in a product row
- **Editing**: Double-click editable cells to modify values
- **Selection**: Click rows to select, view selection info in status bar
- **Scrolling**: Use mouse wheel or scrollbars for large datasets

### Keyboard Shortcuts
- **Ctrl+E**: Expand all product items
- **Ctrl+Shift+E**: Collapse all product items  
- **F5 or Ctrl+R**: Refresh data from file
- **Ctrl+O**: Open different data file
- **Enter/Space**: Toggle expansion on selected product row
- **Tab**: Navigate between editable cells

### Menu Options
- **File Menu**:
  - Open Data File: Load different JSON file
  - Reload: Refresh current data
  - Export Data: Save current data to new file
- **View Menu**:
  - Expand/Collapse All: Bulk row operations
  - Refresh: Reload view

### Visual Indicators
- **Yellow Background**: Required columns (marked with `< >`)
- **Diagonal Lines**: Disabled cells (no data for this item)
- **▶/▼ Arrows**: Expansion state indicators
- **Bold Headers**: Required column headers

## Technical Details

### Architecture
- **MVC Pattern**: Clean separation of Model, View, Controller
- **Qt Model/View Framework**: Leverages Qt's powerful table architecture  
- **Custom Delegates**: Special rendering for different cell states
- **Proxy Model**: Combines ProductItems and RepresentationItems seamlessly

### Key Components
- **DataController**: Manages JSON data, provides unified API
- **NestedTableProxyModel**: Combines product and representation models
- **NestedTableDelegate**: Handles custom cell rendering and editing
- **NestedTableView**: Enhanced QTableView with expansion logic

### Performance Features
- **Lazy Loading**: Representation models created only when needed
- **Efficient Updates**: Incremental model updates
- **Smart Resizing**: Delayed column resizing to prevent UI lag
- **Memory Optimization**: Models released when products collapsed

## Example Data Scenarios

The included `data.json` contains three example product items:

1. **Movie Shot 001 - Compositing**: 
   - Render product with beauty, preview, and thumbnail representations
   - Full metadata including framerange, FPS, colorspace

2. **Movie Shot 002 - Animation**:
   - Cache product with Alembic, FBX, and playblast representations  
   - Mixed data sets demonstrating flexible schema

3. **Movie Shot 003 - Lighting**:
   - Multiple render passes (diffuse, specular) with preview
   - Different framerates and resolution settings

## Troubleshooting

### Common Issues

**Application won't start**:
- Verify `data.json` exists and is valid JSON
- Check Python path and virtual environment activation
- Run `python test_app.py` to diagnose issues

**Data not loading**:
- Validate JSON syntax using online JSON validator
- Ensure required structure with "ProductItems" array
- Check file permissions and path accessibility

**UI display problems**:
- Try different Qt styles via `app.setStyle()` in main.py
- Verify qtpy is using correct Qt backend (PySide6/PyQt5)
- Check display scaling settings

**Performance issues**:
- Reduce data size for testing
- Disable auto-refresh if enabled
- Close and reopen collapsed sections periodically

### Getting Help

1. **Run test suite**: `python test_app.py` 
2. **Check console output**: Look for error messages and tracebacks
3. **Validate data file**: Ensure JSON structure matches specification
4. **Environment check**: Verify all dependencies are installed correctly

## Development Notes

### Extending the Application
- **Add new column types**: Extend `NestedTableDelegate` with custom editors
- **Custom data sources**: Implement new controllers following the existing API
- **Additional views**: Create new view types using the same models
- **Export formats**: Add CSV, Excel export capabilities

### Code Organization
- **UI components** are fully modular and reusable
- **Data layer** is abstracted through controller interface  
- **Models** can be used independently for other Qt applications
- **Delegates** provide examples for complex cell rendering

## Theming and Customization

The application uses a CSS-based theming system that allows easy customization of colors, fonts, and styling without modifying the source code.

### Theme Files

- **`styles.css`**: Default light theme with professional appearance
- **`dark_theme.css`**: Example dark theme for low-light environments
- **Custom themes**: Create your own CSS files following the same structure

### Key Customizable Elements

**Colors and Backgrounds:**
- Main window and content backgrounds
- Table cell colors and alternating row colors
- Selection and hover colors
- Required column highlighting (yellow background)
- Disabled cell visualization (gray with diagonal lines)
- Representation header colors (blue header sections)

**Typography:**
- Font sizes for all UI elements
- Font weights (bold, italic) for headers and labels
- Text colors for different states (normal, disabled, selected)

**Layout and Spacing:**
- Button sizes and padding
- Table cell padding and margins
- Border styles and colors
- Scroll bar appearance

### Switching Themes

To switch themes, modify the `load_stylesheet()` call in `ui/styles.py`:

```python
# Default light theme
css_file_path = project_root / "styles.css"

# Dark theme
css_file_path = project_root / "dark_theme.css"

# Custom theme
css_file_path = project_root / "my_custom_theme.css"
```

### Creating Custom Themes

1. **Copy existing theme**: Start with `styles.css` or `dark_theme.css`
2. **Modify colors**: Update color values in the CSS comments section
3. **Test changes**: Colors update immediately when restarting the application
4. **Key color variables** to customize:
   ```css
   /* Primary interface colors */
   background-color: #f5f5f5;    /* Main background */
   color: #333333;               /* Primary text */
   
   /* Required column colors */
   background-color: #fff8dc;    /* Required field background */
   border: 1px solid #ffd700;    /* Required field border */
   
   /* Representation headers */
   background-color: #6478b4;    /* Header section background */
   color: #ffffff;               /* Header text color */
   ```

### Theme Structure

The CSS file is organized into logical sections:
- **Main Application**: Window and general styling
- **Table Views**: Data table appearance and behavior  
- **Headers**: Column and section header styling
- **Required Columns**: Special highlighting for mandatory fields
- **Disabled Cells**: Styling for non-applicable data cells
- **Representation Headers**: Nested table section headers
- **UI Components**: Buttons, labels, and controls
- **Interactive Elements**: Hover effects and selections

### Advanced Customization

For complex styling needs, you can:
- **Modify delegate painting**: Update colors in `ui/styles.py` ThemeColors class
- **Add new CSS classes**: Extend the stylesheet with new selectors
- **Dynamic theming**: Implement theme switching in the application menu
- **Per-user themes**: Store theme preferences in user settings

This application serves as both a functional tool and a comprehensive example of advanced Qt table view implementation with nested data structures.
</thinking>

<edits>

<old_text line=219>
This application serves as both a functional tool and a comprehensive example of advanced Qt table view implementation with nested data structures.