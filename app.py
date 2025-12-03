from flask import Flask, render_template, request, jsonify
import os
import PyPDF2
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import socket

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

class FinancialReportAnalyzer:
    def extract_text_from_pdf(self, pdf_file):
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text if text.strip() else "No readable text found in PDF"
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
    
    def extract_financial_metrics(self, text):
        metrics = {}
        
        financial_terms = {
            'revenue': [r'revenue.*?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', r'sales.*?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'],
            'net_income': [r'net income.*?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', r'net profit.*?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'],
            'assets': [r'total assets.*?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'],
            'profit': [r'profit.*?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)']
        }
        
        for metric, patterns in financial_terms.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    try:
                        value = float(matches[0].replace(',', ''))
                        metrics[metric] = value
                        break
                    except:
                        continue
        return metrics
    
    def generate_summary(self, text):
        if len(text) < 100:
            return "Document too short for meaningful analysis."
        
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 30]
        if sentences:
            summary = '. '.join(sentences[:3]) + '.'
        else:
            summary = "Content extracted but no clear sentence structure found."
        return summary
    
    def create_chart(self, metrics):
        if not metrics:
            return None
            
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            names = [name.replace('_', ' ').title() for name in metrics.keys()]
            values = list(metrics.values())
            
            bars = ax.bar(names, values, color=['#3498db', '#2ecc71', '#e74c3c'])
            ax.set_title('Financial Metrics', fontweight='bold')
            ax.set_ylabel('Amount ($)')
            
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'${height:,.0f}', ha='center', va='bottom', fontweight='bold')
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            chart_data = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
            
            return chart_data
        except Exception as e:
            print(f"Chart error: {e}")
            return None

analyzer = FinancialReportAnalyzer()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename.lower().endswith('.pdf'):
        try:
            text = analyzer.extract_text_from_pdf(file)
            summary = analyzer.generate_summary(text)
            metrics = analyzer.extract_financial_metrics(text)
            chart = analyzer.create_chart(metrics)
            
            result = {
                'summary': summary,
                'metrics': metrics,
                'chart': chart,
                'status': 'success'
            }
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': f'Processing error: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Please upload a PDF file'}), 400

def find_available_port(start_port=5000, end_port=5010):
    """Find an available port in the range"""
    for port in range(start_port, end_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return port
        except OSError:
            continue
    return start_port  # Fallback

if __name__ == '__main__':
    # Find available port
    port = find_available_port()
    
    print("=" * 50)
    print("🚀 FINANCIAL REPORT ANALYZER")
    print("=" * 50)
    print(f"📍 Server starting on:")
    print(f"   http://localhost:{port}")
    print(f"   http://127.0.0.1:{port}")
    print(f"   http://0.0.0.0:{port}")
    print("📁 Upload PDF files to analyze")
    print("=" * 50)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=port, threaded=True)
    except Exception as e:
        print(f"Error: {e}")
        print("Trying alternative configuration...")
        app.run(debug=True, host='127.0.0.1', port=port)