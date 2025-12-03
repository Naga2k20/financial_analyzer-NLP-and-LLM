import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import PyPDF2
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import numpy as np
import os
from matplotlib import gridspec

class FinancialAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📊 Financial Report Analyzer")
        self.root.geometry("1400x900")  # Larger window
        self.root.configure(bg='#f8f9fa')
        
        # Make window resizable
        self.root.minsize(1200, 800)
        
        self.animation_running = False
        self.current_animation = None
        self.current_canvas = None
        self.setup_ui()
        
    def setup_ui(self):
        # Create main frame
        main_frame = tk.Frame(self.root, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header (smaller to give more space to graphs)
        header_frame = tk.Frame(main_frame, bg='#2c3e50', height=80)
        header_frame.pack(fill='x', pady=(0, 15))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, 
                              text="📊 FINANCIAL REPORT ANALYZER", 
                              font=('Arial', 18, 'bold'), 
                              fg='white', bg='#2c3e50')
        title_label.pack(pady=(15, 5))
        
        subtitle_label = tk.Label(header_frame, 
                                 text="AI-Powered Financial Analysis with Large Animated Visualizations", 
                                 font=('Arial', 10), 
                                 fg='#ecf0f1', bg='#2c3e50')
        subtitle_label.pack(pady=(0, 15))
        
        # Upload Section (compact)
        upload_frame = tk.LabelFrame(main_frame, 
                                    text=" 📁 File Selection ", 
                                    font=('Arial', 11, 'bold'),
                                    bg='#f8f9fa', fg='#2c3e50',
                                    padx=15, pady=15)
        upload_frame.pack(fill='x', pady=(0, 15))
        
        # File selection row
        file_row = tk.Frame(upload_frame, bg='#f8f9fa')
        file_row.pack(fill='x', pady=5)
        
        self.file_label = tk.Label(file_row, 
                                  text="No file selected", 
                                  font=('Arial', 9), 
                                  bg='#f8f9fa', fg='#7f8c8d',
                                  wraplength=400, justify='left')
        self.file_label.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        select_btn = tk.Button(file_row, 
                              text="📂 Select PDF File", 
                              command=self.select_file,
                              font=('Arial', 9, 'bold'),
                              bg='#3498db', fg='white',
                              padx=12, pady=6,
                              relief='raised', bd=2,
                              cursor='hand2')
        select_btn.pack(side='right')
        
        # Analyze button row
        analyze_row = tk.Frame(upload_frame, bg='#f8f9fa')
        analyze_row.pack(fill='x', pady=5)
        
        self.analyze_btn = tk.Button(analyze_row, 
                                    text="🚀 Analyze Report", 
                                    command=self.analyze_report,
                                    font=('Arial', 11, 'bold'),
                                    bg='#27ae60', fg='white',
                                    padx=18, pady=8,
                                    state='disabled',
                                    cursor='hand2')
        self.analyze_btn.pack(pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(upload_frame, mode='indeterminate', length=300)
        
        # Results Section - MAKING THIS MUCH LARGER
        results_frame = tk.LabelFrame(main_frame, 
                                     text=" 📊 Analysis Results ", 
                                     font=('Arial', 12, 'bold'),
                                     bg='#f8f9fa', fg='#2c3e50',
                                     padx=15, pady=15)
        results_frame.pack(fill='both', expand=True)
        
        # Create Notebook for tabs
        style = ttk.Style()
        style.configure('TNotebook', background='#f8f9fa')
        style.configure('TNotebook.Tab', font=('Arial', 10, 'bold'))
        
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.pack(fill='both', expand=True, pady=10)
        
        # Summary Tab (compact)
        summary_frame = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(summary_frame, text="📋 Summary")
        
        summary_label = tk.Label(summary_frame, 
                                text="Document Summary:", 
                                font=('Arial', 11, 'bold'),
                                bg='#f8f9fa', fg='#2c3e50')
        summary_label.pack(anchor='w', pady=(0, 8))
        
        self.summary_text = scrolledtext.ScrolledText(summary_frame, 
                                                     wrap=tk.WORD, 
                                                     font=('Arial', 10),
                                                     width=60, 
                                                     height=8,  # Smaller height
                                                     bg='white', 
                                                     fg='#2c3e50',
                                                     relief='solid', 
                                                     bd=1)
        self.summary_text.pack(fill='both', expand=True)
        
        # Metrics Tab (compact)
        metrics_frame = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(metrics_frame, text="💰 Metrics")
        
        metrics_label = tk.Label(metrics_frame, 
                                text="Extracted Financial Data:", 
                                font=('Arial', 11, 'bold'),
                                bg='#f8f9fa', fg='#2c3e50')
        metrics_label.pack(anchor='w', pady=(0, 8))
        
        self.metrics_text = scrolledtext.ScrolledText(metrics_frame, 
                                                     wrap=tk.WORD, 
                                                     font=('Arial', 10),
                                                     width=60, 
                                                     height=8,  # Smaller height
                                                     bg='white', 
                                                     fg='#2c3e50',
                                                     relief='solid', 
                                                     bd=1)
        self.metrics_text.pack(fill='both', expand=True)
        
        # Chart Tab - MAKING THIS VERY LARGE
        chart_frame = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(chart_frame, text="📈 ANIMATED VISUALIZATIONS")
        
        # Animation controls frame (compact at top)
        controls_frame = tk.Frame(chart_frame, bg='#f8f9fa', height=40)
        controls_frame.pack(fill='x', pady=(0, 5))
        controls_frame.pack_propagate(False)
        
        # Animation type selection
        anim_label = tk.Label(controls_frame, text="Animation Style:", 
                             font=('Arial', 10, 'bold'), bg='#f8f9fa')
        anim_label.pack(side='left', padx=(10, 10))
        
        self.anim_var = tk.StringVar(value="growing_bars")
        anim_options = [
            ("Growing Bars", "growing_bars"),
            ("Pulsing Chart", "pulsing"),
            ("Sequential Reveal", "sequential"),
            ("Rotating 3D", "rotating"),
            ("Financial Flow", "flow")
        ]
        
        for text, mode in anim_options:
            rb = tk.Radiobutton(controls_frame, text=text, variable=self.anim_var, 
                               value=mode, font=('Arial', 9), bg='#f8f9fa',
                               command=self.change_animation)
            rb.pack(side='left', padx=5)
        
        # Animation control buttons
        button_frame = tk.Frame(controls_frame, bg='#f8f9fa')
        button_frame.pack(side='right', padx=10)
        
        self.anim_btn = tk.Button(button_frame, text="▶️ Start Animation", 
                                 command=self.toggle_animation,
                                 font=('Arial', 9, 'bold'),
                                 bg='#3498db', fg='white',
                                 padx=10, pady=4)
        self.anim_btn.pack(side='left', padx=5)
        
        # Fullscreen toggle button
        self.fullscreen_btn = tk.Button(button_frame, text="⛶ Fullscreen", 
                                       command=self.toggle_fullscreen_chart,
                                       font=('Arial', 9, 'bold'),
                                       bg='#9b59b6', fg='white',
                                       padx=10, pady=4)
        self.fullscreen_btn.pack(side='left', padx=5)
        
        # MAIN CHART FRAME - THIS IS WHERE THE LARGE GRAPH GOES
        self.chart_container = tk.Frame(chart_frame, bg='#1a1a1a', relief='sunken', bd=2)
        self.chart_container.pack(fill='both', expand=True, pady=5)
        
        # Status bar
        status_frame = tk.Frame(main_frame, bg='#34495e', height=25)
        status_frame.pack(fill='x', pady=(10, 0))
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, 
                                    text="Ready to analyze financial reports", 
                                    font=('Arial', 9), 
                                    fg='white', bg='#34495e')
        self.status_label.pack(side='left', padx=10)
        
        # Chart size info
        self.size_label = tk.Label(status_frame, 
                                  text="Chart Size: Large", 
                                  font=('Arial', 9), 
                                  fg='#ecf0f1', bg='#34495e')
        self.size_label.pack(side='right', padx=10)
        
    def toggle_fullscreen_chart(self):
        """Toggle between normal and fullscreen chart"""
        if hasattr(self, 'is_fullscreen'):
            self.is_fullscreen = not self.is_fullscreen
        else:
            self.is_fullscreen = True
            
        if self.is_fullscreen:
            # Store current geometry
            self.normal_geometry = self.root.geometry()
            # Fullscreen
            self.root.attributes('-fullscreen', True)
            self.fullscreen_btn.config(text="❎ Exit Fullscreen", bg='#e74c3c')
            self.size_label.config(text="Chart Size: Fullscreen")
        else:
            # Exit fullscreen
            self.root.attributes('-fullscreen', False)
            self.root.geometry(self.normal_geometry)
            self.fullscreen_btn.config(text="⛶ Fullscreen", bg='#9b59b6')
            self.size_label.config(text="Chart Size: Large")
        
        # Refresh chart to fit new size
        if hasattr(self, 'metrics'):
            self.root.after(100, lambda: self.create_animated_chart(self.metrics))
    
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Financial Report PDF",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.file_path = file_path
            filename = os.path.basename(file_path)
            self.file_label.config(text=f"Selected: {filename}", fg='#27ae60')
            self.analyze_btn.config(state='normal', bg='#27ae60')
            self.status_label.config(text=f"Ready to analyze: {filename}")
            
            # Clear previous results
            self.summary_text.delete(1.0, tk.END)
            self.metrics_text.delete(1.0, tk.END)
            self.clear_chart_container()
            
            # Reset notebook to first tab
            self.notebook.select(0)
            self.animation_running = False
    
    def clear_chart_container(self):
        """Clear the chart container completely"""
        for widget in self.chart_container.winfo_children():
            widget.destroy()
        
        if self.current_animation:
            self.current_animation.event_source.stop()
            self.current_animation = None
        
        if self.current_canvas:
            self.current_canvas.get_tk_widget().destroy()
            self.current_canvas = None
    
    def extract_text_from_pdf(self, file_path):
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                total_pages = len(pdf_reader.pages)
                
                for page_num in range(total_pages):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += f"--- Page {page_num + 1} ---\n{page_text}\n\n"
                
                if text.strip():
                    return text, total_pages
                else:
                    return "No readable text found in PDF", 0
                    
        except Exception as e:
            return f"Error reading PDF: {str(e)}", 0
    
    def extract_financial_metrics(self, text):
        """Extract financial metrics from text"""
        metrics = {}
        
        financial_terms = {
            'revenue': [
                r'revenue[\s\S]{0,200}?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'sales[\s\S]{0,200}?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'total revenue[\s\S]{0,200}?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
            ],
            'net_income': [
                r'net income[\s\S]{0,200}?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'net profit[\s\S]{0,200}?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'net earnings[\s\S]{0,200}?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
            ],
            'assets': [
                r'total assets[\s\S]{0,200}?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'assets[\s\S]{0,200}?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
            ],
            'profit': [
                r'profit[\s\S]{0,200}?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'gross profit[\s\S]{0,200}?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
            ],
            'ebitda': [
                r'ebitda[\s\S]{0,200}?[\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
            ]
        }
        
        for metric, patterns in financial_terms.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    try:
                        value_str = matches[0].replace('$', '').replace(',', '').strip()
                        if value_str:
                            metrics[metric] = float(value_str)
                            break
                    except (ValueError, IndexError):
                        continue
        
        return metrics
    
    def generate_summary(self, text):
        """Generate summary from text"""
        if len(text) < 100:
            return "Document too short for meaningful analysis."
        
        sentences = []
        for line in text.split('\n'):
            line = line.strip()
            if line and not line.startswith('--- Page') and len(line) > 30:
                line_sentences = [s.strip() for s in line.split('.') if len(s.strip()) > 20]
                sentences.extend(line_sentences)
        
        if sentences:
            summary = '. '.join(sentences[:5]) + '.'
            if len(summary) > 500:
                summary = summary[:497] + '...'
        else:
            summary = "Content extracted but no clear sentence structure found."
        
        return summary
    
    def create_growing_bars_animation(self, metrics, fig, ax):
        """Create growing bars animation"""
        names = [name.replace('_', ' ').title() for name in metrics.keys()]
        values = list(metrics.values())
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c']
        
        bars = ax.bar(names, [0]*len(values), color=colors[:len(values)], alpha=0.8, edgecolor='white', linewidth=2)
        ax.set_ylim(0, max(values) * 1.2)
        ax.set_title('FINANCIAL METRICS - GROWING ANIMATION', fontsize=16, fontweight='bold', pad=20, color='white')
        ax.set_ylabel('Amount ($)', fontsize=14, fontweight='bold', color='white')
        ax.set_xlabel('Financial Metrics', fontsize=14, fontweight='bold', color='white')
        ax.grid(True, alpha=0.3, color='white', linestyle='--')
        ax.set_axisbelow(True)
        
        # Set tick colors
        ax.tick_params(axis='x', colors='white', labelsize=12, rotation=45)
        ax.tick_params(axis='y', colors='white', labelsize=12)
        
        def animate(frame):
            for i, bar in enumerate(bars):
                target_height = values[i]
                current_height = min(bar.get_height() + target_height/15, target_height)
                bar.set_height(current_height)
                
                # Update value labels
                for txt in ax.texts:
                    txt.remove()
                
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    if height > 0:  # Only show label when bar has height
                        ax.text(bar.get_x() + bar.get_width()/2., height + (height * 0.02),
                               f'${height:,.0f}', ha='center', va='bottom', 
                               fontweight='bold', fontsize=11, color='white',
                               bbox=dict(boxstyle="round,pad=0.3", facecolor='#2c3e50', alpha=0.8))
            
            return bars
        
        return animation.FuncAnimation(fig, animate, frames=100, interval=40, blit=False, repeat=True)
    
    def create_pulsing_animation(self, metrics, fig, ax):
        """Create pulsing chart animation"""
        names = [name.replace('_', ' ').title() for name in metrics.keys()]
        values = list(metrics.values())
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
        
        bars = ax.bar(names, values, color=colors[:len(values)], alpha=0.9, edgecolor='white', linewidth=2)
        ax.set_ylim(0, max(values) * 1.2)
        ax.set_title('FINANCIAL METRICS - PULSING ANIMATION', fontsize=16, fontweight='bold', pad=20, color='white')
        ax.set_ylabel('Amount ($)', fontsize=14, fontweight='bold', color='white')
        ax.grid(True, alpha=0.3, color='white', linestyle='--')
        
        ax.tick_params(axis='x', colors='white', labelsize=12, rotation=45)
        ax.tick_params(axis='y', colors='white', labelsize=12)
        
        def animate(frame):
            pulse = 0.6 + 0.4 * np.sin(frame * 0.2)
            for i, bar in enumerate(bars):
                bar.set_alpha(0.7 + 0.3 * pulse)
                bar.set_edgecolor('white')
                bar.set_linewidth(1 + pulse)
            
            # Pulsing value labels
            for txt in ax.texts:
                txt.remove()
            
            for i, bar in enumerate(bars):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + (height * 0.02),
                       f'${height:,.0f}', ha='center', va='bottom', 
                       fontweight='bold', fontsize=11, color='white',
                       alpha=0.8 + 0.2 * pulse,
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='#2c3e50', alpha=0.8))
            
            return bars
        
        return animation.FuncAnimation(fig, animate, frames=100, interval=50, blit=False, repeat=True)
    
    def create_animated_chart(self, metrics):
        """Create animated financial chart with LARGE size"""
        if not metrics:
            no_data_label = tk.Label(self.chart_container, 
                                    text="No financial metrics found to visualize.\n\nTry using a standard financial report with clear numbers.",
                                    font=('Arial', 14), 
                                    fg='#7f8c8d',
                                    bg='#1a1a1a',
                                    justify='center')
            no_data_label.pack(expand=True, fill='both', pady=50)
            return
        
        try:
            # Clear previous chart
            self.clear_chart_container()
            
            # Create LARGE figure - using most of the container space
            fig = plt.Figure(figsize=(14, 8), dpi=100)  # Much larger figure
            fig.patch.set_facecolor('#1a1a1a')
            
            # Create axis that uses most of the figure space
            ax = fig.add_subplot(111)
            ax.set_facecolor('#2c3e50')
            
            # Set all text to white for better visibility
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.title.set_color('white')
            
            # Get selected animation style
            anim_style = self.anim_var.get()
            
            # Create animation based on style
            if anim_style == "growing_bars":
                anim = self.create_growing_bars_animation(metrics, fig, ax)
            elif anim_style == "pulsing":
                anim = self.create_pulsing_animation(metrics, fig, ax)
            else:
                anim = self.create_growing_bars_animation(metrics, fig, ax)
            
            # Embed LARGE chart in tkinter
            self.current_canvas = FigureCanvasTkAgg(fig, self.chart_container)
            self.current_canvas.draw()
            
            # Pack canvas to fill entire container
            self.current_canvas.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)
            
            # Add navigation toolbar
            from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
            toolbar = NavigationToolbar2Tk(self.current_canvas, self.chart_container)
            toolbar.update()
            toolbar.pack(side='bottom', fill='x')
            
            # Store animation reference
            self.current_animation = anim
            self.animation_running = True
            self.anim_btn.config(text="⏸️ Stop Animation", bg='#e74c3c')
            
            # Update status
            self.status_label.config(text="Large animated chart created! Switch to Visualizations tab.")
            
        except Exception as e:
            error_label = tk.Label(self.chart_container, 
                                  text=f"Animation error: {str(e)}", 
                                  font=('Arial', 12), 
                                  fg='#e74c3c',
                                  bg='#1a1a1a')
            error_label.pack(expand=True, fill='both', pady=50)
    
    def toggle_animation(self):
        """Toggle animation play/pause"""
        if self.current_animation:
            if self.animation_running:
                self.current_animation.pause()
                self.animation_running = False
                self.anim_btn.config(text="▶️ Start Animation", bg='#3498db')
            else:
                self.current_animation.resume()
                self.animation_running = True
                self.anim_btn.config(text="⏸️ Stop Animation", bg='#e74c3c')
    
    def change_animation(self):
        """Change animation style"""
        if hasattr(self, 'metrics'):
            self.create_animated_chart(self.metrics)
    
    def analyze_report(self):
        if not hasattr(self, 'file_path'):
            messagebox.showerror("Error", "Please select a PDF file first.")
            return
        
        self.progress.pack(pady=10)
        self.progress.start(10)
        self.analyze_btn.config(state='disabled', bg='#95a5a6')
        self.status_label.config(text="Analyzing document...")
        self.root.update()
        
        try:
            text, total_pages = self.extract_text_from_pdf(self.file_path)
            self.status_label.config(text=f"Processing {total_pages} pages...")
            self.root.update()
            
            summary = self.generate_summary(text)
            metrics = self.extract_financial_metrics(text)
            self.metrics = metrics  # Store for animation changes
            
            # Display results in summary tab (compact)
            self.summary_text.delete(1.0, tk.END)
            summary_content = f"Document Analysis Summary:\n{'='*40}\n\n"
            summary_content += f"Pages processed: {total_pages}\n"
            summary_content += f"Text extracted: {len(text):,} characters\n\n"
            summary_content += f"Executive Summary:\n{'-'*20}\n{summary}"
            self.summary_text.insert(1.0, summary_content)
            
            # Display results in metrics tab (compact)
            self.metrics_text.delete(1.0, tk.END)
            metrics_content = f"Financial Metrics Analysis:\n{'='*40}\n\n"
            
            if metrics:
                metrics_content += "✅ Financial Metrics Found:\n\n"
                for metric, value in metrics.items():
                    metrics_content += f"• {metric.replace('_', ' ').title():<20}: ${value:,.2f}\n"
                metrics_content += f"\nTotal metrics extracted: {len(metrics)}"
            else:
                metrics_content += "❌ No financial metrics detected.\n\n"
                metrics_content += "Suggestions:\n"
                metrics_content += "• Use standard financial reports\n"
                metrics_content += "• Ensure documents contain clear financial numbers\n"
            
            self.metrics_text.insert(1.0, metrics_content)
            
            # Create LARGE animated chart
            self.create_animated_chart(metrics)
            
            # Switch to animation tab automatically
            self.notebook.select(2)
            
            if metrics:
                self.status_label.config(text=f"✅ Analysis complete! Found {len(metrics)} financial metrics. Check the large animated chart!")
            else:
                self.status_label.config(text="⚠️ Analysis complete but no financial metrics found.")
            
            messagebox.showinfo("Analysis Complete", 
                              f"Financial report analysis completed!\n\n"
                              f"Check the LARGE Animated Visualizations tab for full-screen charts!")
            
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            self.status_label.config(text=f"❌ {error_msg}")
            messagebox.showerror("Analysis Error", error_msg)
            
        finally:
            self.progress.stop()
            self.progress.pack_forget()
            self.analyze_btn.config(state='normal', bg='#27ae60')

def main():
    try:
        root = tk.Tk()
        app = FinancialAnalyzerGUI(root)
        
        # Center the window on screen
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        root.geometry('+%d+%d' % (x, y))
        
        root.mainloop()
        
    except Exception as e:
        print(f"Application error: {e}")
        print("Please make sure all required packages are installed:")
        print("pip install PyPDF2 matplotlib numpy")

if __name__ == "__main__":
    print("🚀 Starting Financial Report Analyzer with LARGE Animated Graphs...")
    print("📁 Select a PDF file to see full-size animated financial visualizations!")
    main()