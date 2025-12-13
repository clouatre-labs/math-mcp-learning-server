# Usage Examples

## Available Tools

### calculate
Safely evaluate mathematical expressions with support for basic operations and math functions.

**Parameters:**
- `expression` (string, required, max 500 chars): Mathematical expression to evaluate

**Supported operations:** +, -, *, /, **, ()  
**Supported functions:** sin, cos, tan, log, sqrt, abs, pow

**Examples:**
```
"2 + 3 * 4" → 14.0
"sqrt(16)" → 4.0
"sin(3.14159/2)" → 1.0
"pow(2, 3)" → 8.0
```

### statistics
Perform statistical calculations on a list of numbers.

**Parameters:**
- `numbers` (array of floats, required, max 10000 elements): List of numbers to analyze
- `operation` (string, required): Statistical operation to perform

**Available operations:** mean, median, mode, std_dev, variance

**Examples:**
```
numbers=[85, 92, 78, 96, 88], operation="mean" → 87.8
numbers=[1, 2, 3, 4, 5], operation="median" → 3.0
numbers=[1, 1, 2, 3], operation="mode" → 1.0
```

### compound_interest
Calculate compound interest for investments.

**Parameters:**
- `principal` (float, required): Initial investment amount
- `rate` (float, required): Annual interest rate as decimal (e.g., 0.045 for 4.5%)
- `time` (float, required): Time period in years
- `compounds_per_year` (integer, optional, default: 1): Compounding frequency

**Formula:** A = P(1 + r/n)^(nt)

**Example:**
```
principal=5000, rate=0.045, time=10, compounds_per_year=12
→ Final: $7814.17, Interest: $2814.17
```

### convert_units
Convert between different units of measurement.

**Parameters:**
- `value` (float, required): Value to convert
- `from_unit` (string, required): Source unit
- `to_unit` (string, required): Target unit
- `unit_type` (string, required): Type of conversion

**Supported unit types:**
- **temperature:** c, f, k (Celsius, Fahrenheit, Kelvin)
- **length:** mm, cm, m, km, in, ft, yd, mi
- **weight:** g, kg, oz, lb

**Examples:**
```
value=25, from_unit="c", to_unit="f", unit_type="temperature" → 77.0 f
value=5, from_unit="mi", to_unit="km", unit_type="length" → 8.047 km
value=1, from_unit="kg", to_unit="lb", unit_type="weight" → 2.205 lb
```

### save_calculation
Save calculation to persistent workspace (survives server restarts).

**Parameters:**
- `name` (string, required, max 50 chars): Variable name (alphanumeric, underscore, hyphen only)
- `expression` (string, required, max 500 chars): Mathematical expression
- `result` (float, required): Calculated result

**Example:**
```
name="portfolio_return", expression="10000 * 1.07^5", result=14025.52
→ Saved successfully
```

### load_variable
Load previously saved calculation from workspace.

**Parameters:**
- `name` (string, required): Variable name to load

**Example:**
```
name="portfolio_return"
→ Returns: expression="10000 * 1.07^5", result=14025.52, timestamp
```

### plot_function
Generate mathematical function plots (requires matplotlib).

**Parameters:**
- `expression` (string, required, max 500 chars): Function to plot (use `x` as variable)
- `x_range` (tuple, required): (min, max) for x-axis
- `num_points` (integer, optional, default: 100, range: 2-10000): Number of points to plot

**Examples:**
```
expression="x**2", x_range=(-5, 5) → Parabola plot
expression="sin(x)", x_range=(-3.14, 3.14) → Sine wave plot
expression="log(x)", x_range=(0.1, 10) → Logarithm plot
```

### create_histogram
Create statistical histogram (requires matplotlib).

**Parameters:**
- `data` (array of floats, required, max 10000 elements): Numerical values
- `bins` (integer, optional, default: 20): Number of histogram bins
- `title` (string, optional, max 100 chars): Chart title

**Returns:** PNG image with mean and median lines

**Example:**
```
data=[1, 2, 2, 3, 3, 3, 4, 4, 5], bins=5, title="Score Distribution"
```

### plot_line_chart
Create line chart from data points (requires matplotlib).

**Parameters:**
- `x_data` (array of floats, required, max 10000 elements): X-axis values
- `y_data` (array of floats, required, max 10000 elements): Y-axis values
- `title` (string, optional, max 100 chars): Chart title
- `x_label` (string, optional, max 100 chars): X-axis label
- `y_label` (string, optional, max 100 chars): Y-axis label
- `color` (string, optional, max 100 chars): Line color (name or hex)
- `show_grid` (boolean, optional, default: true): Display grid lines

**Example:**
```
x_data=[1, 2, 3, 4], y_data=[1, 4, 9, 16], title="Squares", color="blue"
```

### plot_scatter_chart
Create scatter plot for correlation analysis (requires matplotlib).

**Parameters:**
- `x_data` (array of floats, required, max 10000 elements): X-axis values
- `y_data` (array of floats, required, max 10000 elements): Y-axis values
- `title` (string, optional, max 100 chars): Chart title
- `x_label` (string, optional, max 100 chars): X-axis label
- `y_label` (string, optional, max 100 chars): Y-axis label
- `color` (string, optional, max 100 chars): Point color
- `point_size` (integer, optional, default: 50): Size of points

**Example:**
```
x_data=[1, 2, 3, 4], y_data=[2, 4, 5, 8], title="Correlation Study"
```

### plot_box_plot
Create box plot for distribution comparison (requires matplotlib).

**Parameters:**
- `data_groups` (array of arrays, required, max 100 groups): Data groups to compare
- `group_labels` (array of strings, optional): Labels for each group
- `title` (string, optional, max 100 chars): Chart title
- `y_label` (string, optional, max 100 chars): Y-axis label
- `color` (string, optional, max 100 chars): Box color

**Example:**
```
data_groups=[[1,2,3,4], [2,3,4,5], [3,4,5,6]], group_labels=["A", "B", "C"]
```

### plot_financial_line
Generate synthetic financial price data with trends (requires matplotlib).

**Parameters:**
- `days` (integer, optional, default: 30, range: 2-1000): Number of days
- `trend` (string, optional, default: "bullish"): Market trend
- `start_price` (float, optional, default: 100.0): Starting price
- `color` (string, optional, max 100 chars): Line color

**Available trends:** bullish, bearish, volatile

**Note:** Generates synthetic data for educational purposes only, not real market data.

**Example:**
```
days=60, trend="bullish", start_price=150.0, color="green"
```

### matrix_multiply
Multiply two matrices using NumPy (requires `[scientific]` extra).

**Parameters:**
- `matrix_a` (array of arrays, required): First matrix
- `matrix_b` (array of arrays, required): Second matrix

**Examples:**
```
matrix_a=[[1, 2], [3, 4]], matrix_b=[[5, 6], [7, 8]]
→ [[19 22]
   [43 50]]

matrix_a=[[1, 2, 3], [4, 5, 6]], matrix_b=[[7, 8], [9, 10], [11, 12]]
→ [[58  64]
   [139 154]]

matrix_a=[[1, 2], [3, 4]], matrix_b=[[1, 0], [0, 1]]
→ [[1 2]
   [3 4]]  (identity property)
```

**Error handling:**
```
matrix_a=[[1, 2], [3, 4]], matrix_b=[[1, 2, 3]]
→ Error: Incompatible matrix dimensions for multiplication
```

### matrix_transpose
Transpose a matrix (swap rows and columns).

**Parameters:**
- `matrix` (array of arrays, required): Matrix to transpose

**Examples:**
```
matrix=[[1, 2, 3], [4, 5, 6]]
→ [[1 4]
   [2 5]
   [3 6]]

matrix=[[1, 2], [3, 4]]
→ [[1 3]
   [2 4]]

matrix=[[1, 2, 3, 4]]
→ [[1]
   [2]
   [3]
   [4]]
```

### matrix_determinant
Calculate determinant of a square matrix.

**Parameters:**
- `matrix` (array of arrays, required): Square matrix

**Examples:**
```
matrix=[[4, 6], [3, 8]]
→ 14.0

matrix=[[1, 2, 3], [0, 1, 4], [5, 6, 0]]
→ 1.0

matrix=[[1, 2], [2, 4]]
→ 0.0 (singular matrix)
```

**Error handling:**
```
matrix=[[1, 2, 3], [4, 5, 6]]
→ Error: Matrix must be square
```

### matrix_inverse
Compute the inverse of a square matrix.

**Parameters:**
- `matrix` (array of arrays, required): Square matrix to invert

**Examples:**
```
matrix=[[4, 7], [2, 6]]
→ [[ 0.6  -0.7 ]
   [-0.2   0.4 ]]

matrix=[[1, 0], [0, 1]]
→ [[1. 0.]
   [0. 1.]]  (identity inverse)
```

**Error handling:**
```
matrix=[[1, 2], [2, 4]]
→ Error: Matrix is singular and cannot be inverted

matrix=[[1, 2, 3], [4, 5, 6]]
→ Error: Matrix must be square
```

### matrix_eigenvalues
Calculate eigenvalues of a square matrix.

**Parameters:**
- `matrix` (array of arrays, required): Square matrix

**Examples:**
```
matrix=[[4, 2], [1, 3]]
→ [5.0, 2.0]

matrix=[[3, 0, 0], [0, 5, 0], [0, 0, 7]]
→ [3.0, 5.0, 7.0]  (diagonal elements)

matrix=[[1, 0, 0], [0, 1, 0], [0, 0, 1]]
→ [1.0, 1.0, 1.0]  (identity matrix)
```

**Note:** Output may include complex eigenvalues for some matrices.

## Available Resources

### math://test
Simple test resource for verifying MCP connectivity.

**Returns:** Success message confirming resource access is working.

**Example:**
```
math://test
→ "Test resource working successfully!"
```

### math://constants/{constant}
Get mathematical constants with descriptions.

**Available constants:**
- `pi` - Ratio of circle's circumference to diameter (3.14159...)
- `e` - Euler's number, base of natural logarithm (2.71828...)
- `golden_ratio` - Golden ratio φ (1.61803...)
- `euler_gamma` - Euler-Mascheroni constant γ (0.57721...)
- `sqrt2` - Square root of 2 (1.41421...)
- `sqrt3` - Square root of 3 (1.73205...)

**Example:**
```
math://constants/pi
→ Returns: value and description
```

### math://functions
List all available mathematical functions with syntax and examples.

**Returns:** Complete reference including:
- Function signatures
- Parameter descriptions
- Usage examples
- Common patterns

### math://workspace
Get persistent calculation workspace summary.

**Returns:**
- All saved variables with expressions and results
- Total calculation count
- Last access timestamp

### math://history
Get chronological calculation history from workspace.

**Returns:** Last 10 calculations with timestamps (most recent first)

## Available Prompts

### math_tutor
Generate a math tutoring prompt for explaining concepts.

**Arguments:**
- `topic` (string, required): Mathematical topic to explain
- `level` (string, optional, default: "intermediate"): Difficulty level (beginner, intermediate, advanced)
- `include_examples` (boolean, optional, default: true): Include worked examples

**Example:**
```
topic="derivatives", level="beginner", include_examples=true
→ Returns structured teaching prompt
```

### formula_explainer
Generate a prompt for explaining mathematical formulas.

**Arguments:**
- `formula` (string, required): Mathematical formula to explain
- `context` (string, optional, default: "general mathematics"): Mathematical context

**Example:**
```
formula="A = πr²", context="geometry"
→ Returns detailed formula breakdown
```
