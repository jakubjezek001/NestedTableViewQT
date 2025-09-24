# Drop-off Test Application

A simple `qtpy` GUI application that demonstrates drag and drop functionality with a table view and drop zones.

## Features

- **Table Widget**: Displays items from JSON data with drag support
- **Dual Drop Zones**: Two drop areas for different actions (also clickable buttons)
- **Multi-selection**: Select and drag multiple items simultaneously
- **Visual Feedback**: Selected items show brighter background, drag preview under cursor
- **Output Area**: Shows processing results with detailed item information
- **Custom Styling**: Uses prepared CSS theme

## File Structure

```
drop-off-test/
├── main.py              # Application entry point
├── controller.py        # Data management and preparation
├── data.json           # Sample data for table items
├── style.css           # Application styling
├── test_app.py         # Validation tests
└── ui/
    ├── __init__.py     # UI package initialization
    ├── ui.py           # Main window and application setup
    ├── view.py         # Main view with table and drop zones
    ├── model.py        # Table model with drag/drop support
    └── delegate.py     # Custom item rendering
```

## How to Run

1. Ensure you're in the `drop-off-test` directory
2. Run the application:
   ```bash
   python main.py
   ```

## How to Use

### Table View
- The left panel shows a table with item data loaded from `data.json`
- Items have attributes: Name, File Path, Product Name, Product Type, Version
- Items can be selected individually or multiple items at once
- **Selected items show 20% brighter background** for better visibility

### Drag and Drop
1. **Select Items**: Click to select single item, Ctrl+Click for multiple selection
2. **Drag**: Click and drag selected items from the table
   - **Semi-transparent preview** appears under cursor showing item count
3. **Drop**: Drop items onto either drop zone:
   - **Loading to Viewer** (top right)
   - **Adding to Timeline** (bottom right)

### Drop Zones
- **Button Interface**: Drop zones are clickable buttons with dashed borders
- **Click Action**: Select items in table, then click drop zone button to process
- **Drag & Drop**: Traditional drag and drop still works as before
- **Visual Feedback**: Zones highlight when dragging items over them
- **Batch Processing**: Multiple items are processed together
- **Action Results**: Each drop triggers its respective action

### Output Area
- Located at the bottom of the window
- **Clears automatically** before each new action
- Shows detailed information about processed items in structured format
- Each item displays: Name, Path, Product, Type, Version with action identifier

## Item Data Structure

Each item in `data.json` contains:
```json
{
    "name": "Item_Name_v001",
    "file_path": "C:/path/to/file.ext",
    "product_name": "Product Name",
    "product_type": "type",
    "version": "v001"
}
```

## Requirements

- Python 3.7+
- qtpy (Qt wrapper library)
- PySide6 or PyQt6 (via qtpy)

## Testing

Run the test suite to validate functionality:
```bash
python test_app.py
```

The test validates:
- JSON data integrity
- Controller functionality
- Model drag/drop support
- Module imports
- MIME data handling

## Output Format

When items are processed, the output area shows:
```
Item 1 (Loading to Viewer Action):
  Name: Character_Rig_v003
  Path: C:/Projects/Film_A/assets/characters/hero/rig/character_rig_v003.ma
  Product: Hero Character
  Type: rig
  Version: v003

Item 2 (Loading to Viewer Action):
  Name: Environment_Model_v012
  Path: C:/Projects/Film_A/assets/environments/forest/model/environment_model_v012.mb
  Product: Forest Environment
  Type: model
  Version: v012
```

## Usage Tips

- **Multiple Selection**: Use Ctrl+Click or Shift+Click for selecting multiple items
- **Two Ways to Process**: Either drag & drop OR select items and click drop zone buttons
- **Visual Feedback**: 
  - Selected items have brighter background in table
  - Drag preview shows item count under cursor
  - Drop zones change color when items are dragged over them
- **Batch Operations**: All selected items are processed when dropped/clicked
- **Clean Output**: Output area clears before each action for better readability

## Customization

- **Data**: Modify `data.json` to change table contents
- **Styling**: Edit `style.css` to customize appearance
- **Actions**: Extend drop zone actions in `view.py`
- **Columns**: Add/modify columns in `controller.py`
