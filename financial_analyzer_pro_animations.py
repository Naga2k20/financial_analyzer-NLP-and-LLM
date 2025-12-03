import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import PyPDF2
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import numpy as np
import os

class FinancialAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📊 Financial Report Analyzer - 4 GRAPH TYPES")
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
        # Main container
        main_container = tk.Frame(self.root, bg='#2c3e50')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left panel for controls
        left_panel = tk.Frame(main_container, bg='#34495e', width=300)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Right panel for graph (LARGE)
        right_panel = tk.Frame(main_container, bg='#2c3e50')
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Left panel content
        title_label = tk.Label(left_panel, 
                              text="📊 Financial Analyzer", 
                              font=('Arial', 16, 'bold'), 
                              fg='white', bg='#34495e')
        title_label.pack(pady=20)
        
        # File selection
        file_frame = tk.LabelFrame(left_panel, text="File Selection", 
                                  font=('Arial', 10, 'bold'),
                                  bg='#34495e', fg='white',
                                  padx=10, pady=10)
        file_frame.pack(fill='x', padx=10, pady=10)
        
        self.file_label = tk.Label(file_frame, 
                                  text="No file selected", 
                                  font=('Arial', 9), 
                                  bg='#34495e', fg='#bdc3c7',
                                  wraplength=250)
        self.file_label.pack(pady=5)
        
        select_btn = tk.Button(file_frame, 
                              text="📁 Select PDF File", 
                              command=self.select_file,
                              font=('Arial', 10),
                              bg='#3498db', fg='white',
                              padx=10, pady=8,
                              width=15)
        select_btn.pack(pady=5)
        
        self.analyze_btn = tk.Button(file_frame, 
                                    text="🚀 Analyze Report", 
                                    command=self.analyze_report,
                                    font=('Arial', 11, 'bold'),
                                    bg='#27ae60', fg='white',
                                    padx=10, pady=10,
                                    width=15,
                                    state='disabled')
        self.analyze_btn.pack(pady=5)
        
        # Graph Type Selection
        graph_frame = tk.LabelFrame(left_panel, text="📈 Graph Types", 
                                  font=('Arial', 10, 'bold'),
                                  bg='#34495e', fg='white',
                                  padx=10, pady=10)
        graph_frame.pack(fill='x', padx=10, pady=10)
        
        graph_label = tk.Label(graph_frame, text="Select Graph Type:", 
                             font=('Arial', 9, 'bold'), 
                             bg='#34495e', fg='white')
        graph_label.pack(anchor='w', pady=5)
        
        self.graph_var = tk.StringVar(value="bar")
        
        graph_types = [
            ("📊 Bar Chart", "bar"),
            ("🥧 Pie Chart", "pie"),
            ("↔️ Horizontal Bars", "horizontal"),
            ("📈 Line Chart", "line")
        ]
        
        for text, value in graph_types:
            rb = tk.Radiobutton(graph_frame, text=text, variable=self.graph_var,
                               value=value, font=('Arial', 8),
                               bg='#34495e', fg='white', selectcolor='#2c3e50',
                               command=self.change_graph_type)
            rb.pack(anchor='w', pady=2)
        
        # Animation controls
        anim_frame = tk.LabelFrame(left_panel, text="🎬 Animations", 
                                  font=('Arial', 10, 'bold'),
                                  bg='#34495e', fg='white',
                                  padx=10, pady=10)
        anim_frame.pack(fill='x', padx=10, pady=10)
        
        # Animation type
        anim_label = tk.Label(anim_frame, text="Animation Style:", 
                             font=('Arial', 9, 'bold'), 
                             bg='#34495e', fg='white')
        anim_label.pack(anchor='w', pady=5)
        
        self.anim_var = tk.StringVar(value="smooth_grow")
        
        anim_types = [
            ("🌟 Smooth Growth", "smooth_grow"),
            ("💫 Particle Flow", "particle_flow"),
            ("🌈 Gradient Fill", "gradient_fill"),
            ("🌀 Spiral Reveal", "spiral_reveal")
        ]
        
        for text, value in anim_types:
            rb = tk.Radiobutton(anim_frame, text=text, variable=self.anim_var,
                               value=value, font=('Arial', 8),
                               bg='#34495e', fg='white', selectcolor='#2c3e50',
                               command=self.safe_update_animation)
            rb.pack(anchor='w', pady=2)
        
        # Animation control buttons
        btn_frame = tk.Frame(anim_frame, bg='#34495e')
        btn_frame.pack(fill='x', pady=10)
        
        self.start_btn = tk.Button(btn_frame, text="▶ Start Animation", 
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
        
        # Speed control
        speed_frame = tk.Frame(anim_frame, bg='#34495e')
        speed_frame.pack(fill='x', pady=5)
        
        speed_label = tk.Label(speed_frame, text="Animation Speed:", 
                              font=('Arial', 8, 'bold'), 
                              bg='#34495e', fg='white')
        speed_label.pack(side='left')
        
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = tk.Scale(speed_frame, from_=0.5, to=2.0, resolution=0.1,
                              orient='horizontal', variable=self.speed_var,
                              length=120, showvalue=True,
                              bg='#34495e', fg='white', highlightbackground='#34495e')
        speed_scale.pack(side='right')
        
        # Results section in left panel
        results_frame = tk.LabelFrame(left_panel, text="Analysis Results", 
                                     font=('Arial', 10, 'bold'),
                                     bg='#34495e', fg='white',
                                     padx=10, pady=10)
        results_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create notebook for results
        self.results_notebook = ttk.Notebook(results_frame)
        self.results_notebook.pack(fill='both', expand=True)
        
        # Summary tab
        summary_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(summary_frame, text="Summary")
        
        self.summary_text = scrolledtext.ScrolledText(summary_frame, 
                                                     wrap=tk.WORD,
                                                     font=('Arial', 8),
                                                     height=8)
        self.summary_text.pack(fill='both', expand=True)
        
        # Metrics tab
        metrics_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(metrics_frame, text="Metrics")
        
        self.metrics_text = scrolledtext.ScrolledText(metrics_frame, 
                                                     wrap=tk.WORD,
                                                     font=('Arial', 8),
                                                     height=8)
        self.metrics_text.pack(fill='both', expand=True)
        
        # Right panel - GRAPH AREA
        graph_container = tk.Frame(right_panel, bg='#1a1a1a', relief='sunken', bd=2)
        graph_container.pack(fill='both', expand=True)
        
        # Create initial graph placeholder
        self.setup_initial_graph(graph_container)
        
    def setup_initial_graph(self, parent):
        """Setup initial graph placeholder"""
        self.graph_frame = tk.Frame(parent, bg='#1a1a1a')
        self.graph_frame.pack(fill='both', expand=True)
        
        placeholder = tk.Label(self.graph_frame, 
                              text="📈\n4 Different Graph Types\n\n• Bar Charts\n• Pie Charts\n• Horizontal Bars\n• Line Charts\n\nSelect a PDF file to begin!",
                              font=('Arial', 14),
                              fg='#7f8c8d',
                              bg='#1a1a1a',
                              justify='center')
        placeholder.pack(expand=True)
        
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
            'ebitda': r'ebitda.*?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
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
    
    def create_bar_chart(self):
        """Create bar chart"""
        names = [name.replace('_', ' ').title() for name in self.metrics.keys()]
        values = list(self.metrics.values())
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        bars = self.ax.bar(names, [0]*len(values), color=colors[:len(values)], alpha=0.9, edgecolor='white', linewidth=2)
        
        def ease_out_quart(x):
            return 1 - (1 - x) ** 4
        
        def animate(frame):
            for i, bar in enumerate(bars):
                progress = min(frame / 60, 1.0)
                eased_progress = ease_out_quart(progress)
                current_height = values[i] * eased_progress
                bar.set_height(current_height)
                
                # Smooth color transition
                if progress < 1.0:
                    alpha = 0.7 + 0.3 * progress
                    bar.set_alpha(alpha)
                
                # Update labels with smooth fade-in
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
    
    def create_pie_chart_animation(self):
        """Create animated pie chart"""
        names = [name.replace('_', ' ').title() for name in self.metrics.keys()]
        values = list(self.metrics.values())
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        
        # Start with small pie
        wedges, texts, autotexts = self.ax.pie([1]*len(values), labels=names, colors=colors[:len(values)], 
                                              startangle=90, radius=0.3)
        
        def animate(frame):
            progress = min(frame / 80, 1.0)
            current_values = [v * progress for v in values]
            
            # Update pie chart
            for i, wedge in enumerate(wedges):
                wedge.set_theta1(90)
                wedge.set_theta2(90 + 360 * (current_values[i] / sum(values)) if sum(values) > 0 else 0)
                wedge.set_radius(0.3 + 0.4 * progress)  # Grow radius
            
            # Update percentage labels
            for i, autotext in enumerate(autotexts):
                if sum(current_values) > 0:
                    percentage = (current_values[i] / sum(current_values)) * 100
                    autotext.set_text(f'{percentage:.1f}%')
                    autotext.set_fontsize(9 + 3 * progress)
                autotext.set_alpha(progress)
            
            return wedges + autotexts
        
        interval = int(50 / self.speed_var.get())
        return animation.FuncAnimation(self.fig, animate, frames=100, interval=interval, blit=False, repeat=True)
    
    def create_horizontal_bar_animation(self):
        """Create horizontal bar chart animation"""
        names = [name.replace('_', ' ').title() for name in self.metrics.keys()]
        values = list(self.metrics.values())
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        y_pos = np.arange(len(names))
        bars = self.ax.barh(y_pos, [0]*len(values), color=colors[:len(values)], alpha=0.9, edgecolor='white', linewidth=2)
        
        def animate(frame):
            for i, bar in enumerate(bars):
                progress = min(frame / 60, 1.0)
                current_width = values[i] * progress
                bar.set_width(current_width)
                bar.set_alpha(0.7 + 0.3 * progress)
                
                # Update labels
                for txt in self.ax.texts:
                    txt.remove()
                
                for i, bar in enumerate(bars):
                    width = bar.get_width()
                    if width > values[i] * 0.1:
                        self.ax.text(width + (width * 0.01), bar.get_y() + bar.get_height()/2.,
                                   f'${width:,.0f}', ha='left', va='center', 
                                   fontweight='bold', fontsize=10, color='white',
                                   alpha=progress)
            return bars
        
        interval = int(50 / self.speed_var.get())
        return animation.FuncAnimation(self.fig, animate, frames=100, interval=interval, blit=False, repeat=True)
    
    def create_line_chart_animation(self):
        """Create animated line chart"""
        names = [name.replace('_', ' ').title() for name in self.metrics.keys()]
        values = list(self.metrics.values())
        
        x_pos = np.arange(len(names))
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        
        # Create bars as background
        bars = self.ax.bar(x_pos, values, alpha=0.3, color=colors[:len(values)])
        
        # Create line
        line, = self.ax.plot([], [], 'o-', color='white', linewidth=3, markersize=8, alpha=0)
        points = self.ax.scatter([], [], s=100, color=colors[:len(values)], alpha=0, edgecolors='white', linewidths=2)
        
        def animate(frame):
            progress = min(frame / 80, 1.0)
            
            # Animate line
            current_points = int(len(x_pos) * progress)
            if current_points > 0:
                line_x = x_pos[:current_points]
                line_y = values[:current_points]
                line.set_data(line_x, line_y)
                line.set_alpha(progress)
                
                # Animate points
                points.set_offsets(np.column_stack([line_x, line_y]))
                points.set_alpha(progress)
                points.set_sizes([100] * len(line_x))
            
            # Fade in bars
            for bar in bars:
                bar.set_alpha(0.1 + 0.2 * progress)
            
            return [line, points] + bars
        
        interval = int(50 / self.speed_var.get())
        return animation.FuncAnimation(self.fig, animate, frames=100, interval=interval, blit=False, repeat=True)
    
    def create_particle_flow_animation(self):
        """Create particle flow animation"""
        names = [name.replace('_', ' ').title() for name in self.metrics.keys()]
        values = list(self.metrics.values())
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        
        if self.graph_var.get() == "bar":
            bars = self.ax.bar(names, values, color=colors[:len(values)], alpha=0.8)
        elif self.graph_var.get() == "horizontal":
            y_pos = np.arange(len(names))
            bars = self.ax.barh(y_pos, values, color=colors[:len(values)], alpha=0.8)
        else:
            bars = self.ax.bar(names, values, color=colors[:len(values)], alpha=0.8)
        
        # Create particles
        particles = []
        for i, value in enumerate(values):
            for j in range(5):
                if self.graph_var.get() == "horizontal":
                    particles.append({
                        'bar_idx': i,
                        'x': np.random.uniform(0, value),
                        'y': i + np.random.uniform(-0.2, 0.2),
                        'speed': np.random.uniform(0.2, 0.8),
                        'size': np.random.uniform(20, 60),
                        'color': colors[i % len(colors)]
                    })
                else:
                    particles.append({
                        'bar_idx': i,
                        'x': i + np.random.uniform(-0.2, 0.2),
                        'y': np.random.uniform(0, value),
                        'speed': np.random.uniform(0.2, 0.8),
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
                if self.graph_var.get() == "horizontal":
                    p['x'] += p['speed'] * 0.3
                    if p['x'] > values[p['bar_idx']]:
                        p['x'] = 0
                else:
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
        self.fig, self.ax = plt.subplots(figsize=(14, 8))
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
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
        
        if graph_type == "bar":
            # Bar Chart
            bars = self.ax.bar(names, values, color=colors[:len(values)], alpha=0.8, edgecolor='white', linewidth=1)
            self.ax.set_ylim(0, max(values) * 1.2)
            self.ax.set_title('FINANCIAL METRICS - BAR CHART', fontsize=16, fontweight='bold', pad=20)
            self.ax.set_ylabel('Amount ($)', fontsize=12, fontweight='bold')
            self.ax.tick_params(axis='x', colors='white', labelsize=11, rotation=45)
            
            # Add value labels
            for i, bar in enumerate(bars):
                height = bar.get_height()
                self.ax.text(bar.get_x() + bar.get_width()/2., height + (height * 0.01),
                           f'${height:,.0f}', ha='center', va='bottom', 
                           fontweight='bold', fontsize=10, color='white')
                
        elif graph_type == "pie":
            # Pie Chart
            wedges, texts, autotexts = self.ax.pie(values, labels=names, colors=colors[:len(values)], 
                                                  autopct='%1.1f%%', startangle=90)
            self.ax.set_title('FINANCIAL METRICS - PIE CHART', fontsize=16, fontweight='bold', pad=20)
            
            # Style percentage labels
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(11)
                
        elif graph_type == "horizontal":
            # Horizontal Bar Chart
            y_pos = np.arange(len(names))
            bars = self.ax.barh(y_pos, values, color=colors[:len(values)], alpha=0.8, edgecolor='white', linewidth=1)
            self.ax.set_xlim(0, max(values) * 1.2)
            self.ax.set_title('FINANCIAL METRICS - HORIZONTAL VIEW', fontsize=16, fontweight='bold', pad=20)
            self.ax.set_xlabel('Amount ($)', fontsize=12, fontweight='bold')
            self.ax.set_yticks(y_pos)
            self.ax.set_yticklabels(names)
            
            # Add value labels
            for i, bar in enumerate(bars):
                width = bar.get_width()
                self.ax.text(width + (width * 0.01), bar.get_y() + bar.get_height()/2.,
                           f'${width:,.0f}', ha='left', va='center', 
                           fontweight='bold', fontsize=10, color='white')
                
        elif graph_type == "line":
            # Line Chart
            x_pos = np.arange(len(names))
            self.ax.plot(x_pos, values, 'o-', color='white', linewidth=3, markersize=10)
            self.ax.set_ylim(0, max(values) * 1.2)
            self.ax.set_title('FINANCIAL METRICS - LINE CHART', fontsize=16, fontweight='bold', pad=20)
            self.ax.set_ylabel('Amount ($)', fontsize=12, fontweight='bold')
            self.ax.set_xticks(x_pos)
            self.ax.set_xticklabels(names, rotation=45)
            
            # Add value labels
            for i, (x, y) in enumerate(zip(x_pos, values)):
                self.ax.annotate(f'${y:,.0f}', (x, y), textcoords="offset points", 
                               xytext=(0,10), ha='center', fontweight='bold', 
                               color='white', fontsize=10)
        
        # Common styling
        self.ax.grid(True, alpha=0.2, color='white', linestyle='--')
        self.ax.tick_params(axis='y', colors='white', labelsize=11)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def change_graph_type(self):
        """Change graph type when radio button is clicked"""
        if hasattr(self, 'metrics') and self.metrics:
            self.setup_graph()
            # Restart animation if it was running
            if self.animation_running:
                self.safe_start_animation()
    
    def safe_start_animation(self):
        """Safely start animation with error handling"""
        try:
            # Stop any existing animation first
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
            graph_type = self.graph_var.get()
            
            # Clear any existing text
            for txt in self.ax.texts:
                txt.remove()
            
            # Choose animation based on graph type and animation style
            if anim_type == "smooth_grow":
                if graph_type == "bar":
                    self.current_animation = self.create_bar_chart()
                elif graph_type == "pie":
                    self.current_animation = self.create_pie_chart_animation()
                elif graph_type == "horizontal":
                    self.current_animation = self.create_horizontal_bar_animation()
                elif graph_type == "line":
                    self.current_animation = self.create_line_chart_animation()
                    
            elif anim_type == "particle_flow":
                self.current_animation = self.create_particle_flow_animation()
                
            elif anim_type == "gradient_fill":
                self.current_animation = self.create_bar_chart()  # Use bar animation for gradient
                
            elif anim_type == "spiral_reveal":
                self.current_animation = self.create_bar_chart()  # Use bar animation for spiral
            
            if self.current_animation:
                self.animation_running = True
                self.start_btn.config(state='disabled', bg='#95a5a6')
                self.stop_btn.config(state='normal', bg='#e74c3c')
                self.canvas.draw_idle()
            else:
                messagebox.showerror("Error", "Animation not available for this graph type.")
                
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
            
            # Display results
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(1.0, f"Pages processed: {total_pages}\n\n{summary}")
            
            self.metrics_text.delete(1.0, tk.END)
            if self.metrics:
                metrics_text = "✅ Financial Metrics Found:\n\n"
                for metric, value in self.metrics.items():
                    metrics_text += f"• {metric.replace('_', ' ').title()}: ${value:,.2f}\n"
                self.metrics_text.insert(1.0, metrics_text)
            else:
                self.metrics_text.insert(1.0, "❌ No financial metrics detected.")
            
            # Setup graph
            if self.metrics:
                self.setup_graph()
                # Enable animation controls
                self.start_btn.config(state='normal')
                self.stop_btn.config(state='disabled')
                
                messagebox.showinfo("Success", 
                                  f"Analysis complete!\n\nFound {len(self.metrics)} financial metrics.\n\nTry the 4 different graph types!")
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
    print("🚀 Starting Financial Analyzer with 4 GRAPH TYPES...")
    print("💡 Features: Bar, Pie, Horizontal, and Line charts!")
    main()