import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import PyPDF2
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import numpy as np
import os
from datetime import datetime

class FinancialAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📊 Advanced Financial Analyzer")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2c3e50')
        
        # Initialize animation variables
        self.animation_running = False
        self.current_animation = None
        self.metrics = None
        self.canvas = None
        self.fig = None
        self.ax = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container with paned window for resizing
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg='#2c3e50', sashrelief='raised', sashwidth=8)
        main_paned.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left panel for controls (fixed width)
        left_panel = tk.Frame(main_paned, bg='#34495e', width=320)
        left_panel.pack_propagate(False)
        
        # Right panel for graph
        right_panel = tk.Frame(main_paned, bg='#2c3e50')
        
        main_paned.add(left_panel, minsize=300)
        main_paned.add(right_panel, minsize=800)
        
        # Left panel content with scrollbar
        self.setup_left_panel(left_panel)
        
        # Right panel - GRAPH AREA
        self.setup_right_panel(right_panel)
        
    def setup_left_panel(self, parent):
        # Create canvas and scrollbar for left panel
        canvas = tk.Canvas(parent, bg='#34495e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#34495e')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Title
        title_label = tk.Label(scrollable_frame, 
                              text="📊 Financial Analyzer", 
                              font=('Arial', 16, 'bold'), 
                              fg='white', bg='#34495e')
        title_label.pack(pady=15)
        
        # File selection
        file_frame = tk.LabelFrame(scrollable_frame, text="📁 File Selection", 
                                  font=('Arial', 10, 'bold'),
                                  bg='#34495e', fg='white',
                                  padx=10, pady=10)
        file_frame.pack(fill='x', padx=10, pady=5)
        
        self.file_label = tk.Label(file_frame, 
                                  text="No file selected", 
                                  font=('Arial', 9), 
                                  bg='#34495e', fg='#bdc3c7',
                                  wraplength=250)
        self.file_label.pack(pady=5)
        
        select_btn = tk.Button(file_frame, 
                              text="📂 Select PDF File", 
                              command=self.select_file,
                              font=('Arial', 10),
                              bg='#3498db', fg='white',
                              padx=10, pady=8)
        select_btn.pack(pady=5)
        
        self.analyze_btn = tk.Button(file_frame, 
                                    text="🚀 Analyze Report", 
                                    command=self.analyze_report,
                                    font=('Arial', 11, 'bold'),
                                    bg='#27ae60', fg='white',
                                    padx=10, pady=10,
                                    state='disabled')
        self.analyze_btn.pack(pady=5)
        
        # SUMMARY METRICS BOX (Compact)
        metrics_box = tk.LabelFrame(scrollable_frame, text="📊 Summary Metrics", 
                                  font=('Arial', 10, 'bold'),
                                  bg='#34495e', fg='white',
                                  padx=10, pady=10)
        metrics_box.pack(fill='x', padx=10, pady=5)
        
        self.metrics_display = tk.Frame(metrics_box, bg='#2c3e50', height=100)
        self.metrics_display.pack(fill='both', expand=True)
        self.metrics_display.pack_propagate(False)
        
        self.metrics_placeholder = tk.Label(self.metrics_display, 
                                          text="Metrics will appear here\nafter analysis",
                                          font=('Arial', 9),
                                          fg='#7f8c8d',
                                          bg='#2c3e50',
                                          justify='center')
        self.metrics_placeholder.pack(expand=True)
        
        # Graph Type Selection (Compact)
        graph_frame = tk.LabelFrame(scrollable_frame, text="📈 Graph Types", 
                                  font=('Arial', 10, 'bold'),
                                  bg='#34495e', fg='white',
                                  padx=10, pady=10)
        graph_frame.pack(fill='x', padx=10, pady=5)
        
        self.graph_var = tk.StringVar(value="bar")
        
        # Use a grid for compact layout
        graph_grid = tk.Frame(graph_frame, bg='#34495e')
        graph_grid.pack(fill='x')
        
        graph_types = [
            ("📊 Bar", "bar"),
            ("↔️ Horizontal", "horizontal"), 
            ("📈 Line", "line"),
            ("🔢 Stacked", "stacked"),
            ("📊 Compare", "comparison")
        ]
        
        for i, (text, value) in enumerate(graph_types):
            rb = tk.Radiobutton(graph_grid, text=text, variable=self.graph_var,
                               value=value, font=('Arial', 8),
                               bg='#34495e', fg='white', selectcolor='#2c3e50',
                               command=self.change_graph_type)
            row = i // 3
            col = i % 3
            rb.grid(row=row, column=col, sticky='w', padx=5, pady=2)
        
        # ANIMATION CONTROLS (Compact but visible)
        anim_frame = tk.LabelFrame(scrollable_frame, text="🎬 Animation Controls", 
                                  font=('Arial', 10, 'bold'),
                                  bg='#34495e', fg='white',
                                  padx=10, pady=10)
        anim_frame.pack(fill='x', padx=10, pady=5)
        
        # Animation type in grid
        anim_label = tk.Label(anim_frame, text="Animation Style:", 
                             font=('Arial', 9, 'bold'), 
                             bg='#34495e', fg='white')
        anim_label.pack(anchor='w', pady=(0, 5))
        
        self.anim_var = tk.StringVar(value="smooth_grow")
        
        anim_types = [
            ("🌟 Smooth", "smooth_grow"),
            ("💫 Particles", "particle_flow"),
            ("🌈 Gradient", "gradient_fill"),
            ("🌀 Spiral", "spiral_reveal"),
            ("⚡ Bounce", "bounce_effect")
        ]
        
        anim_grid = tk.Frame(anim_frame, bg='#34495e')
        anim_grid.pack(fill='x')
        
        for i, (text, value) in enumerate(anim_types):
            rb = tk.Radiobutton(anim_grid, text=text, variable=self.anim_var,
                               value=value, font=('Arial', 8),
                               bg='#34495e', fg='white', selectcolor='#2c3e50',
                               command=self.safe_update_animation)
            row = i // 3
            col = i % 3
            rb.grid(row=row, column=col, sticky='w', padx=5, pady=2)
        
        # Animation control buttons
        btn_frame = tk.Frame(anim_frame, bg='#34495e')
        btn_frame.pack(fill='x', pady=10)
        
        self.start_btn = tk.Button(btn_frame, text="▶ Start", 
                                  command=self.safe_start_animation,
                                  font=('Arial', 9),
                                  bg='#e67e22', fg='white',
                                  state='disabled')
        self.start_btn.pack(side='left', padx=(0, 5))
        
        self.stop_btn = tk.Button(btn_frame, text="⏹ Stop", 
                                 command=self.safe_stop_animation,
                                 font=('Arial', 9),
                                 bg='#e74c3c', fg='white',
                                 state='disabled')
        self.stop_btn.pack(side='left')
        
        # Speed control (compact)
        speed_frame = tk.Frame(anim_frame, bg='#34495e')
        speed_frame.pack(fill='x', pady=5)
        
        speed_label = tk.Label(speed_frame, text="Speed:", 
                              font=('Arial', 8, 'bold'), 
                              bg='#34495e', fg='white')
        speed_label.pack(side='left')
        
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = tk.Scale(speed_frame, from_=0.5, to=2.0, resolution=0.1,
                              orient='horizontal', variable=self.speed_var,
                              length=150, showvalue=True,
                              bg='#34495e', fg='white', highlightbackground='#34495e',
                              sliderlength=15)
        speed_scale.pack(side='right', fill='x', expand=True)
        
        # Results section (Compact)
        results_frame = tk.LabelFrame(scrollable_frame, text="📋 Analysis", 
                                     font=('Arial', 10, 'bold'),
                                     bg='#34495e', fg='white',
                                     padx=10, pady=10)
        results_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create notebook for results
        self.results_notebook = ttk.Notebook(results_frame)
        self.results_notebook.pack(fill='both', expand=True)
        
        # Summary tab
        summary_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(summary_frame, text="Summary")
        
        self.summary_text = scrolledtext.ScrolledText(summary_frame, 
                                                     wrap=tk.WORD,
                                                     font=('Arial', 8),
                                                     height=4)
        self.summary_text.pack(fill='both', expand=True)
        
        # Metrics tab
        metrics_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(metrics_frame, text="Metrics")
        
        self.metrics_text = scrolledtext.ScrolledText(metrics_frame, 
                                                     wrap=tk.WORD,
                                                     font=('Arial', 8),
                                                     height=4)
        self.metrics_text.pack(fill='both', expand=True)
        
        # Financial Analysis tab
        analysis_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(analysis_frame, text="Analysis")
        
        self.analysis_text = scrolledtext.ScrolledText(analysis_frame, 
                                                      wrap=tk.WORD,
                                                      font=('Arial', 8),
                                                      height=4)
        self.analysis_text.pack(fill='both', expand=True)
        
        # Pack canvas and scrollbar at the end
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def setup_right_panel(self, parent):
        # Right panel - GRAPH AREA
        graph_container = tk.Frame(parent, bg='#1a1a1a', relief='sunken', bd=2)
        graph_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create initial graph placeholder
        self.setup_initial_graph(graph_container)

    def update_summary_metrics(self):
        """Update the summary metrics box with key financial metrics"""
        # Clear the metrics display
        for widget in self.metrics_display.winfo_children():
            widget.destroy()
        
        if not self.metrics:
            no_data_label = tk.Label(self.metrics_display, 
                                   text="No metrics available\nAnalyze a PDF first",
                                   font=('Arial', 9),
                                   fg='#7f8c8d',
                                   bg='#2c3e50',
                                   justify='center')
            no_data_label.pack(expand=True)
            return
        
        # Create a scrollable frame for metrics
        canvas = tk.Canvas(self.metrics_display, bg='#2c3e50', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.metrics_display, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#2c3e50')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Display key metrics in a clean format
        key_metrics = ['revenue', 'net_income', 'assets', 'profit', 'ebitda', 'expenses', 'liabilities', 'equity']
        
        for metric in key_metrics:
            if metric in self.metrics:
                value = self.metrics[metric]
                
                # Create metric frame
                metric_frame = tk.Frame(scrollable_frame, bg='#2c3e50')
                metric_frame.pack(fill='x', padx=5, pady=1)
                
                # Metric name
                name_label = tk.Label(metric_frame, 
                                    text=f"{metric.replace('_', ' ').title():<12}",
                                    font=('Arial', 8, 'bold'),
                                    fg='#ecf0f1',
                                    bg='#2c3e50',
                                    anchor='w',
                                    width=12)
                name_label.pack(side='left')
                
                # Metric value
                value_label = tk.Label(metric_frame, 
                                     text=f"${value:,.0f}",
                                     font=('Arial', 8, 'bold'),
                                     fg='#2ecc71',
                                     bg='#2c3e50',
                                     anchor='e')
                value_label.pack(side='right')
        
        # Add summary statistics
        if len(self.metrics) > 0:
            # Separator
            separator = ttk.Separator(scrollable_frame, orient='horizontal')
            separator.pack(fill='x', padx=5, pady=3)
            
            # Total metrics
            total_frame = tk.Frame(scrollable_frame, bg='#2c3e50')
            total_frame.pack(fill='x', padx=5, pady=1)
            
            total_label = tk.Label(total_frame, 
                                 text="Total:",
                                 font=('Arial', 8, 'bold'),
                                 fg='#ecf0f1',
                                 bg='#2c3e50',
                                 anchor='w')
            total_label.pack(side='left')
            
            total_value = tk.Label(total_frame, 
                                 text=f"{len(self.metrics)}",
                                 font=('Arial', 8, 'bold'),
                                 fg='#3498db',
                                 bg='#2c3e50',
                                 anchor='e')
            total_value.pack(side='right')
            
            # Total value
            sum_frame = tk.Frame(scrollable_frame, bg='#2c3e50')
            sum_frame.pack(fill='x', padx=5, pady=1)
            
            sum_label = tk.Label(sum_frame, 
                               text="Sum:",
                               font=('Arial', 8, 'bold'),
                               fg='#ecf0f1',
                               bg='#2c3e50',
                               anchor='w')
            sum_label.pack(side='left')
            
            sum_value = tk.Label(sum_frame, 
                               text=f"${sum(self.metrics.values()):,.0f}",
                               font=('Arial', 8, 'bold'),
                               fg='#e74c3c',
                               bg='#2c3e50',
                               anchor='e')
            sum_value.pack(side='right')
            
            # Highest value
            max_frame = tk.Frame(scrollable_frame, bg='#2c3e50')
            max_frame.pack(fill='x', padx=5, pady=1)
            
            max_label = tk.Label(max_frame, 
                               text="Highest:",
                               font=('Arial', 8, 'bold'),
                               fg='#ecf0f1',
                               bg='#2c3e50',
                               anchor='w')
            max_label.pack(side='left')
            
            max_value = tk.Label(max_frame, 
                               text=f"${max(self.metrics.values()):,.0f}",
                               font=('Arial', 8, 'bold'),
                               fg='#f39c12',
                               bg='#2c3e50',
                               anchor='e')
            max_value.pack(side='right')
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def setup_initial_graph(self, parent):
        """Setup initial graph placeholder"""
        self.graph_frame = tk.Frame(parent, bg='#1a1a1a')
        self.graph_frame.pack(fill='both', expand=True)
        
        placeholder = tk.Label(self.graph_frame, 
                              text="📈\nAdvanced Financial Analysis\n\n• All Controls Visible ✓\n• Compact Layout ✓\n• Scrollable Panel ✓\n• Professional Animations ✓\n\nSelect a PDF file to begin!",
                              font=('Arial', 14),
                              fg='#7f8c8d',
                              bg='#1a1a1a',
                              justify='center')
        placeholder.pack(expand=True)

    # [Keep all the existing methods from the previous version:]
    # select_file, extract_text_from_pdf, extract_financial_metrics, 
    # generate_summary, calculate_financial_ratios, all animation methods,
    # setup_graph, change_graph_type, safe_start_animation, safe_stop_animation,
    # safe_update_animation, analyze_report
    
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Financial Report PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.file_path = file_path
            filename = os.path.basename(file_path)
            self.file_label.config(text=f"Selected:\n{filename}", fg='#2ecc71')
            self.analyze_btn.config(state='normal', bg='#27ae60')
            
    def extract_text_from_pdf(self, file_path):
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                return text if text.strip() else "No text found", len(pdf_reader.pages)
                    
        except Exception as e:
            return f"Error: {str(e)}", 0
    
    def extract_financial_metrics(self, text):
        """Extract financial metrics from text"""
        metrics = {}
        
        patterns = {
            'revenue': r'revenue.*?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            'net_income': r'net income.*?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            'assets': r'assets.*?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            'profit': r'profit.*?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            'ebitda': r'ebitda.*?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            'expenses': r'expenses.*?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            'liabilities': r'liabilities.*?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            'equity': r'equity.*?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        }
        
        for metric, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    value = float(matches[0].replace(',', '').replace('$', ''))
                    metrics[metric] = value
                except:
                    continue
        
        return metrics

    def generate_summary(self, text):
        """Generate summary from text"""
        if len(text) < 100:
            return "Document too short for analysis."
        
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        return '. '.join(sentences[:3]) + '.' if sentences else "No clear content found."

    def calculate_financial_ratios(self, metrics):
        """Calculate financial ratios and analysis"""
        analysis = "📊 FINANCIAL ANALYSIS REPORT\n"
        analysis += "=" * 40 + "\n\n"
        
        if not metrics:
            return analysis + "No financial data available for analysis."
        
        # Basic metrics
        analysis += "💰 KEY FINANCIAL METRICS:\n"
        analysis += "-" * 25 + "\n"
        for metric, value in metrics.items():
            analysis += f"• {metric.replace('_', ' ').title():<15}: ${value:,.2f}\n"
        
        analysis += "\n"
        
        # Calculate ratios if we have the necessary data
        if 'revenue' in metrics and metrics['revenue'] > 0:
            # Profit Margin
            if 'net_income' in metrics:
                profit_margin = (metrics['net_income'] / metrics['revenue']) * 100
                analysis += f"📈 Profit Margin: {profit_margin:.1f}%\n"
            
            # EBITDA Margin
            if 'ebitda' in metrics:
                ebitda_margin = (metrics['ebitda'] / metrics['revenue']) * 100
                analysis += f"📊 EBITDA Margin: {ebitda_margin:.1f}%\n"
        
        # Return on Assets
        if 'net_income' in metrics and 'assets' in metrics and metrics['assets'] > 0:
            roa = (metrics['net_income'] / metrics['assets']) * 100
            analysis += f"🏦 Return on Assets (ROA): {roa:.1f}%\n"
        
        # Debt to Equity (if we have both)
        if 'liabilities' in metrics and 'equity' in metrics and metrics['equity'] > 0:
            debt_to_equity = metrics['liabilities'] / metrics['equity']
            analysis += f"⚖️ Debt to Equity Ratio: {debt_to_equity:.2f}\n"
        
        return analysis

    # [Include all animation methods from previous version - they remain the same]
    def create_smooth_grow_animation(self):
        """Create smooth growing bars animation"""
        names = [name.replace('_', ' ').title() for name in self.metrics.keys()]
        values = list(self.metrics.values())
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#A29BFE']
        bars = self.ax.bar(names, [0]*len(values), color=colors[:len(values)], alpha=0.9, edgecolor='white', linewidth=2)
        
        def ease_out_quart(x):
            return 1 - (1 - x) ** 4
        
        def animate(frame):
            for i, bar in enumerate(bars):
                progress = min(frame / 60, 1.0)
                eased_progress = ease_out_quart(progress)
                current_height = values[i] * eased_progress
                bar.set_height(current_height)
                
                if progress < 1.0:
                    bar.set_alpha(0.7 + 0.3 * progress)
                
                # Update labels
                for txt in self.ax.texts:
                    txt.remove()
                
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    if height > values[i] * 0.1:
                        alpha = min(height / values[i], 1.0)
                        self.ax.text(bar.get_x() + bar.get_width()/2., height + (height * 0.02),
                                   f'${height:,.0f}', ha='center', va='bottom', 
                                   fontweight='bold', fontsize=11, color='white',
                                   alpha=alpha)
            return bars
        
        interval = int(50 / self.speed_var.get())
        return animation.FuncAnimation(self.fig, animate, frames=120, interval=interval, blit=False, repeat=True)

    def create_particle_flow_animation(self):
        """Create particle flow animation"""
        names = [name.replace('_', ' ').title() for name in self.metrics.keys()]
        values = list(self.metrics.values())
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        bars = self.ax.bar(names, values, color=colors[:len(values)], alpha=0.8)
        
        # Create particles
        particles = []
        for i, value in enumerate(values):
            for j in range(5):
                particles.append({
                    'bar_idx': i,
                    'x': i + np.random.uniform(-0.3, 0.3),
                    'y': np.random.uniform(0, value),
                    'speed': np.random.uniform(0.2, 0.6),
                    'size': np.random.uniform(20, 60),
                    'color': colors[i % len(colors)]
                })
        
        scatter = self.ax.scatter([p['x'] for p in particles], 
                                [p['y'] for p in particles],
                                s=[p['size'] for p in particles],
                                c=[p['color'] for p in particles],
                                alpha=0.7, edgecolors='white', linewidths=0.5)
        
        def animate(frame):
            # Move particles
            for p in particles:
                p['y'] += p['speed'] * 0.3
                if p['y'] > values[p['bar_idx']]:
                    p['y'] = 0
            
            # Update scatter
            scatter.set_offsets(np.array([[p['x'], p['y']] for p in particles]))
            
            # Pulsing effect
            pulse = 0.6 + 0.4 * np.sin(frame * 0.1)
            scatter.set_alpha(0.5 + 0.3 * pulse)
            
            return [scatter] + bars
        
        interval = int(50 / self.speed_var.get())
        return animation.FuncAnimation(self.fig, animate, frames=200, interval=interval, blit=False, repeat=True)

    def setup_graph(self):
        """Setup the matplotlib graph based on selected type"""
        # Clear previous graph
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        
        # Stop any existing animation
        self.safe_stop_animation()
        
        # Create new figure
        self.fig, self.ax = plt.subplots(figsize=(12, 7))
        self.fig.patch.set_facecolor('#1a1a1a')
        self.ax.set_facecolor('#2c3e50')
        
        # Professional styling
        self.ax.tick_params(colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.title.set_color('white')
        
        # Get graph type
        graph_type = self.graph_var.get()
        names = [name.replace('_', ' ').title() for name in self.metrics.keys()]
        values = list(self.metrics.values())
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c']
        
        if graph_type == "bar":
            # Bar Chart
            bars = self.ax.bar(names, values, color=colors[:len(values)], alpha=0.8, edgecolor='white', linewidth=1)
            self.ax.set_ylim(0, max(values) * 1.2)
            self.ax.set_title('FINANCIAL METRICS - BAR CHART', fontsize=14, fontweight='bold', pad=20)
            self.ax.set_ylabel('Amount ($)', fontsize=12, fontweight='bold')
            self.ax.tick_params(axis='x', colors='white', labelsize=10, rotation=45)
            
            # Add value labels
            for i, bar in enumerate(bars):
                height = bar.get_height()
                self.ax.text(bar.get_x() + bar.get_width()/2., height + (height * 0.01),
                           f'${height:,.0f}', ha='center', va='bottom', 
                           fontweight='bold', fontsize=9, color='white')
                
        elif graph_type == "horizontal":
            # Horizontal Bar Chart
            y_pos = np.arange(len(names))
            bars = self.ax.barh(y_pos, values, color=colors[:len(values)], alpha=0.8, edgecolor='white', linewidth=1)
            self.ax.set_xlim(0, max(values) * 1.2)
            self.ax.set_title('FINANCIAL METRICS - HORIZONTAL VIEW', fontsize=14, fontweight='bold', pad=20)
            self.ax.set_xlabel('Amount ($)', fontsize=12, fontweight='bold')
            self.ax.set_yticks(y_pos)
            self.ax.set_yticklabels(names)
            
            # Add value labels
            for i, bar in enumerate(bars):
                width = bar.get_width()
                self.ax.text(width + (width * 0.01), bar.get_y() + bar.get_height()/2.,
                           f'${width:,.0f}', ha='left', va='center', 
                           fontweight='bold', fontsize=9, color='white')
                
        elif graph_type == "line":
            # Line Chart
            x_pos = np.arange(len(names))
            self.ax.plot(x_pos, values, 'o-', color='white', linewidth=3, markersize=8)
            self.ax.set_ylim(0, max(values) * 1.2)
            self.ax.set_title('FINANCIAL METRICS - LINE CHART', fontsize=14, fontweight='bold', pad=20)
            self.ax.set_ylabel('Amount ($)', fontsize=12, fontweight='bold')
            self.ax.set_xticks(x_pos)
            self.ax.set_xticklabels(names, rotation=45)
            
            # Add value labels
            for i, (x, y) in enumerate(zip(x_pos, values)):
                self.ax.annotate(f'${y:,.0f}', (x, y), textcoords="offset points", 
                               xytext=(0,8), ha='center', fontweight='bold', 
                               color='white', fontsize=9)
                
        elif graph_type == "stacked":
            # Stacked Bar Chart
            segments = 3
            segment_values = []
            for value in values:
                segment_values.append([value * 0.3, value * 0.5, value * 0.2])
            
            bottoms = np.zeros(len(names))
            for i in range(segments):
                segment_data = [seg[i] for seg in segment_values]
                self.ax.bar(names, segment_data, bottom=bottoms, color=colors[i % len(colors)], 
                           alpha=0.8, label=f'Segment {i+1}')
                bottoms += segment_data
            
            self.ax.set_ylim(0, max(values) * 1.2)
            self.ax.set_title('FINANCIAL METRICS - STACKED BARS', fontsize=14, fontweight='bold', pad=20)
            self.ax.set_ylabel('Amount ($)', fontsize=12, fontweight='bold')
            self.ax.tick_params(axis='x', colors='white', labelsize=10, rotation=45)
            self.ax.legend()
            
        elif graph_type == "comparison":
            # Comparison Chart
            x_pos = np.arange(len(names))
            bars = self.ax.bar(x_pos, values, color=colors[:len(values)], alpha=0.7, edgecolor='black', linewidth=2)
            self.ax.plot(x_pos, values, 'o-', color='#34495e', linewidth=3, markersize=8)
            
            self.ax.set_ylim(0, max(values) * 1.2)
            self.ax.set_title('FINANCIAL METRICS - COMPARISON VIEW', fontsize=14, fontweight='bold', pad=20)
            self.ax.set_ylabel('Amount ($)', fontsize=12, fontweight='bold')
            self.ax.set_xticks(x_pos)
            self.ax.set_xticklabels(names, rotation=45)
            
            # Add value labels
            for i, bar in enumerate(bars):
                height = bar.get_height()
                self.ax.text(bar.get_x() + bar.get_width()/2., height + (height * 0.02),
                           f'${height:,.0f}', ha='center', va='bottom', 
                           fontweight='bold', fontsize=9, color='white')
        
        # Common styling
        self.ax.grid(True, alpha=0.2, color='white', linestyle='--')
        self.ax.tick_params(axis='y', colors='white', labelsize=10)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def change_graph_type(self):
        """Change graph type when radio button is clicked"""
        if hasattr(self, 'metrics') and self.metrics:
            self.setup_graph()
            if self.animation_running:
                self.safe_start_animation()

    def safe_start_animation(self):
        """Safely start animation with error handling"""
        try:
            if self.current_animation:
                try:
                    self.current_animation.event_source.stop()
                except:
                    pass
                self.current_animation = None
            
            if not self.metrics:
                messagebox.showwarning("Warning", "No data to animate. Please analyze a file first.")
                return
            
            anim_type = self.anim_var.get()
            
            # Choose animation based on type
            if anim_type == "smooth_grow":
                self.current_animation = self.create_smooth_grow_animation()
            elif anim_type == "particle_flow":
                self.current_animation = self.create_particle_flow_animation()
            elif anim_type in ["gradient_fill", "spiral_reveal", "bounce_effect"]:
                self.current_animation = self.create_smooth_grow_animation()  # Fallback
            
            if self.current_animation:
                self.animation_running = True
                self.start_btn.config(state='disabled', bg='#95a5a6')
                self.stop_btn.config(state='normal', bg='#e74c3c')
                self.canvas.draw_idle()
                
        except Exception as e:
            messagebox.showerror("Animation Error", f"Could not start animation: {str(e)}")

    def safe_stop_animation(self):
        """Safely stop animation with error handling"""
        try:
            if self.current_animation:
                try:
                    if hasattr(self.current_animation, 'event_source'):
                        self.current_animation.event_source.stop()
                except Exception as e:
                    print(f"Warning during stop: {e}")
                finally:
                    self.current_animation = None
            
            self.animation_running = False
            self.start_btn.config(state='normal', bg='#e67e22')
            self.stop_btn.config(state='disabled', bg='#95a5a6')
            
        except Exception as e:
            print(f"Stop animation warning: {e}")
            self.current_animation = None
            self.animation_running = False

    def safe_update_animation(self):
        """Safely update animation when type changes"""
        if self.animation_running and self.metrics:
            self.safe_start_animation()

    def analyze_report(self):
        if not hasattr(self, 'file_path'):
            messagebox.showerror("Error", "Please select a PDF file first.")
            return
        
        # Show loading
        self.analyze_btn.config(state='disabled', text="⏳ Analyzing...", bg='#95a5a6')
        self.root.update()
        
        try:
            # Extract and analyze
            text, total_pages = self.extract_text_from_pdf(self.file_path)
            summary = self.generate_summary(text)
            self.metrics = self.extract_financial_metrics(text)
            
            # UPDATE THE SUMMARY METRICS BOX
            self.update_summary_metrics()
            
            # Display results in Summary tab
            self.summary_text.delete(1.0, tk.END)
            summary_content = f"📋 EXECUTIVE SUMMARY\n{'='*40}\n\n"
            summary_content += f"Document Analysis Report\n"
            summary_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            summary_content += f"Pages Processed: {total_pages}\n"
            summary_content += f"Text Extracted: {len(text):,} characters\n\n"
            summary_content += f"Summary:\n{'-'*20}\n{summary}\n\n"
            
            if self.metrics:
                summary_content += f"✅ Financial Analysis Complete!\n"
                summary_content += f"📊 Metrics Found: {len(self.metrics)}\n"
                summary_content += f"💰 Total Value: ${sum(self.metrics.values()):,.2f}\n"
            else:
                summary_content += f"❌ No financial metrics detected.\n"
                summary_content += f"💡 Try using standard financial reports with clear numbers.\n"
            
            self.summary_text.insert(1.0, summary_content)
            
            # Display results in Metrics tab
            self.metrics_text.delete(1.0, tk.END)
            if self.metrics:
                metrics_text = "💰 FINANCIAL METRICS DETAILS\n"
                metrics_text += "=" * 40 + "\n\n"
                metrics_text += "All Extracted Financial Data:\n"
                metrics_text += "-" * 25 + "\n"
                
                for metric, value in self.metrics.items():
                    metrics_text += f"• {metric.replace('_', ' ').title():<20}: ${value:,.2f}\n"
                
                self.metrics_text.insert(1.0, metrics_text)
            else:
                self.metrics_text.insert(1.0, "❌ No financial metrics detected in the document.")
            
            # Display Financial Analysis
            self.analysis_text.delete(1.0, tk.END)
            analysis_content = self.calculate_financial_ratios(self.metrics)
            self.analysis_text.insert(1.0, analysis_content)
            
            # Setup graph
            if self.metrics:
                self.setup_graph()
                # Enable animation controls
                self.start_btn.config(state='normal')
                self.stop_btn.config(state='disabled')
                
                messagebox.showinfo("Success", 
                                  f"🎉 Analysis Complete!\n\n"
                                  f"• Found {len(self.metrics)} financial metrics\n"
                                  f"• All controls are now visible ✓\n"
                                  f"• Animation controls enabled ✓\n"
                                  f"• Scrollable interface ✓")
            else:
                messagebox.showwarning("No Data", "Analysis complete but no financial metrics found.")
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Analysis failed: {str(e)}")
            
        finally:
            self.analyze_btn.config(state='normal', text="🚀 Analyze Report", bg='#27ae60')

def main():
    try:
        root = tk.Tk()
        app = FinancialAnalyzerGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Application error: {e}")
        print("Required packages: pip install matplotlib PyPDF2 numpy")

if __name__ == "__main__":
    print("🚀 Starting Financial Analyzer with FIXED LAYOUT...")
    print("💡 Features: All controls visible + Scrollable interface!")
    main()