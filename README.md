# Korea Investment Data Analyzer

An interactive web application built with Dash and Plotly for analyzing and visualizing Korean investment data. The application provides both raw and accumulated views of market data with customizable date ranges and interactive charts.

## Features

- Interactive dual-axis charts showing market index and trading volumes
- Raw and accumulated data views
- Customizable date range selection with quick presets
- Bootstrap-themed responsive interface
- Range slider for easy timeframe navigation
- Detailed tooltips and hover information
- Supports multiple data series:
  - Market Index (지수)
  - Foreign Investors (외국인)
  - Individual Investors (개인)
  - Institutional Investors (기관종합)

## Requirements

- Python 3.8+
- pip (Python package installer)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd data_analyzer
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows
   python -m venv .venv
   .\.venv\Scripts\activate

   # Linux/macOS
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Data Setup

1. Place your Excel data file in the `data/` directory
2. The expected filename format is: `시간별 일별동향_YYYYMMDD_HHMMSS.xls`
3. Ensure the Excel file contains the following columns:
   - 날짜 (Date)
   - 지수 (Index)
   - 외국인 (Foreign Investors)
   - 개인 (Individual Investors)
   - 기관종합 (Institutional Investors)

## Running the Application

1. Make sure your virtual environment is activated
2. Run the application:
   ```bash
   python data_analyzer.py
   ```
3. Open your web browser and navigate to:
   ```
   http://127.0.0.1:8050
   ```

## Usage

### Date Range Selection

- Use the dropdown menu for quick date range presets:
  - 전체 기간 (All Time)
  - 최근 7일 (Last 7 days)
  - 최근 30일 (Last 30 days)
  - 최근 90일 (Last 90 days)
  - 최근 1-5년 (Last 1-5 years)
  - 최근 10년 (Last 10 years)
- Alternatively, use the date pickers for custom date ranges

### Charts

1. Raw Data View (상단 차트):
   - Shows the original data without accumulation
   - Market index on left axis
   - Trading volumes on right axis

2. Accumulated View (하단 차트):
   - Shows cumulative trading volumes
   - Market index remains as raw data for reference
   - Accumulated trading volumes on right axis

### Interactive Features

- Hover over data points for detailed information
- Use the range slider below each chart to zoom
- Click legend items to show/hide series
- Double-click legend items to isolate a series

## Project Structure

```
data_analyzer/
├── data/                      # Data directory for Excel files
├── .venv/                     # Virtual environment (created during setup)
├── data_analyzer.py          # Main application file
├── pyproject.toml            # Project metadata and dependencies
├── README.md                 # This documentation
└── requirements.txt          # Package dependencies
```

## Development

For development purposes:
- The application runs in debug mode by default
- Hot reloading is enabled for code changes
- Bind address is set to localhost (127.0.0.1) for security

## Troubleshooting

1. If the Excel file is not found:
   - Check that the file exists in the `data/` directory
   - Verify the filename matches the expected format

2. If the data doesn't load:
   - Ensure the Excel file has the required columns
   - Check that the date format in the Excel file is correct

3. If the application doesn't start:
   - Verify that all dependencies are installed
   - Check that the virtual environment is activated
   - Ensure port 8050 is not in use by another application
