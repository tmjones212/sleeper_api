import ast
import os
import csv
from typing import Dict, List, Set, Tuple
import pandas as pd
from graphviz import Digraph
import json

class CodeAnalyzer:
    def __init__(self):
        self.class_info: Dict[str, Dict] = {}
        self.function_calls: Dict[str, Set[str]] = {}
        self.file_info: Dict[str, List[Tuple[str, str, Set[str], str]]] = {}
        
    def analyze_file(self, file_path: str) -> None:
        """Analyze a Python file and extract class/function information."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                tree = ast.parse(file.read())
            
            self.file_info[file_path] = []
            
            # Find all classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._process_class(node, file_path)
                elif isinstance(node, ast.FunctionDef):
                    self._process_function(node, None, file_path)  # Functions not in classes
                    
        except Exception as e:
            print(f"Error analyzing {file_path}: {str(e)}")
    
    def _process_class(self, class_node: ast.ClassDef, file_path: str) -> None:
        """Process a class node and extract its methods."""
        class_name = class_node.name
        
        # Get class description from docstring
        description = ast.get_docstring(class_node) or ""
        description = " ".join(description.split())
        
        # Store class info
        self.file_info[file_path].append((None, class_name, set(), description))
        
        for node in ast.walk(class_node):
            if isinstance(node, ast.FunctionDef):
                self._process_function(node, class_name, file_path)
    
    def _process_function(self, func_node: ast.FunctionDef, class_name: str = None, file_path: str = None) -> None:
        """Process a function node and extract its calls."""
        func_name = func_node.name
        full_func_name = f"{class_name}.{func_name}" if class_name else func_name
            
        # Get function description from docstring
        description = ast.get_docstring(func_node) or ""
        description = " ".join(description.split())
            
        # Find all function calls within this function
        calls = set()
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.function_calls or any(
                        info[1] == node.func.id for infos in self.file_info.values() 
                        for info in infos):
                        calls.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in self.function_calls or any(
                        info[1] == node.func.attr for infos in self.file_info.values() 
                        for info in infos):
                        calls.add(node.func.attr)
        
        self.function_calls[full_func_name] = calls
        self.file_info[file_path].append((class_name, func_name, calls, description))

    def export_to_obsidian(self, output_dir: str = "code_notes") -> None:
        """Export the analysis results as Obsidian markdown files."""
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Create a reverse mapping of function calls
        called_by = {}
        for func, calls in self.function_calls.items():
            for called_func in calls:
                if called_func not in called_by:
                    called_by[called_func] = set()
                called_by[called_func].add(func)

        # Create index file
        with open(os.path.join(output_dir, "Code Structure.md"), 'w', encoding='utf-8') as f:
            f.write("# Code Structure\n\n")
            
            # Group by file
            for file_path in sorted(self.file_info.keys()):
                f.write(f"## {os.path.basename(file_path)}\n\n")
                
                # List classes
                classes = {item[1] for item in self.file_info[file_path] if item[0] is None}
                if classes:
                    f.write("### Classes\n\n")
                    for class_name in sorted(classes):
                        f.write(f"- [[{class_name}]]\n")
                    f.write("\n")
                
                # List standalone functions
                functions = {item[1] for item in self.file_info[file_path] if item[0] is None and item[1] not in classes}
                if functions:
                    f.write("### Functions\n\n")
                    for func_name in sorted(functions):
                        f.write(f"- [[{func_name}]]\n")
                    f.write("\n")

        # Create individual notes for each class and function
        for file_path, items in self.file_info.items():
            for class_name, name, calls, description in items:
                # Create the note filename
                note_name = f"{class_name}.{name}" if class_name else name
                note_path = os.path.join(output_dir, f"{note_name}.md")
                
                with open(note_path, 'w', encoding='utf-8') as f:
                    # Add YAML frontmatter with description
                    if description:
                        f.write("---\n")
                        f.write(f"description: {description}\n")
                        f.write("---\n\n")
                    
                    # Title
                    f.write(f"# {name}\n\n")
                    
                    # Metadata
                    f.write(f"**File:** {os.path.basename(file_path)}\n")
                    if class_name:
                        f.write(f"**Class:** [[{class_name}]]\n")
                    f.write("\n")
                    
                    # Description
                    if description:
                        f.write("## Description\n\n")
                        f.write(f"{description}\n\n")
                    
                    # Function calls
                    if calls:
                        f.write("## Calls\n\n")
                        for called_func in sorted(calls):
                            f.write(f"- [[{called_func}]]\n")
                        f.write("\n")
                    
                    # Called by
                    if name in called_by and called_by[name]:
                        f.write("## Called By\n\n")
                        for caller in sorted(called_by[name]):
                            f.write(f"- [[{caller}]]\n")
                        f.write("\n")

def analyze_directory(directory: str) -> None:
    """Analyze Python files in a directory (not including subdirectories)."""
    analyzer = CodeAnalyzer()
    
    # Only look at files in the specified directory, not subdirectories
    for file in os.listdir(directory):
        if file.endswith('.py'):
            file_path = os.path.join(directory, file)
            print(f"Analyzing: {file_path}")
            analyzer.analyze_file(file_path)
    
    analyzer.export_to_obsidian()
    print("\nAnalysis complete! Results saved to code_notes/")

def create_flow_diagram(csv_file="code_structure.csv", output_file="code_flow"):
    # Read the CSV
    df = pd.read_csv(csv_file)
    
    # Convert data to a format suitable for D3.js
    nodes = []
    links = []
    node_map = {}  # To keep track of node indices
    
    # Create nodes
    index = 0
    for _, row in df.iterrows():
        # Create node data
        node_data = {
            'id': index,
            'name': row['Function'],
            'file': row['File'],
            'class': row['Class'] if pd.notna(row['Class']) else '',
            'description': row['Description'] if pd.notna(row['Description']) else '',
            'type': 'class' if pd.notna(row['Class']) else 'function'
        }
        
        # Create unique identifier
        node_id = f"{row['Class']}.{row['Function']}" if pd.notna(row['Class']) else row['Function']
        node_map[node_id] = index
        nodes.append(node_data)
        index += 1
    
    # Create links
    for _, row in df.iterrows():
        source_id = f"{row['Class']}.{row['Function']}" if pd.notna(row['Class']) else row['Function']
        if pd.notna(row['Calls']) and row['Calls']:
            for target in row['Calls'].split('|'):
                # Find the full name of the target
                target_full = None
                for _, target_row in df.iterrows():
                    if target_row['Function'] == target:
                        target_full = f"{target_row['Class']}.{target}" if pd.notna(target_row['Class']) else target
                        break
                
                if target_full and target_full in node_map:
                    links.append({
                        'source': node_map[source_id],
                        'target': node_map[target_full]
                    })
    
    # Create the HTML file with embedded data
    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Code Structure Visualization</title>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            body { margin: 0; font-family: Arial, sans-serif; }
            #container { display: flex; height: 100vh; }
            #sidebar { 
                width: 400px; 
                padding: 20px; 
                background: #f5f5f5;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
            }
            #graph { flex-grow: 1; }
            .node { cursor: pointer; }
            .node.highlighted { stroke: #ff0000; stroke-width: 2px; }
            .link { stroke: #999; stroke-opacity: 0.6; }
            .link.highlighted { stroke: #ff0000; stroke-opacity: 1; }
            .filter-section { margin-bottom: 20px; }
            .filter-section h3 { margin: 0 0 10px 0; }
            select { width: 100%; margin-bottom: 10px; }
            
            /* Table styles */
            .functions-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
                flex-grow: 1;
                overflow-y: auto;
            }
            .functions-table th, .functions-table td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            .functions-table tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .functions-table tr:hover {
                background-color: #f0f0f0;
                cursor: pointer;
            }
            .functions-table th {
                background-color: #4CAF50;
                color: white;
            }
            .selected-row {
                background-color: #e0e0e0 !important;
            }
        </style>
    </head>
    <body>
        <div id="container">
            <div id="sidebar">
                <div class="filter-section">
                    <h3>File Selection</h3>
                    <select id="fileFilter">
                        <option value="">Select a File</option>
                    </select>
                </div>
                <div class="table-container">
                    <h3>Functions</h3>
                    <table class="functions-table">
                        <thead>
                            <tr>
                                <th>Function</th>
                                <th>Class</th>
                            </tr>
                        </thead>
                        <tbody id="functionsTableBody">
                        </tbody>
                    </table>
                </div>
            </div>
            <div id="graph"></div>
        </div>
        <script>
        // Embed the data directly in the HTML
        const graphData = {
            nodes: ''' + json.dumps(nodes) + ''',
            links: ''' + json.dumps(links) + '''
        };

        // Set up the visualization
        const width = window.innerWidth - 400;
        const height = window.innerHeight;

        const svg = d3.select("#graph")
            .append("svg")
            .attr("width", width)
            .attr("height", height);

        // Create the force simulation with better spacing
        const simulation = d3.forceSimulation(graphData.nodes)
            .force("link", d3.forceLink(graphData.links)
                .id(d => d.id)
                .distance(150)  // Increased distance between nodes
            )
            .force("charge", d3.forceManyBody()
                .strength(-1000)  // Stronger repulsion
                .distanceMax(500)  // Limit the repulsion range
            )
            .force("collide", d3.forceCollide()
                .radius(50)  // Prevent node overlap
                .strength(1)
            )
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("x", d3.forceX(width / 2).strength(0.1))
            .force("y", d3.forceY(height / 2).strength(0.1));

        // Draw the links with curves
        const link = svg.append("g")
            .selectAll("path")  // Changed from line to path
            .data(graphData.links)
            .join("path")  // Using paths instead of lines
            .attr("class", "link")
            .attr("stroke", "#999")
            .attr("stroke-width", 1.5)
            .attr("fill", "none")
            .attr("marker-end", "url(#arrowhead)");  // Add arrowheads

        // Add arrowhead marker
        svg.append("defs").selectAll("marker")
            .data(["arrowhead"])
            .join("marker")
            .attr("id", "arrowhead")
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 20)  // Position of the arrowhead
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", "#999");

        // Draw the nodes with larger radius
        const node = svg.append("g")
            .selectAll("circle")
            .data(graphData.nodes)
            .join("circle")
            .attr("class", "node")
            .attr("r", 12)  // Larger radius
            .attr("fill", d => d.type === 'class' ? "#69b3a2" : "#404080")
            .attr("stroke", "#fff")
            .attr("stroke-width", 2);

        // Add labels with background
        const label = svg.append("g")
            .selectAll("g")
            .data(graphData.nodes)
            .join("g");

        // Add label background
        label.append("rect")
            .attr("rx", 5)
            .attr("ry", 5)
            .attr("fill", "white")
            .attr("opacity", 0.8);

        // Add label text
        const labelText = label.append("text")
            .attr("dx", 15)
            .attr("dy", ".35em")
            .text(d => d.name)
            .each(function() {
                const bbox = this.getBBox();
                const parent = this.parentNode;
                const rect = parent.querySelector("rect");
                rect.setAttribute("x", bbox.x - 2);
                rect.setAttribute("y", bbox.y - 2);
                rect.setAttribute("width", bbox.width + 4);
                rect.setAttribute("height", bbox.height + 4);
            });

        // Update tick function for curved links
        simulation.on("tick", () => {
            link.attr("d", d => {
                const dx = d.target.x - d.source.x;
                const dy = d.target.y - d.source.y;
                const dr = Math.sqrt(dx * dx + dy * dy);
                return `M${d.source.x},${d.source.y}A${dr},${dr} 0 0,1 ${d.target.x},${d.target.y}`;
            });

            node
                .attr("cx", d => d.x = Math.max(20, Math.min(width - 20, d.x)))
                .attr("cy", d => d.y = Math.max(20, Math.min(height - 20, d.y)));

            label
                .attr("transform", d => `translate(${d.x},${d.y})`);
        });

        // Set up the file filter
        const files = [...new Set(graphData.nodes.map(n => n.file))];
        d3.select("#fileFilter")
            .selectAll("option")
            .data(files)
            .enter()
            .append("option")
            .text(d => d);

        // Update table based on file selection
        function updateFunctionsTable() {
            const selectedFile = d3.select("#fileFilter").property("value");
            const tbody = d3.select("#functionsTableBody");
            
            // Clear existing rows
            tbody.html("");
            
            // Filter nodes for selected file
            const fileNodes = graphData.nodes.filter(n => n.file === selectedFile);
            
            // Create table rows
            const rows = tbody.selectAll("tr")
                .data(fileNodes)
                .enter()
                .append("tr")
                .on("click", function(event, d) {
                    // Remove previous selection
                    tbody.selectAll("tr").classed("selected-row", false);
                    // Highlight selected row
                    d3.select(this).classed("selected-row", true);
                    
                    // Find connected nodes
                    const connectedNodes = findConnectedNodes(d.id);
                    
                    // Update visibility
                    node.style("display", n => connectedNodes.has(n.id) ? "block" : "none");
                    label.style("display", n => connectedNodes.has(n.id) ? "block" : "none");
                    link.style("display", l => 
                        connectedNodes.has(l.source.id) && connectedNodes.has(l.target.id) 
                            ? "block" : "none");
                });
            
            rows.append("td").text(d => d.name);
            rows.append("td").text(d => d.class || "");
        }

        // Add event listener for file filter
        d3.select("#fileFilter").on("change", updateFunctionsTable);

        // Add zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => {
                svg.selectAll("g").attr("transform", event.transform);
            });

        svg.call(zoom);

        // Add drag behavior
        node.call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));

        function dragstarted(event) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }

        function dragged(event) {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }

        function dragended(event) {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }
        </script>
    </body>
    </html>
    '''

    # Write the HTML file
    with open(f"{output_file}.html", 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\nVisualization created! Open {output_file}.html in your web browser.")

if __name__ == "__main__":
    directory = "."  # Current directory
    analyze_directory(directory)
    create_flow_diagram()
